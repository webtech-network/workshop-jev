# SETUP WEB — o workshop inteiro no navegador

Para quem não vai instalar nada: nenhum Python, nenhum Git, nenhum terminal na
máquina. Só o navegador e uma conta no GitHub.

Use este guia se você está num PC de laboratório, numa máquina sem permissão de
instalar programas, ou se simplesmente prefere não mexer no seu ambiente. Para
a instalação local, veja o [SETUP.md](SETUP.md).

> **O que é igual nas duas trilhas:** todos os comandos `python3 ...` das 7
> etapas são **exatamente os mesmos**. O que muda é só onde você digita e onde
> a chave da API fica guardada.

---

## Qual trilha escolher

| | **Replit** | **GitHub Codespaces** |
|---|---|---|
| Conta necessária | GitHub **+** Replit | só GitHub |
| Tem IA integrada | **sim** (veja [IA.md](IA.md)) | sim, com Copilot se você tiver |
| Git já autenticado | precisa conectar | **sim, de fábrica** |
| Franquia gratuita | créditos limitados, **confira antes** | 120 h/mês na conta pessoal Free |
| Terminal | painel **Shell** | terminal do VS Code |

**Não sabe escolher?** Vá de **Codespaces**: você já precisa da conta do GitHub
para entregar o pull request, o Git já vem autenticado, e a franquia gratuita é
folgada para um workshop de 3 h. Vá de **Replit** se quiser usar a IA integrada
durante os exercícios.

> ⚠️ **Sobre a franquia do Replit.** O plano gratuito (Starter) funciona por
> créditos de agente e de nuvem, e a Replit não publica os limites exatos na
> página de preços. Pode ser que um workshop de 3 h caiba com folga, pode ser
> que não. **Teste com uma conta gratuita antes do dia** — ou use a trilha
> Codespaces, cujo limite está documentado.

---

# Trilha A — GitHub Codespaces

## A.1 Faça o fork primeiro

**Este passo vem antes de abrir qualquer ambiente.** Se você abrir um Codespace
direto no repositório da WebTech, vai cair num repositório onde não tem
permissão de escrever, e descobre isso só na hora de entregar.

1. Abra **https://github.com/webtech-network/workshop-jev**
2. Clique em **Fork**, no canto superior direito.
3. Confirme. Agora você está em `github.com/SEU-USUARIO/workshop-jev`.

## A.2 Abra o Codespace **no seu fork**

Confira que a barra de endereço mostra **o seu usuário**, não `webtech-network`.

Então: botão verde **Code** → aba **Codespaces** → **Create codespace on main**.

A primeira abertura leva 1–2 minutos: o GitHub monta um contêiner com Python
3.12, Git e o repositório já clonado, a partir do
[`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json) que vem no
repositório.

## A.3 A chave da API

No Codespaces, a chave vai num arquivo, como na trilha local. No terminal:

```bash
cp .env.example .env.local
```

Abra o `.env.local` na barra lateral e cole a chave do instrutor depois do `=`,
sem espaços e sem aspas.

O `.env.local` está no `.gitignore`, então ele não entra em commit nenhum.

## A.4 Verifique

```bash
python3 verificar.py
```

Pule para [Verificação final](#verificação-final).

---

# Trilha B — Replit

## B.1 Faça o fork primeiro

Igual à trilha A: **o fork vem antes**.

1. Abra **https://github.com/webtech-network/workshop-jev**
2. Clique em **Fork** → confirme.
3. Copie a URL do **seu** fork: `https://github.com/SEU-USUARIO/workshop-jev`

## B.2 Importe o **seu fork** no Replit

1. Entre em **https://replit.com** e faça login (dá para entrar com a conta do
   GitHub).
2. Vá em **https://replit.com/import**.
3. Cole a URL **do seu fork** — não a da WebTech.
4. Confirme. O Replit clona o repositório e monta o ambiente Python.

> Se o Replit perguntar como rodar o projeto, aponte para `verificar.py`, ou
> simplesmente ignore: o workshop é feito pelo painel **Shell**, digitando os
> comandos.

