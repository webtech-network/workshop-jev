#!/usr/bin/env python3
"""Compara as notas do Jev com as notas humanas do Essay-BR.

Le o cache gravado por evaluate.py (nunca a API) e reporta, por competencia e
para o total:
  QWK   - Quadratic Weighted Kappa, metrica padrao para correcao automatica
  MAE   - erro medio absoluto, em pontos ENEM
  exata - % de acerto na faixa exata
  adj   - % de acerto dentro de uma faixa de 40 pontos
  r     - correlacao de Pearson

Inclui uma baseline constante (prever sempre a nota mais frequente). A
distribuicao do corpus e concentrada, entao sem essa baseline um QWK medíocre
parece bom.

    python3 compare.py [--cache resultados.jsonl] [--csv metricas.csv]
"""
import argparse, json, math, sys
from collections import Counter
from pathlib import Path

COMPS = ["c1", "c2", "c3", "c4", "c5"]


def qwk(a, b, minimo, maximo, passo):
    """Quadratic Weighted Kappa sobre notas discretas de minimo a maximo."""
    niveis = list(range(minimo, maximo + 1, passo))
    idx = {v: i for i, v in enumerate(niveis)}
    n = len(niveis)
    if len(a) == 0:
        return float("nan")

    O = [[0] * n for _ in range(n)]
    for x, y in zip(a, b):
        O[idx[x]][idx[y]] += 1

    ha, hb = Counter(a), Counter(b)
    total = len(a)
    E = [[ha[niveis[i]] * hb[niveis[j]] / total for j in range(n)] for i in range(n)]

    num = den = 0.0
    for i in range(n):
        for j in range(n):
            w = ((i - j) ** 2) / ((n - 1) ** 2)
            num += w * O[i][j]
            den += w * E[i][j]
    if den == 0:
        return float("nan")
    return 1 - num / den


def pearson(a, b):
    n = len(a)
    if n < 2:
        return float("nan")
    ma, mb = sum(a) / n, sum(b) / n
    va = math.sqrt(sum((x - ma) ** 2 for x in a))
    vb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if va == 0 or vb == 0:
        return float("nan")
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb)


def metricas(gold, pred, minimo, maximo, passo):
    n = len(gold)
    arred = [min(maximo, max(minimo, round(p / passo) * passo)) for p in pred]
    return {
        "n": n,
        "qwk": qwk(gold, arred, minimo, maximo, passo),
        "mae": sum(abs(g - p) for g, p in zip(gold, pred)) / n,
        "exata": 100 * sum(g == p for g, p in zip(gold, arred)) / n,
        "adjacente": 100 * sum(abs(g - p) <= passo for g, p in zip(gold, arred)) / n,
        "vies": sum(p - g for g, p in zip(gold, pred)) / n,
        "r": pearson(gold, pred),
    }


def fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "  n/a"
    return f"{v:6.3f}" if abs(v) < 100 else f"{v:6.1f}"


def linha(nome, m):
    return (f"{nome:<22} {m['n']:>4}  {fmt(m['qwk'])}  {m['mae']:>7.1f}  {m['vies']:>+7.1f}  "
            f"{m['exata']:>6.1f}%  {m['adjacente']:>6.1f}%  {fmt(m['r'])}")


# Moda do split de teste inteiro (686 redacoes), medida uma vez: 600, com 91
# ocorrencias. Fica aqui como constante para que a baseline funcione sem o
# dataset clonado -- o workshop ja vem com a amostra pronta.
MODA_TESTE = 600


