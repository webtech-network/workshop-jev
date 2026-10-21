# Etapa 7 — Publicando o seu resultado

⏱ 20 min · 🔌 não usa a API

> **Objetivo:** empacotar o que você fez num pull request que outra pessoa
> consiga ler e julgar. Essa é a habilidade que fica depois do workshop.

---

## 7.1 Primeiro: confirme que a chave não vai junto

Antes de qualquer `git add`:

```bash
git status --short
```

**`.env.local` não pode aparecer nessa lista.** Nem `debug/`, nem
`resultados-meus*.jsonl`.

Dupla checagem explícita:

```bash
git check-ignore -v .env.local debug resultados-meus-v2.jsonl
```

Deve imprimir três linhas, cada uma citando o `.gitignore`. Se alguma faltar,
**pare e chame o instrutor** — não comite.

> Por que tanto cuidado: o seu fork é público, e o histórico do Git é
> permanente. Apagar a chave num commit seguinte **não a remove** — ela
> continua no histórico, indexável. Uma chave vazada tem de ser revogada, e
> aí o workshop acaba para a turma inteira.

---

## 7.2 Escreva o `NOTAS.md`

É o conteúdo do seu PR. Um PR com números e raciocínio vale dez vezes um com
"mudei a rubrica". Estrutura sugerida:

```markdown
# Notas de SEU-USUARIO

## O que eu mudei
Reescrevi as âncoras de C3 trocando adjetivos ("domínio mediano") por
contagens de argumentos desenvolvidos e presença de evidência concreta.
Mudei o `limiar_confianca` de 0,60 para 0,70.

## Por quê
A matriz de confusão mostrou o Jev pondo 85 de 100 redações no nível 4 de C3,
dando o mesmo nível para redação nota 0 e nota 200. Isso não é viés — é falta
de discriminação, e adjetivos como "mediano" não dão ao modelo nada
verificável para decidir entre dois níveis vizinhos.

## Hipótese (escrita antes de rodar)
Esperava que C3 passasse a usar pelo menos 3 níveis e que o viés de +38
caísse. Não esperava mudança grande no QWK com só 10 redações.

## Resultado (10 redações de sample-mini.jsonl)

| | QWK antes | QWK depois | viés antes | viés depois |
|---|---|---|---|---|
| C3 | 0,317 | ... | +38,8 | ... |
| TOTAL | 0,615 | ... | +43,9 | ... |

Distribuição de níveis em C3:
- antes: {3: 3, 4: 7}
- depois: ...

## O que eu NÃO posso concluir
Com 10 redações, uma diferença pequena no QWK é ruído — o próprio cache de
referência dá 0,495 em 100 redações e 0,615 nestas 10, **com a mesma
rubrica**. O que acho defensável é a mudança na distribuição de níveis, se ela
for grande.

## O que eu tentaria com mais orçamento
Rodar as mesmas duas rubricas em 300 redações do split de desenvolvimento.
```

> As colunas "antes" e a distribuição `{3: 3, 4: 7}` são os números **reais**
> do cache de referência nessas 10 redações — pode copiá-los. As reticências
> são o que **você** mede: não invente, cole a saída do `compare.py`.

A seção **"o que eu NÃO posso concluir"** é a que mais impressiona quem lê.
Quase ninguém escreve.

---

## 7.3 Comite

Veja exatamente o que mudou na rubrica:

```bash
git diff rubric.json
```

Leia esse diff antes de comitar. É o seu trabalho da etapa 6 inteiro.

```bash
git add rubric.json NOTAS.md
```

```bash
git commit -m "Reescreve ancoras de C3 como contagens e sobe o limiar para 0,70"
```

> **Mensagem de commit.** Diga o que mudou, no imperativo, em uma linha.
> "Reescreve âncoras de C3" é útil. "update", "ajustes", "wip" e "final2" não
> dizem nada a quem for ler o histórico depois — inclusive você, em um mês.

---

## 7.4 Empurre e abra o PR

```bash
git push
```

Com o `gh`, o PR sai do terminal:

