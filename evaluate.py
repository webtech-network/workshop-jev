#!/usr/bin/env python3
"""Avalia redacoes do Essay-BR com o modelo typesafe-ai/jev via Vercel AI Gateway.

Uma requisicao por redacao, carregando as 5 competencias como perguntas do tipo
'score' avaliadas em paralelo contra o mesmo estado (o texto da redacao).

Primeira execucao recomendada (barata e diagnostica):
    python3 evaluate.py --dry-run                 # nenhuma chamada: so mostra o request
    python3 evaluate.py --limit 1 --verbose       # 1 redacao, resposta crua em debug/

Depois:
    python3 evaluate.py --limit 5 --cache resultados-meus.jsonl

No workshop a chave e compartilhada pela turma: use --limit baixo. O provedor
devolve 429 sob carga, e o cache torna qualquer execucao retomavel.

As respostas cruas sao gravadas em cache (JSONL). O compare.py le o cache,
nunca a API, para que iterar na rubrica nao custe chamadas repetidas.
"""
import argparse, json, os, sys, time, urllib.error, urllib.request
from pathlib import Path

RAIZ = Path(__file__).parent
# Endpoint de avaliacao do gateway. NAO e /v1/chat/completions: aquele recusa
# o Jev com "is an evaluation model, not a language model".
ENDPOINT = "https://ai-gateway.vercel.sh/v1/evaluate"
MODELO = "typesafe-ai/jev"


def carregar_chave():
    """Le a chave, dando precedencia ao .env.local sobre o ambiente.

    O arquivo do projeto e a fonte da verdade: uma variavel exportada antes
    (por ex. com `set -a && . ./.env.local`) fica velha na sessao do shell e
    silenciosamente venceria uma chave recem-editada. Quando as duas divergem,
    avisa em vez de escolher calado.
    """
    do_ambiente = os.environ.get("AI_GATEWAY_API_KEY")
    do_arquivo = None
    env = RAIZ / ".env.local"
    if env.exists():
        # utf-8-sig descarta o BOM que o Notepad do Windows acrescenta em
        # "UTF-8 with BOM"; sem isso o startswith abaixo falha calado. E o
        # `echo > arquivo` do PowerShell grava UTF-16, que estoura em utf-8.
        texto = None
        for codificacao in ("utf-8-sig", "utf-16"):
            try:
                texto = env.read_text(encoding=codificacao)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        if texto is None:
            sys.exit(f"nao consegui ler {env}: codificacao desconhecida.\n"
                     "Recrie o arquivo em UTF-8 (no Windows, use o Git Bash).")
        for linha in texto.splitlines():
            linha = linha.strip().lstrip("\ufeff")
            if "=" not in linha or linha.startswith("#"):
                continue
            # tolerante de proposito: numa sala de aula, "CHAVE = 'x'" com
            # espacos e aspas e o erro mais comum, e travar nele custa 10 min.
            nome, valor = linha.split("=", 1)
            if nome.strip() == "AI_GATEWAY_API_KEY":
                do_arquivo = valor.strip().strip('"\'') or None

    chave, fonte = (do_arquivo, ".env.local") if do_arquivo else (do_ambiente, "ambiente")
    if not chave:
        sys.exit("AI_GATEWAY_API_KEY ausente.\n"
                 "Crie o arquivo .env.local na raiz do projeto com uma linha:\n"
                 "    AI_GATEWAY_API_KEY=a-chave-que-o-instrutor-passou\n"
                 "Passo a passo em SETUP.md (secao 'A chave da API').")

    if do_arquivo and do_ambiente and do_arquivo != do_ambiente:
        print(f"[aviso] a variavel de ambiente (...{do_ambiente[-6:]}) difere do "
              f".env.local (...{do_arquivo[-6:]}); usando o arquivo.")
        print("        para limpar a do shell: unset AI_GATEWAY_API_KEY")

    print(f"chave em uso: ...{chave[-6:]} (fonte: {fonte})")
    return chave


