# Etapa 5 — Medindo: o Jev é bom nisso?

⏱ 35 min · 🔌 não usa a API

> **Objetivo:** sair daqui capaz de responder "o modelo funciona?" com números,
> e de desmontar um relatório de IA que não traz baseline.

Nesta etapa você só lê o cache. Nenhuma chamada, nenhum custo, rode quantas
vezes quiser.

---

## 5.1 O relatório completo

```bash
python3 compare.py --cache referencia/resultados-referencia-v1.jsonl --sample sample.jsonl
```

> Rode da **raiz** do repositório (`cd ..` se você está em `etapas/`).

São cinco blocos. Vamos por partes.

---

## 5.2 Bloco 1 e 2 — as duas leituras

```
--- valor esperado ---
                          n     QWK      MAE     vies    exata      adj       r
c1                      100   0.357     36.2    -22.9    28.0%    84.0%   0.511
c2                      100   0.501     34.4    +14.5    38.0%    87.0%   0.699
c3                      100   0.184     50.9    +44.5    24.0%    63.0%   0.649
c4                      100   0.437     36.0    +13.9    37.0%    86.0%   0.673
c5                      100   0.402     56.2    +31.9    22.0%    60.0%   0.472
TOTAL                   100   0.495    160.2    +81.9     5.0%    25.0%   0.706
```

As colunas:

| Coluna | O que é | Bom é |
|---|---|---|
| **QWK** | Quadratic Weighted Kappa — concordância **descontando o acerto por sorte**. É a métrica padrão para correção automática. | perto de 1 |
| **MAE** | erro médio absoluto, em pontos ENEM | baixo |
| **viés** | erro médio **com sinal**: positivo = generoso demais | perto de 0 |
| **exata** | % de acerto na faixa cheia de 40 pontos | alto |
| **adj** | % de acerto errando no máximo uma faixa | alto |
| **r** | correlação de Pearson — mede se ele **ordena** bem, ignorando o nível | perto de 1 |

### Por que QWK e não "acurácia"?

Porque errar por 40 pontos e errar por 200 não são o mesmo erro. O QWK pesa o
erro pelo **quadrado da distância**: confundir 160 com 200 custa pouco,
confundir 0 com 200 custa muito. Acurácia simples trataria os dois como "errou".

Esse peso pela distância ao quadrado é o **QW** de *Quadratic Weighted*. O
**K**, de *Kappa*, resolve o outro problema: num corpus concentrado, chutar
sempre o valor mais comum já acerta bastante, e o kappa desconta exatamente
essa concordância por sorte. Daí a métrica inteira: **Q**uadratic
**W**eighted **K**appa — peso pela distância, descontando o acaso.

---

## 5.3 Bloco 3 — a baseline burra (o bloco mais importante)

```
--- baseline constante (sempre 600, moda do split de teste) ---
TOTAL baseline          100   0.000    213.2     +9.2     5.0%    15.0%    n/a
```

Esta "baseline" não olha a redação. Ela chuta **sempre 600**, a nota mais
frequente do corpus. É um programa de uma linha:

```python
def corrigir(redacao):
    return 600
```

E olhe o que ela consegue: **5% de acerto exato — o mesmo do Jev** — e um viés
de só +9,2. Se alguém te mostrasse apenas "5% de acerto exato e viés de 9
pontos", soaria razoável.

É por isso que a baseline é obrigatória. O veredito:

| | Jev | Chutar 600 |
|---|---|---|
| QWK | **0,495** | 0,000 |
| MAE | **160,2** | 213,2 |
| adjacente | **25%** | 15% |

O Jev bate a baseline com folga — **em QWK e MAE, não em acerto exato.** Ele
está fazendo algo real; só não é atribuir a nota certa.

> **Leve isto para a vida profissional:** todo relatório de IA sem baseline é
> suspeito. Quando alguém disser "nosso modelo acerta 85%", a primeira pergunta
> é "e o que acerta chutando sempre a resposta mais comum?".

---

## 5.4 Lendo o veredito

Volte à tabela da 5.2 e observe três coisas.

