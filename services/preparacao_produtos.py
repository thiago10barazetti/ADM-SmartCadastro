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
    configuracao_codigo = configuracoes.get(
        "codigo_secreto"
    )

    for produto in produtos:
        produto.codigo_custo = gerar_codigo_custo(
            produto.valor_unitario,
            configuracao=configuracao_codigo,
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

        partes_descricao = [
            descricao_base.strip()
        ]

        if produto.codigo_custo:
            partes_descricao.append(
                produto.codigo_custo
            )

        produto.descricao_final = " ".join(
            parte
            for parte in partes_descricao
            if parte
        )
