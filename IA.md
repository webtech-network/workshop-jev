# Usando IA no workshop

O Replit tem um assistente de IA embutido, e você provavelmente tem o
ChatGPT, o Claude ou o Copilot à mão. Usar é permitido e incentivado — mas
num workshop sobre **avaliar se um modelo funciona**, usar IA sem critério é
a forma mais rápida de terminar com um resultado que você não sabe defender.

Este documento é curto e tem duas partes: as três regras, e onde a IA ajuda
de verdade.

> Tudo aqui é **opcional**. As 7 etapas funcionam inteiras sem IA nenhuma, e a
> franquia gratuita de IA do Replit é limitada — não gaste com o que você faria
> melhor sozinho.

---

## As três regras

### 1. A chave nunca entra no chat

**Não cole a chave da API numa conversa com IA.** Não peça para a IA
"configurar a chave", "consertar o erro de autenticação" ou "criar o arquivo
de ambiente".

O motivo é concreto, e já aconteceu com gente competente: você mostra o erro
`AI_GATEWAY_API_KEY ausente`, o assistente resolve escrevendo a chave
direto dentro de um arquivo `.py` ou `.json` — que **não** está no
`.gitignore` — e no fim do workshop esse arquivo vai num pull request para um
repositório **público**. A chave é compartilhada pela turma: vazou, o
instrutor tem de revogar, e o workshop acaba para todo mundo.

Problema com a chave? Siga o [SETUP-WEB.md](SETUP-WEB.md) ou chame o
instrutor. Nunca o assistente.

### 2. A IA pode mexer na rubrica, não no pipeline

| Pode | Não pode |
|---|---|
| `rubric.json` | `evaluate.py` |
| `NOTAS.md` | `compare.py` |
| explicar qualquer código | `sample.py` |
| interpretar a saída do `compare.py` | instalar bibliotecas |

A razão não é burocrática: se o pipeline mudar entre a sua medição "antes" e a
"depois", **os dois números deixam de ser comparáveis** e o seu experimento
perde o sentido. Assistentes de IA adoram "melhorar" o código de passagem —
trocar uma biblioteca, refatorar uma função, adicionar um `requirements.txt`.
Aqui isso destrói o resultado.

Se o assistente editar um desses arquivos sem você pedir, desfaça:

```bash
git checkout evaluate.py compare.py sample.py
```

### 3. A hipótese é sua, escrita antes

Na [etapa 6](etapas/06-sua-rubrica.md) você vai reescrever âncoras da rubrica.
A ordem importa:

1. **Você** olha o diagnóstico e escreve no `NOTAS.md` o que acha que está
   errado e o que espera que mude.
2. **Depois** disso, se quiser, chama a IA para ajudar a redigir.

Invertido, o que acontece é que a IA propõe algo, você acha razoável, roda, e
qualquer resultado parece confirmar alguma coisa. Com a hipótese escrita antes,
o resultado pode te contrariar — e é aí que você aprende.

---

## Onde a IA ajuda de verdade

### Entender o código (etapas 2 a 4)

Cole um trecho e pergunte. Prompts que funcionam melhor que "explica isso":

> Este é um trecho de um script que avalia redações. Explique o que a função
> `extrair_notas` faz, e **por que** ela guarda dois valores diferentes para a
> mesma nota em vez de escolher um.

> Neste JSON de resposta, `score` vale 2.49 e as probabilidades são
> `{0: 0, 1: 0.04, 2: 0.48, 3: 0.43, 4: 0.05, 5: 0}`. Que relação existe entre
> os dois? Mostre a conta.

### Interpretar as métricas (etapa 5)

> Esta é a saída de um script que compara notas de um modelo com notas de
> corretores humanos, em 100 redações: [cole a saída]. Explique o que o QWK
> mede e por que o relatório inclui uma "baseline constante". Não me diga se o
> modelo é bom — eu quero entender as métricas para decidir isso sozinho.

A última frase é o truque: sem ela o assistente entrega a conclusão pronta, e
você perde o exercício.

### Reescrever âncoras (etapa 6)

Depois de escrever a sua hipótese. Dê o contexto completo:

> Estou ajustando uma rubrica do ENEM usada por um modelo que escolhe **um
> entre 6 níveis** (0 a 5, que viram notas 0 a 200 de 40 em 40). O modelo está
> pondo quase todas as redações no nível 4 da competência 3 — ele não está
> enviesado, está **sem discriminação**: redação nota 0 e redação nota 200
> recebem o mesmo nível.
>
> As âncoras atuais são estas: [cole os 6 `criteria` de c3]
>
> Reescreva as 6 âncoras trocando adjetivos vagos ("domínio mediano") por
> critérios **contáveis e verificáveis no texto** da redação. Mantenha
> exatamente 6, em ordem crescente, sem acentos. Não mude nenhuma outra parte
> do arquivo.

Depois valide **sempre** — a IA erra a contagem de âncoras com frequência:

```bash
python3 verificar.py
```

### Escrever o `NOTAS.md` (etapa 7)

Use a IA para revisar, não para inventar:

> Revise este texto que descreve um experimento. Os números são meus e estão
> corretos — não mude nenhum. Aponte onde eu afirmo mais do que os dados
> sustentam, considerando que a amostra tem só 10 redações.

Essa é, aliás, a melhor aplicação de IA num relatório técnico: caçar o excesso
de confiança que a gente não enxerga no próprio texto.

---

## O detalhe bonito deste workshop

Repare no que você está fazendo na etapa 6: usando um **LLM generativo** (que
escreve texto livre) para redigir as âncoras que vão guiar um **modelo de
decisão tipada** (que não escreve nada, só escolhe um nível com probabilidade).

É exatamente a divisão de trabalho da [etapa 2](etapas/02-conceito.md) — e é
assim que sistemas reais combinam os dois: o generativo redige e explica, o
tipado decide e dá a confiança. Nenhum dos dois faz bem o trabalho do outro.
