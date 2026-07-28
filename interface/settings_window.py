from collections.abc import Callable
from tkinter import messagebox

import customtkinter as ctk

from database.settings_repository import (
    carregar_configuracoes,
    salvar_configuracoes,
)
from interface.styles import (
    COR_AZUL,
    COR_AZUL_HOVER,
    COR_BORDA,
    COR_FUNDO,
    COR_FUNDO_SECUNDARIO,
    COR_TEXTO,
    COR_TEXTO_BOTAO,
    COR_TEXTO_SECUNDARIO,
    FONTE_PRINCIPAL,
    TAMANHO_BOTAO,
    TAMANHO_SUBTITULO,
    TAMANHO_TEXTO,
    TAMANHO_TITULO,
)


class SettingsWindow(ctk.CTkToplevel):
    """Janela de configurações do motor de abreviação."""

    def __init__(
        self,
        master,
        ao_salvar: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master)

        self.ao_salvar = ao_salvar
        self.configuracoes = carregar_configuracoes()

        self.title("Configurações - ADM SmartCadastro")
        self.geometry("900x620")
        self.minsize(760, 520)
        self.configure(fg_color=COR_FUNDO)

        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.criar_cabecalho()
        self.criar_abas()
        self.criar_botoes()
        self.carregar_campos()

    def criar_cabecalho(self) -> None:
        cabecalho = ctk.CTkFrame(
            self,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        cabecalho.grid(
            row=0,
            column=0,
            padx=25,
            pady=(20, 10),
            sticky="ew",
        )

        titulo = ctk.CTkLabel(
            cabecalho,
            text="Configurações",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TITULO,
                weight="bold",
            ),
        )
        titulo.pack(anchor="w")

        subtitulo = ctk.CTkLabel(
            cabecalho,
            text=(
                "Edite as regras utilizadas para preparar "
                "as descrições dos produtos."
            ),
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_SUBTITULO,
            ),
        )
        subtitulo.pack(anchor="w", pady=(4, 0))

    def criar_abas(self) -> None:
        self.abas = ctk.CTkTabview(
            self,
            fg_color=COR_FUNDO_SECUNDARIO,
            segmented_button_fg_color="#E5E7EB",
            segmented_button_selected_color=COR_AZUL,
            segmented_button_selected_hover_color=COR_AZUL_HOVER,
            segmented_button_unselected_color="#E5E7EB",
            segmented_button_unselected_hover_color="#D1D5DB",
            text_color=COR_TEXTO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=4,
        )
        self.abas.grid(
            row=1,
            column=0,
            padx=25,
            pady=10,
            sticky="nsew",
        )

        nomes_abas = (
            "Palavras removidas",
            "Substituições",
            "Abreviações",
            "Tamanhos",
            "Cores",
        )

        for nome in nomes_abas:
            self.abas.add(nome)

        self.campo_palavras = self.criar_campo_texto(
            nome_aba="Palavras removidas",
            explicacao=(
                "Digite uma palavra por linha. Essas palavras serão "
                "retiradas da descrição."
            ),
        )

        self.campo_substituicoes = self.criar_campo_texto(
            nome_aba="Substituições",
            explicacao=(
                "Digite uma regra por linha usando o formato:\n"
                "EXPRESSÃO ORIGINAL = EXPRESSÃO FINAL"
            ),
        )

        self.campo_abreviacoes = self.criar_campo_texto(
            nome_aba="Abreviações",
            explicacao=(
                "Digite uma abreviação por linha usando o formato:\n"
                "PALAVRA ORIGINAL = ABREVIAÇÃO"
            ),
        )

        self.campo_tamanhos = self.criar_campo_texto(
            nome_aba="Tamanhos",
            explicacao=(
                "Digite um tamanho por linha. Esses valores serão "
                "mantidos nas descrições."
            ),
        )

        self.campo_cores = self.criar_campo_texto(
            nome_aba="Cores",
            explicacao=(
                "Digite uma cor principal por linha. O sistema manterá "
                "a cor e removerá sua variante posterior."
            ),
        )

    def criar_campo_texto(
        self,
        nome_aba: str,
        explicacao: str,
    ) -> ctk.CTkTextbox:
        aba = self.abas.tab(nome_aba)
        aba.configure(fg_color=COR_FUNDO_SECUNDARIO)

        aba.grid_columnconfigure(0, weight=1)
        aba.grid_rowconfigure(1, weight=1)

        label = ctk.CTkLabel(
            aba,
            text=explicacao,
            justify="left",
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        label.grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 10),
            sticky="ew",
        )

        campo = ctk.CTkTextbox(
            aba,
            fg_color=COR_FUNDO,
            text_color=COR_TEXTO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=3,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        campo.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )

        return campo

    def criar_botoes(self) -> None:
        area_botoes = ctk.CTkFrame(
            self,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        area_botoes.grid(
            row=2,
            column=0,
            padx=25,
            pady=(10, 20),
            sticky="ew",
        )
        area_botoes.grid_columnconfigure(0, weight=1)

        botao_cancelar = ctk.CTkButton(
            area_botoes,
            text="Cancelar",
            width=120,
            height=38,
            corner_radius=4,
            fg_color=COR_FUNDO,
            hover_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
            ),
            command=self.destroy,
        )
        botao_cancelar.grid(
            row=0,
            column=1,
            padx=(0, 10),
        )

        botao_salvar = ctk.CTkButton(
            area_botoes,
            text="Salvar configurações",
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
            command=self.salvar,
        )
        botao_salvar.grid(
            row=0,
            column=2,
        )

    def carregar_campos(self) -> None:
        self.inserir_lista(
            self.campo_palavras,
            self.configuracoes["palavras_removidas"],
        )

        self.inserir_mapeamento(
            self.campo_substituicoes,
            self.configuracoes["substituicoes_expressoes"],
        )

        self.inserir_mapeamento(
            self.campo_abreviacoes,
            self.configuracoes["abreviacoes"],
        )

        self.inserir_lista(
            self.campo_tamanhos,
            self.configuracoes["tamanhos_validos"],
        )

        self.inserir_lista(
            self.campo_cores,
            self.configuracoes["cores_base"],
        )

    @staticmethod
    def inserir_lista(
        campo: ctk.CTkTextbox,
        valores: list[str],
    ) -> None:
        campo.delete("1.0", "end")
        campo.insert("1.0", "\n".join(valores))

    @staticmethod
    def inserir_mapeamento(
        campo: ctk.CTkTextbox,
        valores: dict[str, str],
    ) -> None:
        linhas = [
            f"{original} = {resultado}"
            for original, resultado in valores.items()
        ]

        campo.delete("1.0", "end")
        campo.insert("1.0", "\n".join(linhas))

    @staticmethod
    def ler_lista(
        campo: ctk.CTkTextbox,
    ) -> list[str]:
        texto = campo.get("1.0", "end")

        valores = []

        for linha in texto.splitlines():
            valor = " ".join(linha.upper().split())

            if valor and valor not in valores:
                valores.append(valor)

        return valores

    @staticmethod
    def ler_mapeamento(
        campo: ctk.CTkTextbox,
        nome_configuracao: str,
    ) -> dict[str, str]:
        texto = campo.get("1.0", "end")
        resultado: dict[str, str] = {}

        for numero_linha, linha in enumerate(
            texto.splitlines(),
            start=1,
        ):
            linha = linha.strip()

            if not linha:
                continue

            if "=" not in linha:
                raise ValueError(
                    f'Erro em "{nome_configuracao}", linha '
                    f"{numero_linha}: use o símbolo =."
                )

            original, substituicao = linha.split("=", 1)

            original = " ".join(
                original.upper().split()
            )
            substituicao = " ".join(
                substituicao.upper().split()
            )

            if not original or not substituicao:
                raise ValueError(
                    f'Erro em "{nome_configuracao}", linha '
                    f"{numero_linha}: informe os dois lados da regra."
                )

            resultado[original] = substituicao

        return resultado

    def salvar(self) -> None:
        try:
            configuracoes = {
                "palavras_removidas": self.ler_lista(
                    self.campo_palavras
                ),
                "substituicoes_expressoes": self.ler_mapeamento(
                    self.campo_substituicoes,
                    "Substituições",
                ),
                "abreviacoes": self.ler_mapeamento(
                    self.campo_abreviacoes,
                    "Abreviações",
                ),
                "tamanhos_validos": self.ler_lista(
                    self.campo_tamanhos
                ),
                "cores_base": self.ler_lista(
                    self.campo_cores
                ),
            }

            salvar_configuracoes(configuracoes)

        except ValueError as erro:
            messagebox.showerror(
                "Configuração inválida",
                str(erro),
                parent=self,
            )
            return

        if self.ao_salvar is not None:
            self.ao_salvar()

        messagebox.showinfo(
            "Configurações salvas",
            "As configurações foram atualizadas com sucesso.",
            parent=self,
        )

        self.destroy()