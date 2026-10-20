"""
Motor do simulador do IDEB (ideb/motor.js) contra a aba "Simulador Ideb" da
planilha do Nucleo da Seplag (1_Simulador_Idepe_Ideb_e_Atingimento_de_metas).

Os valores esperados sao os que a propria planilha calculou: os casos foram
digitados nas celulas amarelas e a planilha recalculada no LibreOffice. P e N
batem ate a 9a casa; o IDEB, com uma casa, como a celula C14 exibe.

Diferencas de proposito:
- taxa de aprovacao zero: a planilha soma IFERROR(1/taxa; 0) e divide pelo
  COUNT, entao o zero aumenta P. O motor segue o Inep: o zero entra na media
  harmonica e leva P, e o IDEB, a zero;
- com N x P = 0 a planilha deixa o IDEB em branco (o AND da C14 trata zero
  como falso). O motor devolve 0,0.
- limites dos Anos Finais: a planilha usa 100-400 nas duas disciplinas; o
  motor usa os dos Anos Iniciais (LP 49-324, MT 60-322), por decisao do NGR.
  Nos casos AF, P vem da planilha e N e o IDEB sao calculados a parte.

    python3 tests/test_ideb.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MOTOR = Path(__file__).resolve().parent.parent / "motor.js"

# (descricao, etapa, aprovacoes preenchidas, LP, MT, P, N, IDEB da planilha)
CASOS = [
    ("AI cinco anos", "ai", [95, 92.5, 88, 90, 97.3], 210.5, 225.3,
     0.924396112552462, 6.09094378903539, 5.63044476035988),
    # AF: P da planilha; N com os limites dos AI (decisao do NGR, a planilha
    # usa 100-400), calculado a parte em Decimal.
    ("AF sem o 7o ano", "af", [85, 80.2, 91], 255, 250,
     0.85172721531153, 7.37140874392783, 6.27842944238871),
    ("EM com 4a serie", "em", [78, 82.5, 90, 100], 280, 275.6,
     0.868567572127552, 4.75191751328803, 4.12736145746698),
    ("AI no teto", "ai", [100, 100, 100, 100, 100], 324, 322,
     1.0, 10.0, 10.0),
    ("AF no piso: planilha em branco, motor 0", "af", [70], 49, 60,
     0.7, 0.0, 0.0),
    ("EM LP no teto, MT no piso", "em", [60.55], 451, 111,
     0.6055, 5.0, 3.0275),
    ("AI so o 5o ano", "ai", [99.9], 180.25, 200.75,
     0.999, 5.07243233865371, 5.06735990631506),
    ("AF quatro anos quebrados", "af", [65, 72.33, 88.88, 93.1], 240.4, 233.9,
     0.781213365803825, 6.79870229007634, 5.31123709912871),
    ("EM tres series", "em", [85, 88, 92], 270, 268,
     0.882407249102411, 4.49547534145193, 3.96684002945832),
    # Anos Finais das capturas da planilha (Rendimento F22, IDEB C29).
    ("AF tudo 100 no teto", "af", [100, 100, 100, 100], 324, 322,
     1.0, 10.0, 10.0),
    ("AF 100/80/80/80 no teto", "af", [100, 80, 80, 80], 324, 322,
     0.842105263157895, 10.0, 8.42105263157895),
    ("AF 100/90/40/30 no teto", "af", [100, 90, 40, 30], 324, 322,
     0.503496503496503, 10.0, 5.03496503496503),
]


def arredondar_excel(valor: float, casas: int) -> float:
    """Como a celula 0.0 exibe: empate para longe do zero."""
    from decimal import ROUND_HALF_UP, Decimal

    return float(Decimal(repr(valor)).quantize(Decimal(10) ** -casas, ROUND_HALF_UP))


def respostas_js() -> list[dict]:
    entrada = [
        {"chave": etapa, "dados": {"aprovacoes": ap, "lp": lp, "mt": mt}}
        for _, etapa, ap, lp, mt, *_ in CASOS
    ]
    runner = f"""
{MOTOR.read_text("utf-8")}
const casos = {json.dumps(entrada)};
process.stdout.write(JSON.stringify(casos.map((c) => calcularIdeb(c.chave, c.dados))));
"""
    processo = subprocess.run(["node", "-e", runner], capture_output=True, text=True)
    if processo.returncode != 0:
        raise RuntimeError(f"Motor JS falhou:\n{processo.stderr}")
    return json.loads(processo.stdout)


def conferir_limites() -> list[str]:
    """Dentro dos limites, P fica em 0..1, notas e N em 0..10 e o IDEB em
    0..10, nas tres etapas. Fora deles, o motor recusa."""
    runner = f"""
{MOTOR.read_text("utf-8")}
const falhas = [];
const dentro = (v, lo, hi) => v >= lo && v <= hi;
const passos = [0, 0.01, 1, 30, 50, 70.5, 99.99, 100];
for (const chave of ['ai', 'af', 'em']) {{
  const l = LIMITES_SAEB[chave];
  const profs = (lim) => [lim.inf, lim.inf + 0.0001, (lim.inf + lim.sup) / 2, lim.sup - 0.0001, lim.sup];
  for (const a of passos) for (const b of passos) for (const lp of profs(l.lp)) for (const mt of profs(l.mt)) {{
    const r = calcularIdeb(chave, {{aprovacoes: [a, b, 100], lp, mt}});
    if (!dentro(r.rendimento, 0, 1) || !dentro(r.nota_lp, 0, 10) || !dentro(r.nota_mt, 0, 10)
        || !dentro(r.nota_saeb, 0, 10) || !dentro(r.ideb, 0, 10)) {{
      falhas.push(`${{chave}} ${{a}}/${{b}}/100 LP ${{lp}} MT ${{mt}}: ${{JSON.stringify(r)}}`);
    }}
  }}
  const fora = [
    {{aprovacoes: [101], lp: l.lp.inf, mt: l.mt.inf}},
    {{aprovacoes: [-1], lp: l.lp.inf, mt: l.mt.inf}},
    {{aprovacoes: [90], lp: l.lp.inf - 1, mt: l.mt.inf}},
    {{aprovacoes: [90], lp: l.lp.inf, mt: l.mt.sup + 1}},
  ];
  for (const d of fora) {{
    try {{ calcularIdeb(chave, d); falhas.push(`${{chave}} aceitou fora do limite: ${{JSON.stringify(d)}}`); }} catch (e) {{}}
  }}
}}
process.stdout.write(JSON.stringify(falhas.slice(0, 5)));
"""
    processo = subprocess.run(["node", "-e", runner], capture_output=True, text=True)
    if processo.returncode != 0:
        return [f"limites: motor JS falhou: {processo.stderr}"]
    return [f"limites: {f}" for f in json.loads(processo.stdout)]


def main() -> int:
    falhas = []
    for caso, r in zip(CASOS, respostas_js()):
        nome, *_, p, n, ideb = caso
        if abs(r["rendimento"] - p) > 1e-9:
            falhas.append(f"{nome}: P {r['rendimento']} != planilha {p}")
        if abs(r["nota_saeb"] - n) > 1e-9:
            falhas.append(f"{nome}: N {r['nota_saeb']} != planilha {n}")
        if r["ideb"] != arredondar_excel(ideb, 1):
            falhas.append(f"{nome}: IDEB {r['ideb']} != planilha {arredondar_excel(ideb, 1)}")

    # Taxa zero: P vai a zero (1/0 = infinito), nao a erro. Caso do EM com a
    # 4a serie zerada, em que a planilha da 4,6 (P 0,97) e o Inep da 0.
    zero = subprocess.run(
        ["node", "-e", f"{MOTOR.read_text('utf-8')}\nconst r = calcularIdeb('em', {{aprovacoes: [100, 90, 50, 0], lp: 423, mt: 123}});"
         "\nprocess.stdout.write(`${r.rendimento} ${r.ideb}`);"],
        capture_output=True, text=True,
    )
    if zero.stdout != "0 0":
        falhas.append(f"taxa zero: P e IDEB deviam ser 0, veio {zero.stdout or zero.stderr}")

    falhas += conferir_limites()

    for f in falhas:
        print("FALHA", f)
    print(f"{len(CASOS) + 2 - len(falhas)}/{len(CASOS) + 2} casos ok")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
