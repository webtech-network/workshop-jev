# Guia do instrutor — Workshop JEV

Documento interno. **Não é material do aluno** — ele contém os spoilers das
etapas 5 e 6.

---

## O desenho do workshop

A tese pedagógica: o aluno não aprende "usar uma API de IA", ele aprende
**avaliar se um modelo funciona**. Por isso a sequência é diagnóstico →
hipótese → medição → conclusão com ressalva, e não tutorial de endpoint.

Três decisões de desenho que vale a pena preservar se você adaptar:

1. **Os alunos começam com a rubrica v1, não a v3.** Assim eles descobrem o
   colapso de C3 sozinhos, na etapa 5, em vez de receberem a resposta. A v3
   fica em `rubric-referencia-v3.json` como gabarito da etapa 6.
2. **O `limiar_confianca` de partida é 0,60** — um palpite razoável que os
   dados reprovam. O `compare.py` marca a linha do limiar configurado com
   `<- rubric.json`, e ela aparece **pior que não filtrar**. É o momento mais
   eficiente do workshop: o palpite deles está na tela, reprovado por uma
   tabela.
3. **Só duas etapas gastam API** (3 e 6), ~13 chamadas por aluno. Todo o resto
   roda sobre `referencia/resultados-referencia-v1.jsonl`, que já vem pago.

---

## As trilhas

O material roda em três ambientes, com **os mesmos comandos** nas 7 etapas:

| Trilha | Onde a chave fica | Instalação | Risco |
|---|---|---|---|
| **GitHub Codespaces** | `.env.local` | nenhuma | franquia documentada: 120 h/mês por conta pessoal Free, e um workshop de 3 h num contêiner de 2 núcleos consome ~6 h dessa cota. **É a trilha padrão do material** por isso — se preferir o Replit na frente, troque a recomendação no `README.md` e no `SETUP-WEB.md` |
| **Replit** | **Secrets** | nenhuma | **franquia não documentada** — veja abaixo |
| **Local** | `.env.local` | Python + Git | PCs de laboratório podem não permitir |

Os arquivos que sustentam isso: [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json)
(Codespaces), [`.replit`](.replit) e o `verificar.py`, que detecta sozinho em
qual ambiente está e dá a dica certa.

**O que foi testado de verdade, e o que não foi:**

| | Situação |
|---|---|
| `verificar.py` nos 3 ambientes | testado, simulando as variáveis de cada um |
| A imagem do devcontainer | testada no Docker local: Python, Git e o `verificar.py` rodam nela |
| O ciclo completo do Codespaces | **não testado** — exigiria abrir um Codespace de verdade |
| A trilha Replit inteira | **não testada** — veja o preflight abaixo |

> ⚠️ **O risco do Replit, declarado.** O plano gratuito (Starter) funciona por
> créditos de agente e de nuvem, e a Replit **não publica os limites na página
> de preços** — ela lista só Core, Pro e Enterprise. Não dá para afirmar que
> uma turma inteira atravessa 3 h no plano gratuito.
>
> O que fazer: rode o **preflight abaixo** com uma conta gratuita nova. Se não
> couber, as opções são a trilha Codespaces (limite conhecido e folgado) ou um
> plano pago/educacional da Replit. Em qualquer cenário o material é o mesmo —
> a troca de trilha não custa nada no meio do workshop.

### Preflight do Replit — 15 minutos, faça antes de prometer essa trilha

A trilha Replit **não foi testada de ponta a ponta**: ela foi escrita a partir
da documentação da Replit, não de uma execução real. Rode isto com uma **conta
gratuita nova**, de preferência de um PC da própria PUC:

1. **Importe o seu fork** em `replit.com/import`.
2. No painel **Shell**, confirme que há Python:
   ```
   python3 --version && python3 verificar.py
   ```
   Deve imprimir `(Replit)` na primeira linha. Se `python3` não existir, o Repl
   ficou sem Python — adicione pelo painel de dependências e **anote**, porque
   o aluno vai topar com isso.
3. **Crie o Secret** `AI_GATEWAY_API_KEY`.
4. **Reabra o Shell** e rode `python3 verificar.py` de novo. A seção 4 tem de
   dizer `fonte: variavel de ambiente (Secrets)`.
5. Faça **uma** chamada real:
   ```
   python3 evaluate.py --sample sample-mini.jsonl --limit 1
   ```
6. **Veja quanto de crédito isso consumiu** e extrapole para 3 h × o tamanho da
   turma. Esse número é o que decide se a trilha Replit é viável.

