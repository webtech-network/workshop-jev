#!/usr/bin/env python3
"""Separa uma amostra estratificada do Essay-BR (split de teste) para avaliacao.

Estratifica pela nota total para que a amostra cubra a faixa inteira em vez de
se acumular em 600/680, que dominam a distribuicao do corpus.

    python3 sample.py --n 10 --out sample.jsonl
"""
import argparse, ast, csv, json, random, sys
from collections import defaultdict
from pathlib import Path

CSV_TESTE = Path(__file__).parent / "data/essay/essay-br/splits/testing.csv"


def carregar(caminho):
    csv.field_size_limit(10**7)
    if not Path(caminho).exists():
        sys.exit(f"dataset nao encontrado em {caminho}\n"
                 "O workshop ja vem com sample.jsonl pronto -- voce so precisa do\n"
                 "dataset se quiser gerar uma amostra nova. Para baixa-lo, veja SETUP.md\n"
                 "(secao 'Opcional: o dataset completo').")
    with open(caminho, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    redacoes, descartadas = [], 0
    for i, linha in enumerate(linhas):
        comp = ast.literal_eval(linha["competence"])
        total = int(linha["score"])
        # Nunca confie no dataset sem checar: a soma das 5 competencias tem de
        # bater com o total. Linhas que discordam sao excluidas e reportadas.
        if len(comp) != 5 or sum(comp) != total:
            descartadas += 1
            continue
        redacoes.append({
            "idx": i,
            "prompt_id": int(linha["prompt"]),
            "titulo": linha["title"],
            "texto": "\n\n".join(ast.literal_eval(linha["essay"])),
            "gold_competencias": comp,
            "gold_total": total,
        })
    return redacoes, descartadas


def estratificar(redacoes, n, seed):
    """Amostra espalhada pela faixa de notas.

    Escolhe n estratos equidistantes ao longo das notas existentes (nao os n
    primeiros), para que a amostra cubra do piso ao teto do corpus. Se n for
    maior que o numero de estratos, completa em round-robin.
    """
    random.seed(seed)
    estratos = defaultdict(list)
    for r in redacoes:
        estratos[r["gold_total"]].append(r)
    for v in estratos.values():
        random.shuffle(v)

    chaves = sorted(estratos)
    if n >= len(chaves):
        alvos = list(chaves)
    else:
        # indices equidistantes: primeiro, ultimo e n-2 intermediarios
        alvos = [chaves[round(j * (len(chaves) - 1) / (n - 1))] for j in range(n)] \
            if n > 1 else [chaves[len(chaves) // 2]]

    amostra, i = [], 0
    vistos = list(dict.fromkeys(alvos))
    while len(amostra) < n:
        disponiveis = [k for k in vistos if estratos[k]] or [k for k in chaves if estratos[k]]
        if not disponiveis:
            break
        k = disponiveis[i % len(disponiveis)]
        amostra.append(estratos[k].pop())
        i += 1
    return sorted(amostra, key=lambda r: r["gold_total"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--csv", default=str(CSV_TESTE))
    p.add_argument("--out", default="sample.jsonl")
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()

    redacoes, descartadas = carregar(a.csv)
    print(f"corpus: {len(redacoes)} redacoes validas, {descartadas} descartadas (soma != total)")
    if not redacoes:
        sys.exit("nenhuma redacao valida encontrada")

    amostra = estratificar(redacoes, a.n, a.seed)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in amostra:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    notas = [r["gold_total"] for r in amostra]
    print(f"amostra: {len(amostra)} redacoes -> {a.out}")
    print(f"faixa de notas: {min(notas)} a {max(notas)} | notas: {notas}")


if __name__ == "__main__":
    main()
