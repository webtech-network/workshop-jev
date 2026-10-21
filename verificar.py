#!/usr/bin/env python3
"""Confere se o ambiente esta pronto para o workshop. NAO chama a API.

Funciona igual no Replit, no Codespaces e na maquina local. Rode:

    python3 verificar.py

Cada checagem imprime [ok] ou [--] com o que fazer para resolver.
"""
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).parent
COMPS = ["c1", "c2", "c3", "c4", "c5"]

ok = []
falta = []
avisos = []


def checar(nome, condicao, dica="", critico=True):
    """critico=False marca o que impede so parte do workshop, nao tudo.

    A chave da API e o caso: ela chega no dia, e sem ela 5 das 7 etapas
    rodam. Reprovar a verificacao inteira por causa dela faria o aluno
    achar que o ambiente esta quebrado.
    """
    if condicao:
        ok.append((nome, dica))
    elif critico:
        falta.append((nome, dica))
    else:
        avisos.append((nome, dica))
    marca = "ok" if condicao else ("--" if critico else "??")
    print(f"  [{marca}] {nome}")
    if not condicao and dica:
        print(f"       -> {dica}")
    return condicao


def onde_estamos():
    """Identifica o ambiente so para dar a dica certa quando algo falta."""
    if os.environ.get("REPL_ID") or os.environ.get("REPLIT_DEV_DOMAIN"):
        return "Replit"
    if os.environ.get("CODESPACES") or os.environ.get("CODESPACE_NAME"):
        return "Codespaces"
    return "local"


def main():
    ambiente = onde_estamos()
    print(f"Workshop JEV - verificacao de ambiente ({ambiente})\n")

    print("1. Python")
    checar(f"versao {sys.version_info.major}.{sys.version_info.minor} (precisa de 3.10+)",
           sys.version_info >= (3, 10),
           "instale uma versao mais nova; veja SETUP.md")

    print("\n2. Arquivos do workshop")
    precisos = ["rubric.json", "sample.jsonl", "sample-mini.jsonl",
                "evaluate.py", "compare.py",
                "referencia/resultados-referencia-v1.jsonl"]
    for nome in precisos:
        checar(nome, (RAIZ / nome).exists(),
               "voce esta rodando de outra pasta? entre na raiz do repositorio")

    print("\n3. A rubrica e valida")
    try:
        rub = json.loads((RAIZ / "rubric.json").read_text(encoding="utf-8"))
        checar("rubric.json e um JSON valido", True)
        tamanhos = {c: len(rub["competencias"][c]["criteria"]) for c in COMPS}
        checar(f"6 ancoras em cada competencia {tamanhos}",
               all(v == 6 for v in tamanhos.values()),
               "cada 'criteria' precisa de exatamente 6 ancoras, ou a escala 0-200 quebra")
    except FileNotFoundError:
        checar("rubric.json existe", False, "entre na raiz do repositorio")
    except json.JSONDecodeError as e:
        checar(f"rubric.json e um JSON valido (erro: {e})", False,
               "virgula sobrando e o erro mais comum")

    print("\n4. A chave da API")
    do_ambiente = os.environ.get("AI_GATEWAY_API_KEY")
    env_local = RAIZ / ".env.local"
    do_arquivo = None
    if env_local.exists():
        try:
            texto = env_local.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            texto = env_local.read_text(encoding="utf-16")
        for linha in texto.splitlines():
            linha = linha.strip().lstrip("﻿")
            if "=" in linha and not linha.startswith("#"):
                nome, valor = linha.split("=", 1)
                if nome.strip() == "AI_GATEWAY_API_KEY":
                    do_arquivo = valor.strip().strip("\"'") or None

    chave = do_arquivo or do_ambiente
    if ambiente == "Replit":
        dica = "abra Tools -> Secrets e crie AI_GATEWAY_API_KEY com a chave do instrutor"
    elif ambiente == "Codespaces":
        dica = "rode: cp .env.example .env.local  e cole a chave dentro"
    else:
        dica = "crie .env.local com AI_GATEWAY_API_KEY=... (veja SETUP.md)"
    if checar("AI_GATEWAY_API_KEY encontrada", bool(chave), dica, critico=False):
        fonte = ".env.local" if do_arquivo else "variavel de ambiente (Secrets)"
        print(f"       fonte: {fonte} | termina em ...{chave[-6:]}")

    print("\n5. A chave esta protegida do Git")
    gitignore = RAIZ / ".gitignore"
    protegido = gitignore.exists() and ".env.local" in gitignore.read_text(encoding="utf-8")
    checar(".env.local esta no .gitignore", protegido,
           "PARE e avise o instrutor: a chave pode ser comitada por acidente")

    print("\n6. O cache de referencia abre")
    try:
        linhas = (RAIZ / "referencia/resultados-referencia-v1.jsonl").read_text(
            encoding="utf-8").splitlines()
        regs = [json.loads(l) for l in linhas if l.strip()]
        checar(f"{len(regs)} redacoes no cache de referencia", len(regs) == 100,
               "o arquivo parece incompleto; baixe o repositorio de novo")
    except Exception as e:
        checar(f"cache de referencia legivel ({e})", False)

    print()
    if falta:
        print(f"{len(ok)} checagens passaram, {len(falta)} com problema:")
        for nome, _ in falta:
            print(f"  - {nome}")
        print("\nResolva o que esta acima e rode de novo: python3 verificar.py")
        sys.exit(1)

    print(f"Ambiente pronto ({len(ok)} checagens).")
    if avisos:
        print("\nFalta so isto, e nao e bloqueio agora:")
        for nome, dica in avisos:
            print(f"  - {nome}")
            if dica:
                print(f"    {dica}")
        print("\nA chave chega no dia do workshop. Sem ela voce ja faz as etapas")
        print("1, 2, 4, 5 e 7 -- so a 3 e a 6 precisam chamar a API.")

    print("\nProximo passo, que tambem nao gasta API:")
    print("  python3 compare.py --cache referencia/resultados-referencia-v1.jsonl --sample sample.jsonl")


if __name__ == "__main__":
    main()
