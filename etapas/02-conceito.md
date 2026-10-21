# Etapa 2 — O conceito: dois tipos de IA

⏱ 20 min · 🔌 não usa a API

> **Objetivo:** entender por que o Jev não é um chatbot, o que é uma *pergunta
> tipada*, e por que isso muda o jeito de escrever o sistema inteiro.

---

## 2.1 A distinção que sustenta tudo

| | **LLM generativo** (ChatGPT, Claude) | **Modelo de decisão** (Jev) |
|---|---|---|
| O que devolve | Texto livre | Um valor **tipado** + probabilidades |
| Analogia | Um ensaísta que escreve um parecer | Um avaliador com prancheta que marca X num formulário |
| Você pergunta | "Avalie esta redação" | "Numa escala de 6 níveis, qual o nível da gramática?" |
| Resposta | Três parágrafos de opinião | `nível 2, confiança 0,62` |
| Problema típico | Você precisa **extrair** o número do texto | Nenhum: o número já vem como número |
| Velocidade | segundos | ~0,5 s |

**Tipado** quer dizer que o formato da resposta é decidido *antes* da pergunta.
Você não recebe "acho que uns 120 pontos, mas depende" — recebe um índice de 0
a 5, **sempre**, com a probabilidade de cada um.

O Jev é chamado de modelo **System One**, nome emprestado da psicologia
(Kahneman): "Sistema 1" é o pensamento rápido e automático, "Sistema 2" o lento
e deliberativo. O Jev é o reflexo, não a reflexão.

**Consequência prática que vale repetir:** o Jev **não escreve texto nenhum**.
Ele não é capaz de redigir o feedback para o aluno. Ele só dá as notas. Feedback
em texto seria um segundo passo, com outro modelo — e é um dos itens em aberto
no projeto original.

---

## 2.2 Por que isso importa para um corretor

Imagine corrigir com um LLM generativo. Você pede "dê a nota de 0 a 200 para a
competência 1" e recebe:

> "A redação apresenta bom domínio da norma padrão, com alguns desvios de
> pontuação. Eu daria algo em torno de 160, talvez 140 dependendo do rigor."

Agora você tem três problemas novos:

1. **Extrair o número** de um texto que pode dizer "160, talvez 140".
2. **Garantir o formato** na próxima chamada — ele pode responder diferente.
3. **Não saber a confiança.** "Talvez" não é um número com que se filtre nada.

Com o Jev, a resposta é `{score: 3.2, confidence: 0.71, probabilities: {...}}`.
Não há o que extrair, e a confiança vem de graça — é ela que, na etapa 5, vai
definir quais redações sobem para revisão humana.

---

## 2.3 A unidade básica: a pergunta tipada

Abra o `rubric.json` e olhe uma competência:

```bash
python3 -c "import json; print(json.dumps(json.load(open('rubric.json'))['competencias']['c1'], ensure_ascii=False, indent=2))"
```

> **Todos os comandos deste workshop rodam da raiz do repositório** (a pasta
> `workshop-jev`), nunca de dentro de `etapas/`. Se der "No such file or
> directory", é quase sempre isso: `cd` para a raiz.

Três partes:

- **`nome`** — só para a gente, o modelo não vê.
- **`instructions`** — o enunciado da pergunta: o que avaliar.
- **`criteria`** — a **lista ordenada de âncoras**. São 6, e a ordem é tudo: a
  posição 0 é a pior, a posição 5 a melhor.

É essa lista de 6 âncoras que vira a escala. O Jev devolve um índice de 0 a 5,
e nós multiplicamos por **40** para chegar à nota ENEM:

```
índice 0 → 0      índice 3 → 120
índice 1 → 40     índice 4 → 160
índice 2 → 80     índice 5 → 200
```

Cinco competências × 200 = **1000**, a nota total do ENEM. A escala do ENEM
cabe exatamente em 6 âncoras — não é coincidência, foi escolhido assim.

**Esta é a ideia central do workshop:** a rubrica é o arquivo que carrega todo
o conhecimento do domínio. O código Python não sabe nada sobre redações. Trocar
a régua é editar um JSON, não reescrever o programa.

---

## 2.4 As 5 competências do ENEM

| | Competência | O que mede |
|---|---|---|
| C1 | Domínio da escrita formal | ortografia, concordância, pontuação, registro |
| C2 | Tema e estrutura | compreendeu a proposta? é dissertativo-argumentativo? |
| C3 | Seleção e organização de argumentos | defende uma tese com evidência? |
| C4 | Mecanismos de coesão | conectivos, retomada por pronome |
| C5 | Proposta de intervenção | agente, ação, meio, efeito, detalhamento |

Guarde esta divisão: ela vai explicar os resultados. C1 e C4 são **contáveis**
(dá para contar erros e conectivos). C3 e C5 exigem **julgamento** (o argumento
é bom?). Modelos se comportam muito diferente nos dois grupos — e é por isso
que o `compare.py` reporta cada competência separada, nunca só a média.

---

## 2.5 Leitura (10 min, em silêncio)

Abra o guia de arquitetura e leia as seções **1 a 8**:

```bash
xdg-open docs/arquitetura.html   # Linux
```

```bash
open docs/arquitetura.html       # macOS
```

No Windows, dê dois cliques em `docs/arquitetura.html`. Ou leia a versão em
texto: [docs/ARQUITETURA.md](../docs/ARQUITETURA.md).

As seções 7 e 8 são as que você mais vai usar na etapa 4. Pode voltar nelas.

---

## 2.6 Perguntas para discutir (não para o Google)

1. Por que 6 âncoras e não 5 ou 10? O que quebra se você mudar para 5?
2. O que aconteceria se as âncoras **não** estivessem em ordem crescente?
3. Se o Jev não escreve texto, como um produto real daria feedback ao aluno?
4. A `instructions` fala "avalie o domínio da escrita formal". O modelo nunca
   vê a palavra "ENEM" nem o número 200. Isso é um problema ou uma vantagem?

---

## Checklist

- [ ] Sei dizer, numa frase, a diferença entre LLM generativo e modelo de decisão
- [ ] Sei que 6 âncoras × 40 = escala 0–200, e que 5 × 200 = 1000
- [ ] Sei que o Jev **não escreve texto**
- [ ] Abri o `rubric.json` e localizei `instructions` e `criteria`
- [ ] Li as seções 1 a 8 do guia de arquitetura

**Próxima:** [Etapa 3 — A primeira chamada](03-primeira-chamada.md)
