"""
Motor do simulador do IDEB (motor.js).

N e conferido contra a aba "Simulador Ideb" da planilha do Nucleo da Seplag
(1_Simulador_Idepe_Ideb_e_Atingimento_de_metas): os casos foram digitados nas
celulas amarelas e a planilha recalculada no LibreOffice; bate ate a 9a casa.

P e a media simples das aprovacoes preenchidas, de 0 a 1 (decisao do NGR; a
planilha e o Inep usam outra regra, ver README). O esperado e calculado aqui,
em Decimal, sem passar pelo motor. O IDEB = N x P, com uma casa.

    python3 tests/test_ideb.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

MOTOR = Path(__file__).resolve().parent.parent / "motor.js"

# (descricao, etapa, aprovacoes preenchidas, LP, MT, N da planilha)
CASOS = [
    ("AI cinco anos", "ai", [95, 92.5, 88, 90, 97.3], 210.5, 225.3, 6.09094378903539),
    ("AF sem o 7o ano", "af", [85, 80.2, 91], 255, 250, 5.08333333333333),
    ("EM com 4a serie", "em", [78, 82.5, 90, 100], 280, 275.6, 4.75191751328803),
    ("AI no teto", "ai", [100, 100, 100, 100, 100], 324, 322, 10.0),
    ("AF no piso", "af", [70], 100, 100, 0.0),
    ("EM LP no teto, MT no piso", "em", [60.55], 451, 111, 5.0),
    ("AI so o 5o ano", "ai", [99.9], 180.25, 200.75, 5.07243233865371),
    ("AF quatro anos quebrados", "af", [65, 72.33, 88.88, 93.1], 240.4, 233.9, 4.57166666666667),
    ("EM tres series", "em", [85, 88, 92], 270, 268, 4.49547534145193),
    # Taxa zero: entra na media e reduz P, sem zerar a etapa.
    ("EM 0/0/0/100 no teto", "em", [0, 0, 0, 100], 451, 467, 10.0),
    ("EM 100/90/50/0", "em", [100, 90, 50, 0], 423, 123, 4.74937764919599),
    ("EM 100/80/50/0", "em", [100, 80, 50, 0], 213, 442, 6.08600215299738),
    ("AF so zeros", "af", [0, 0], 260, 255, 5.25),
]


def arredondar_excel(valor: float, casas: int) -> float:
    """Como a celula 0.0 exibe: empate para longe do zero."""
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


def main() -> int:
    falhas = []
    for caso, r in zip(CASOS, respostas_js()):
        nome, _, aprovacoes, _, _, n = caso
        p = sum(Decimal(repr(t)) for t in aprovacoes) / len(aprovacoes) / 100
        ideb = arredondar_excel(float(Decimal(repr(n)) * p), 1)
        if abs(r["rendimento"] - float(p)) > 1e-9:
            falhas.append(f"{nome}: P {r['rendimento']} != {p}")
        if abs(r["nota_saeb"] - n) > 1e-9:
            falhas.append(f"{nome}: N {r['nota_saeb']} != planilha {n}")
        if r["ideb"] != ideb:
            falhas.append(f"{nome}: IDEB {r['ideb']} != {ideb}")

    for f in falhas:
        print("FALHA", f)
    print(f"{len(CASOS) - len(falhas)}/{len(CASOS)} casos ok")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
