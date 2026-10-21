/* ============================================================================
   Motor IDEB — porte da aba "Simulador Ideb" da planilha do Núcleo da Seplag.

   IDEB = N x P, calculado por etapa. Nao existe IDEB unico da escola.

     P   rendimento, de 0 a 1: media harmonica das taxas de aprovacao dos
         anos da etapa, como o HARMEAN(...)/100 da planilha. Ano em branco
         (a escola nao tem a serie) e ano com taxa zero ficam fora da media,
         como faz o Inep: nao existe media harmonica com zero.
     Fluxo  inverso do rendimento, 1 / P.
     N   nota SAEB da etapa, de 0 a 10: media das notas padronizadas de LP e MT no
         SAEB, nota = (proficiencia - limite inferior) / (superior - inferior)
         x 10, com os limites do SAEB 1997 (Inep), diferentes por etapa.
     IDEB  N x P, de 0 a 10, divulgado com uma casa decimal.

   Os limites sao condicao de entrada: taxa fora de 0 a 100 ou proficiencia
   fora dos limites da etapa param o calculo com erro. Assim P nunca passa de
   1, nenhuma nota passa de 10 e o IDEB fica sempre entre 0 e 10.

   Diferencas para a planilha, de proposito: com taxa zero o HARMEAN da erro
   e P, Fluxo e IDEB ficam em branco; aqui o zero fica fora da media, como o
   ano em branco. Com N x P = 0 a C14 fica em branco, porque o AND(...; E11*G7)
   trata zero como falso; aqui o IDEB e 0,0.
   ============================================================================ */

var LIMITES_SAEB = {
    ai: { lp: { inf: 49, sup: 324 }, mt: { inf: 60, sup: 322 } },
    af: { lp: { inf: 100, sup: 400 }, mt: { inf: 100, sup: 400 } },
    em: { lp: { inf: 117, sup: 451 }, mt: { inf: 111, sup: 467 } },
};

var ANOS_DA_ETAPA = {
    ai: ['1º ano', '2º ano', '3º ano', '4º ano', '5º ano'],
    af: ['6º ano', '7º ano', '8º ano', '9º ano'],
    em: ['1ª série', '2ª série', '3ª série', '4ª série'],
};

/**
 * Arredonda como a celula do Excel exibe: empate vai para longe do zero. O
 * toPrecision(12) descarta o residuo binario do produto (4,45 que chega como
 * 4,4499999...).
 */
function arredondar(valor, casas) {
    var fator = Math.pow(10, casas);
    var escalado = Number((Math.abs(valor) * fator).toPrecision(12));
    return (valor < 0 ? -1 : 1) * Math.round(escalado) / fator;
}

/**
 * P, de 0 a 1: HARMEAN(taxas)/100. Recebe as taxas em percentual (0 a 100),
 * uma por ano da etapa. Ano em branco (null, undefined ou '') e ano com taxa
 * zero ficam fora da media; precisa sobrar ao menos uma taxa acima de zero.
 */
function calcularRendimento(aprovacoes) {
    var taxas = aprovacoes.filter(function (taxa) {
        return taxa !== null && taxa !== undefined && taxa !== '';
    }).map(Number);
    taxas.forEach(function (taxa) {
        if (!(taxa >= 0 && taxa <= 100)) {
            throw new Error('Taxa de aprovação fora de 0 a 100: ' + taxa);
        }
    });
    var validas = taxas.filter(function (taxa) { return taxa > 0; });
    if (validas.length === 0) {
        throw new Error('Informe ao menos uma taxa de aprovação da etapa maior que zero.');
    }
    var somaInversos = validas.reduce(function (s, taxa) { return s + 100 / taxa; }, 0);
    return validas.length / somaInversos;
}

/** Nota de 0 a 10. A proficiencia precisa estar dentro dos limites da etapa. */
function padronizar(proficiencia, limite) {
    if (!(proficiencia >= limite.inf && proficiencia <= limite.sup)) {
        throw new Error('Proficiência fora dos limites do SAEB (' + limite.inf + ' a ' + limite.sup + '): ' + proficiencia);
    }
    return ((proficiencia - limite.inf) / (limite.sup - limite.inf)) * 10;
}

/**
 * IDEB de uma etapa. `chave` e 'ai', 'af' ou 'em'; `dados` traz
 * { aprovacoes: [taxa de cada ano, null no ano em branco], lp, mt }.
 */
function calcularIdeb(chave, dados) {
    var limites = LIMITES_SAEB[chave];
    var rendimento = calcularRendimento(dados.aprovacoes);
    var notaLp = padronizar(dados.lp, limites.lp);
    var notaMt = padronizar(dados.mt, limites.mt);
    var notaSaeb = (notaLp + notaMt) / 2;
    return {
        rendimento: rendimento,
        fluxo: 1 / rendimento,
        nota_lp: notaLp,
        nota_mt: notaMt,
        nota_saeb: notaSaeb,
        ideb: arredondar(notaSaeb * rendimento, 1),
    };
}
