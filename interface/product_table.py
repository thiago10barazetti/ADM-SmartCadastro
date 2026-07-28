from collections import Counter
from collections.abc import Callable
from decimal import Decimal
import re
from tkinter import messagebox, simpledialog, ttk

import customtkinter as ctk

from database.description_repository import (
    salvar_descricao_aprendida,
)
from database.settings_repository import (
    adicionar_palavras_removidas,
    carregar_configuracoes,
)
from interface.styles import (
    COR_AZUL,
    COR_AZUL_CLARO,
    COR_AZUL_CLARO_HOVER,
    COR_BORDA,
    COR_ERRO_FUNDO,
    COR_ERRO_TEXTO,
    COR_FUNDO,
    COR_TEXTO,
    COR_TEXTO_BOTAO,
    FONTE_PRINCIPAL,
    TAMANHO_TABELA,
)
from models.produto import Produto


def formatar_decimal(
    valor: Decimal,
    casas: int | None = None,
) -> str:
    """Formata valores decimais usando vírgula."""

    if casas is not None:
        texto = f"{valor:.{casas}f}"
    else:
        texto = format(
            valor.normalize(),
            "f",
        )

    return texto.replace(".", ",")


def extrair_palavras(texto: str) -> list[str]:
    """Extrai palavras e números de uma descrição."""

    return re.findall(
        r"[A-ZÀ-Ü0-9]+",
        texto.upper(),
    )


def identificar_palavras_removidas(
    descricao_anterior: str,
    descricao_nova: str,
) -> list[str]:
    """Identifica as palavras removidas durante a edição."""

    palavras_anteriores = extrair_palavras(
        descricao_anterior
    )

    contagem_nova = Counter(
        extrair_palavras(descricao_nova)
    )

    removidas: list[str] = []

    for palavra in palavras_anteriores:
        if contagem_nova[palavra] > 0:
            contagem_nova[palavra] -= 1
            continue

        if palavra not in removidas:
            removidas.append(palavra)

    return removidas


