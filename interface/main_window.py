from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk


# Aparência geral do sistema
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    """Janela principal do ADM SmartCadastro."""

    def __init__(self) -> None:
        super().__init__()

        self.title("ADM SmartCadastro")
        self.geometry("1000x650")
        self.minsize(850, 550)
        self.configure(fg_color="#FFFFFF")

        self.arquivo_xml: Path | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.criar_cabecalho()
        self.criar_conteudo()

    def criar_cabecalho(self) -> None:
        cabecalho = ctk.CTkFrame(
            self,
            height=95,
            corner_radius=0,
            fg_color="#FFFFFF",
            border_width=0,
        )
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            cabecalho,
            text="ADM SmartCadastro",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#1F2937",
        )
        titulo.grid(row=0, column=0, padx=30, pady=(20, 3))

        subtitulo = ctk.CTkLabel(
            cabecalho,
            text="Cadastro inteligente de produtos",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280",
        )
        subtitulo.grid(row=1, column=0, padx=30, pady=(0, 15))

        separador = ctk.CTkFrame(
            self,
            height=1,
            corner_radius=0,
            fg_color="#D1D5DB",
        )
        separador.grid(row=0, column=0, sticky="sew")

    def criar_conteudo(self) -> None:
        conteudo = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
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
            fg_color="#FFFFFF",
            corner_radius=0,
        )
        area_selecao.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        area_selecao.grid_columnconfigure(1, weight=1)

        botao_xml = ctk.CTkButton(
            area_selecao,
            text="Selecionar XML",
            width=160,
            height=38,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.selecionar_xml,
        )
        botao_xml.grid(row=0, column=0, padx=(0, 15))

        self.label_arquivo = ctk.CTkLabel(
            area_selecao,
            text="Nenhum arquivo selecionado",
            anchor="w",
            text_color="#6B7280",
            font=ctk.CTkFont(size=13),
        )
        self.label_arquivo.grid(row=0, column=1, sticky="ew")

        self.label_quantidade = ctk.CTkLabel(
            conteudo,
            text="Produtos encontrados: 0",
            anchor="w",
            text_color="#1F2937",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.label_quantidade.grid(
            row=2,
            column=0,
            pady=(0, 10),
            sticky="ew",
        )

        area_produtos = ctk.CTkFrame(
            conteudo,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=3,
        )
        area_produtos.grid(
            row=3,
            column=0,
            sticky="nsew",
        )

        mensagem = ctk.CTkLabel(
            area_produtos,
            text="Selecione um XML para visualizar os produtos.",
            text_color="#6B7280",
            font=ctk.CTkFont(size=14),
        )
        mensagem.place(relx=0.5, rely=0.5, anchor="center")

        area_botoes = ctk.CTkFrame(
            conteudo,
            fg_color="#FFFFFF",
            corner_radius=0,
        )
        area_botoes.grid(row=4, column=0, pady=(20, 0), sticky="ew")
        area_botoes.grid_columnconfigure(1, weight=1)

        botao_configuracoes = ctk.CTkButton(
            area_botoes,
            text="Configurações",
            width=140,
            height=38,
            corner_radius=4,
            fg_color="#FFFFFF",
            hover_color="#F3F4F6",
            border_width=1,
            border_color="#9CA3AF",
            text_color="#374151",
        )
        botao_configuracoes.grid(row=0, column=0, sticky="w")

        self.botao_iniciar = ctk.CTkButton(
            area_botoes,
            text="Iniciar Cadastro",
            width=165,
            height=38,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled",
        )
        self.botao_iniciar.grid(row=0, column=2, sticky="e")

    def selecionar_xml(self) -> None:
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

        self.label_arquivo.configure(
            text=f"Arquivo: {self.arquivo_xml.name}",
            text_color="#374151",
        )