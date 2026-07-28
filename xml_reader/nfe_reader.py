from decimal import Decimal, InvalidOperation
from pathlib import Path
import xml.etree.ElementTree as ET

from models.produto import Produto


def _obter_texto(
    elemento: ET.Element,
    tag: str,
    padrao: str = "",
) -> str:
    """Obtém o texto de uma tag XML com ou sem namespace."""

    campo = elemento.find(f"{{*}}{tag}")

    if campo is None or campo.text is None:
        return padrao

    return campo.text.strip()


def _converter_decimal(valor: str) -> Decimal:
    """Converte um texto numérico do XML para Decimal."""

    try:
        return Decimal(valor)

    except (InvalidOperation, TypeError):
        return Decimal("0")


def ler_produtos_xml(
    caminho_xml: str | Path,
) -> list[Produto]:
    """Lê um XML de NF-e e retorna seus produtos."""

    caminho = Path(caminho_xml)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    try:
        arvore = ET.parse(caminho)

    except ET.ParseError as erro:
        raise ValueError(
            "O arquivo selecionado não é um XML válido."
        ) from erro

    raiz = arvore.getroot()
    produtos_encontrados: list[Produto] = []

    for detalhe in raiz.findall(".//{*}det"):
        dados_produto = detalhe.find("{*}prod")

        if dados_produto is None:
            continue

        codigo_barras = _obter_texto(
            dados_produto,
            "cEAN",
        )

        if (
            not codigo_barras
            or codigo_barras.upper() == "SEM GTIN"
        ):
            codigo_barras = _obter_texto(
                dados_produto,
                "cEANTrib",
            )

        if codigo_barras.upper() == "SEM GTIN":
            codigo_barras = ""

        produto = Produto(
            referencia=_obter_texto(
                dados_produto,
                "cProd",
            ),
            descricao_original=_obter_texto(
                dados_produto,
                "xProd",
            ),
            codigo_barras=codigo_barras,
            ncm=_obter_texto(
                dados_produto,
                "NCM",
            ),
            cfop=_obter_texto(
                dados_produto,
                "CFOP",
            ),
            unidade=_obter_texto(
                dados_produto,
                "uCom",
            ),
            quantidade=_converter_decimal(
                _obter_texto(
                    dados_produto,
                    "qCom",
                    "0",
                )
            ),
            valor_unitario=_converter_decimal(
                _obter_texto(
                    dados_produto,
                    "vUnCom",
                    "0",
                )
            ),
            valor_total=_converter_decimal(
                _obter_texto(
                    dados_produto,
                    "vProd",
                    "0",
                )
            ),
        )

        produtos_encontrados.append(produto)

    if not produtos_encontrados:
        raise ValueError(
            "Nenhum produto foi encontrado no XML selecionado."
        )

    return produtos_encontrados