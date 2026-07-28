import re


PALAVRAS_REMOVIDAS = {
    "INVERNO",
    "INV",
    "STRETCH",
    "MODAL",
}


SUBSTITUICOES_DE_EXPRESSOES = {
    "RAYON TWILL": "RAYON",
}


ABREVIACOES = {
    "FEMININA": "FEM",
    "FEMININO": "FEM",
    "MASCULINA": "MASC",
    "MASCULINO": "MASC",
}


TAMANHOS_VALIDOS = {
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
}


CORES_BASE = {
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
}


def remover_variantes_de_cor(
    palavras: list[str],
) -> list[str]:
    """
    Mantém apenas a cor base e remove a variante posterior.

    Exemplos:
        G PRETO REATIVO -> G PRETO
        M VERDE FLORENA -> M VERDE
        PP BRANCO OFF WHITE -> PP BRANCO
    """

    ultimo_tamanho = -1

    for indice, palavra in enumerate(palavras):
        if palavra in TAMANHOS_VALIDOS:
            ultimo_tamanho = indice

    for indice, palavra in enumerate(palavras):
        if palavra not in CORES_BASE:
            continue

        cor_depois_do_tamanho = (
            ultimo_tamanho >= 0
            and indice > ultimo_tamanho
        )

        cor_proxima_do_final = (
            indice >= len(palavras) - 3
        )

        if not (
            cor_depois_do_tamanho
            or cor_proxima_do_final
        ):
            continue

        # Preserva algum tamanho que eventualmente apareça
        # depois da cor.
        tamanhos_posteriores = [
            item
            for item in palavras[indice + 1:]
            if item in TAMANHOS_VALIDOS
        ]

        return (
            palavras[:indice + 1]
            + tamanhos_posteriores
        )

    return palavras


def abreviar_descricao(
    descricao_original: str,
) -> str:
    """Cria uma descrição curta e padronizada."""

    descricao = descricao_original.upper().strip()
    descricao = re.sub(r"\s+", " ", descricao)

    for expressao, substituicao in (
        SUBSTITUICOES_DE_EXPRESSOES.items()
    ):
        descricao = re.sub(
            rf"\b{re.escape(expressao)}\b",
            substituicao,
            descricao,
        )

    palavras_finais: list[str] = []

    for palavra in descricao.split():
        palavra_limpa = palavra.strip(
            ".,;:/\\-_"
        )

        if not palavra_limpa:
            continue

        if palavra_limpa in PALAVRAS_REMOVIDAS:
            continue

        if palavra_limpa in TAMANHOS_VALIDOS:
            palavras_finais.append(
                palavra_limpa
            )
            continue

        if palavra_limpa.isdigit():
            continue

        palavra_final = ABREVIACOES.get(
            palavra_limpa,
            palavra_limpa,
        )

        palavras_finais.append(
            palavra_final
        )

    palavras_finais = remover_variantes_de_cor(
        palavras_finais
    )

    return " ".join(palavras_finais)