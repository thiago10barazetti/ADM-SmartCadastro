from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Produto:
    """Representa um produto encontrado no XML da nota fiscal."""

    referencia: str
    descricao_original: str
    codigo_barras: str
    ncm: str
    cfop: str
    unidade: str
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal
    csosn: str