## B.3 A chave da API vai em **Secrets**, não num arquivo

Esta é a diferença importante da trilha Replit.

1. Na barra lateral, abra **Tools** → **Secrets**.
2. **New secret**, com:
   - **Key:** `AI_GATEWAY_API_KEY`
   - **Value:** a chave que o instrutor passou
3. Salve.

**Não crie um `.env.local` no Replit.** Secrets é melhor por dois motivos
concretos: o valor não entra no histórico do Git e não é copiado quando alguém
faz um fork do seu Repl. Um arquivo faz as duas coisas erradas.

O `evaluate.py` lê a chave da variável de ambiente quando não há `.env.local`, e
o Replit expõe cada Secret como variável de ambiente. Não é preciso mudar nada
no código.

## B.4 Verifique

Abra o painel **Shell** (não o Console) e digite:

```bash
python3 verificar.py
```

Ele deve imprimir `(Replit)` na primeira linha e, na seção 4,
`fonte: variavel de ambiente (Secrets)`.

---

## Verificação final

Vale para as duas trilhas. Nenhum dos comandos chama a API.

```bash
python3 verificar.py
```

Esperado: `Ambiente pronto (12 checagens)` — ou 11 mais um aviso, se a chave
ainda não chegou, o que é normal antes do dia.

```bash
python3 compare.py --cache referencia/resultados-referencia-v1.jsonl --sample sample.jsonl
```

Esperado: as tabelas de métricas, começando com `100 redacoes avaliadas`.

**Passaram? Você está pronto.** Vá para a [etapa 1](etapas/01-github.md).

---

## Entregar o pull request sem usar Git

A etapa 7 pede um pull request. Nas trilhas web, o caminho mais confiável
**não usa Git nenhum** — é a interface do próprio GitHub:

1. Abra o seu fork no navegador.
2. Clique no arquivo (`rubric.json` ou `NOTAS.md`) e no ícone de **lápis**.
3. Edite e clique em **Commit changes**.
4. Escolha **"Create a new branch for this commit and start a pull request"**.
5. Nomeie a branch `rubrica-SEU-USUARIO` e confirme.

Isso cria branch, commit e pull request de uma vez. A [etapa 7](etapas/07-pull-request.md)
detalha o que escrever.

> **Por que não `git push` do ambiente web?** Dá para fazer, e a etapa 7 explica
> como. Mas no Replit depende de conectar a conta do GitHub, e num Codespace
> aberto a partir de um fork o `gh pr create` às vezes não enxerga o
> repositório de origem. A interface web funciona sempre.

---

## Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `python3: command not found` no Replit | você está no **Console**, não no **Shell** | abra o painel Shell |
| `AI_GATEWAY_API_KEY ausente` no Replit | Secret com nome errado, ou criado depois do Shell abrir | confira o nome exato e **reabra o Shell** |
| `cache nao encontrado` | você está em outra pasta | `cd ~/workspace/workshop-jev` (Replit) ou `cd /workspaces/workshop-jev` (Codespaces) |
| Não consigo dar push | você abriu o repositório da WebTech, não o seu fork | confira a URL; refaça o fork |
| `429 rate_limit_exceeded` | a turma está chamando a API junto | normal; espere e rode de novo, o cache retoma |
| O Codespace parou sozinho | ele hiberna após ~30 min parado | reabra pelo github.com; os arquivos continuam lá |
| Acabaram os créditos do Replit | franquia do plano gratuito | troque para a trilha Codespaces; o material é o mesmo |

---

## Se a rede da PUC bloquear os sites

As chamadas à API partem do ambiente de nuvem, **não** do PC do laboratório —
então a rede da PUC só precisa abrir os sites, não a API da Vercel.

Se `replit.com` ou `github.com` estiverem bloqueados, avise o instrutor: o
material roda igual numa máquina local com Python (veja o [SETUP.md](SETUP.md)),
e 5 das 7 etapas não precisam nem de internet depois do download, porque usam o
cache de referência que já vem no repositório.
