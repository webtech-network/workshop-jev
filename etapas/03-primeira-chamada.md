# Etapa 3 — A primeira chamada

⏱ 25 min · 🔌 **usa a API** (poucas chamadas, por favor)

> **Objetivo:** entender o request antes de gastar uma chamada, depois fazer
> uma chamada de verdade e ler a resposta crua.

> ⚠️ **A chave é compartilhada pela turma.** O provedor devolve `429` sob
> carga. Siga os `--limit` desta etapa: **1**, depois **3**. Quem roda 100
> derruba o workshop para todos.

---

## 3.1 Olhe antes de pagar: `--dry-run`

O `evaluate.py` tem um modo que monta a requisição e imprime, **sem chamar
nada**. Use-o sempre que mexer na rubrica.

```bash
python3 evaluate.py --dry-run --sample sample-mini.jsonl
```

Role para o começo da saída. Você está vendo o corpo exato que iria para a rede:

```json
{
  "model": "typesafe-ai/jev",
  "state": "Titulo: ...\n\n<o texto da redação>",
  "questions": {
    "c1": { "type": "score", "instructions": "...", "criteria": ["...", "..."] },
    "c2": { ... }
  }
}
```

Três coisas para notar, e todas elas são contraintuitivas:

1. **Não existe `messages`.** Isto não é uma conversa. O texto avaliado vai
   num campo chamado **`state`** — "o estado do mundo sobre o qual você vai
   decidir".
2. **As 5 competências vão numa requisição só.** O Jev avalia as 5 perguntas
   em paralelo contra o mesmo `state`. Uma redação = uma chamada, não cinco.
3. **O endpoint é `/v1/evaluate`**, não `/v1/chat/completions`. Veja em
   [`evaluate.py`](../evaluate.py) perto do topo. O endpoint de chat **recusa**
   este modelo com a mensagem:

   ```
   "is an evaluation model, not a language model"
   ```

   Essa frase de erro é a prova de que a distinção da etapa 2 não é teoria: a
   própria API trata os dois tipos de modelo como coisas diferentes.

---

## 3.2 Uma chamada de verdade

Todas as suas rodadas usam `sample-mini.jsonl`: 10 redações espalhadas de 0 a
1000. O `sample.jsonl` grande está **ordenado por nota**, então `--limit` nele
daria só redações nota 0.

Agora uma redação só, com `--verbose` para gravar o request e a resposta crus
em `debug/`:

```bash
python3 evaluate.py --sample sample-mini.jsonl --limit 1 --verbose --cache resultados-meus.jsonl
```

Saída esperada — algo como:

```
chave em uso: ...abc123 (fonte: .env.local)
[verbose] cruas gravadas em .../debug/633_*.json
[ok] idx=633 gold=0 jev=440 (0.8s)
```

> Os números podem sair um pouco diferentes dos daqui: o modelo não é
> estritamente determinístico, e estes valores vêm do cache de referência.

Leia essa última linha com atenção. `gold=0` é a nota humana; `jev=440` é a do
Jev. **Uma redação que o corretor humano zerou recebeu 440 do modelo.** Guarde
essa dissonância — a etapa 5 vai explicá-la, e ela não é um bug.

Deu `429`? É o esperado numa sala cheia. O script faz backoff exponencial e o
cache torna tudo retomável: espere e rode o mesmo comando de novo.

Deu `AI_GATEWAY_API_KEY ausente`? Volte ao [SETUP.md](../SETUP.md), passo 5.

---

## 3.3 Leia a resposta crua

```bash
ls debug/
```

```bash
cat debug/*_response.json
```

A estrutura é esta (números de uma redação real):

```json
{
  "model": "typesafe-ai/jev",
  "answers": {
    "c1": {
      "type": "score",
      "score": 2.49,
      "probabilities": {"0": 0, "1": 0.04, "2": 0.48, "3": 0.43, "4": 0.05, "5": 0},
      "confidence": 0.62
    },
    "c2": { "...": "..." }
  },
  "usage": { "inputTokens": 1850, "outputTokens": 74 },
  "providerMetadata": { "...": "..." }
}
```

O que cada campo é:

| Campo | O que é |
|---|---|
| `probabilities` | A distribuição sobre as 6 âncoras. **É o produto de verdade** — o modelo não "escolhe" um nível, ele distribui crença entre eles. |
| `confidence` | O quanto o modelo está concentrado numa âncora só. É isso que alimenta a fila de revisão humana. |
| `score` | **Não é o índice escolhido.** É o tema da etapa 4. Não olhe ainda. |
| `usage.inputTokens` | ~1850 por redação. A ~US$ 0,000078 cada, 100 redações custam menos de um centavo. |

Repare nas probabilidades do exemplo: `0.48` no nível 2 e `0.43` no nível 3.
O modelo está **praticamente em dúvida** entre 80 e 120 pontos. Um corretor
humano que hesitasse assim diria "é 80 ou 120, não sei". O Jev diz a mesma
coisa, só que em número — e por isso dá para automatizar a decisão de quando
chamar um humano.

---

## 3.4 Mais duas, e o cache

```bash
python3 evaluate.py --sample sample-mini.jsonl --limit 3 --cache resultados-meus.jsonl
```

Note a saída:

```
[pulado] idx=633 ja em cache
[ok] idx=597 gold=280 jev=400 (0.7s)
[ok] idx=86 gold=400 jev=440 (0.8s)
```

**A primeira redação não foi repetida.** O cache é um JSONL que cresce, e o
script lê os `idx` já feitos antes de começar. Consequências:

- Você pode interromper com `Ctrl+C` e retomar.
- Um `429` no meio da rodada não perde o trabalho anterior.
- Iterar na rubrica não repaga as chamadas que já deram certo... **desde que
  você troque o `--cache`**, senão ele pula tudo e você mede a rubrica velha.

Essa última linha é a pegadinha operacional mais fácil de cair. Na etapa 6 o
comando tem um `--cache` diferente de propósito.

E há uma armadilha irmã: **errar o nome do `--cache` não dá erro.** Se você
digitar `resultados-meus.jesonl`, o script cria um arquivo novo e vazio e
reavalia tudo, cobrando as chamadas de novo. Confira sempre o que existe:

```bash
ls -la *.jsonl
```

Olhe o conteúdo do seu cache:

```bash
python3 -c "import json;[print(json.loads(l)['idx'], json.loads(l)['gold_total']) for l in open('resultados-meus.jsonl')]"
```

---

## 3.5 Por que não `--limit 100`?

Porque não é necessário. O repositório já traz
`referencia/resultados-referencia-v1.jsonl`: as 100 redações da amostra, já
avaliadas com a `rubric.json` de partida, no laboratório original.

É esse arquivo que as etapas 4 e 5 usam. Você gastou 3 chamadas para entender
o mecanismo; as métricas vêm de um cache que já está pago.

---

## Checklist

- [ ] Rodei `--dry-run` e sei dizer o que vai em `state` e em `questions`
- [ ] Sei por que o endpoint não é `/v1/chat/completions`
- [ ] Fiz uma chamada real e li o `debug/*_response.json`
- [ ] Sei o que são `probabilities` e `confidence`
- [ ] Entendi que o cache pula o que já foi feito — e por que isso é uma faca de dois gumes
- [ ] Sei que errar o nome do `--cache` não dá erro, só cobra de novo
- [ ] **Não** rodei `--limit 100`

**Próxima:** [Etapa 4 — A pegadinha do `score`](04-pegadinha-score.md)
