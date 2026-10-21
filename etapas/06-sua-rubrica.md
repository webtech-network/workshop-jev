# Etapa 6 — Sua rubrica

⏱ 40 min · 🔌 **usa a API** (10 chamadas por aluno)

> **Objetivo:** você diagnosticou, agora conserte. Edite as âncoras, re-rode e
> veja se melhorou — com honestidade sobre o que 10 redações podem provar.

Esta é a etapa em que o workshop vira trabalho de verdade. Não há resposta
única, e a sua pode ser melhor que a do laboratório original.

---

## 6.1 O diagnóstico, em duas linhas

Da etapa 5:

- **C3 (argumentação) não está enviesado — está sem discriminação.** Ele põe
  85 de 100 redações no nível 4. Redação nota 0 e redação nota 200 recebem o
  mesmo nível. A confiança média em C3 é **0,84** — a mais alta das cinco
  competências. Ele está **confiante no erro**, que é o pior caso possível.
- **C1 (escrita formal) está mal calibrado.** Usa a escala toda, mas deslocada
  ~1 nível para baixo (viés −23).

E a lição que separa as duas doenças:

| Doença | Sintoma | O que mudar nas âncoras |
|---|---|---|
| **Discriminação** | empilha tudo num nível | torná-las **distinguíveis**: contagens, critérios verificáveis |
| **Calibração** | usa a escala, mas deslocada | **mover** o que cada nível descreve, mantendo o estilo |

---

## 6.2 A mini-amostra

Para esta etapa você usa `sample-mini.jsonl`: **10 redações escolhidas da
amostra grande, espalhadas de 0 a 1000**.

```bash
python3 -c "import json;print([json.loads(l)['gold_total'] for l in open('sample-mini.jsonl')])"
```

```
[0, 280, 400, 480, 560, 640, 720, 840, 920, 1000]
```

Por que uma mini-amostra, e não as 10 primeiras da grande? Porque o
`sample.jsonl` está **ordenado por nota**: `--limit 10` nele te daria dez
redações nota 0 e uma métrica sem sentido.

A vantagem de usar estas 10: elas estão **todas dentro do cache de
referência**. Então o "antes" e o "depois" são medidos nas **mesmas redações** —
comparação justa, não duas coortes diferentes.

Meça o **antes**, para ter com o que comparar:

```bash
python3 compare.py --cache referencia/resultados-referencia-v1.jsonl --sample sample-mini.jsonl
```

Anote no `NOTAS.md` a linha `TOTAL` e as 5 competências do bloco **valor
esperado**. Esse é o seu ponto de partida.

> Ele vai avisar `[filtro] 90 registros do cache ignorados`. É correto: o cache
> tem 100 redações e você está medindo 10.

---

## 6.3 Antes de digitar: a regra da honestidade

Os números que você vai produzir vêm de **10 redações**. Compare:

| | QWK TOTAL |
|---|---|
| referência em 100 redações | 0,495 |
| referência nas mesmas 10 | **0,615** |

**São os mesmos dados e a mesma rubrica.** A diferença de 0,12 é só ruído de
amostra pequena.

Consequência: se a sua rubrica mudar o QWK em 0,05, **você não mediu nada**.
Para uma mudança desse tamanho ser real, precisaria de ~300 redações. O que
10 redações mostram de forma confiável é o grosso:

- um nível que **deixou de ser usado** passou a ser usado;
- um viés de **+40 pontos** virou +10;
- uma competência que dava a mesma nota para tudo passou a variar.

Mire nisso, não na terceira casa decimal. E escreva no `NOTAS.md` o que você
**esperava** que acontecesse antes de rodar — é a única forma de não se
convencer depois de qualquer resultado.

---

## 6.4 Edite o `rubric.json`

Abra o `rubric.json`. Você mexe **só nele** — o pipeline não muda.

### Escolha um alvo

Não mude as 5 competências de uma vez: você não vai saber o que causou o quê.
Escolha **uma ou duas**, e tenha uma hipótese escrita.

**Alvo A — C3, problema de discriminação.** As âncoras atuais são adjetivos:

```
"Dominio insuficiente...", "Dominio mediano...", "Bom dominio..."
```

"Mediano" e "bom" não são verificáveis — não há nada no texto da redação que
decida entre eles, então o modelo escolhe o nível do meio-para-cima e fica lá.
Troque por algo **contável**:

```
"2 argumentos desenvolvidos, nenhum com evidencia concreta"
"2 ou mais argumentos desenvolvidos, ao menos 1 com evidencia concreta (dado, fato, exemplo nomeado)"
```

Use também o campo `instructions` para dar a instrução de contagem:

```
"Conte os argumentos DESENVOLVIDOS (uma afirmacao seguida de justificativa
ou evidencia; uma frase solta nao conta) e verifique se cada um traz
evidencia concreta. Escolha o nivel pelo numero de argumentos."
```

**Alvo B — C1, problema de calibração.** Aqui o estilo descritivo funciona; o
que está errado é **onde cada nível corta**. O modelo é severo demais, então
**afrouxe** o que ele exige de cada nível: o que hoje é descrito no nível 4
deveria estar no nível 3.

### Regras técnicas (quebrar qualquer uma destas estraga a medição)

1. **Exatamente 6 âncoras** em cada `criteria`. A escala 0–200 em faixas de 40
   depende disso. Com 5 ou 7 as notas saem erradas sem nenhum erro na tela.
2. **Ordem crescente**: posição 0 = pior, posição 5 = melhor.
3. **Sem acentos** nas âncoras, para seguir o padrão do arquivo.
4. **JSON válido.** Vírgula sobrando é o erro nº 1. Valide:

```bash
python3 -c "import json;r=json.load(open('rubric.json'));print('JSON ok |', {c: len(v['criteria']) for c,v in r['competencias'].items()})"
```

Esperado: `JSON ok | {'c1': 6, 'c2': 6, 'c3': 6, 'c4': 6, 'c5': 6}`. Se algum
número não for 6, conserte antes de gastar chamadas.

### Ajuste o limiar também

A etapa 5 mostrou que `limiar_confianca: 0.6` é **pior que não filtrar**.
Mude-o para o valor que os dados apoiam:

```json
"limiar_confianca": 0.7
```

---

## 6.5 Confira o request antes de pagar

```bash
python3 evaluate.py --dry-run --sample sample-mini.jsonl
```

Leia as âncoras na saída. Elas são as suas? Então vá.

---

## 6.6 Rode

```bash
python3 evaluate.py --sample sample-mini.jsonl --cache resultados-meus-v2.jsonl
```

Dez chamadas, ~15 segundos. Três pontos de atenção:

- **`--cache` novo.** Rubrica nova exige cache novo. Se você reusar o da etapa
  3, o script pula tudo com `[pulado]` e você mede a rubrica velha acreditando
  medir a nova.
- **`429`?** Normal com a turma toda chamando junto. Rode o mesmo comando de
  novo: o cache retoma de onde parou.
- **Não rode dois `evaluate.py` no mesmo `--cache`** ao mesmo tempo — eles
  duplicam registros, e o `compare.py` não deduplica.

---

## 6.7 Meça o depois

```bash
python3 compare.py --cache resultados-meus-v2.jsonl --sample sample-mini.jsonl
```

Monte a comparação no `NOTAS.md`:

| | QWK antes | QWK depois | viés antes | viés depois |
|---|---|---|---|---|
| C3 | 0,317 | ? | +38,8 | ? |
| TOTAL | 0,615 | ? | +43,9 | ? |

E o teste que importa mais que o QWK — **o modelo voltou a usar a escala?**

```bash
python3 -c "
import json
from collections import Counter
regs = [json.loads(l) for l in open('resultados-meus-v2.jsonl')]
for c in ['c1','c2','c3','c4','c5']:
    niveis = Counter(r['jev'][c]['indice_argmax'] for r in regs)
    print(f'{c}: {dict(sorted(niveis.items()))}')
"
```

Compare com a distribuição **antes**, nas mesmas 10 redações (medida no cache
de referência):

```
c1: {1: 2, 2: 6, 3: 1, 4: 1}
c2: {2: 2, 3: 3, 4: 5}
c3: {3: 3, 4: 7}        <- dois niveis, 7 num so
c4: {2: 2, 3: 5, 4: 3}
c5: {0: 1, 1: 1, 3: 1, 4: 5, 5: 2}
```

Para gerá-la você mesmo:

