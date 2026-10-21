# Workshop JEV — corrigindo redações com um modelo de decisão

> Workshop prático da **WebTech**. Você vai, junto com o instrutor, montar um
> corretor automático de redações do ENEM usando o modelo **Jev** e descobrir
> — medindo, não opinando — o quanto ele concorda com corretores humanos.

Ao final você vai saber:

- a diferença entre um **LLM generativo** (ChatGPT, Claude) e um **modelo de decisão tipada** (Jev), e quando cada um serve;
- como chamar uma API de avaliação e ler a resposta **sem cair na pegadinha** que produz notas erradas;
- como medir concordância com gente de verdade (**QWK**, MAE, viés) e por que uma **baseline burra** é obrigatória;
- como transformar uma rubrica em código e **iterar nela** com validação honesta;
- o fluxo de GitHub que times usam de verdade: fork → branch → commit → pull request.

**Não precisa de GPU, nem de placa de vídeo, nem de conta paga.** A chave da API é
fornecida pelo instrutor no dia.

---

## Antes do workshop (faça em casa, ~20 min)

**Escolha onde vai trabalhar.** As 7 etapas são idênticas nas duas trilhas —
os mesmos comandos `python3 ...`, os mesmos exercícios. Muda só onde você
digita e onde a chave fica guardada.

| | Trilha | Para quem |
|---|---|---|
| 🌐 | **[SETUP-WEB.md](SETUP-WEB.md)** — Replit ou GitHub Codespaces | **Não instala nada.** PC de laboratório, máquina sem permissão de instalar, ou quem prefere não mexer no próprio ambiente. Precisa só do navegador e de uma conta no GitHub. |
| 💻 | **[SETUP.md](SETUP.md)** — Python e Git na sua máquina | Quem já tem o ambiente, ou quer ficar com ele montado depois do workshop. |

Na dúvida, vá de **web**: nada para instalar, e nada para dar errado na hora.

Qualquer que seja a trilha, ela termina com:

```bash
python3 verificar.py
```

Se passar, você está pronto. Se travar, chegue 15 minutos antes e resolvemos
juntos — não deixe para a hora.

> 🤖 **Vai usar IA?** O Replit tem assistente embutido, e você pode usar
> ChatGPT, Claude ou Copilot em qualquer trilha. É incentivado, com três
> regras que protegem a chave e o seu aprendizado: **[IA.md](IA.md)**.

---

## Agenda

| | Etapa | Duração | Precisa da API? |
|---|---|---|---|
| 1 | [Setup e GitHub](etapas/01-github.md) — fork, clone, branch | 20 min | não |
| 2 | [O conceito](etapas/02-conceito.md) — dois tipos de IA, pergunta tipada | 20 min | não |
| 3 | [A primeira chamada](etapas/03-primeira-chamada.md) — `--dry-run`, depois 1 redação de verdade | 25 min | **sim** |
| 4 | [A pegadinha do `score`](etapas/04-pegadinha-score.md) — o campo que não é o que parece | 20 min | não |
| 5 | [Medindo](etapas/05-metricas.md) — QWK, baseline, viés, limiar de confiança | 35 min | não |
| 6 | [Sua rubrica](etapas/06-sua-rubrica.md) — diagnosticar, editar, re-rodar | 40 min | **sim** |
| 7 | [Pull request](etapas/07-pull-request.md) — publicar o seu resultado | 20 min | não |

Só as etapas 3 e 6 gastam chamadas de API, e de propósito: a chave é
compartilhada pela turma, então cada aluno roda poucas redações. Todo o resto
funciona **offline**, usando um cache de resultados que já vem no repositório.

---

## Mapa dos arquivos

### O que você edita

| Arquivo | Papel |
|---|---|
| **`rubric.json`** | **A régua.** As 5 competências do ENEM, 6 âncoras cada, e o limiar de confiança. É o arquivo da etapa 6. Mexer aqui é o trabalho — o pipeline fica intacto. |

### O pipeline (leia, não precisa mudar)

| Arquivo | Papel |
|---|---|
| `verificar.py` | Confere se o seu ambiente está pronto: Python, arquivos, rubrica válida, chave e proteção do `.gitignore`. **Não chama a API.** Funciona igual nas três trilhas e sabe em qual você está. |
| `sample.py` | Separa uma amostra estratificada por nota, para cobrir de 0 a 1000 em vez de empilhar no 600. |
| `evaluate.py` | Chama o Jev, uma requisição por redação, com cache em JSONL e backoff em erro 429. |
| `compare.py` | Lê o cache e reporta QWK, MAE, viés, acerto exato/adjacente, Pearson, baseline constante e a tabela de limiar. **Nunca toca a API.** |

