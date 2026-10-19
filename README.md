# Simulador IDEB — NGR-EDU · Seplag

Simula o IDEB da escola por etapa, a partir das taxas de aprovação do Censo
Escolar e das proficiências do SAEB. Porta a aba "Simulador Ideb" da planilha
do Núcleo da Seplag para o mesmo front-end do Simulador BDE.

Página estática: não tem backend. Esta pasta é autossuficiente — o **conteúdo**
dela (não a pasta) vai para a raiz do repositório, e o GitHub Pages serve o
`index.html` da raiz.

## A regra

IDEB = N × P, por etapa (não existe IDEB único da escola).

- **P (fluxo):** média simples das taxas de aprovação dos anos da etapa, de
  0 a 1. Ano que a escola não tem fica em branco e fora da média. Taxa zero
  (ninguém aprovado) entra na média e reduz P: 0, 0, 0 e 100 dão P = 0,25.
- **N (aprendizado):** média das notas de LP e MT no SAEB, cada uma
  padronizada por (proficiência − Sinf) ÷ (Ssup − Sinf) × 10, com os limites
  do SAEB 1997 (Inep):

  | Etapa | LP Sinf–Ssup | MT Sinf–Ssup |
  | --- | --- | --- |
  | Anos Iniciais (1º ao 5º ano) | 49–324 | 60–322 |
  | Anos Finais (6º ao 9º ano) | 100–400 | 100–400 |
  | Ensino Médio (1ª à 4ª série) | 117–451 | 111–467 |

- **Resultado com uma casa decimal.**

Diferenças de propósito:

- **Fluxo pela média simples.** O Inep usa a média harmônica das aprovações,
  em que um único ano com aprovação zero leva P, e o IDEB, a zero. A planilha
  de referência soma `IFERROR(1/taxa; 0)` e divide pelo `COUNT`, o que faz o
  zero *aumentar* P. O simulador usa a média simples, por decisão do NGR: o
  zero pesa, mas não zera a etapa. Com aprovações sem zero e parecidas entre
  si, as duas médias ficam próximas; com aprovações muito diferentes, a média
  simples dá um P maior que a do Inep.
- **N × P = 0.** A planilha deixa a célula em branco; o simulador mostra 0,0.

## Arquivos

- `motor.js` — o cálculo, sem DOM
- `wizard.js` — navegação e telas
- `estilo.css` — cópia do estilo do Simulador BDE + o que só o IDEB usa
- `img/logo-ngr.png`
- `tests/test_ideb.py` — confere N contra a própria planilha e P e o IDEB
  contra a média simples (`python3 tests/test_ideb.py`, precisa do Node)

Para ver localmente: `python3 -m http.server` nesta pasta e abra
http://127.0.0.1:8000.
