# De onde vêm as redações

## Essay-BR

As redações deste workshop vêm do corpus **Essay-BR**: 4.570 redações
escritas por estudantes brasileiros do ensino médio, **corrigidas por
profissionais** segundo os critérios do ENEM.

- Repositório: [rafaelanchieta/essay](https://github.com/rafaelanchieta/essay)
- Licença: **MIT** (cópia em [`LICENSE-essay-br`](LICENSE-essay-br))
- Versão estendida do corpus: [lplnufpi/essay-br](https://github.com/lplnufpi/essay-br)

### Os splits

| Split | Redações | Uso aqui |
|---|---|---|
| training | 3.198 | não usado |
| development | 686 | onde o laboratório original selecionou a rubrica v3 |
| **testing** | **686** | de onde sai a amostra do workshop |

### Formato original

Cada linha do CSV traz `prompt, title, essay, competence, score`:

- `competence` — lista com as 5 notas, de 0 a 200 cada, em faixas de 40;
- `score` — o total, de 0 a 1000.

### A checagem que foi feita

**Nunca confie num dataset sem verificar.** No split de teste (as 686 linhas),
foi confirmado que `sum(competence) == score` em todas elas — nenhuma linha
descartada. O `sample.py` refaz essa checagem a cada execução e reporta
descartes se você apontar o `--csv` para outro split.

---

## O que está neste repositório

### `sample.jsonl` — 100 redações

Amostra **estratificada pela nota total**, extraída do split de teste. A
estratificação é o detalhe que importa: a distribuição do corpus é concentrada
(a nota 600 aparece 91 vezes em 686), então uma amostra aleatória empilharia
tudo em volta de 600 e não diria nada sobre os extremos. Esta cobre de **0 a
1000**.

Gerada com:

```bash
python3 sample.py --n 100 --out sample.jsonl --seed 42
```

### `sample-mini.jsonl` — 10 redações

Subconjunto de `sample.jsonl`, 10 redações espalhadas pela faixa inteira:
notas `0, 280, 400, 480, 560, 640, 720, 840, 920, 1000`.

Serve para as rodadas dos alunos na etapa 6. Como todas as 10 estão dentro do
cache de referência, o "antes" e o "depois" são medidos **nas mesmas
redações**.

### `resultados-referencia-v1.jsonl` — o cache pago

As 100 redações de `sample.jsonl`, avaliadas pelo Jev com a `rubric.json` de
partida (v1, âncoras descritivas), no laboratório original.

Cada linha guarda a resposta **crua** — inclusive a distribuição de
probabilidades inteira — e não só a nota final. É isso que permite responder
perguntas novas sobre os dados sem gastar uma chamada: o princípio "grave o
dado cru, derive as leituras depois", da etapa 4.

Custo real da rodada: ~1.850 tokens de entrada por redação, US$ 0,000078 cada.
**As 100 custaram menos de um centavo de dólar.**

---

## Citação

Se você usar este corpus em qualquer trabalho, cite:

```bibtex
@inproceedings{marinho-et-al-21,
  author = {Jeziel Marinho and Rafael Anchiêta and Raimundo Moura},
  title = {Essay-BR: a Brazilian Corpus of Essays},
  booktitle = {Anais do III Dataset Showcase Workshop},
  year = {2021},
  pages = {53--64},
  publisher = {Sociedade Brasileira de Computação},
  address = {Online},
  doi = {10.5753/dsw.2021.17414},
  url = {https://sol.sbc.org.br/index.php/dsw/article/view/17414}
}
```

---

## Uma nota sobre as pessoas por trás dos textos

São redações de estudantes reais. O corpus não traz identificação — nem nome,
nem escola, nem ano — e **não tente reconstruir nenhuma dessas informações**.

O que você vai ver em algumas delas: textos de quem recebeu zero, com erros
que denunciam dificuldade real de escolarização. É material de estudo, não de
chacota. Trate como você gostaria que o seu texto de 17 anos fosse tratado.