```bash
gh pr create --title "Rubrica de SEU-USUARIO: C3 contavel + limiar 0,70" --body-file NOTAS.md
```

Ele vai perguntar para onde enviar — escolha
`webtech-network/workshop-jev` na branch `main`.

Sem o `gh`: abra o seu fork no navegador. O GitHub mostra uma faixa amarela
com **"Compare & pull request"**. Clique, confirme que a comparação é
`webtech-network/workshop-jev: main ← SEU-USUARIO/workshop-jev:
rubrica-SEU-USUARIO`, cole o `NOTAS.md` na descrição e envie.

```bash
gh pr view --web
```

---

## 7.5 Revise o PR de um colega

Pegue o PR de outra pessoa (`gh pr list`) e comente **uma** coisa:

- Ele mudou uma competência ou várias? Dá para saber o que causou o quê?
- A conclusão é sustentada pelo tamanho da amostra?
- Alguma mudança nas âncoras que você não teria pensado?

Revisar é metade do trabalho de engenharia, e é a parte que ninguém treina.

---

## 7.6 Depois do workshop

A chave do instrutor será **revogada** — ela existe só para o dia. Para
continuar:

**Sua própria chave.** Crie uma conta na [Vercel](https://vercel.com), vá em
**AI Gateway → API Keys** e gere uma. Ponha no seu `.env.local`. O custo real
medido é de **US$ 0,000078 por redação** — 1.000 redações custam menos de 10
centavos de dólar. Procure um limite de gasto nas configurações de billing e
configure um de qualquer jeito — é barato errar um `--limit`.

**Sem chave nenhuma:** todo o `compare.py` e todas as análises continuam
funcionando com `referencia/resultados-referencia-v1.jsonl`. Os exercícios de
leitura de dados não precisam da API.

**Os itens que o laboratório deixou abertos**, se você quiser continuar:

- [ ] **Fechar a validação da v3 no split de teste** — 22 de 100 feitos, o
      provedor começou a recusar as chamadas. É o item mais valioso: hoje a
      v3 não tem número confiável.
- [ ] Rodar em ~300 redações para uma métrica estável.
- [ ] **A camada de feedback em texto.** O Jev não escreve — precisaria de um
      segundo modelo, generativo. E a definição do produto ainda não existe:
      um parágrafo por competência ou um resumo único? Endereçado ao aluno ou
      ao professor? Essa decisão vem antes do código.
- [ ] Open-Jev self-hosted ([Zefan-Cai/Open-Jev](https://github.com/Zefan-Cai/Open-Jev)),
      réplica MIT com modelos 2B/9B/27B em Docker — sem custo por chamada, mas
      precisa de GPU.

---

## Checklist final

- [ ] `git status` confirmou que `.env.local` não está sendo comitado
- [ ] `NOTAS.md` tem: o que mudei, por quê, hipótese, números antes/depois, e o que **não** posso concluir
- [ ] Commit com mensagem que diz o que mudou
- [ ] Push na minha branch
- [ ] Pull request aberto contra `webtech-network/workshop-jev`
- [ ] Revisei o PR de um colega

---

## O que você leva daqui

Nada disso é específico do Jev:

1. **Modelo de decisão tipada ≠ LLM generativo.** São ferramentas diferentes
   para problemas diferentes, e a API trata as duas como coisas distintas.
2. **Quando uma API devolve um número, pergunte que grandeza ele mede.** O
   `score` do Jev parecia um índice e era um valor esperado — e o bug não
   trava, só mente.
3. **Grave o dado cru, derive as leituras depois.** Foi isso que permitiu
   responder perguntas novas sem pagar chamadas novas.
4. **Relatório sem baseline é propaganda.** "5% de acerto exato" era o mesmo
   que chutar 600 em todas.
5. **Diagnostique antes de consertar.** Viés e falta de discriminação parecem
   o mesmo erro e exigem consertos opostos — tratar os dois igual **piorou** o
   resultado, e isso foi medido, não suposto.
6. **Diga onde o seu número não existe.** A v3 não tem validação fechada, e o
   projeto diz isso em voz alta. É o que separa engenharia de marketing.

**[← Voltar ao README](../README.md)**