Teste também, no mesmo Repl, se o `git push` funciona depois de conectar a
conta do GitHub. Se não funcionar com facilidade, instrua a turma a entregar o
pull request pela interface do GitHub — o `SETUP-WEB.md` já traz o passo a
passo, na ordem certa (rubrica primeiro, `NOTAS.md` depois, na mesma branch).

### Teste na PUC antes do dia

As chamadas à API saem do **ambiente de nuvem**, não do PC do laboratório. A
rede da PUC só precisa abrir os sites. De uma máquina da sala, confirme:

1. `github.com` abre e deixa fazer login.
2. `replit.com` abre (se você vai oferecer essa trilha).
3. Um Codespace abre e roda `python3 verificar.py`.

Se algum estiver bloqueado, peça liberação ao TI com antecedência — ou caia na
trilha local, que precisa de Python instalado nas máquinas.

## Antes do dia

### A chave da API — faça assim

1. Crie uma chave **dedicada ao workshop** no painel da Vercel (AI Gateway →
   API Keys). Não use a sua chave de trabalho.
2. **Configure um limite de gasto, se o painel permitir** (procure por
   *spending limit* / *usage limit* nas configurações de billing do AI Gateway;
   não confirmei se há um teto por chave ou só por conta). O custo real é de
   US$ 0,000078 por redação, então uma turma de 25 alunos × 13 chamadas custa
   frações de centavo — o limite é proteção contra um `--limit 4570` acidental,
   não contra o uso normal.
3. **Distribua por chat ou slide**, nunca por commit. O repositório é público
   e forks de repositório público são públicos.
4. **Revogue depois do workshop.** Avise os alunos — a etapa 7 já explica como
   eles criam a própria.

### Publicar o repositório

A pasta está pronta mas **não foi inicializada como git nem publicada** — isso
é decisão sua. Para publicar:

```bash
cd "Workshop JEV" && git init -b main && git add -A && git commit -m "Workshop JEV: material inicial"
```

> O `-b main` importa: sem ele o Git cria `master` (a não ser que o seu
> `init.defaultBranch` diga outra coisa), e as etapas 1 e 7 instruem os alunos
> a abrir o PR contra `main`.

Antes de empurrar, confira que a chave não entrou. **Nenhum dos três comandos
abaixo deve imprimir nada** — chaves da Vercel começam com `vck_`, não com
`sk-`, então um grep por `sk` daria falso negativo:

```bash
git grep -lE 'vck_[A-Za-z0-9]' -- . ':(exclude)docs/*'
```

```bash
git ls-files | grep -iE 'env\.local|chave-backup'
```

E o teste definitivo — procure o **valor literal** da chave que você vai
distribuir, substituindo `COLE_A_CHAVE`:

```bash
git grep -lF "COLE_A_CHAVE"
```

> Os arquivos em `docs/` contêm o placeholder `Bearer vck_...` em um exemplo
> de requisição. É texto de documentação, não uma chave — por isso o primeiro
> comando exclui `docs/`.

Crie o repositório público e empurre:

```bash
gh repo create webtech-network/workshop-jev --public --source=. --push
```

> Se você usar outro nome de repositório, procure `workshop-jev` no `SETUP.md`
> e nas etapas 1 e 7 e ajuste. São poucas ocorrências:
> `grep -rn "workshop-jev" . --include=*.md`

### Teste o caminho do aluno numa máquina limpa

O erro mais comum de workshop é o material funcionar só na máquina de quem
escreveu. Clone num diretório novo, sem `.env.local`, e rode:

```bash
python3 evaluate.py --dry-run && python3 compare.py --cache referencia/resultados-referencia-v1.jsonl --sample sample.jsonl
```

Os dois devem passar **sem a chave e sem o dataset**.

---

## Cronograma (3h com 15 min de intervalo)

| Hora | Etapa | O que você faz |
|---|---|---|
| 0:00 | 1 — Setup e GitHub | Checagem em voz alta. Separe quem travou; os outros avançam. |
| 0:20 | 2 — Conceito | Exposição da tabela LLM vs. decisão. **Não pule.** É o que sustenta tudo. |
| 0:40 | 3 — Primeira chamada | `--dry-run` projetado na tela antes de qualquer um rodar. |
| 1:05 | 4 — Pegadinha do `score` | Faça a conta de `0,51 × 40 = 20` no quadro. Peça o erro **antes** de explicar. |
| 1:25 | **Intervalo** | |
| 1:40 | 5 — Métricas | A baseline é o clímax. Mostre-a **antes** dos resultados do Jev. |
| 2:15 | 6 — Sua rubrica | Circule. Gargalo: JSON inválido e `--cache` reusado. |
| 2:55 | 7 — Pull request | Revisão cruzada em pares. Encerramento com os 6 pontos finais. |

