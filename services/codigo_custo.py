from decimal import Decimal


MAPA_CUSTO = str.maketrans(
    "0123456789",
    "XABCDEFGHI",
)


def gerar_codigo_custo(valor_unitario: Decimal) -> str:
    """
    Converte a parte inteira do valor unitário para o código oculto.

    Exemplo:
        159,99 -> 159 -> (AEI)
    """

    valor_inteiro = int(valor_unitario)
    numero_texto = str(valor_inteiro)

    codigo = numero_texto.translate(MAPA_CUSTO)

    return f"({codigo})"