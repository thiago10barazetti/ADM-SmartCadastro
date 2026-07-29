import csv
from datetime import datetime
from pathlib import Path


class RelatorioExecucao:
    """Registra e salva os resultados de uma execução."""

    CABECALHO = (
        "execucao",
        "inicio",
        "fim",
        "resultado_geral",
        "modo",
        "total_itens",
        "item",
        "referencia",
        "codigo_barras",
        "descricao_original",
        "descricao_final",
        "resultado_item",
        "detalhe",
        "data_hora_item",
    )

    def __init__(
        self,
        modo: str,
        total_itens: int,
    ) -> None:
        self.modo = modo
        self.total_itens = total_itens
        self.inicio = datetime.now()
        self.registros: list[dict[str, str | int]] = []
        self.caminho_salvo: Path | None = None

    def registrar(
        self,
        numero_item: int,
        produto,
        resultado_item: str,
        detalhe: str = "",
    ) -> None:
        """Adiciona o resultado de um produto ao relatório."""

        self.registros.append(
            {
                "item": numero_item,
                "referencia": self.obter_texto(
                    produto,
                    "referencia",
                ),
                "codigo_barras": self.obter_texto(
                    produto,
                    "codigo_barras",
                ),
                "descricao_original": self.obter_texto(
                    produto,
                    "descricao_original",
                ),
                "descricao_final": self.obter_texto(
                    produto,
                    "descricao_final",
                ),
                "resultado_item": resultado_item,
                "detalhe": detalhe,
                "data_hora_item": (
                    datetime.now().strftime(
                        "%d/%m/%Y %H:%M:%S"
                    )
                ),
            }
        )

    def salvar(
        self,
        resultado_geral: str,
    ) -> Path:
        """Salva o relatório CSV e retorna o caminho."""

        if self.caminho_salvo is not None:
            return self.caminho_salvo

        fim = datetime.now()

        raiz_projeto = (
            Path(__file__).resolve().parents[1]
        )
        pasta_relatorios = (
            raiz_projeto
            / "logs"
            / "relatorios"
        )
        pasta_relatorios.mkdir(
            parents=True,
            exist_ok=True,
        )

        identificador = self.inicio.strftime(
            "%Y-%m-%d_%H-%M-%S"
        )
        nome_arquivo = (
            f"cadastro_{identificador}_{self.modo}.csv"
        )
        caminho = pasta_relatorios / nome_arquivo

        dados_globais = {
            "execucao": identificador,
            "inicio": self.inicio.strftime(
                "%d/%m/%Y %H:%M:%S"
            ),
            "fim": fim.strftime(
                "%d/%m/%Y %H:%M:%S"
            ),
            "resultado_geral": resultado_geral,
            "modo": self.modo,
            "total_itens": self.total_itens,
        }

        registros = self.registros or [
            {
                "item": "",
                "referencia": "",
                "codigo_barras": "",
                "descricao_original": "",
                "descricao_final": "",
                "resultado_item": "",
                "detalhe": (
                    "Execução encerrada sem resultados "
                    "individuais registrados."
                ),
                "data_hora_item": "",
            }
        ]

        with caminho.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as arquivo:
            escritor = csv.DictWriter(
                arquivo,
                fieldnames=self.CABECALHO,
                delimiter=";",
            )
            escritor.writeheader()

            for registro in registros:
                linha = {
                    **dados_globais,
                    **registro,
                }
                escritor.writerow(linha)

        self.caminho_salvo = caminho
        return caminho

    @staticmethod
    def obter_texto(
        produto,
        atributo: str,
    ) -> str:
        """Obtém um atributo do produto como texto."""

        valor = getattr(
            produto,
            atributo,
            "",
        )

        if valor is None:
            return ""

        return str(valor)
