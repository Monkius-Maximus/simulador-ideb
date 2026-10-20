# Simulador IDEB — NGR-EDU · Seplag

Simula o IDEB da escola por etapa, a partir das taxas de aprovação do Censo
Escolar e das proficiências do SAEB. Porta a aba "Simulador Ideb" da planilha
do Núcleo da Seplag para o mesmo front-end do Simulador BDE.

Página estática: não tem backend. Esta pasta é autossuficiente — o **conteúdo**
dela (não a pasta) vai para a raiz do repositório, e o GitHub Pages serve o
`index.html` da raiz.

## A regra

IDEB = N × P, por etapa (não existe IDEB único da escola).

- **P (rendimento, de 0 a 1):** média harmônica das taxas de aprovação dos anos da etapa.
  Ano que a escola não tem fica em branco e fora da média. Taxa zero (ninguém
  aprovado) entra na média e leva P, e o IDEB da etapa, a zero.
- **N (aprendizado, de 0 a 10):** média das notas de LP e MT no SAEB, cada uma
  padronizada por (proficiência − Sinf) ÷ (Ssup − Sinf) × 10, com os limites
  definidos pelo NGR:

  | Etapa | LP Sinf–Ssup | MT Sinf–Ssup |
  | --- | --- | --- |
  | Anos Iniciais (1º ao 5º ano) | 49–324 | 60–322 |
  | Anos Finais (6º ao 9º ano) | 49–324 | 60–322 |
  | Ensino Médio (1ª à 4ª série) | 117–451 | 111–467 |

- **IDEB de 0 a 10, com uma casa decimal.**

Os limites são condição de entrada, no `motor.js` e na tela: taxa fora de 0 a
100 ou proficiência fora dos limites da etapa não são calculadas. Assim P
nunca passa de 1, nenhuma nota passa de 10 e o IDEB fica entre 0 e 10.

Diferenças de propósito para a planilha:

- **Limites dos Anos Finais.** O Inep (SAEB 1997) e a planilha (C26, D26 e a
  validação A26:B26) usam 100–400 nas duas disciplinas. Por decisão do NGR, o
  simulador usa nos Anos Finais os mesmos limites dos Anos Iniciais. Com isso
  a nota padronizada dos Anos Finais sai maior que a do Inep para a mesma
  proficiência (LP 250 dá 7,31 em vez de 5,00).
- **Taxa de aprovação zero.** A planilha soma `IFERROR(1/taxa; 0)` e divide
  pelo `COUNT` dos anos preenchidos: o zero não soma nada mas conta no
  divisor, e com isso *aumenta* P (pode passar de 1 e levar o IDEB acima
  de 10). O simulador segue o Inep: o zero entra na média harmônica e leva P
  a zero. A tela avisa disso ao lado das aprovações.
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