def montar_perguntas(rubrica):
    return {
        cid: {
            "type": "score",
            "instructions": c["instructions"],
            "criteria": c["criteria"],
        }
        for cid, c in rubrica["competencias"].items()
    }


def montar_corpo(texto, titulo, perguntas):
    """Monta o corpo para POST /v1/evaluate.

    Confirmado empiricamente: o endpoint recebe {model, state, questions} e o
    texto avaliado vai em 'state' (string). Nao usa 'messages'.
    Tipos aceitos em questions[*].type: 'boolean' | 'choice' | 'score'
    (o gateway chama 'boolean' o que a doc nativa da TypeSafe chama 'noul').
    """
    return {
        "model": MODELO,
        "state": f"Titulo: {titulo}\n\n{texto}",
        "questions": perguntas,
    }


def chamar(corpo, chave, timeout=120, tentativas=5):
    """POST no endpoint de avaliacao, com backoff em 429 e 5xx.

    O provedor upstream devolve 429 sob carga; sem backoff uma varredura de 100
    redacoes perde a maior parte das chamadas.
    """
    dados = json.dumps(corpo).encode("utf-8")
    espera = 2.0
    for tentativa in range(1, tentativas + 1):
        req = urllib.request.Request(
            ENDPOINT, data=dados,
            headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            bruto = e.read().decode("utf-8", "replace")
            try:
                resposta = json.loads(bruto)
            except json.JSONDecodeError:
                resposta = {"erro_bruto": bruto}
            if e.code in (429, 500, 502, 503, 504) and tentativa < tentativas:
                print(f"    [{e.code}] tentativa {tentativa}/{tentativas}, aguardando {espera:.0f}s")
                time.sleep(espera)
                espera *= 2
                continue
            return e.code, resposta
        except (urllib.error.URLError, TimeoutError) as e:
            if tentativa < tentativas:
                print(f"    [rede] {e}, aguardando {espera:.0f}s")
                time.sleep(espera)
                espera *= 2
                continue
            return 0, {"erro_bruto": str(e)}


def extrair_notas(resposta, escala):
    """Converte a resposta do Jev em notas ENEM.

    ATENCAO ao campo 'score': ele NAO e o indice escolhido, e o valor esperado
    ja ponderado pelas probabilidades (ex.: score 0.51 com p={0:0.50, 1:0.49,
    2:0.01}, pois 0x0.50 + 1x0.49 + 2x0.01 = 0.51). Por isso guardamos:
      - nota_esperada: score x escala (sinal continuo, melhor correlacao)
      - nota_argmax:   indice de maior probabilidade x escala (nota ENEM discreta)
    """
    respostas = resposta.get("answers") or {}
    out = {}
    for cid, a in respostas.items():
        score = a.get("score")
        probs = a.get("probabilities") or {}

        idx_argmax = None
        if probs:
            try:
                idx_argmax = int(max(probs, key=lambda k: float(probs[k])))
            except (ValueError, TypeError):
                idx_argmax = None
        if idx_argmax is None and score is not None:
            idx_argmax = round(float(score))  # sem probabilidades, arredonda o score

        out[cid] = {
            "indice_argmax": idx_argmax,
            "nota_argmax": None if idx_argmax is None else round(idx_argmax * escala),
            "score_bruto": score,
            "nota_esperada": None if score is None else round(float(score) * escala, 1),
            "confianca": a.get("confidence"),
            "probabilities": probs,
        }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sample", default="sample.jsonl")
    p.add_argument("--rubric", default="rubric.json")
    p.add_argument("--cache", default="resultados.jsonl")
    p.add_argument("--limit", type=int, default=None, help="avalia no maximo N redacoes")
    p.add_argument("--verbose", action="store_true", help="grava request/response crus em debug/")
    p.add_argument("--dry-run", action="store_true", help="monta o request e mostra, sem chamar a API")
    p.add_argument("--force", action="store_true", help="reavalia mesmo o que ja esta em cache")
    a = p.parse_args()

    rubrica = json.loads(Path(a.rubric).read_text(encoding="utf-8"))
    escala = rubrica["escala"]
    perguntas = montar_perguntas(rubrica)

    redacoes = [json.loads(l) for l in Path(a.sample).read_text(encoding="utf-8").splitlines() if l.strip()]
    if a.limit:
        redacoes = redacoes[: a.limit]

    feitos = set()
    cache = Path(a.cache)
    if cache.exists() and not a.force:
        for l in cache.read_text(encoding="utf-8").splitlines():
            if l.strip():
                feitos.add(json.loads(l)["idx"])

    if a.dry_run:
        r = redacoes[0]
        corpo = montar_corpo(r["texto"], r["titulo"], perguntas)
        print(json.dumps(corpo, ensure_ascii=False, indent=2)[:2500])
        print(f"\n[dry-run] {len(redacoes)} redacoes seriam avaliadas; nenhuma chamada feita.")
        return

    chave = carregar_chave()
    debug = RAIZ / "debug"
    if a.verbose:
        debug.mkdir(exist_ok=True)

    ok = falhas = 0
    with cache.open("a", encoding="utf-8") as f:
        for r in redacoes:
            if r["idx"] in feitos:
                print(f"[pulado] idx={r['idx']} ja em cache")
                continue

            corpo = montar_corpo(r["texto"], r["titulo"], perguntas)
            t0 = time.time()
            status, resposta = chamar(corpo, chave)
            dt = time.time() - t0

            if a.verbose:
                (debug / f"{r['idx']}_request.json").write_text(
                    json.dumps(corpo, ensure_ascii=False, indent=2), encoding="utf-8")
                (debug / f"{r['idx']}_response.json").write_text(
                    json.dumps(resposta, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"[verbose] cruas gravadas em {debug}/{r['idx']}_*.json")

            if status != 200:
                falhas += 1
                msg = (resposta.get("error") or {}).get("message") or str(resposta)[:200]
                print(f"[ERRO {status}] idx={r['idx']}: {msg}")
                if falhas == 1 and status in (401, 403):
                    print("  -> bloqueio de conta/credencial: interrompendo para nao repetir.")
                    break
                continue

            notas = extrair_notas(resposta, escala)
            if not notas:
                # 200 com formato inesperado e pior que um erro: geraria cache
                # vazio e metricas silenciosamente erradas. Para aqui.
                falhas += 1
                print(f"[FORMATO INESPERADO] idx={r['idx']}: status 200, mas nenhuma "
                      f"competencia foi extraida.")
                print(f"  chaves no topo da resposta: {sorted(resposta.keys())}")
                print(f"  esperado 'answers' (contrato nativo do Jev); o gateway pode "
                      f"estar devolvendo formato OpenAI ('choices').")
                if a.verbose:
                    print(f"  inspecione: debug/{r['idx']}_response.json")
                else:
                    print(f"  rode de novo com --verbose para gravar a resposta crua.")
                print("  -> interrompendo para nao gastar chamadas com parse quebrado.")
                break

            registro = {
                "idx": r["idx"],
                "titulo": r["titulo"],
                "gold_competencias": r["gold_competencias"],
                "gold_total": r["gold_total"],
                "jev": notas,
                "modelo": resposta.get("model"),
                "usage": resposta.get("usage"),
                "segundos": round(dt, 2),
            }
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
            f.flush()
            ok += 1
            time.sleep(1.0)
            prev = sum(v["nota_argmax"] or 0 for v in notas.values())
            print(f"[ok] idx={r['idx']} gold={r['gold_total']} jev={prev} ({dt:.1f}s)")

    print(f"\n{ok} avaliadas, {falhas} falhas -> {cache}")
    if ok:
        print("proximo passo: python3 compare.py")


if __name__ == "__main__":
    main()
