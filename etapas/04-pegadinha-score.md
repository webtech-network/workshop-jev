# Etapa 4 — A pegadinha do `score`

⏱ 20 min · 🔌 não usa a API

> **Objetivo:** entender o erro que produziria notas silenciosamente erradas —
> sem exceção, sem travar, sem mensagem — e como o código se defende dele.

Esta é a etapa mais importante do workshop em termos de engenharia. O bug que
ela descreve não quebra nada: ele devolve números plausíveis e errados.

---

## 4.1 O experimento

Olhe de novo uma resposta do Jev:

```json
{
  "score": 2.49,
  "probabilities": {"0": 0, "1": 0.04, "2": 0.48, "3": 0.43, "4": 0.05, "5": 0},
  "confidence": 0.62
}
```

Seis âncoras, índices 0 a 5. O `score` vale `2.49`.

**Pergunta:** qual nível o modelo escolheu?

A resposta intuitiva — "o 2, e o `.49` é um arredondamento" — está errada, e
é exatamente por isso que o bug passa despercebido: nesse caso ela até dá o
resultado certo.

Faça a conta:

```bash
python3 -c "
p = {0:0.0, 1:0.04, 2:0.48, 3:0.43, 4:0.05, 5:0.0}
print('soma das probabilidades:', sum(p.values()))
print('media ponderada:', sum(i*v for i,v in p.items()))
"
```

```
soma das probabilidades: 1.0
media ponderada: 2.49
```

**O `score` é o valor esperado da distribuição**, não o índice escolhido. É
`0×0,00 + 1×0,04 + 2×0,48 + 3×0,43 + 4×0,05 + 5×0,00`.

---

## 4.2 Por que isso é perigoso

Um caso real do laboratório original:

```
score: 0.51    probabilities: {0: 0.50, 1: 0.49, 2: 0.01}
```

O modelo está **rachado ao meio** entre o nível 0 e o nível 1. O `score` cai
em `0,51` — um valor que **nenhuma das duas âncoras representa**.

Se você tratar `score` como índice e multiplicar por 40:

| Leitura | Conta | Nota |
|---|---|---|
| `score` como índice | `0,51 × 40` | **20 pontos** |
| âncora mais provável | `0 × 40` | **0 pontos** |

20 não é uma nota do ENEM. As notas são múltiplos de 40. Você produziu um
número que parece uma nota, não é uma nota, e ninguém vai reclamar: o programa
não quebra, o CSV sai bonitinho, e o relatório está errado.

**A lição transferível:** quando uma API devolve um número, pergunte sempre
*qual grandeza ele mede*. "Número entre 0 e 5" não é um contrato suficiente.

---

## 4.3 Como o código se defende

Abra a função que faz a conversão:

```bash
sed -n '/^def extrair_notas/,/^    return out/p' evaluate.py
```

Ela não escolhe uma leitura — **guarda as duas**, com nomes que dizem o que
cada uma é:

| Campo gravado | Como é calculado | O que é |
|---|---|---|
| `nota_argmax` | âncora de maior probabilidade × 40 | A **nota ENEM discreta**. Sempre múltiplo de 40. É a que um professor escreveria. |
| `nota_esperada` | `score` × 40 | Um **sinal contínuo**. Não é uma nota válida, mas correlaciona melhor, porque carrega a dúvida do modelo. |
| `score_bruto` | o `score` original | Guardado sem transformação, para auditoria. |
| `probabilities` | a distribuição inteira | Guardada para você poder refazer qualquer leitura depois. |

Veja a diferença nos dados reais:

```bash
python3 -c "
import json
r = json.loads(open('referencia/resultados-referencia-v1.jsonl').readline())
print('idx', r['idx'], '| nota humana:', r['gold_total'])
for c, v in r['jev'].items():
    print(f\"  {c}: argmax={v['nota_argmax']:>3}  esperada={v['nota_esperada']:>6}  score={v['score_bruto']}\")
"
```

As duas colunas discordam. E, na etapa 5, você vai ver que elas **discordam nas
métricas também** — por isso o `compare.py` imprime um relatório para cada uma.

---

## 4.4 O princípio de projeto

Há uma decisão de engenharia escondida aqui, e ela vale mais que o detalhe do
Jev:

> **Grave o dado cru. Derive as leituras depois.**

O `evaluate.py` guarda `probabilities` inteira no cache. Isso significa que
qualquer pergunta nova — "e se eu usar a mediana?", "e se eu descartar decisões
com duas âncoras empatadas?" — se responde **sem nenhuma chamada nova**.

Se o script tivesse gravado só a nota final, cada ideia nova custaria 100
chamadas de API. É a diferença entre um experimento de 5 segundos e um de 20
minutos pagos.

---

## 4.5 Exercício: a terceira leitura

Já existem `nota_argmax` e `nota_esperada`. Invente uma terceira e veja se é
melhor. Sugestão: **moda com desempate pelo esperado** — use o argmax, mas se
as duas âncoras mais prováveis diferirem em menos de 0,05, use o esperado
arredondado.

```bash
python3 -c "
import json
regs = [json.loads(l) for l in open('referencia/resultados-referencia-v1.jsonl')]
COMPS = ['c1','c2','c3','c4','c5']
empatados = 0
for r in regs:
    for c in COMPS:
        p = sorted((float(v) for v in r['jev'][c]['probabilities'].values()), reverse=True)
        if len(p) > 1 and p[0] - p[1] < 0.05:
            empatados += 1
print(f'{empatados} de {len(regs)*5} decisoes estao praticamente empatadas entre duas ancoras')
"
```

Quantas decisões o modelo toma essencialmente jogando moeda? Esse número é o
argumento mais forte a favor de uma fila de revisão humana — assunto da
próxima etapa.

---

## Checklist

- [ ] Sei explicar, com a conta, por que `score` é `2.49` e não `2`
- [ ] Sei dizer por que esse bug é mais perigoso que um que trava o programa
- [ ] Sei a diferença entre `nota_argmax` e `nota_esperada`
- [ ] Entendi o princípio "grave o dado cru, derive as leituras depois"

**Próxima:** [Etapa 5 — Medindo](05-metricas.md)
