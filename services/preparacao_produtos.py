from abbreviation.engine import abreviar_descricao
from models.produto import Produto
from services.codigo_custo import gerar_codigo_custo


def preparar_produtos(produtos: list[Produto]) -> None:
    """Prepara as descrições e os códigos dos produtos."""

    for produto in produtos:
        produto.codigo_custo = gerar_codigo_custo(
            produto.valor_unitario
        )

        descricao_abreviada = abreviar_descricao(
            produto.descricao_original
        )

        produto.descricao_final = (
            f"{descricao_abreviada} "
            f"{produto.codigo_custo}"
        )