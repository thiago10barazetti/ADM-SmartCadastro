import re


def remover_variantes_de_cor(
    palavras: list[str],
    tamanhos_validos: set[str],
    cores_base: set[str],
) -> list[str]:
    """
    Mantém a cor principal e remove suas variantes.

    Exemplos:
        PRETO REATIVO -> PRETO
        VERDE FLORENA -> VERDE
        BEGE ALHAMBRA -> BEGE
    """

    ultimo_tamanho = -1

    for indice, palavra in enumerate(palavras):
        if palavra in tamanhos_validos:
            ultimo_tamanho = indice

    for indice, palavra in enumerate(palavras):
        if palavra not in cores_base:
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

        tamanhos_posteriores = [
            item
            for item in palavras[indice + 1:]
            if item in tamanhos_validos
        ]

        return (
            palavras[:indice + 1]
            + tamanhos_posteriores
        )

    return palavras


def abreviar_descricao(
    descricao_original: str,
    configuracoes: dict,
) -> str:
    """Cria uma descrição curta usando as configurações."""

    palavras_removidas = set(
        configuracoes["palavras_removidas"]
    )

    substituicoes = configuracoes[
        "substituicoes_expressoes"
    ]

    abreviacoes = configuracoes["abreviacoes"]

    tamanhos_validos = set(
        configuracoes["tamanhos_validos"]
    )

    cores_base = set(
        configuracoes["cores_base"]
    )

    descricao = descricao_original.upper().strip()
    descricao = re.sub(r"\s+", " ", descricao)

    # Expressões maiores são processadas primeiro.
    expressoes_ordenadas = sorted(
        substituicoes.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for expressao, substituicao in expressoes_ordenadas:
        descricao = re.sub(
            rf"\b{re.escape(expressao.upper())}\b",
            substituicao.upper(),
            descricao,
        )

    palavras_finais: list[str] = []

    for palavra in descricao.split():
        palavra_limpa = palavra.strip(
            ".,;:/\\-_"
        )

        if not palavra_limpa:
            continue

        if palavra_limpa in palavras_removidas:
            continue

        if palavra_limpa in tamanhos_validos:
            palavras_finais.append(
                palavra_limpa
            )
            continue

        if palavra_limpa.isdigit():
            continue

        palavra_final = abreviacoes.get(
            palavra_limpa,
            palavra_limpa,
        )

        palavras_finais.append(
            palavra_final
        )

    palavras_finais = remover_variantes_de_cor(
        palavras=palavras_finais,
        tamanhos_validos=tamanhos_validos,
        cores_base=cores_base,
    )

    return " ".join(palavras_finais)