# SETUP — faça isto antes do workshop

Tempo estimado: **20 minutos**. Ao final há um comando de verificação; se ele
passar, você está pronto.

Se travar em qualquer passo, chegue 15 minutos antes do workshop — resolvemos
juntos. Não deixe para a hora.

---

## 1. Python 3.10 ou mais novo

Confira o que você tem:

```bash
python3 --version
```

Se aparecer `Python 3.10.x` ou maior, pule para o passo 2.

**Linux (Ubuntu/Debian):**

```bash
sudo apt update && sudo apt install -y python3 python3-pip git
```

**macOS** (com [Homebrew](https://brew.sh)):

```bash
brew install python git
```

**Windows:** instale pelo [python.org/downloads](https://www.python.org/downloads/).
Na primeira tela do instalador, **marque "Add python.exe to PATH"** — sem isso
nada funciona no terminal.

> ### Windows: use o Git Bash, não o CMD nem o PowerShell
>
> O material usa comandos de shell Unix (`cat`, `sed`, `ls -la`) e blocos
> `python3 -c "..."` de várias linhas. No **CMD** uma quebra de linha encerra o
> comando, e no **PowerShell** as aspas escapadas se comportam de outro jeito —
> metade dos exercícios não roda.
>
> **O Git Bash já vem instalado com o Git** (passo 2). Abra-o pelo menu
> Iniciar → "Git Bash" e rode **tudo** por ele. Nele os comandos deste
> workshop funcionam exatamente como estão escritos.
>
> **`python` ou `python3`?** No Windows o comando normalmente é `python`. Se
> `python3 --version` falhar e `python --version` funcionar, troque `python3`
> por `python` em todos os comandos. Para não ter de pensar nisso o resto do
> dia, crie um atalho no Git Bash:
>
> ```bash
> echo "alias python3=python" >> ~/.bashrc && source ~/.bashrc
> ```

**Este workshop não usa nenhuma biblioteca externa.** Só a biblioteca padrão do
Python — nada de `pip install`, nada de ambiente virtual. Se algum comando
pedir um pacote, algo está errado; chame o instrutor.

---

## 2. Git configurado

```bash
git --version
```

Se não tiver, instale junto com o Python no passo 1 (Linux/macOS) ou pelo
[git-scm.com](https://git-scm.com/downloads) (Windows).

Agora diga ao Git quem você é — sem isso ele recusa commits:

```bash
git config --global user.name "Seu Nome"
```

```bash
git config --global user.email "seu-email@exemplo.com"
```

Use o **mesmo e-mail da sua conta do GitHub**, senão os commits não aparecem
ligados ao seu perfil.

---

## 3. Autenticação no GitHub

> ⚠️ **Senha de conta não funciona mais.** O GitHub removeu autenticação por
> senha em 2021. Se o terminal pedir "Password" e você digitar a senha do
> site, vai falhar. Use uma das opções abaixo.

### Opção A — GitHub CLI (recomendada, é a mais rápida)

Instale o `gh`:

- **Linux:** `sudo apt install gh` (ou veja [cli.github.com](https://cli.github.com))
- **macOS:** `brew install gh`
- **Windows:** `winget install GitHub.cli`

Depois autentique:

```bash
gh auth login
```

Responda: `GitHub.com` → `HTTPS` → `Y` (autenticar o Git com suas credenciais)
→ `Login with a web browser`. Ele mostra um código de 8 caracteres, você cola
no navegador e pronto. Confira:

```bash
gh auth status
```

### Opção B — GitHub Desktop (se você prefere clicar)

Instale o [GitHub Desktop](https://desktop.github.com/) e faça login nele.
Ele cuida da autenticação do Git automaticamente. Você ainda vai precisar do
terminal para rodar os scripts Python — o Desktop só cuida do Git.

### Opção C — Personal Access Token (último recurso)

Em **github.com → Settings → Developer settings → Personal access tokens →
Tokens (classic) → Generate new token**, marque o escopo `repo`. Guarde o
token: quando o Git pedir "Password", cole o token em vez da senha.

---

## 4. Fork e clone deste repositório

**Fork** é a sua cópia pessoal do repositório na sua conta do GitHub. Você
trabalha no fork e, no fim do workshop, abre um *pull request* de volta.

Com o `gh` (faz o fork e o clone num comando):

```bash
gh repo fork webtech-network/workshop-jev --clone
```

Sem o `gh`: abra `https://github.com/webtech-network/workshop-jev`, clique em
**Fork** no canto superior direito, e depois clone a **sua** cópia:

```bash
git clone https://github.com/SEU-USUARIO/workshop-jev.git
```

Entre na pasta:

```bash
cd workshop-jev
```

> **Rode tudo daqui.** Os scripts procuram `rubric.json` e `sample.jsonl` no
> diretório atual. Se você rodar de outra pasta, eles não acham nada.

---

## 5. A chave da API

O instrutor passa a chave no dia (chat, slide ou quadro). Ela **não está** no
repositório e nunca deve entrar nele.

Copie o modelo:

```bash
cp .env.example .env.local
```

Abra `.env.local` num editor de texto e cole a chave depois do `=`:

```
AI_GATEWAY_API_KEY=cole-a-chave-aqui
```

Regras para não perder tempo depurando:

- **Sem espaços** em volta do `=`.
- **Sem aspas** em volta da chave.
- **Uma linha só**, sem quebra no meio.

> ### Windows: duas armadilhas neste arquivo
>
> **1. O Notepad salva `.env.local.txt`.** O Bloco de Notas acrescenta `.txt`
> escondido. Na caixa "Salvar como", escolha **Tipo: Todos os arquivos** e
> digite o nome entre aspas: `".env.local"`.
>
> **2. O PowerShell grava em UTF-16.** Se você criar o arquivo com
> `echo ... > .env.local` no PowerShell, ele sai em UTF-16 e não em UTF-8. O
> `evaluate.py` deste workshop já lida com isso (e com o BOM do Notepad), mas
> outras ferramentas não — é um erro que vale conhecer.
>
> **O jeito que funciona sempre:** crie o arquivo no **Git Bash**, que grava
> UTF-8 limpo:
>
> ```bash
> echo AI_GATEWAY_API_KEY=cole-a-chave-aqui > .env.local
> ```
>
> Confirme o nome com `ls -a`: deve listar `.env.local`, **não**
> `.env.local.txt`.

### Confirme que o Git está ignorando a chave

Este comando é a sua apólice de seguro. Rode-o:

```bash
git check-ignore -v .env.local
```

Deve imprimir uma linha citando o `.gitignore`. Se **não imprimir nada**, pare
e chame o instrutor: significa que a chave pode ser comitada por acidente.

E confirme que ela não está no que você vai comitar:

```bash
git status --short
```

`.env.local` **não deve aparecer** nessa lista.

---

## 6. Verificação final

Rode os dois comandos abaixo. Nenhum deles chama a API nem gasta nada.

```bash
python3 evaluate.py --dry-run
```

Esperado: um JSON grande na tela, terminando com
`[dry-run] 100 redacoes seriam avaliadas; nenhuma chamada feita.`

```bash
python3 compare.py --cache referencia/resultados-referencia-v1.jsonl --sample sample.jsonl
```

Esperado: as tabelas de métricas, começando com `100 redacoes avaliadas` e uma
linha `TOTAL` com QWK em torno de `0.5`.

**Os dois passaram? Você está pronto.** Vá para a
[etapa 1](etapas/01-github.md) no dia do workshop.

---

## Opcional: o dataset completo

O repositório já traz `sample.jsonl` com as 100 redações que vamos usar, então
**você não precisa do dataset** para o workshop. Baixe-o só se quiser gerar uma
amostra diferente com o `sample.py`:

```bash
git clone https://github.com/rafaelanchieta/essay data/essay
```

Depois disso o `sample.py` funciona:

```bash
python3 sample.py --n 10 --out sample-minha.jsonl
```

A pasta `data/` está no `.gitignore` — ela tem o `.git` dela própria e não
entra no seu fork.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `python3: command not found` | Windows, ou PATH não configurado | Use `python`. Se também falhar, reinstale marcando "Add to PATH". |
| No Windows, um `python3 -c "..."` de várias linhas para no meio | Você está no CMD ou no PowerShell | Use o **Git Bash** (passo 1). |
| `cat`, `sed` ou `ls -la` não existem | Idem | Use o **Git Bash**. |
| `UnicodeDecodeError` ao ler a chave | `.env.local` gravado em UTF-16 pelo PowerShell | Recrie o arquivo no Git Bash. |
| `AI_GATEWAY_API_KEY ausente` | `.env.local` não existe, tem nome errado (`.env.local.txt`) ou está vazio | Veja o passo 5. Confirme com `ls -a`. |
| `cache nao encontrado` | Você rodou de outra pasta | `cd` para a raiz do repositório clonado. |
| `fatal: not a git repository` | Idem | `cd workshop-jev` |
| Git pede "Password" e recusa | Senha de conta não funciona | Passo 3: `gh auth login` ou use um token. |
| `Permission denied (publickey)` | Clone por SSH sem chave configurada | Clone por HTTPS: `https://github.com/...`, não `git@github.com:...`. |
| `429 rate_limit_exceeded` | A turma está chamando a API ao mesmo tempo | Normal. Espere e rode de novo — o cache retoma de onde parou. |
