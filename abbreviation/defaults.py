"""Configurações padrão do motor de abreviação."""


CONFIGURACOES_PADRAO = {
    "palavras_removidas": [
        "INVERNO",
        "INV",
        "STRETCH",
        "MODAL",
    ],

    "substituicoes_expressoes": {
        "RAYON TWILL": "RAYON",
    },

    "abreviacoes": {
        "FEMININA": "FEM",
        "FEMININO": "FEM",
        "MASCULINA": "MASC",
        "MASCULINO": "MASC",
    },

    "tamanhos_validos": [
        "34",
        "36",
        "38",
        "40",
        "42",
        "44",
        "46",
        "48",
        "50",
        "52",
        "54",
        "PP",
        "P",
        "M",
        "G",
        "GG",
        "XG",
        "G1",
        "G2",
        "G3",
    ],

    "cores_base": [
        "PRETO",
        "BRANCO",
        "AZUL",
        "VERDE",
        "VERMELHO",
        "AMARELO",
        "ROSA",
        "LILAS",
        "LILÁS",
        "ROXO",
        "BEGE",
        "MARROM",
        "CINZA",
        "LARANJA",
        "VINHO",
        "NUDE",
        "DOURADO",
        "PRATA",
    ],

    "codigo_secreto": {
        "ativo": True,
        "simbolos": {
            "0": "X",
            "1": "A",
            "2": "B",
            "3": "C",
            "4": "D",
            "5": "E",
            "6": "F",
            "7": "G",
            "8": "H",
            "9": "I",
        },
        "prefixo": "(",
        "sufixo": ")",
    },

    "limite_descricao": 35,
}