### Dados que já vêm prontos

| Arquivo | Papel |
|---|---|
| `sample.jsonl` | 100 redações do Essay-BR com nota humana, amostra estratificada de 0 a 1000. É a turma inteira avaliando as mesmas redações. |
| `sample-mini.jsonl` | 10 dessas 100, espalhadas pela faixa inteira. É a amostra das **suas** rodadas (etapa 6): poucas chamadas, e o "antes" já está no cache de referência, então a comparação é nas mesmas redações. |
| `referencia/resultados-referencia-v1.jsonl` | Cache de uma rodada completa das 100 redações com a `rubric.json` de partida. **É o que faz as etapas 4, 5 e 7 rodarem sem gastar API.** |
| `referencia/DADOS.md` | De onde vêm as redações, licença e citação. |
| `rubric-referencia-v3.json` | **Gabarito.** A rubrica a que o laboratório original chegou. Não abra antes da etapa 6. |

### Para entender a fundo

| Arquivo | Papel |
|---|---|
| `docs/ARQUITETURA.md` | Guia didático completo: como o Jev funciona, anatomia da chamada e da resposta, padrões de código, cartão de memorização. Leia na etapa 2. |
| `docs/arquitetura.html` | O mesmo guia como página web, com os diagramas renderizados. Abra no navegador. |

---

## Os três comandos que você vai repetir

Rode **sempre da raiz do repositório** (a pasta `workshop-jev`) — os scripts
procuram `rubric.json` e `sample.jsonl` no diretório atual.

Onde digitar: no **Shell** do Replit, no **terminal** do Codespaces, ou no seu
terminal local (no Windows, use o **Git Bash**).

**1. Ver a requisição sem gastar nada:**

```bash
python3 evaluate.py --dry-run --sample sample-mini.jsonl
```

**2. Avaliar as 10 redações da mini-amostra com a sua rubrica:**

```bash
python3 evaluate.py --sample sample-mini.jsonl --cache resultados-meus-v2.jsonl
```

> **Um `--cache` novo por rubrica.** O cache pula o que já foi avaliado. Se
> você reusar o arquivo de uma rubrica anterior, o script devolve `[pulado]` e
> você mede a rubrica velha acreditando medir a nova.

**3. Medir — e comparar com o "antes" nas mesmas 10 redações:**

```bash
python3 compare.py --cache resultados-meus-v2.jsonl --sample sample-mini.jsonl
```

```bash
python3 compare.py --cache referencia/resultados-referencia-v1.jsonl --sample sample-mini.jsonl
```

> Use `--sample sample-mini.jsonl` nas suas rodadas, não `sample.jsonl`. O
> `sample.jsonl` está **ordenado por nota**: pegar as primeiras com `--limit`
> daria só redações nota 0, e a métrica não diria nada.

---

## Regras do workshop

1. **A chave é compartilhada.** Rode sempre sobre `sample-mini.jsonl`, que são
   10 redações — na etapa 3, com `--limit` menor ainda. Quem roda as 100 de
   `sample.jsonl` derruba o provedor para a turma inteira: ele devolve `429`
   sob carga, às vezes por minutos.
2. **Nunca comite a chave.** No Replit ela vive em **Secrets**; nas outras
   trilhas, em `.env.local`, que está no `.gitignore`. Forks de repositório
   público são públicos. E ela **nunca** entra num chat com IA — veja
   [IA.md](IA.md).
3. **Cada rubrica merece seu próprio `--cache`.** Misturar rodadas no mesmo
   arquivo mistura coortes e produz métrica sem sentido.
4. **Não rode dois `evaluate.py` sobre o mesmo `--cache`** ao mesmo tempo:
   eles duplicam registros.

---

## Onde isto nasceu

Este workshop é a versão didática do **LAB Jev** da WebTech, que investigou se
o Jev serve como corretor de trabalhos acadêmicos. O laboratório chegou a um
QWK de ~0,50 contra uma baseline de 0,00 — utilizável como **ranqueador**, não
ainda como atribuidor de nota absoluta. Você vai refazer esse caminho e,
na etapa 6, tentar melhorá-lo.

Licença das redações e citação do corpus: [referencia/DADOS.md](referencia/DADOS.md).