Apertado? Corte a 7.5 (revisão cruzada) e peça o PR como tarefa. Nunca corte
a 2 nem a baseline da 5.

---

## Os três momentos que carregam o workshop

### 1. A conta `0,51 × 40 = 20` (etapa 4)

Escreva no quadro `score: 0.51`, `probabilities: {0: 0.50, 1: 0.49}` e
pergunte: **"qual nível o modelo escolheu?"**

Deixe alguém dizer "o 0,51, então uns 20 pontos". Só então diga que 20 não
existe no ENEM — as notas são múltiplas de 40. O bug não trava, não avisa, e
o relatório sai bonito.

Pergunta de fechamento: *"quantos bugs assim existem em produção agora, em
sistemas que ninguém auditou?"*

### 2. A baseline (etapa 5)

**Mostre a baseline primeiro, com o Jev escondido.**

Escreva na tela:

```python
def corrigir(redacao):
    return 600
```

Diga: 5% de acerto exato, viés de +9 pontos. Pergunte se parece bom. Só então
revele que o Jev também acerta 5% exato — e que a diferença está no QWK (0,495
vs 0,000) e no MAE (160 vs 213).

### 3. O limiar reprovado (etapa 5)

Peça um palpite em voz alta para o limiar de confiança **antes** de mostrar a
tabela. Alguém vai dizer 0,6 ou 0,7. Mostre que 0,60 — o valor no
`rubric.json` deles — produz QWK **0,335**, pior que a linha sem filtro
(0,349).

---

## Spoilers: as respostas dos exercícios

### Etapa 4 — decisões praticamente empatadas

`40 de 500`. 8% das decisões são essencialmente cara ou coroa entre duas
âncoras. É o argumento mais forte a favor da fila de revisão humana.

### Etapa 5 — matriz de confusão de C3

```
humano   0  -> nivel 3 x5, nivel 4 x3
humano  40  -> nivel 3 x4, nivel 4 x5
humano  80  -> nivel 4 x22
humano 120  -> nivel 4 x26
humano 160  -> nivel 4 x21
humano 200  -> nivel 4 x8, nivel 5 x1

niveis usados: {2: 1, 3: 13, 4: 85, 5: 1}
```

Respostas: (1) efetivamente 2 níveis, com 85% num só. (2) **Sim** — redação 0
e redação 200 recebem nível 4. (3) Confiança média de C3 = **0,84**, a **mais
alta** das cinco competências (c1 0,72 · c2 0,70 · c4 0,75 · c5 0,65). Ele
está confiante justamente onde é pior — o pior caso possível.

> Não confunda com **0,76**, que é o pico médio de probabilidade em C3. São
> campos diferentes: `confidence` é o que o modelo devolve; o pico é o maior
> valor em `probabilities`. O número a dizer em voz alta é 0,84.

Distribuição em todas as competências, para comparar:

```
c1: {1: 7, 2: 43, 3: 40, 4: 10}     <- usa a escala, deslocado  = calibracao
c2: {2: 12, 3: 23, 4: 60, 5: 5}
c3: {2: 1, 3: 13, 4: 85, 5: 1}      <- degenerado               = discriminacao
c4: {2: 7, 3: 44, 4: 48, 5: 1}
c5: {0: 8, 1: 10, 2: 1, 3: 11, 4: 30, 5: 40}
```

C1 e C3 lado a lado são a aula inteira: mesma métrica ruim, doenças opostas.

### Etapa 6 — as questões de discussão

1. **Quando escolher a v2 apesar de pior no total?** Se o produto é a fila de
   priorização, o que importa é discriminar, e a v2 discrimina melhor em C3.
   Um ranqueador tolera viés; não tolera dar a mesma nota para tudo.
2. **O risco da v3.** Ela foi montada escolhendo o melhor de cada competência
   *no split de desenvolvimento* — é seleção em cima dos dados, e parte do
   ganho pode ser ruído daquele split. Por isso a validação no split de teste
   era necessária, e por isso o projeto diz que a v3 **não tem número
   confiável** enquanto ela não fechar.
3. **Por que validar em split diferente.** Se você diagnostica e valida no
   mesmo conjunto, mede a sua capacidade de ajustar àquelas 100 redações, não
   de corrigir redação.
4. **300 chamadas: uma rubrica × 300 ou 3 × 100?** Não há resposta única, e é
   isso que faz a pergunta boa. Se as rubricas candidatas são claramente
   diferentes, 3 × 100 descobre a direção; se você já tem a direção, 1 × 300
   produz o número que dá para publicar. A resposta errada é fingir que 1 × 100
   já dava os dois.