**1. Ele ordena melhor do que pontua.** `r = 0,71` no total é uma correlação
boa: o Jev sabe distinguir redação ruim de redação boa. Mas o acerto exato é
5%. Tradução de produto: **serve como ranqueador** ("ordene estas 300 redações
para o professor começar pelas piores"), **não serve** como atribuidor de nota
oficial.

**2. O viés é de +82 pontos, mas não é uniforme.**

| | viés |
|---|---|
| C1 escrita formal | **−22,9** |
| C2 tema | +14,5 |
| C3 argumentação | **+44,5** |
| C4 coesão | +13,9 |
| C5 proposta | +31,9 |

O modelo é **severo com gramática e generoso com conteúdo**. Faz sentido: erro
de concordância é objetivo e visível; "o argumento é bom?" é julgamento, e na
dúvida ele é gentil.

**3. C3 é o ponto fraco** (QWK 0,18) e C2 o mais forte (0,50). Coerente com a
divisão da etapa 2: julgar seleção de argumentos é mais difícil que checar
estrutura.

---

## 5.5 Bloco 4 — quanto do erro é conserto fácil?

```
--- efeito de remover o vies medio (calibracao simples) ---
          QWK antes  QWK depois  MAE antes  MAE depois
c1            0.357       0.469       36.2        27.6
c2            0.501       0.510       34.4        33.8
c3            0.184       0.346       50.9        36.6
c4            0.437       0.491       36.0        34.9
c5            0.402       0.451       56.2        46.5
TOTAL         0.495       0.536      160.2       147.7
```

Este bloco faz uma coisa só: **subtrai o viés médio** de cada competência e
remede. É um conserto grátis, sem nenhuma chamada nova.

C3 salta de **0,18 para 0,35** — quase dobra. C1 vai de 0,36 para 0,47.

Como ler isso: o erro de um modelo se divide em **viés** (ele erra sempre para
o mesmo lado — corrigível) e **ruído** (ele erra para lados aleatórios — não
corrigível somando uma constante). Um ganho grande aqui significa que boa parte
do erro é viés.

**E viés aponta para a rubrica, não para o modelo.** Se o Jev dá 160 quando o
humano dá 120, a âncora do nível 4 está descrevendo uma redação mais fraca do
que deveria. Isso é texto que você pode reescrever — e é a etapa 6.

> **Por que não simplesmente subtrair o viés no código e pronto?** Porque você
> teria calibrado em cima destas 100 redações. Em dados novos o viés é outro.
> O conserto honesto é a rubrica; a calibração é só o **diagnóstico** que diz
> onde ela está torta.

---

## 5.6 Bloco 5 — o limiar de revisão humana

```
--- limiar de confianca: qualidade do que fica automatizado ---
 limiar  automat.  revisao   QWK auto  MAE auto
   0.00      100%       0%      0.349      42.7
   0.50       96%       4%      0.350      42.1
   0.60       89%      11%      0.335      41.9  <- rubric.json
   0.65       78%      22%      0.350      39.5
   0.70       59%      41%      0.426      36.6
   0.80       31%      69%      0.455      37.9
```

Aqui está a decisão de produto. A ideia é: decisões em que o modelo tem pouca
confiança **sobem para um corretor humano**; o resto fica automático.

A pergunta é onde cortar. Leia a tabela assim:

- Linha `0.00` é o controle: **nenhum filtro**, QWK 0,349.
- O `rubric.json` que vocês receberam está em **0,60** — e olhe o resultado:
  QWK **0,335**, *pior que não filtrar*. O limiar descarta 11% das decisões,
  manda gente trabalhar, e o que sobra é de qualidade **menor**.
- O ganho real só começa em **0,70**: QWK sobe para 0,426 — mas custa **41% de
  revisão humana**.

**Abaixo de 0,70 a confiança do Jev não discrimina.** Ela só começa a separar
acerto de erro acima disso.

E repare no que essa tabela realmente decide: se o produto precisa de 41% de
revisão humana, a conta de viabilidade é essa, não o QWK. Um corretor que
automatiza 59% das decisões ainda economiza quase metade do trabalho — mas
quem vendeu "correção automática" vai ter uma conversa difícil.

> **Exercício de bolso:** o 0,60 no `rubric.json` foi um palpite razoável, do
> tipo que todo mundo faz. Os dados o reprovaram. Quantas decisões de produto
> você já viu tomadas no mesmo tipo de palpite, sem essa tabela?

---

## 5.7 Exercício: encontre o pior critério e explique

Rode o diagnóstico de C3 — a matriz de confusão:

```bash
python3 -c "
import json
from collections import Counter
regs = [json.loads(l) for l in open('referencia/resultados-referencia-v1.jsonl')]
dist = Counter()
for r in regs:
    humana = r['gold_competencias'][2]          # C3
    nivel = r['jev']['c3']['indice_argmax']     # 0..5
    dist[(humana, nivel)] += 1
print('nota humana -> nivel dado pelo Jev (contagem)')
for (h, n), q in sorted(dist.items()):
    print(f'  humano {h:>3}  ->  nivel {n}   x{q}')
niveis = Counter(n for (_, n), q in dist.items() for _ in range(q))
print()
print('quantas vezes cada nivel foi usado:', dict(sorted(niveis.items())))
print()
for c in ['c1','c2','c3','c4','c5']:
    confs = [r['jev'][c]['confianca'] for r in regs]
    print(f'confianca media em {c}: {sum(confs)/len(confs):.2f}')
"
```

Responda, com o colega:

1. Quantos dos 6 níveis o Jev realmente usa em C3?
2. Redações que o humano deu 0 e redações que deu 200 recebem o mesmo nível?
3. A confiança média em C3 é **mais alta ou mais baixa** que nas outras quatro
   competências? O que isso significa, se C3 é justamente a pior delas?

Se a resposta da pergunta 2 for "sim", você acabou de descobrir que **C3 não
está enviesado — está sem discriminação nenhuma.** São doenças diferentes:

| Doença | Sintoma | Conserto |
|---|---|---|
| **Calibração** | usa a escala toda, mas deslocada para um lado | mover as âncoras de nível |
| **Discriminação** | empilha quase tudo num nível só | reescrever as âncoras para serem **distinguíveis** |

Essa distinção é o que você vai usar na etapa 6. Tratar as duas do mesmo jeito
**piora** o resultado — e isso não é teoria, foi medido.

---

## Checklist

- [ ] Sei explicar o que o QWK desconta que a acurácia não
- [ ] Sei por que a baseline de chutar 600 é obrigatória num relatório
- [ ] Sei dizer para que o Jev serve hoje (ranqueador) e para que não serve
- [ ] Sei que o viés de C1 tem sinal oposto ao das outras competências, e por quê
- [ ] Vi que o limiar de 0,60 do `rubric.json` é **pior que não filtrar**
- [ ] Sei a diferença entre problema de calibração e problema de discriminação
- [ ] Rodei a matriz de confusão de C3 e sei quantos níveis ele usa

**Próxima:** [Etapa 6 — Sua rubrica](06-sua-rubrica.md)
