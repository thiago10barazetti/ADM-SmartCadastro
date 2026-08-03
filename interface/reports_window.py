import csv
import os
import subprocess
import sys
from pathlib import Path
from tkinter import messagebox, ttk

import customtkinter as ctk

from services.app_paths import PASTA_RELATORIOS
from interface.styles import (
    COR_AZUL,
    COR_AZUL_HOVER,
    COR_BORDA,
    COR_BORDA_ESCURA,
    COR_ERRO_TEXTO,
    COR_FUNDO,
    COR_FUNDO_SECUNDARIO,
    COR_TEXTO,
    COR_TEXTO_BOTAO,
    COR_TEXTO_SECUNDARIO,
    FONTE_PRINCIPAL,
    TAMANHO_BOTAO,
    TAMANHO_SUBTITULO,
    TAMANHO_TEXTO,
    TAMANHO_TEXTO_DESTAQUE,
    TAMANHO_TITULO,
)


FILTRO_TODOS = "Todos"
FILTRO_SALVOS = "Salvos"
FILTRO_PULADOS = "Pulados"
FILTRO_ERROS = "Erros"

FILTROS = (
    FILTRO_TODOS,
    FILTRO_SALVOS,
    FILTRO_PULADOS,
    FILTRO_ERROS,
)


class ReportsWindow(ctk.CTkToplevel):
    """Exibe os relatórios de execução do cadastro."""

    def __init__(
        self,
        master,
    ) -> None:
        super().__init__(master)

        self.title("Relatórios de execução")
        self.geometry("1220x740")
        self.minsize(980, 620)
        self.configure(fg_color=COR_FUNDO)

        self.pasta_relatorios = PASTA_RELATORIOS

        self.caminho_atual: Path | None = None
        self.registros_atuais: list[
            dict[str, str]
        ] = []
        self.botoes_relatorios: list[
            ctk.CTkButton
        ] = []

        self.grid_columnconfigure(
            0,
            weight=1,
        )
        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self.criar_cabecalho()
        self.criar_conteudo()
        self.configurar_tabela()
        self.carregar_lista_relatorios()

        self.after(
            150,
            self.lift,
        )

    def criar_cabecalho(self) -> None:
        """Cria o cabeçalho da janela."""

        cabecalho = ctk.CTkFrame(
            self,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        cabecalho.grid(
            row=0,
            column=0,
            padx=28,
            pady=(22, 14),
            sticky="ew",
        )
        cabecalho.grid_columnconfigure(
            0,
            weight=1,
        )

        titulo = ctk.CTkLabel(
            cabecalho,
            text="Relatórios de execução",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TITULO,
                weight="bold",
            ),
        )
        titulo.grid(
            row=0,
            column=0,
            sticky="w",
        )

        subtitulo = ctk.CTkLabel(
            cabecalho,
            text=(
                "Consulte os produtos salvos, pulados "
                "e interrompidos em cada execução."
            ),
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_SUBTITULO,
            ),
        )
        subtitulo.grid(
            row=1,
            column=0,
            pady=(3, 0),
            sticky="w",
        )

        botao_atualizar = ctk.CTkButton(
            cabecalho,
            text="Atualizar",
            width=110,
            height=36,
            corner_radius=4,
            fg_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            text_color=COR_TEXTO_BOTAO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
                weight="bold",
            ),
            command=self.carregar_lista_relatorios,
        )
        botao_atualizar.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=(14, 0),
            sticky="e",
        )

    def criar_conteudo(self) -> None:
        """Cria a lista, resumo e tabela."""

        conteudo = ctk.CTkFrame(
            self,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        conteudo.grid(
            row=1,
            column=0,
            padx=28,
            pady=(0, 24),
            sticky="nsew",
        )
        conteudo.grid_columnconfigure(
            0,
            weight=0,
        )
        conteudo.grid_columnconfigure(
            1,
            weight=1,
        )
        conteudo.grid_rowconfigure(
            0,
            weight=1,
        )

        painel_lista = ctk.CTkFrame(
            conteudo,
            width=310,
            fg_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=5,
        )
        painel_lista.grid(
            row=0,
            column=0,
            padx=(0, 16),
            sticky="ns",
        )
        painel_lista.grid_propagate(False)
        painel_lista.grid_columnconfigure(
            0,
            weight=1,
        )
        painel_lista.grid_rowconfigure(
            1,
            weight=1,
        )

        label_lista = ctk.CTkLabel(
            painel_lista,
            text="Execuções encontradas",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO_DESTAQUE,
                weight="bold",
            ),
        )
        label_lista.grid(
            row=0,
            column=0,
            padx=14,
            pady=(14, 10),
            sticky="ew",
        )

        self.lista_relatorios = ctk.CTkScrollableFrame(
            painel_lista,
            fg_color=COR_FUNDO_SECUNDARIO,
            corner_radius=0,
        )
        self.lista_relatorios.grid(
            row=1,
            column=0,
            padx=8,
            pady=(0, 8),
            sticky="nsew",
        )
        self.lista_relatorios.grid_columnconfigure(
            0,
            weight=1,
        )

        botoes_pasta = ctk.CTkFrame(
            painel_lista,
            fg_color=COR_FUNDO_SECUNDARIO,
            corner_radius=0,
        )
        botoes_pasta.grid(
            row=2,
            column=0,
            padx=10,
            pady=(2, 12),
            sticky="ew",
        )
        botoes_pasta.grid_columnconfigure(
            0,
            weight=1,
        )
        botoes_pasta.grid_columnconfigure(
            1,
            weight=1,
        )

        botao_abrir_csv = ctk.CTkButton(
            botoes_pasta,
            text="Abrir CSV",
            height=34,
            corner_radius=4,
            fg_color=COR_FUNDO,
            hover_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA_ESCURA,
            text_color=COR_TEXTO,
            command=self.abrir_csv_atual,
        )
        botao_abrir_csv.grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="ew",
        )

        botao_abrir_pasta = ctk.CTkButton(
            botoes_pasta,
            text="Abrir pasta",
            height=34,
            corner_radius=4,
            fg_color=COR_FUNDO,
            hover_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA_ESCURA,
            text_color=COR_TEXTO,
            command=self.abrir_pasta_relatorios,
        )
        botao_abrir_pasta.grid(
            row=0,
            column=1,
            padx=(5, 0),
            sticky="ew",
        )

        painel_detalhes = ctk.CTkFrame(
            conteudo,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        painel_detalhes.grid(
            row=0,
            column=1,
            sticky="nsew",
        )
        painel_detalhes.grid_columnconfigure(
            0,
            weight=1,
        )
        painel_detalhes.grid_rowconfigure(
            2,
            weight=1,
        )

        self.area_resumo = ctk.CTkFrame(
            painel_detalhes,
            fg_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=5,
        )
        self.area_resumo.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        for coluna in range(4):
            self.area_resumo.grid_columnconfigure(
                coluna,
                weight=1,
            )

        self.label_nome_relatorio = (
            self.criar_campo_resumo(
                coluna=0,
                titulo="Relatório",
            )
        )
        self.label_modo_relatorio = (
            self.criar_campo_resumo(
                coluna=1,
                titulo="Modo",
            )
        )
        self.label_resultado_relatorio = (
            self.criar_campo_resumo(
                coluna=2,
                titulo="Resultado",
            )
        )
        self.label_periodo_relatorio = (
            self.criar_campo_resumo(
                coluna=3,
                titulo="Período",
            )
        )

        area_filtro = ctk.CTkFrame(
            painel_detalhes,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        area_filtro.grid(
            row=1,
            column=0,
            pady=(14, 9),
            sticky="ew",
        )
        area_filtro.grid_columnconfigure(
            0,
            weight=1,
        )

        self.label_resumo_itens = ctk.CTkLabel(
            area_filtro,
            text="Nenhum relatório selecionado",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO_DESTAQUE,
                weight="bold",
            ),
        )
        self.label_resumo_itens.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.seletor_filtro = ctk.CTkOptionMenu(
            area_filtro,
            values=list(FILTROS),
            width=140,
            height=34,
            corner_radius=4,
            fg_color=COR_AZUL,
            button_color=COR_AZUL,
            button_hover_color=COR_AZUL_HOVER,
            text_color=COR_TEXTO_BOTAO,
            command=self.aplicar_filtro,
        )
        self.seletor_filtro.grid(
            row=0,
            column=1,
            padx=(12, 0),
            sticky="e",
        )
        self.seletor_filtro.set(
            FILTRO_TODOS
        )

        area_tabela = ctk.CTkFrame(
            painel_detalhes,
            fg_color=COR_FUNDO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=4,
        )
        area_tabela.grid(
            row=2,
            column=0,
            sticky="nsew",
        )
        area_tabela.grid_columnconfigure(
            0,
            weight=1,
        )
        area_tabela.grid_rowconfigure(
            0,
            weight=1,
        )

        colunas = (
            "item",
            "referencia",
            "resultado",
            "descricao",
            "detalhe",
        )

        self.tabela = ttk.Treeview(
            area_tabela,
            columns=colunas,
            show="headings",
            style="Relatorios.Treeview",
        )

        self.tabela.heading(
            "item",
            text="Item",
        )
        self.tabela.heading(
            "referencia",
            text="Referência",
        )
        self.tabela.heading(
            "resultado",
            text="Resultado",
        )
        self.tabela.heading(
            "descricao",
            text="Descrição final",
        )
        self.tabela.heading(
            "detalhe",
            text="Detalhe",
        )

        self.tabela.column(
            "item",
            width=55,
            minwidth=45,
            anchor="center",
            stretch=False,
        )
        self.tabela.column(
            "referencia",
            width=115,
            minwidth=90,
            anchor="w",
            stretch=False,
        )
        self.tabela.column(
            "resultado",
            width=160,
            minwidth=130,
            anchor="w",
            stretch=False,
        )
        self.tabela.column(
            "descricao",
            width=300,
            minwidth=220,
            anchor="w",
        )
        self.tabela.column(
            "detalhe",
            width=320,
            minwidth=220,
            anchor="w",
        )

        barra_vertical = ttk.Scrollbar(
            area_tabela,
            orient="vertical",
            command=self.tabela.yview,
        )
        barra_horizontal = ttk.Scrollbar(
            area_tabela,
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
        )
        barra_vertical.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        barra_horizontal.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        self.label_status = ctk.CTkLabel(
            painel_detalhes,
            text="Aguardando a seleção de um relatório.",
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        self.label_status.grid(
            row=3,
            column=0,
            pady=(8, 0),
            sticky="ew",
        )

    def criar_campo_resumo(
        self,
        coluna: int,
        titulo: str,
    ) -> ctk.CTkLabel:
        """Cria um campo do resumo superior."""

        quadro = ctk.CTkFrame(
            self.area_resumo,
            fg_color=COR_FUNDO_SECUNDARIO,
            corner_radius=0,
        )
        quadro.grid(
            row=0,
            column=coluna,
            padx=14,
            pady=12,
            sticky="nsew",
        )

        label_titulo = ctk.CTkLabel(
            quadro,
            text=titulo,
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        label_titulo.grid(
            row=0,
            column=0,
            sticky="w",
        )

        label_valor = ctk.CTkLabel(
            quadro,
            text="—",
            anchor="w",
            justify="left",
            wraplength=210,
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
                weight="bold",
            ),
        )
        label_valor.grid(
            row=1,
            column=0,
            pady=(3, 0),
            sticky="w",
        )

        return label_valor

    def configurar_tabela(self) -> None:
        """Configura a aparência da tabela."""

        estilo = ttk.Style(self)

        try:
            estilo.theme_use("clam")
        except Exception:
            pass

        estilo.configure(
            "Relatorios.Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#1F2937",
            rowheight=30,
            borderwidth=0,
            font=(FONTE_PRINCIPAL, 10),
        )
        estilo.configure(
            "Relatorios.Treeview.Heading",
            background="#F3F4F6",
            foreground="#1F2937",
            relief="flat",
            font=(
                FONTE_PRINCIPAL,
                10,
                "bold",
            ),
        )
        estilo.map(
            "Relatorios.Treeview",
            background=[
                ("selected", "#DBEAFE"),
            ],
            foreground=[
                ("selected", "#1F2937"),
            ],
        )

    def carregar_lista_relatorios(self) -> None:
        """Carrega os arquivos CSV da pasta de relatórios."""

        self.pasta_relatorios.mkdir(
            parents=True,
            exist_ok=True,
        )

        for widget in (
            self.lista_relatorios.winfo_children()
        ):
            widget.destroy()

        self.botoes_relatorios = []

        caminhos = sorted(
            self.pasta_relatorios.glob(
                "cadastro_*.csv"
            ),
            key=lambda caminho: (
                caminho.stat().st_mtime
            ),
            reverse=True,
        )

        if not caminhos:
            label_vazio = ctk.CTkLabel(
                self.lista_relatorios,
                text=(
                    "Nenhum relatório encontrado.\n\n"
                    "Execute um cadastro para gerar "
                    "o primeiro relatório."
                ),
                justify="left",
                wraplength=245,
                text_color=COR_TEXTO_SECUNDARIO,
                font=ctk.CTkFont(
                    family=FONTE_PRINCIPAL,
                    size=TAMANHO_TEXTO,
                ),
            )
            label_vazio.grid(
                row=0,
                column=0,
                padx=8,
                pady=14,
                sticky="ew",
            )

            self.limpar_detalhes()
            return

        for indice, caminho in enumerate(
            caminhos
        ):
            texto = self.obter_texto_botao(
                caminho
            )

            botao = ctk.CTkButton(
                self.lista_relatorios,
                text=texto,
                height=58,
                corner_radius=4,
                anchor="w",
                fg_color=COR_FUNDO,
                hover_color="#E5E7EB",
                border_width=1,
                border_color=COR_BORDA,
                text_color=COR_TEXTO,
                font=ctk.CTkFont(
                    family=FONTE_PRINCIPAL,
                    size=TAMANHO_TEXTO,
                ),
                command=lambda arquivo=caminho: (
                    self.selecionar_relatorio(
                        arquivo
                    )
                ),
            )
            botao.grid(
                row=indice,
                column=0,
                padx=2,
                pady=(0, 7),
                sticky="ew",
            )
            self.botoes_relatorios.append(
                botao
            )

        destino_inicial = caminhos[0]

        if (
            self.caminho_atual is not None
            and self.caminho_atual in caminhos
        ):
            destino_inicial = self.caminho_atual

        self.selecionar_relatorio(
            destino_inicial
        )

    def obter_texto_botao(
        self,
        caminho: Path,
    ) -> str:
        """Monta o texto resumido do botão de relatório."""

        try:
            registros = self.ler_relatorio(
                caminho
            )
        except (
            OSError,
            csv.Error,
            UnicodeError,
        ):
            return (
                f"{caminho.name}\n"
                "Arquivo inválido ou indisponível"
            )

        if not registros:
            return (
                f"{caminho.name}\n"
                "Relatório vazio"
            )

        primeiro = registros[0]
        modo = self.formatar_modo(
            primeiro.get("modo", "")
        )
        resultado = self.formatar_resultado_geral(
            primeiro.get(
                "resultado_geral",
                "",
            )
        )
        inicio = primeiro.get(
            "inicio",
            "",
        )

        return (
            f"{inicio} • {modo}\n"
            f"{resultado} • {caminho.name}"
        )

    def selecionar_relatorio(
        self,
        caminho: Path,
    ) -> None:
        """Seleciona e exibe um relatório."""

        try:
            registros = self.ler_relatorio(
                caminho
            )

        except (
            OSError,
            csv.Error,
            UnicodeError,
        ) as erro:
            messagebox.showerror(
                "Erro ao abrir relatório",
                str(erro),
                parent=self,
            )
            return

        self.caminho_atual = caminho
        self.registros_atuais = registros
        self.seletor_filtro.set(
            FILTRO_TODOS
        )

        self.atualizar_resumo()
        self.aplicar_filtro(
            FILTRO_TODOS
        )

    def ler_relatorio(
        self,
        caminho: Path,
    ) -> list[dict[str, str]]:
        """Lê um relatório CSV."""

        with caminho.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as arquivo:
            leitor = csv.DictReader(
                arquivo,
                delimiter=";",
            )

            if not leitor.fieldnames:
                return []

            return [
                {
                    str(chave): (
                        valor
                        if valor is not None
                        else ""
                    )
                    for chave, valor in linha.items()
                }
                for linha in leitor
            ]

    def atualizar_resumo(self) -> None:
        """Atualiza os dados gerais do relatório."""

        if (
            self.caminho_atual is None
            or not self.registros_atuais
        ):
            self.limpar_detalhes()
            return

        primeiro = self.registros_atuais[0]

        self.label_nome_relatorio.configure(
            text=self.caminho_atual.name
        )
        self.label_modo_relatorio.configure(
            text=self.formatar_modo(
                primeiro.get("modo", "")
            )
        )
        self.label_resultado_relatorio.configure(
            text=self.formatar_resultado_geral(
                primeiro.get(
                    "resultado_geral",
                    "",
                )
            )
        )

        inicio = primeiro.get(
            "inicio",
            "—",
        )
        fim = primeiro.get(
            "fim",
            "—",
        )
        self.label_periodo_relatorio.configure(
            text=f"{inicio}\n{fim}"
        )

        salvos = sum(
            1
            for registro in self.registros_atuais
            if registro.get(
                "resultado_item"
            ) == "SALVO"
        )
        pulados = sum(
            1
            for registro in self.registros_atuais
            if registro.get(
                "resultado_item"
            ) == "PULADO_JA_CADASTRADO"
        )
        erros = (
            len(self.registros_atuais)
            - salvos
            - pulados
        )

        total_declarado = primeiro.get(
            "total_itens",
            str(len(self.registros_atuais)),
        )

        self.label_resumo_itens.configure(
            text=(
                f"Total: {total_declarado} | "
                f"Salvos: {salvos} | "
                f"Pulados: {pulados} | "
                f"Ocorrências: {erros}"
            )
        )

    def aplicar_filtro(
        self,
        filtro: str,
    ) -> None:
        """Filtra e exibe os itens na tabela."""

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        registros = [
            registro
            for registro in self.registros_atuais
            if self.registro_corresponde_filtro(
                registro,
                filtro,
            )
        ]

        for registro in registros:
            resultado_bruto = registro.get(
                "resultado_item",
                "",
            )

            self.tabela.insert(
                "",
                "end",
                values=(
                    registro.get("item", ""),
                    registro.get(
                        "referencia",
                        "",
                    ),
                    self.formatar_resultado_item(
                        resultado_bruto
                    ),
                    registro.get(
                        "descricao_final",
                        "",
                    ),
                    registro.get(
                        "detalhe",
                        "",
                    ),
                ),
            )

        self.label_status.configure(
            text=(
                f"{len(registros)} registro(s) exibido(s)."
            ),
            text_color=(
                COR_TEXTO_SECUNDARIO
                if registros
                else COR_ERRO_TEXTO
            ),
        )

    def registro_corresponde_filtro(
        self,
        registro: dict[str, str],
        filtro: str,
    ) -> bool:
        """Verifica se um registro pertence ao filtro."""

        resultado = registro.get(
            "resultado_item",
            "",
        )

        if filtro == FILTRO_SALVOS:
            return resultado == "SALVO"

        if filtro == FILTRO_PULADOS:
            return (
                resultado
                == "PULADO_JA_CADASTRADO"
            )

        if filtro == FILTRO_ERROS:
            return resultado not in {
                "SALVO",
                "PULADO_JA_CADASTRADO",
            }

        return True

    def limpar_detalhes(self) -> None:
        """Limpa os detalhes quando não há relatório."""

        self.caminho_atual = None
        self.registros_atuais = []

        for label in (
            self.label_nome_relatorio,
            self.label_modo_relatorio,
            self.label_resultado_relatorio,
            self.label_periodo_relatorio,
        ):
            label.configure(
                text="—"
            )

        self.label_resumo_itens.configure(
            text="Nenhum relatório selecionado"
        )

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        self.label_status.configure(
            text="Nenhum relatório disponível.",
            text_color=COR_TEXTO_SECUNDARIO,
        )

    def abrir_csv_atual(self) -> None:
        """Abre o relatório atualmente selecionado."""

        if self.caminho_atual is None:
            messagebox.showwarning(
                "Relatório necessário",
                "Selecione primeiro um relatório.",
                parent=self,
            )
            return

        self.abrir_caminho(
            self.caminho_atual
        )

    def abrir_pasta_relatorios(self) -> None:
        """Abre a pasta que contém os relatórios."""

        self.pasta_relatorios.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.abrir_caminho(
            self.pasta_relatorios
        )

    def abrir_caminho(
        self,
        caminho: Path,
    ) -> None:
        """Abre um arquivo ou pasta no sistema operacional."""

        try:
            if sys.platform.startswith("win"):
                os.startfile(caminho)  # type: ignore[attr-defined]

            elif sys.platform == "darwin":
                subprocess.Popen(
                    ["open", str(caminho)]
                )

            else:
                subprocess.Popen(
                    ["xdg-open", str(caminho)]
                )

        except OSError as erro:
            messagebox.showerror(
                "Não foi possível abrir",
                str(erro),
                parent=self,
            )

    @staticmethod
    def formatar_modo(
        modo: str,
    ) -> str:
        """Formata o modo de execução."""

        if modo.lower() == "automatico":
            return "Automático"

        if modo.lower() == "assistido":
            return "Assistido"

        return modo or "—"

    @staticmethod
    def formatar_resultado_geral(
        resultado: str,
    ) -> str:
        """Formata o resultado geral."""

        mapa = {
            "concluido": "Concluído",
            "erro": "Interrompido por erro",
            "interrompido": (
                "Interrompido pelo usuário"
            ),
        }

        return mapa.get(
            resultado.lower(),
            resultado or "—",
        )

    @staticmethod
    def formatar_resultado_item(
        resultado: str,
    ) -> str:
        """Formata o resultado de cada produto."""

        mapa = {
            "SALVO": "Salvo",
            "PULADO_JA_CADASTRADO": (
                "Já cadastrado"
            ),
            "LEITURA_INCERTA": "Leitura incerta",
            "ERRO_DETECCAO": "Erro na detecção",
            "ERRO_PREPARACAO": "Erro na preparação",
            "ERRO_SALVAMENTO": "Erro no salvamento",
            "ESTADO_DESCONHECIDO": (
                "Estado desconhecido"
            ),
            "INTERROMPIDO_PELO_USUARIO": (
                "Interrompido pelo usuário"
            ),
            "INTERROMPIDO_PELA_PROTECAO": (
                "Proteção acionada"
            ),
        }

        return mapa.get(
            resultado,
            resultado or "—",
        )