```bash
python3 -c "
import json
from collections import Counter
mini = {json.loads(l)['idx'] for l in open('sample-mini.jsonl')}
regs = [json.loads(l) for l in open('referencia/resultados-referencia-v1.jsonl')]
regs = [r for r in regs if r['idx'] in mini]
for c in ['c1','c2','c3','c4','c5']:
    print(f'{c}: {dict(sorted(Counter(r[\"jev\"][c][\"indice_argmax\"] for r in regs).items()))}')
"
```

Se C3 antes usava `{3: 3, 4: 7}` e agora espalha por 3 ou 4 níveis, **você
consertou a discriminação** — mesmo que o QWK tenha andado pouco. Essa é a
melhoria real; o QWK em 10 redações é só um indício.

---

## 6.8 O gabarito (só agora)

O laboratório original passou por este mesmo caminho. O que ele achou:

**v2 — contagens em todas as 5 competências.** Validado em 100 redações de um
split **diferente** (o de desenvolvimento, nunca usado antes):

| | QWK v1 | QWK v2 | Δ |
|---|---|---|---|
| C1 escrita | 0,410 | 0,196 | **−0,213** |
| C2 tema | 0,454 | 0,231 | **−0,224** |
| C3 argumentação | 0,123 | 0,160 | +0,038 |
| C4 coesão | 0,391 | 0,431 | +0,039 |
| C5 proposta | 0,281 | 0,224 | −0,057 |
| **TOTAL** | **0,429** | **0,377** | **−0,053** |

**A v2 piorou no geral** — e esse é o resultado mais instrutivo do projeto.
Mas o colapso de C3 caiu de 86/100 para 51/100 no nível 4, e ele passou a usar
3 níveis em vez de 2.

A lição:

> Contagens **ajudam** onde o problema é discriminação (C3, C4) e **atrapalham**
> onde é calibração (C1, C2, C5). Descrever "2 a 4 desvios" tornou o modelo
> ainda mais severo justamente onde ele já era severo demais.

**v3 — híbrida:** contagens em C3/C4, descritivas em C1/C2/C5. É o que está em
`rubric-referencia-v3.json`. Abra agora e compare com a sua:

```bash
python3 -c "
import json
a = json.load(open('rubric.json'))
b = json.load(open('rubric-referencia-v3.json'))
for c in ['c1','c2','c3','c4','c5']:
    igual = a['competencias'][c]['criteria'] == b['competencias'][c]['criteria']
    print(f'{c}: {\"identica a v3\" if igual else \"difere da v3\"}')
"
```

Partindo da v1, C3 e C4 já aparecem como `difere da v3` — são exatamente as
duas que o laboratório trocou. Se você também mexeu nelas, compare o **texto**
das suas âncoras com as da v3: chegou à mesma conclusão por outro caminho?

E a ressalva que o laboratório faz de si mesmo: a validação da v3 no split de
teste **ficou incompleta** (22 de 100, o provedor começou a recusar as
chamadas). **Até ela fechar, a v3 não tem número confiável.** O que se sabe é
que ela combina as partes que melhoraram em dados não vistos — não que o total
melhore.

Isso também é parte da aula: um projeto honesto diz onde o número não existe.

---

## 6.9 Questões para discutir

1. A v2 piorou o total mas melhorou C3. Em que situação você ainda escolheria a
   v2?
2. A v3 foi montada escolhendo, competência por competência, o que foi melhor
   no split de desenvolvimento. Que risco isso cria?
3. Por que validar num split *diferente* daquele em que você diagnosticou?
4. Se você tivesse orçamento para 300 chamadas, gastaria em 300 redações com
   uma rubrica, ou em 3 rubricas × 100 redações?

---

## Checklist

- [ ] Medi o **antes** em `sample-mini.jsonl` e anotei no `NOTAS.md`
- [ ] Escrevi minha hipótese **antes** de rodar
- [ ] Editei o `rubric.json` com alvo escolhido, não tudo de uma vez
- [ ] Validei o JSON e conferi que cada `criteria` tem 6 âncoras
- [ ] Ajustei o `limiar_confianca` para o valor que os dados apoiam
- [ ] Rodei com `--cache` novo e medi o depois
- [ ] Olhei a distribuição de níveis, não só o QWK
- [ ] Comparei com a v3 e sei dizer por que contagens ajudam em C3 e não em C1

**Próxima:** [Etapa 7 — Pull request](07-pull-request.md)
