# Etapa 1 — Setup e GitHub

⏱ 20 min · 🔌 não usa a API

> **Objetivo:** todo mundo com o repositório clonado, uma branch própria criada
> e os dois comandos de verificação passando.

---

## 1.1 Checagem rápida (todos juntos)

Rode os três comandos e compare com o colega ao lado:

```bash
python3 --version
```

```bash
git config user.email
```

```bash
git check-ignore -v .env.local
```

O que esperar:

1. Python 3.10 ou maior.
2. O e-mail da sua conta do GitHub.
3. Uma linha citando `.gitignore` — prova de que a chave não vai ser comitada.

Se o terceiro comando não imprimir nada, **pare e avise**. Esse é o único erro
desta etapa que tem consequência fora da sua máquina.

Não passou algum? Volte ao [SETUP.md](../SETUP.md).

---

## 1.2 O fluxo de Git que vamos usar

Este é o fluxo que times usam de verdade. Vale a pena entender o desenho antes
de digitar.

```
webtech-network/workshop-jev     ← o repositório original ("upstream")
            │
            │  fork  (sua cópia na sua conta)
            ▼
   SEU-USUARIO/workshop-jev      ← o "origin", onde você tem permissão de escrever
            │
            │  clone  (cópia na sua máquina)
            ▼
     ./workshop-jev              ← onde você trabalha
            │
            │  branch → commit → push
            ▼
      pull request  ──────────►  de volta para o upstream
```

Três nomes para guardar:

- **`upstream`** — o repositório da WebTech. Você **lê**, não escreve.
- **`origin`** — o seu fork. Você escreve aqui.
- **branch** — uma linha de trabalho paralela. Você nunca commita direto na
  `main`, para que a `main` continue sendo o ponto de partida limpo.

Confira os seus remotos:

```bash
git remote -v
```

Se o `gh repo fork --clone` fez o trabalho, você vê `origin` (seu fork) e
`upstream` (o original). Se só aparecer `origin` apontando para o seu fork,
adicione o upstream:

```bash
git remote add upstream https://github.com/webtech-network/workshop-jev.git
```

---

## 1.3 Crie a sua branch

O nome da branch é o seu identificador no workshop. Use o seu usuário do
GitHub:

```bash
git switch -c rubrica-SEU-USUARIO
```

> `git switch -c` cria e já troca para a branch nova. Em versões antigas do
> Git o comando é `git checkout -b` — faz o mesmo.

Confirme onde você está:

```bash
git status
```

Deve dizer `On branch rubrica-SEU-USUARIO`. É nela que você vai trabalhar até
a etapa 7.

---

## 1.4 Primeiro commit (de mentira, para treinar o fluxo)

Vamos exercitar o ciclo inteiro com uma mudança trivial, antes de ter algo
valioso para perder.

Crie um arquivo com o seu nome:

```bash
echo "# Notas de SEU-USUARIO" > NOTAS.md
```

Veja o que o Git enxerga:

```bash
git status --short
```

Você deve ver `?? NOTAS.md`. **Não deve ver `.env.local`** — se vir, pare e
chame o instrutor.

Adicione, comite e envie:

```bash
git add NOTAS.md
```

```bash
git commit -m "Adiciona notas de SEU-USUARIO"
```

```bash
git push -u origin rubrica-SEU-USUARIO
```

O `-u` só é necessário no primeiro push de uma branch: ele liga a sua branch
local à do servidor. Depois disso, `git push` sozinho basta.

Abra o seu fork no navegador e confirme que a branch e o arquivo apareceram:

```bash
gh repo view --web
```

---

## 1.5 Use o `NOTAS.md` de verdade

Esse arquivo não é descartável — ele é o seu caderno do workshop, e vai virar
o conteúdo do seu pull request na etapa 7. Anote nele, à medida que avança:

- o que você mudou na rubrica e **por quê**;
- os números antes e depois;
- o que te surpreendeu.

Um pull request com números e um parágrafo de raciocínio é o que diferencia
"fiz o exercício" de "entendi o problema".

---

## Checklist

- [ ] `python3 --version` → 3.10+
- [ ] `git config user.email` → o e-mail do seu GitHub
- [ ] `git check-ignore -v .env.local` → imprime uma linha
- [ ] `.env.local` existe e tem a chave do instrutor
- [ ] Branch `rubrica-SEU-USUARIO` criada
- [ ] Primeiro commit empurrado e visível no GitHub
- [ ] `python3 compare.py --cache referencia/resultados-referencia-v1.jsonl --sample sample.jsonl` roda

**Próxima:** [Etapa 2 — O conceito](02-conceito.md)
