from decimal import Decimal

from abbreviation.defaults import CONFIGURACOES_PADRAO


def obter_configuracao_codigo(
    configuracao: dict | None,
) -> dict:
    """Combina a configuração informada com o padrão."""

    padrao = CONFIGURACOES_PADRAO["codigo_secreto"]

    resultado = {
        "ativo": padrao["ativo"],
        "simbolos": dict(padrao["simbolos"]),
        "prefixo": padrao["prefixo"],
        "sufixo": padrao["sufixo"],
    }

    if not isinstance(configuracao, dict):
        return resultado

    if "ativo" in configuracao:
        resultado["ativo"] = bool(
            configuracao["ativo"]
        )

    simbolos = configuracao.get("simbolos")

    if isinstance(simbolos, dict):
        for numero in "0123456789":
            valor = simbolos.get(numero)

            if isinstance(valor, str) and valor:
                resultado["simbolos"][numero] = valor

    prefixo = configuracao.get("prefixo")

    if isinstance(prefixo, str) and prefixo:
        resultado["prefixo"] = prefixo

    sufixo = configuracao.get("sufixo")

    if isinstance(sufixo, str) and sufixo:
        resultado["sufixo"] = sufixo

    return resultado


def gerar_codigo_custo(
    valor_unitario: Decimal,
    configuracao: dict | None = None,
) -> str:
    """
    Converte a parte inteira do valor unitário para o código secreto.

    Exemplo com o padrão:
        159,99 -> 159 -> (AEI)

    Quando o código estiver desativado, retorna uma string vazia.
    """

    codigo_configurado = obter_configuracao_codigo(
        configuracao
    )

    if not codigo_configurado["ativo"]:
        return ""

    valor_inteiro = int(valor_unitario)
    numero_texto = str(valor_inteiro)
    simbolos = codigo_configurado["simbolos"]

    partes = []

    for caractere in numero_texto:
        if caractere in simbolos:
            partes.append(
                simbolos[caractere]
            )
        else:
            partes.append(caractere)

    codigo = "".join(partes)

    return (
        f"{codigo_configurado['prefixo']}"
        f"{codigo}"
        f"{codigo_configurado['sufixo']}"
    )
