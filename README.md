# Simulador IDEB — NGR-EDU · Seplag

Simula o IDEB da escola por etapa, a partir das taxas de aprovação do Censo
Escolar e das proficiências do SAEB. Porta a aba "Simulador Ideb" da planilha
do Núcleo da Seplag para o mesmo front-end do Simulador BDE.

Página estática: não tem backend. Esta pasta é autossuficiente — o **conteúdo**
dela (não a pasta) vai para a raiz do repositório, e o GitHub Pages serve o
`index.html` da raiz.

## A regra

IDEB = N × P, por etapa (não existe IDEB único da escola).

- **P (rendimento, de 0 a 1):** média harmônica das taxas de aprovação dos
  anos da etapa, como na planilha: `P = HARMEAN(taxas) / 100`. Ano que a
  escola não tem fica em branco e fora da conta (null, undefined ou texto
  vazio não entram no divisor). Taxa zero também fica fora, como o Inep
  calcula: não existe média harmônica com zero. A etapa precisa de ao menos
  uma taxa acima de zero. Ex.: 100, 90 e 80 dão P = 0,89, com ou sem um
  quarto ano em branco ou com 0.
- **Fluxo:** o inverso do rendimento, 1 ÷ P.
- **N (nota SAEB da etapa, de 0 a 10):** média das notas de LP e MT no SAEB, cada uma
  padronizada por (proficiência − Sinf) ÷ (Ssup − Sinf) × 10, com os limites
  do SAEB 1997 (Inep):

  | Etapa | LP Sinf–Ssup | MT Sinf–Ssup |
  | --- | --- | --- |
  | Anos Iniciais (1º ao 5º ano) | 49–324 | 60–322 |
  | Anos Finais (6º ao 9º ano) | 100–400 | 100–400 |
  | Ensino Médio (1ª à 4ª série) | 117–451 | 111–467 |

- **IDEB de 0 a 10, com uma casa decimal.**

Os limites são condição de entrada, no `motor.js` e na tela: taxa fora de 0 a
100 ou proficiência fora dos limites da etapa não são calculadas. Assim P
nunca passa de 1, nenhuma nota passa de 10 e o IDEB fica entre 0 e 10.

Diferenças de propósito para a planilha:

- **Taxa de aprovação zero.** O `HARMEAN` dá erro e a planilha deixa P,
  Fluxo e IDEB em branco. O simulador deixa o zero fora da média, como o ano
  em branco. A tela avisa disso ao lado das aprovações.
- **N × P = 0.** A planilha deixa a célula em branco; o simulador mostra 0,0.

## Arquivos

- `motor.js` — o cálculo, sem DOM
- `wizard.js` — navegação e telas
- `estilo.css` — cópia do estilo do Simulador BDE + o que só o IDEB usa
- `img/logo-ngr.png`
- `tests/test_ideb.py` — confere o motor contra valores calculados pela
  própria planilha (`python3 tests/test_ideb.py`, precisa do Node)

Para ver localmente: `python3 -m http.server` nesta pasta e abra
http://127.0.0.1:8000.