class ProductTable(ctk.CTkFrame):
    """Tabela que exibe e permite revisar os produtos."""

    def __init__(
        self,
        master,
        ao_alterar_regras: (
            Callable[[], None] | None
        ) = None,
        ao_atualizar_validacao: (
            Callable[[], None] | None
        ) = None,
    ) -> None:
        super().__init__(
            master,
            fg_color=COR_FUNDO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=3,
        )

        self.produtos: list[Produto] = []
        self.ao_alterar_regras = ao_alterar_regras
        self.ao_atualizar_validacao = (
            ao_atualizar_validacao
        )

        self.limite_descricao = 35

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.configurar_estilo()

        colunas = (
            "referencia",
            "descricao_original",
            "descricao_final",
            "caracteres",
            "quantidade",
            "valor_unitario",
            "codigo_custo",
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
            "descricao_original",
            text="Descrição original",
        )

        self.tabela.heading(
            "descricao_final",
            text="Descrição final",
        )

        self.tabela.heading(
            "caracteres",
            text="Caracteres",
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
            "codigo_custo",
            text="Código",
        )

        self.tabela.column(
            "referencia",
            width=110,
            minwidth=100,
            anchor="center",
            stretch=False,
        )

        self.tabela.column(
            "descricao_original",
            width=260,
            minwidth=200,
            anchor="w",
        )

        self.tabela.column(
            "descricao_final",
            width=290,
            minwidth=220,
            anchor="w",
        )

        self.tabela.column(
            "caracteres",
            width=85,
            minwidth=80,
            anchor="center",
            stretch=False,
        )

        self.tabela.column(
            "quantidade",
            width=90,
            minwidth=80,
            anchor="center",
            stretch=False,
        )

        self.tabela.column(
            "valor_unitario",
            width=120,
            minwidth=110,
            anchor="e",
            stretch=False,
        )

        self.tabela.column(
            "codigo_custo",
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

        self.tabela.tag_configure(
            "invalido",
            background=COR_ERRO_FUNDO,
            foreground=COR_ERRO_TEXTO,
        )

        self.tabela.bind(
            "<Double-1>",
            self.editar_descricao,
        )

    def configurar_estilo(self) -> None:
        """Configura as fontes e cores da tabela."""

        estilo = ttk.Style(self)

        estilo.configure(
            "Produtos.Treeview",
            background=COR_FUNDO,
            fieldbackground=COR_FUNDO,
            foreground=COR_TEXTO,
            rowheight=31,
            borderwidth=0,
            font=(
                FONTE_PRINCIPAL,
                TAMANHO_TABELA,
            ),
        )

        estilo.configure(
            "Produtos.Treeview.Heading",
            background=COR_AZUL_CLARO,
            foreground=COR_TEXTO,
            relief="flat",
            font=(
                FONTE_PRINCIPAL,
                TAMANHO_TABELA,
                "bold",
            ),
        )

        estilo.map(
            "Produtos.Treeview",
            background=[
                ("selected", COR_AZUL),
            ],
            foreground=[
                ("selected", COR_TEXTO_BOTAO),
            ],
        )

        estilo.map(
            "Produtos.Treeview.Heading",
            background=[
                (
                    "active",
                    COR_AZUL_CLARO_HOVER,
                ),
            ],
        )

    def carregar_limite(self) -> None:
        """Carrega o limite salvo nas configurações."""

        configuracoes = carregar_configuracoes()

        try:
            self.limite_descricao = int(
                configuracoes.get(
                    "limite_descricao",
                    35,
                )
            )
        except (TypeError, ValueError):
            self.limite_descricao = 35

    def limpar(self) -> None:
        """Remove todos os produtos da tabela."""

        self.produtos = []

        for item in self.tabela.get_children():
            self.tabela.delete(item)

    def carregar_produtos(
        self,
        produtos: list[Produto],
    ) -> None:
        """Exibe os produtos encontrados no XML."""

        self.carregar_limite()
        self.limpar()
        self.produtos = produtos

        for indice, produto in enumerate(produtos):
            self.inserir_produto(
                indice=indice,
                produto=produto,
            )

        self.notificar_validacao()

    def inserir_produto(
        self,
        indice: int,
        produto: Produto,
    ) -> None:
        """Insere um produto na tabela."""

        quantidade = formatar_decimal(
            produto.quantidade
        )

        valor_unitario = formatar_decimal(
            produto.valor_unitario,
            casas=2,
        )

        quantidade_caracteres = len(
            produto.descricao_final
        )

        tags = ()

        if quantidade_caracteres > self.limite_descricao:
            tags = ("invalido",)

        self.tabela.insert(
            "",
            "end",
            iid=str(indice),
            values=(
                produto.referencia,
                produto.descricao_original,
                produto.descricao_final,
                (
                    f"{quantidade_caracteres}/"
                    f"{self.limite_descricao}"
                ),
                quantidade,
                f"R$ {valor_unitario}",
                produto.codigo_custo,
            ),
            tags=tags,
        )

    def atualizar_linha(
        self,
        linha: str,
        produto: Produto,
    ) -> None:
        """Atualiza uma linha após editar a descrição."""

        quantidade_caracteres = len(
            produto.descricao_final
        )

        valores = list(
            self.tabela.item(
                linha,
                "values",
            )
        )

        valores[2] = produto.descricao_final
        valores[3] = (
            f"{quantidade_caracteres}/"
            f"{self.limite_descricao}"
        )

        tags = ()

        if quantidade_caracteres > self.limite_descricao:
            tags = ("invalido",)

        self.tabela.item(
            linha,
            values=valores,
            tags=tags,
        )

    def contar_descricoes_invalidas(self) -> int:
        """Conta as descrições acima do limite."""

        return sum(
            1
            for produto in self.produtos
            if len(produto.descricao_final)
            > self.limite_descricao
        )

    def tem_descricoes_invalidas(self) -> bool:
        """Informa se existe alguma descrição acima do limite."""

        return self.contar_descricoes_invalidas() > 0

    def obter_limite_descricao(self) -> int:
        """Retorna o limite atual."""

        return self.limite_descricao

    def notificar_validacao(self) -> None:
        """Avisa a janela principal para atualizar o botão."""

        if self.ao_atualizar_validacao is not None:
            self.ao_atualizar_validacao()

    def editar_descricao(self, evento) -> None:
        """Permite editar a descrição final com duplo clique."""

        linha = self.tabela.identify_row(
            evento.y
        )

        coluna = self.tabela.identify_column(
            evento.x
        )

        if not linha:
            return

        if coluna != "#3":
            return

        indice = int(linha)
        produto = self.produtos[indice]

        descricao_sem_codigo = (
            produto.descricao_final
        )

        if descricao_sem_codigo.endswith(
            produto.codigo_custo
        ):
            descricao_sem_codigo = descricao_sem_codigo[
                :-len(produto.codigo_custo)
            ].strip()

        nova_descricao = simpledialog.askstring(
            title="Editar descrição",
            prompt=(
                "Digite a descrição do produto.\n\n"
                "O código do custo será adicionado "
                "automaticamente:"
            ),
            initialvalue=descricao_sem_codigo,
            parent=self,
        )

        if nova_descricao is None:
            return

        nova_descricao = " ".join(
            nova_descricao.upper().split()
        )

        if not nova_descricao:
            messagebox.showwarning(
                "Descrição inválida",
                "A descrição não pode ficar vazia.",
                parent=self,
            )
            return

        palavras_removidas = (
            identificar_palavras_removidas(
                descricao_anterior=descricao_sem_codigo,
                descricao_nova=nova_descricao,
            )
        )

        configuracoes = carregar_configuracoes()

        palavras_ja_removidas = set(
            configuracoes["palavras_removidas"]
        )

        palavras_adicionar: list[str] = []

        for palavra in palavras_removidas:
            if palavra in palavras_ja_removidas:
                continue

            remover_globalmente = messagebox.askyesno(
                "Nova regra de remoção",
                (
                    f'Você removeu a palavra "{palavra}".\n\n'
                    "Deseja removê-la automaticamente "
                    "de todas as descrições futuras?\n\n"
                    "Sim: adicionar às palavras removidas.\n"
                    "Não: aplicar somente neste produto."
                ),
                parent=self,
            )

            if remover_globalmente:
                palavras_adicionar.append(
                    palavra
                )

        palavras_realmente_adicionadas = (
            adicionar_palavras_removidas(
                palavras_adicionar
            )
        )

        salvar_descricao_aprendida(
            descricao_original=produto.descricao_original,
            descricao_final=nova_descricao,
        )

        produto.descricao_final = (
            f"{nova_descricao} "
            f"{produto.codigo_custo}"
        )

        if (
            palavras_realmente_adicionadas
            and self.ao_alterar_regras is not None
        ):
            self.ao_alterar_regras()
            return

        self.atualizar_linha(
            linha=linha,
            produto=produto,
        )

        self.notificar_validacao()