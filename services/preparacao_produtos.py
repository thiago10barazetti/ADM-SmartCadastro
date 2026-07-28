from abbreviation.engine import abreviar_descricao
from database.description_repository import (
    buscar_descricao_aprendida,
)
from database.settings_repository import (
    carregar_configuracoes,
)
from models.produto import Produto
from services.codigo_custo import gerar_codigo_custo


def preparar_produtos(
    produtos: list[Produto],
) -> None:
    """Prepara descrições e códigos dos produtos."""

    configuracoes = carregar_configuracoes()

    for produto in produtos:
        produto.codigo_custo = gerar_codigo_custo(
            produto.valor_unitario
        )

        descricao_aprendida = (
            buscar_descricao_aprendida(
                produto.descricao_original
            )
        )

        if descricao_aprendida:
            descricao_base = descricao_aprendida

        else:
            descricao_base = abreviar_descricao(
                descricao_original=(
                    produto.descricao_original
                ),
                configuracoes=configuracoes,
            )

        produto.descricao_final = (
            f"{descricao_base} "
            f"{produto.codigo_custo}"
        )