from models.produto import Produto
from services.codigo_custo import gerar_codigo_custo


def preparar_produtos(produtos: list[Produto]) -> None:
    """
    Prepara os produtos para serem exibidos e cadastrados.

    A descrição ainda não é abreviada nesta etapa.
    """

    for produto in produtos:
        produto.codigo_custo = gerar_codigo_custo(
            produto.valor_unitario
        )

        produto.descricao_final = (
            f"{produto.descricao_original} "
            f"{produto.codigo_custo}"
        )