---

## Plano B

### A trilha web não funciona na sala

- **Replit sem créditos:** mande todo mundo para Codespaces. Os comandos são os
  mesmos; só a chave muda de lugar (Secrets → `.env.local`). Custa 2 minutos.
- **Os dois bloqueados pela rede:** se houver Python nas máquinas, use a trilha
  local. Se não houver nem isso, 5 das 7 etapas (1, 2, 4, 5 e 7) só precisam de
  um navegador com GitHub: o material é legível no próprio repositório, e a
  discussão das métricas pode ser conduzida com os números do cache de
  referência projetados por você.
- **Último recurso, só para análise:** os blocos de `compare.py` rodam em
  qualquer notebook Python na web, inclusive Google Colab, clonando o
  repositório com `!git clone`. Não há fluxo de Git ali, então a etapa 7 teria
  de ser feita pela interface do GitHub. Não documentei essa trilha no material
  do aluno de propósito: quatro trilhas em sete etapas viram instruções que se
  contradizem.

### O provedor está devolvendo 429 continuamente

Já aconteceu no laboratório, por períodos longos. Não é falha do material.

1. Diga à turma que `429` **é conteúdo**: é como a infraestrutura de IA se
   comporta de verdade sob carga, e é por isso que o script tem backoff e
   cache.
2. Pule as chamadas reais. **As etapas 4, 5 e 7 rodam inteiras** sobre o cache
   de referência.
3. Para a etapa 6 sem API: entregue a edição da rubrica como exercício escrito
   — âncoras novas + hipótese no `NOTAS.md` — e peça a defesa oral. O
   raciocínio é o que está sendo avaliado, não a chamada HTTP.
4. Para dar números na etapa 6 mesmo sem API: use a comparação v1 × v2 da
   seção 6.8, que já está medida em 100 redações do split de desenvolvimento.

### Um aluno não consegue instalar Python/Git

Pareie com quem conseguiu. Duas pessoas numa máquina funciona — a discussão
melhora.

### Alguém comitou a chave

1. **Revogue a chave imediatamente** no painel da Vercel. É a única ação que
   resolve: apagar o commit não remove nada do histórico já empurrado.
2. Gere uma nova e redistribua.
3. Use como aula: mostre que o commit continua acessível pelo histórico e pela
   API do GitHub mesmo depois de "apagado". É a lição mais barata que eles vão
   ter sobre segredos em repositório.

### Acabou tempo na etapa 6

Peça como tarefa, com o PR como entrega. Eles precisam da chave para isso —
ou mande fazer com a chave própria, que a etapa 7.6 explica como criar.

---

## O que foi mudado em relação ao LAB Jev

Para quem conhece o laboratório original:

| Mudança | Por quê |
|---|---|
| `rubric.json` = v1 (não v3) | Para o aluno descobrir o colapso de C3 |
| `limiar_confianca` = 0,60 (não 0,70) | Para o palpite dele ser reprovado pelos dados |
| `rubric-referencia-v3.json` | Gabarito da etapa 6 |
| `sample-mini.jsonl` (10 redações, 0 a 1000) | `sample.jsonl` é ordenado por nota: `--limit 10` nele daria dez redações nota 0 |
| `referencia/resultados-referencia-v1.jsonl` | Cache pago, para 5 das 7 etapas rodarem offline |
| `.env.example` | Nunca entregar `.env.local` versionado |
| `MODA_TESTE = 600` no `compare.py` | A baseline funcionava só com o dataset clonado; agora funciona sem |
| Bug corrigido no `compare.py` | A variável do laço do limiar sobrescrevia o namespace do argparse e `--csv` quebrava com `AttributeError`. **Vale corrigir no LAB Jev também.** |
| Mensagens de erro apontando para o `SETUP.md` | Autoatendimento em sala |
| `verificar.py` | Uma checagem só, igual nas três trilhas, que detecta o ambiente |
| `SETUP-WEB.md`, `.replit`, `.devcontainer/` | Workshop sem instalar nada |
| `IA.md` | A IA é permitida com três regras: a chave nunca entra no chat, o pipeline não se toca, e a hipótese vem antes |
| `docs/` copiado sem alteração | O guia de arquitetura já era didático |

O que **não** veio: `.env.local`, `.chave-backup.json`, `debug/`, `data/`,
os caches de desenvolvimento, `rubric-v1.json` (virou o `rubric.json`) e o
README de pesquisa (virou este guia + o README do aluno).
