from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from automation.cadastro_assistido import (
    CadastroAssistido,
)
from interface.product_table import ProductTable
from interface.settings_window import SettingsWindow
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
from services.preparacao_produtos import preparar_produtos
from xml_reader.nfe_reader import ler_produtos_xml


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    """Janela principal do ADM SmartCadastro."""

    def __init__(self) -> None:
        super().__init__()

        self.title("ADM SmartCadastro")
        self.geometry("1000x650")
        self.minsize(850, 550)
        self.configure(fg_color=COR_FUNDO)

        self.arquivo_xml: Path | None = None
        self.produtos = []

        self.janela_configuracoes: (
            SettingsWindow | None
        ) = None

        self.controlador_cadastro: (
            CadastroAssistido | None
        ) = None
        self.cadastro_em_andamento = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.criar_cabecalho()
        self.criar_conteudo()

    def criar_cabecalho(self) -> None:
        """Cria o cabeçalho principal."""

        cabecalho = ctk.CTkFrame(
            self,
            height=95,
            corner_radius=0,
            fg_color=COR_FUNDO,
            border_width=0,
        )
        cabecalho.grid(
            row=0,
            column=0,
            sticky="ew",
        )
        cabecalho.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            cabecalho,
            text="ADM SmartCadastro",
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TITULO,
                weight="bold",
            ),
            text_color=COR_TEXTO,
        )
        titulo.grid(
            row=0,
            column=0,
            padx=30,
            pady=(20, 3),
        )

        subtitulo = ctk.CTkLabel(
            cabecalho,
            text="Cadastro inteligente de produtos",
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_SUBTITULO,
            ),
            text_color=COR_TEXTO_SECUNDARIO,
        )
        subtitulo.grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
        )

        separador = ctk.CTkFrame(
            self,
            height=1,
            corner_radius=0,
            fg_color=COR_BORDA,
        )
        separador.grid(
            row=0,
            column=0,
            sticky="sew",
        )

    def criar_conteudo(self) -> None:
        """Cria o conteúdo principal."""

        conteudo = ctk.CTkFrame(
            self,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        conteudo.grid(
            row=1,
            column=0,
            padx=30,
            pady=25,
            sticky="nsew",
        )

        conteudo.grid_columnconfigure(0, weight=1)
        conteudo.grid_rowconfigure(3, weight=1)

        area_selecao = ctk.CTkFrame(
            conteudo,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        area_selecao.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 20),
        )
        area_selecao.grid_columnconfigure(1, weight=1)

        botao_xml = ctk.CTkButton(
            area_selecao,
            text="Selecionar XML",
            width=160,
            height=38,
            corner_radius=4,
            fg_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            text_color=COR_TEXTO_BOTAO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
                weight="bold",
            ),
            command=self.selecionar_xml,
        )
        botao_xml.grid(
            row=0,
            column=0,
            padx=(0, 15),
        )

        self.label_arquivo = ctk.CTkLabel(
            area_selecao,
            text="Nenhum arquivo selecionado",
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        self.label_arquivo.grid(
            row=0,
            column=1,
            sticky="ew",
        )

        self.label_quantidade = ctk.CTkLabel(
            conteudo,
            text="Produtos encontrados: 0",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO_DESTAQUE,
                weight="bold",
            ),
        )
        self.label_quantidade.grid(
            row=2,
            column=0,
            pady=(0, 10),
            sticky="ew",
        )

        self.tabela_produtos = ProductTable(
            conteudo,
            ao_alterar_regras=(
                self.atualizar_produtos_apos_configuracao
            ),
            ao_atualizar_validacao=(
                self.atualizar_estado_botao
            ),
        )
        self.tabela_produtos.grid(
            row=3,
            column=0,
            sticky="nsew",
        )

        area_botoes = ctk.CTkFrame(
            conteudo,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        area_botoes.grid(
            row=4,
            column=0,
            pady=(20, 0),
            sticky="ew",
        )
        area_botoes.grid_columnconfigure(1, weight=1)

        botao_configuracoes = ctk.CTkButton(
            area_botoes,
            text="Configurações",
            width=140,
            height=38,
            corner_radius=4,
            fg_color=COR_FUNDO,
            hover_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA_ESCURA,
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
            ),
            command=self.abrir_configuracoes,
        )
        botao_configuracoes.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.botao_iniciar = ctk.CTkButton(
            area_botoes,
            text="Iniciar Cadastro",
            width=180,
            height=38,
            corner_radius=4,
            fg_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            text_color=COR_TEXTO_BOTAO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
                weight="bold",
            ),
            state="disabled",
            command=self.iniciar_cadastro,
        )
        self.botao_iniciar.grid(
            row=0,
            column=2,
            sticky="e",
        )

    def selecionar_xml(self) -> None:
        """Seleciona e processa o XML."""

        if self.cadastro_em_andamento:
            return

        caminho = filedialog.askopenfilename(
            title="Selecionar XML da nota fiscal",
            filetypes=[
                ("Arquivos XML", "*.xml"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not caminho:
            return

        self.arquivo_xml = Path(caminho)

        try:
            self.produtos = ler_produtos_xml(
                self.arquivo_xml
            )

            preparar_produtos(
                self.produtos
            )

        except (
            ValueError,
            FileNotFoundError,
            OSError,
        ) as erro:
            self.produtos = []
            self.tabela_produtos.limpar()

            self.label_quantidade.configure(
                text="Produtos encontrados: 0",
                text_color=COR_TEXTO,
            )

            self.label_arquivo.configure(
                text="Nenhum arquivo selecionado",
                text_color=COR_TEXTO_SECUNDARIO,
            )

            self.botao_iniciar.configure(
                state="disabled"
            )

            messagebox.showerror(
                "Erro ao ler XML",
                str(erro),
                parent=self,
            )
            return

        quantidade = len(self.produtos)

        self.label_arquivo.configure(
            text=f"Arquivo: {self.arquivo_xml.name}",
            text_color=COR_TEXTO,
        )

        self.label_quantidade.configure(
            text=f"Produtos encontrados: {quantidade}",
            text_color=COR_TEXTO,
        )

        self.tabela_produtos.carregar_produtos(
            self.produtos
        )

    def abrir_configuracoes(self) -> None:
        """Abre a janela de configurações."""

        if self.cadastro_em_andamento:
            return

        if (
            self.janela_configuracoes is not None
            and self.janela_configuracoes.winfo_exists()
        ):
            self.janela_configuracoes.focus()
            return

        self.janela_configuracoes = SettingsWindow(
            master=self,
            ao_salvar=(
                self.atualizar_produtos_apos_configuracao
            ),
        )

    def atualizar_produtos_apos_configuracao(
        self,
    ) -> None:
        """Reprocessa os produtos após alterar regras."""

        if (
            not self.produtos
            or self.cadastro_em_andamento
        ):
            return

        preparar_produtos(
            self.produtos
        )

        self.tabela_produtos.carregar_produtos(
            self.produtos
        )

    def atualizar_estado_botao(self) -> None:
        """Habilita ou bloqueia o início do cadastro."""

        if self.cadastro_em_andamento:
            self.botao_iniciar.configure(
                state="disabled",
                text="Cadastro em andamento...",
            )
            return

        quantidade = len(self.produtos)

        if quantidade == 0:
            self.label_quantidade.configure(
                text="Produtos encontrados: 0",
                text_color=COR_TEXTO,
            )

            self.botao_iniciar.configure(
                state="disabled",
                text="Iniciar Cadastro",
            )
            return

        invalidas = (
            self.tabela_produtos
            .contar_descricoes_invalidas()
        )

        limite = (
            self.tabela_produtos
            .obter_limite_descricao()
        )

        if invalidas > 0:
            self.label_quantidade.configure(
                text=(
                    f"Produtos encontrados: {quantidade} | "
                    f"Acima de {limite} caracteres: {invalidas}"
                ),
                text_color=COR_ERRO_TEXTO,
            )

            self.botao_iniciar.configure(
                state="disabled",
                text="Iniciar Cadastro",
            )
            return

        self.label_quantidade.configure(
            text=(
                f"Produtos encontrados: {quantidade} | "
                "Descrições válidas"
            ),
            text_color=COR_TEXTO,
        )

        self.botao_iniciar.configure(
            state="normal",
            text="Iniciar Cadastro",
        )

    def iniciar_cadastro(self) -> None:
        """Inicia o cadastro assistido no ADM."""

        if self.cadastro_em_andamento:
            return

        if not self.produtos:
            messagebox.showwarning(
                "Produtos necessários",
                "Selecione primeiro o XML da nota.",
                parent=self,
            )
            return

        invalidas = (
            self.tabela_produtos
            .contar_descricoes_invalidas()
        )

        if invalidas > 0:
            messagebox.showwarning(
                "Descrições inválidas",
                (
                    "Corrija as descrições destacadas "
                    "antes de iniciar."
                ),
                parent=self,
            )
            return

        controlador = CadastroAssistido(
            master=self,
            produtos=self.produtos,
            ao_atualizar_status=(
                self.atualizar_status_cadastro
            ),
            ao_encerrar=(
                self.encerrar_cadastro
            ),
        )

        iniciado = controlador.iniciar()

        if not iniciado:
            return

        self.controlador_cadastro = controlador
        self.cadastro_em_andamento = True

        self.botao_iniciar.configure(
            state="disabled",
            text="Cadastro em andamento...",
        )

    def atualizar_status_cadastro(
        self,
        texto: str,
        cor: str,
    ) -> None:
        """Exibe o andamento do cadastro na interface."""

        self.label_quantidade.configure(
            text=texto,
            text_color=cor,
        )
        self.update_idletasks()

    def encerrar_cadastro(
        self,
        resultado: str,
        resumo: dict,
    ) -> None:
        """Restaura a interface ao terminar o processo."""

        self.cadastro_em_andamento = False
        self.controlador_cadastro = None

        self.botao_iniciar.configure(
            text="Iniciar Cadastro",
        )

        if resultado == "concluido":
            self.label_quantidade.configure(
                text=(
                    "Cadastro concluído | "
                    f"Salvos: {resumo['salvos']} | "
                    f"Já cadastrados: {resumo['pulados']}"
                ),
                text_color="#166534",
            )

        elif resultado == "interrompido":
            self.label_quantidade.configure(
                text=(
                    "Cadastro interrompido pelo usuário. "
                    "O produto atual não foi salvo."
                ),
                text_color="#B45309",
            )

        else:
            self.label_quantidade.configure(
                text=(
                    "Cadastro interrompido por erro. "
                    "Confira a mensagem apresentada."
                ),
                text_color=COR_ERRO_TEXTO,
            )

        invalidas = (
            self.tabela_produtos
            .contar_descricoes_invalidas()
        )

        if self.produtos and invalidas == 0:
            self.botao_iniciar.configure(
                state="normal"
            )
        else:
            self.botao_iniciar.configure(
                state="disabled"
            )