def moda_do_corpus(caminho="data/essay/essay-br/splits/testing.csv"):
    """Nota total mais frequente no split de teste completo (686 redacoes).

    Recalcula do CSV quando ele existe; senao usa a constante medida.
    """
    import csv as _csv
    p = Path(caminho)
    if not p.exists():
        return MODA_TESTE
    _csv.field_size_limit(10**7)
    with open(p, encoding="utf-8") as f:
        notas = [int(l["score"]) for l in _csv.DictReader(f)]
    return Counter(notas).most_common(1)[0][0] if notas else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cache", default="resultados.jsonl")
    p.add_argument("--csv", default=None, help="grava as metricas tambem em CSV")
    p.add_argument("--sample", default="sample.jsonl",
                   help="restringe o calculo aos idx desta amostra (evita misturar coortes)")
    p.add_argument("--todos", action="store_true",
                   help="usa todo o cache, mesmo registros de amostras anteriores")
    a = p.parse_args()

    caminho = Path(a.cache)
    if not caminho.exists():
        sys.exit(f"cache nao encontrado: {caminho}\nrode antes: python3 evaluate.py --limit 1 --verbose")

    regs = [json.loads(l) for l in caminho.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not regs:
        sys.exit("cache vazio")

    # O cache e cumulativo e sobrevive a troca de amostra. Sem este filtro, uma
    # nova rodada de rubrica misturaria coortes diferentes no mesmo QWK.
    amostra = Path(a.sample)
    if not a.todos and amostra.exists():
        alvo = {json.loads(l)["idx"] for l in amostra.read_text(encoding="utf-8").splitlines() if l.strip()}
        fora = [r for r in regs if r["idx"] not in alvo]
        regs = [r for r in regs if r["idx"] in alvo]
        if fora:
            print(f"[filtro] {len(fora)} registros do cache ignorados (fora de {amostra}); "
                  f"use --todos para inclui-los")
        faltando = len(alvo) - len(regs)
        if faltando > 0:
            print(f"[aviso] {faltando} redacoes da amostra ainda nao foram avaliadas")
        if not regs:
            sys.exit(f"nenhum registro do cache pertence a {amostra}")

    print(f"{len(regs)} redacoes avaliadas\n")
    cab = (f"{'':<22} {'n':>4}  {'QWK':>6}  {'MAE':>7}  {'vies':>7}  "
           f"{'exata':>7}  {'adj':>7}  {'r':>6}")
    linhas_csv = [["metrica", "n", "qwk", "mae", "vies", "exata", "adjacente", "r"]]

    for rotulo, chave in [("argmax (nota ENEM)", "nota_argmax"), ("valor esperado", "nota_esperada")]:
        print(f"--- {rotulo} ---")
        print(cab)
        for c in COMPS:
            gold = [r["gold_competencias"][COMPS.index(c)] for r in regs if r["jev"].get(c, {}).get(chave) is not None]
            pred = [r["jev"][c][chave] for r in regs if r["jev"].get(c, {}).get(chave) is not None]
            if not gold:
                print(f"{c:<22}  sem dados")
                continue
            m = metricas(gold, pred, 0, 200, 40)
            print(linha(c, m))
            linhas_csv.append([f"{chave}:{c}", m["n"], m["qwk"], m["mae"], m["vies"], m["exata"], m["adjacente"], m["r"]])

        gold_t = [r["gold_total"] for r in regs]
        pred_t = [sum(r["jev"][c][chave] for c in COMPS if r["jev"].get(c, {}).get(chave) is not None) for r in regs]
        mt = metricas(gold_t, pred_t, 0, 1000, 40)
        print(linha("TOTAL", mt))
        linhas_csv.append([f"{chave}:total", mt["n"], mt["qwk"], mt["mae"], mt["vies"], mt["exata"], mt["adjacente"], mt["r"]])
        print()

    # Baseline: prever sempre a nota mais frequente DO CORPUS (nao da amostra).
    # A amostra e estratificada de proposito, entao a moda dela nao representa
    # nada; a baseline honesta e a moda do split de teste inteiro.
    moda = moda_do_corpus() or Counter(r["gold_total"] for r in regs).most_common(1)[0][0]
    mb = metricas([r["gold_total"] for r in regs], [moda] * len(regs), 0, 1000, 40)
    print(f"--- baseline constante (sempre {moda}, moda do split de teste) ---")
    print(cab)
    print(linha("TOTAL baseline", mb))
    linhas_csv.append([f"baseline_{moda}:total", mb["n"], mb["qwk"], mb["mae"], mb["vies"], mb["exata"], mb["adjacente"], mb["r"]])
    print("\nO Jev so e util se superar essa baseline em MAE e QWK.")

    # Quanto do erro e vies sistematico (corrigivel) e quanto e ruido.
    print("\n--- efeito de remover o vies medio (calibracao simples) ---")
    print(f"{'':<8} {'QWK antes':>10} {'QWK depois':>11} {'MAE antes':>10} {'MAE depois':>11}")
    for i, c in enumerate(COMPS):
        gold = [r["gold_competencias"][i] for r in regs if r["jev"].get(c, {}).get("nota_esperada") is not None]
        pred = [r["jev"][c]["nota_esperada"] for r in regs if r["jev"].get(c, {}).get("nota_esperada") is not None]
        if not gold:
            continue
        vies = sum(p - g for g, p in zip(gold, pred)) / len(gold)
        antes = metricas(gold, pred, 0, 200, 40)
        depois = metricas(gold, [p - vies for p in pred], 0, 200, 40)
        print(f"{c:<8} {antes['qwk']:>10.3f} {depois['qwk']:>11.3f} "
              f"{antes['mae']:>10.1f} {depois['mae']:>11.1f}")
    vies_t = sum(p - g for g, p in zip(gold_t, pred_t)) / len(gold_t)
    at = metricas(gold_t, pred_t, 0, 1000, 40)
    dt = metricas(gold_t, [p - vies_t for p in pred_t], 0, 1000, 40)
    print(f"{'TOTAL':<8} {at['qwk']:>10.3f} {dt['qwk']:>11.3f} {at['mae']:>10.1f} {dt['mae']:>11.1f}")
    print("Ganho grande aqui = as ancoras da rubrica estao deslocadas; ajuste-as em rubric.json.")

    # Limiar de revisao humana: o que sobra automatizado vale a pena?
    rub = Path("rubric.json")
    limiar_cfg = json.loads(rub.read_text(encoding="utf-8")).get("limiar_confianca") if rub.exists() else None
    pares = []
    for r in regs:
        for i, c in enumerate(COMPS):
            v = r["jev"].get(c) or {}
            if v.get("nota_esperada") is not None and v.get("confianca") is not None:
                pares.append((v["confianca"], r["gold_competencias"][i], v["nota_esperada"]))
    if pares:
        print("\n--- limiar de confianca: qualidade do que fica automatizado ---")
        print(f"{'limiar':>7} {'automat.':>9} {'revisao':>8}  {'QWK auto':>9} {'MAE auto':>9}")
        for lim in (0.0, 0.50, 0.60, 0.65, 0.70, 0.80):
            # nao reusar o nome 'a' aqui: ele e o namespace do argparse e seria
            # sobrescrito, quebrando o --csv la embaixo.
            acima = [(g, p) for cf, g, p in pares if cf >= lim]
            if len(acima) < 5:
                continue
            m = metricas([g for g, _ in acima], [p for _, p in acima], 0, 200, 40)
            marca_cfg = "  <- rubric.json" if limiar_cfg is not None and abs(lim - limiar_cfg) < 1e-9 else ""
            print(f"{lim:>7.2f} {100*len(acima)/len(pares):>8.0f}% "
                  f"{100*(len(pares)-len(acima))/len(pares):>7.0f}%  "
                  f"{m['qwk']:>9.3f} {m['mae']:>9.1f}{marca_cfg}")
        print("Um limiar so compensa se o QWK automatizado superar o da linha 0.00.")

    confs = [v.get("confianca") for r in regs for v in r["jev"].values() if v.get("confianca") is not None]
    if confs:
        baixa = sum(1 for c in confs if c < 0.6)
        print(f"\nconfianca media: {sum(confs)/len(confs):.2f} | "
              f"{baixa}/{len(confs)} decisoes abaixo de 0.60 (candidatas a revisao humana)")

    if a.csv:
        import csv as _csv
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            _csv.writer(f).writerows(linhas_csv)
        print(f"\nmetricas gravadas em {a.csv}")


if __name__ == "__main__":
    main()
