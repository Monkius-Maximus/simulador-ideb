/* ============================================================================
   Motor IDEB — porte da aba "Simulador Ideb" da planilha do Núcleo da Seplag.

   IDEB = N x P, calculado por etapa. Nao existe IDEB unico da escola.

     P   rendimento, de 0 a 1: media harmonica das taxas de aprovacao dos
         anos da etapa que a escola tem (metodologia do Inep). Ano em branco
         fica fora da media; taxa zero (ninguem aprovado) leva P a zero.
     N   aprendizado, de 0 a 10: media das notas padronizadas de LP e MT no
         SAEB, nota = (proficiencia - limite inferior) / (superior - inferior)
         x 10. Limites definidos pelo NGR: AI e AF com LP 49-324 e MT
         60-322; EM com LP 117-451 e MT 111-467. Nos AF o Inep e a planilha
         usam 100-400; aqui os AF seguem os limites dos AI, por decisao do NGR.
     IDEB  N x P, de 0 a 10, divulgado com uma casa decimal.

   Os limites sao condicao de entrada: taxa fora de 0 a 100 ou proficiencia
   fora dos limites da etapa param o calculo com erro. Assim P nunca passa de
   1, nenhuma nota passa de 10 e o IDEB fica sempre entre 0 e 10.

   Diferenca para a planilha, de proposito: com N x P = 0 a C14 fica em
   branco, porque o AND(...; E11*G7) trata zero como falso. Aqui o IDEB e 0,0.
   ============================================================================ */

var LIMITES_SAEB = {
    ai: { lp: { inf: 49, sup: 324 }, mt: { inf: 60, sup: 322 } },
    af: { lp: { inf: 49, sup: 324 }, mt: { inf: 60, sup: 322 } },
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
 * P, de 0 a 1. Recebe as taxas em percentual (0 a 100), so dos anos
 * preenchidos, e devolve a media harmonica delas. Uma taxa zero leva P a zero.
 */
function calcularRendimento(aprovacoes) {
    if (aprovacoes.length === 0) {
        throw new Error('Informe ao menos uma taxa de aprovação da etapa.');
    }
    aprovacoes.forEach(function (taxa) {
        if (!(taxa >= 0 && taxa <= 100)) {
            throw new Error('Taxa de aprovação fora de 0 a 100: ' + taxa);
        }
    });
    if (aprovacoes.indexOf(0) !== -1) return 0;
    var somaInversos = aprovacoes.reduce(function (s, taxa) { return s + 100 / taxa; }, 0);
    return aprovacoes.length / somaInversos;
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
 * { aprovacoes: [taxas preenchidas], lp, mt }.
 */
function calcularIdeb(chave, dados) {
    var limites = LIMITES_SAEB[chave];
    var rendimento = calcularRendimento(dados.aprovacoes);
    var notaLp = padronizar(dados.lp, limites.lp);
    var notaMt = padronizar(dados.mt, limites.mt);
    var notaSaeb = (notaLp + notaMt) / 2;
    return {
        rendimento: rendimento,
        nota_lp: notaLp,
        nota_mt: notaMt,
        nota_saeb: notaSaeb,
        ideb: arredondar(notaSaeb * rendimento, 1),
    };
}
