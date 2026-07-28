from decimal import Decimal
from tkinter import ttk

import customtkinter as ctk

from models.produto import Produto


def formatar_decimal(valor: Decimal, casas: int | None = None) -> str:
    """Formata valores decimais usando vírgula."""

    if casas is not None:
        texto = f"{valor:.{casas}f}"
    else:
        texto = format(valor.normalize(), "f")

    return texto.replace(".", ",")


class ProductTable(ctk.CTkFrame):
    """Tabela utilizada para exibir os produtos do XML."""

    def __init__(self, master) -> None:
        super().__init__(
            master,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=3,
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.configurar_estilo()

        colunas = (
            "referencia",
            "descricao",
            "quantidade",
            "valor_unitario",
            "csosn",
        )

        self.tabela = ttk.Treeview(
            self,
            columns=colunas,
            show="headings",
            style="Produtos.Treeview",
        )

        self.tabela.heading(
            "referencia",
            text="Referência",
        )
        self.tabela.heading(
            "descricao",
            text="Descrição original",
        )
        self.tabela.heading(
            "quantidade",
            text="Quantidade",
        )
        self.tabela.heading(
            "valor_unitario",
            text="Valor unitário",
        )
        self.tabela.heading(
            "csosn",
            text="CSOSN",
        )

        self.tabela.column(
            "referencia",
            width=110,
            minwidth=90,
            anchor="center",
            stretch=False,
        )
        self.tabela.column(
            "descricao",
            width=450,
            minwidth=250,
            anchor="w",
        )
        self.tabela.column(
            "quantidade",
            width=110,
            minwidth=90,
            anchor="center",
            stretch=False,
        )
        self.tabela.column(
            "valor_unitario",
            width=130,
            minwidth=110,
            anchor="e",
            stretch=False,
        )
        self.tabela.column(
            "csosn",
            width=90,
            minwidth=80,
            anchor="center",
            stretch=False,
        )

        barra_vertical = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tabela.yview,
        )

        barra_horizontal = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tabela.xview,
        )

        self.tabela.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )

        self.tabela.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(1, 0),
            pady=(1, 0),
        )

        barra_vertical.grid(
            row=0,
            column=1,
            sticky="ns",
            pady=(1, 0),
        )

        barra_horizontal.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(1, 0),
        )

    def configurar_estilo(self) -> None:
        estilo = ttk.Style(self)

        estilo.configure(
            "Produtos.Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#1F2937",
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 10),
        )

        estilo.configure(
            "Produtos.Treeview.Heading",
            background="#EAF1FF",
            foreground="#1F2937",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )

        estilo.map(
            "Produtos.Treeview",
            background=[
                ("selected", "#2563EB"),
            ],
            foreground=[
                ("selected", "#FFFFFF"),
            ],
        )

        estilo.map(
            "Produtos.Treeview.Heading",
            background=[
                ("active", "#DCE8FF"),
            ],
        )

    def limpar(self) -> None:
        """Remove todos os produtos da tabela."""

        for item in self.tabela.get_children():
            self.tabela.delete(item)

    def carregar_produtos(self, produtos: list[Produto]) -> None:
        """Mostra na tabela os produtos encontrados no XML."""

        self.limpar()

        for produto in produtos:
            quantidade = formatar_decimal(produto.quantidade)
            valor_unitario = formatar_decimal(
                produto.valor_unitario,
                casas=2,
            )

            self.tabela.insert(
                "",
                "end",
                values=(
                    produto.referencia,
                    produto.descricao_original,
                    quantidade,
                    f"R$ {valor_unitario}",
                    produto.csosn or "-",
                ),
            )