from tkinter import messagebox

import customtkinter as ctk
import pyautogui

from automation.calibration_repository import (
    carregar_calibracao,
    salvar_calibracao,
)


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2


PONTOS = {
    "mais_primeira_linha": {
        "titulo": "Botão + da primeira linha",
        "instrucao": (
            "Posicione o mouse no centro do + verde "
            "da primeira linha."
        ),
    },

    "mais_segunda_linha": {
        "titulo": "Botão + da segunda linha",
        "instrucao": (
            "Posicione o mouse no centro do + verde "
            "da segunda linha."
        ),
    },

    "limite_inferior_tabela": {
        "titulo": "Limite inferior da tabela",
        "instrucao": (
            "Na coluna dos botões +, posicione o mouse "
            "próximo ao fim da área da tabela, imediatamente "
            "antes da barra inferior do ADM."
        ),
    },

    "aba_tributacao": {
        "titulo": "Aba Tributação",
        "instrucao": (
            "Abra o Cadastro de Produtos e posicione "
            "o mouse no centro da aba Tributação."
        ),
    },

    "botao_salvar": {
        "titulo": "Botão Salvar",
        "instrucao": (
            "Com o Cadastro de Produtos aberto, posicione "
            "o mouse no centro do botão Salvar."
        ),
    },
}


class CalibrationWindow(ctk.CTk):
    """Ferramenta segura de calibração do ADM."""

    def __init__(self) -> None:
        super().__init__()

        self.title(
            "Calibração - ADM SmartCadastro"
        )
        self.geometry("840x610")
        self.minsize(760, 560)

        self.configure(
            fg_color="#FFFFFF"
        )

        dados = carregar_calibracao()

        self.pontos: dict[
            str,
            dict[str, int],
        ] = dados.get(
            "pontos",
            {},
        )

        self.labels_coordenadas: dict[
            str,
            ctk.CTkLabel,
        ] = {}

        self.status = None
        self.chave_em_captura: str | None = None

        self.grid_columnconfigure(
            0,
            weight=1,
        )
        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self.criar_cabecalho()
        self.criar_lista_pontos()
        self.criar_rodape()

    def criar_cabecalho(self) -> None:
        """Cria o cabeçalho."""

        frame = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
        )
        frame.grid(
            row=0,
            column=0,
            padx=25,
            pady=(20, 10),
            sticky="ew",
        )

        titulo = ctk.CTkLabel(
            frame,
            text="Calibração da automação",
            anchor="w",
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=25,
                weight="bold",
            ),
        )
        titulo.pack(
            anchor="w"
        )

        explicacao = ctk.CTkLabel(
            frame,
            text=(
                "Clique em Capturar, aguarde a janela desaparecer "
                "e coloque o mouse sobre o ponto indicado. "
                "A posição será registrada após 4 segundos.\n\n"
                "Nenhum clique será realizado no ADM."
            ),
            justify="left",
            anchor="w",
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
            ),
        )
        explicacao.pack(
            anchor="w",
            pady=(6, 0),
        )

    def criar_lista_pontos(self) -> None:
        """Cria a área com os pontos de calibração."""

        frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#F3F4F6",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=4,
        )
        frame.grid(
            row=1,
            column=0,
            padx=25,
            pady=10,
            sticky="nsew",
        )

        frame.grid_columnconfigure(
            0,
            weight=1,
        )

        for indice, (
            chave,
            informacoes,
        ) in enumerate(PONTOS.items()):
            self.criar_linha_ponto(
                frame=frame,
                linha=indice,
                chave=chave,
                titulo=informacoes["titulo"],
                instrucao=informacoes["instrucao"],
            )

    def criar_linha_ponto(
        self,
        frame,
        linha: int,
        chave: str,
        titulo: str,
        instrucao: str,
    ) -> None:
        """Cria uma linha de calibração."""

        item = ctk.CTkFrame(
            frame,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=4,
        )
        item.grid(
            row=linha,
            column=0,
            padx=8,
            pady=6,
            sticky="ew",
        )

        item.grid_columnconfigure(
            0,
            weight=1,
        )

        label_titulo = ctk.CTkLabel(
            item,
            text=titulo,
            anchor="w",
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
        )
        label_titulo.grid(
            row=0,
            column=0,
            padx=14,
            pady=(12, 2),
            sticky="ew",
        )

        label_instrucao = ctk.CTkLabel(
            item,
            text=instrucao,
            anchor="w",
            justify="left",
            wraplength=460,
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        label_instrucao.grid(
            row=1,
            column=0,
            padx=14,
            pady=(0, 12),
            sticky="ew",
        )

        label_coordenada = ctk.CTkLabel(
            item,
            text=self.formatar_coordenada(
                chave
            ),
            width=105,
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
            ),
        )
        label_coordenada.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=8,
        )

        botao_capturar = ctk.CTkButton(
            item,
            text="Capturar",
            width=95,
            height=34,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
            command=lambda ponto=chave: (
                self.iniciar_captura(ponto)
            ),
        )
        botao_capturar.grid(
            row=0,
            column=2,
            rowspan=2,
            padx=(4, 6),
        )

        botao_testar = ctk.CTkButton(
            item,
            text="Testar",
            width=80,
            height=34,
            corner_radius=4,
            fg_color="#FFFFFF",
            hover_color="#E5E7EB",
            border_width=1,
            border_color="#9CA3AF",
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
            ),
            command=lambda ponto=chave: (
                self.testar_ponto(ponto)
            ),
        )
        botao_testar.grid(
            row=0,
            column=3,
            rowspan=2,
            padx=(0, 12),
        )

        self.labels_coordenadas[
            chave
        ] = label_coordenada

    def criar_rodape(self) -> None:
        """Cria o rodapé e o botão de salvar."""

        frame = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
        )
        frame.grid(
            row=2,
            column=0,
            padx=25,
            pady=(10, 20),
            sticky="ew",
        )

        frame.grid_columnconfigure(
            0,
            weight=1,
        )

        self.status = ctk.CTkLabel(
            frame,
            text=(
                "Mova o mouse para o canto superior esquerdo "
                "da tela para interromper movimentos do PyAutoGUI."
            ),
            anchor="w",
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        self.status.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        botao_salvar = ctk.CTkButton(
            frame,
            text="Salvar calibração",
            width=170,
            height=38,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
            command=self.salvar,
        )
        botao_salvar.grid(
            row=0,
            column=1,
        )

    def formatar_coordenada(
        self,
        chave: str,
    ) -> str:
        """Formata a coordenada apresentada na tela."""

        ponto = self.pontos.get(
            chave
        )

        if not ponto:
            return "Não capturado"

        return (
            f'X: {ponto["x"]}\n'
            f'Y: {ponto["y"]}'
        )

    def iniciar_captura(
        self,
        chave: str,
    ) -> None:
        """Inicia a captura com quatro segundos de espera."""

        self.chave_em_captura = chave

        titulo = PONTOS[
            chave
        ]["titulo"]

        self.status.configure(
            text=(
                f'Capturando "{titulo}". '
                "Coloque o mouse no ponto indicado."
            ),
            text_color="#2563EB",
        )

        self.after(
            500,
            self.ocultar_para_captura,
        )

    def ocultar_para_captura(self) -> None:
        """Esconde a janela durante a captura."""

        self.withdraw()

        self.after(
            4000,
            self.finalizar_captura,
        )

    def finalizar_captura(self) -> None:
        """Registra a posição atual do mouse."""

        posicao = pyautogui.position()

        chave = self.chave_em_captura

        if chave is not None:
            self.pontos[chave] = {
                "x": int(posicao.x),
                "y": int(posicao.y),
            }

            self.labels_coordenadas[
                chave
            ].configure(
                text=self.formatar_coordenada(
                    chave
                )
            )

        self.deiconify()
        self.lift()
        self.focus_force()

        self.status.configure(
            text=(
                f"Posição registrada: "
                f"X {posicao.x}, Y {posicao.y}."
            ),
            text_color="#1F2937",
        )

        self.chave_em_captura = None

    def testar_ponto(
        self,
        chave: str,
    ) -> None:
        """Move o mouse até o ponto sem clicar."""

        ponto = self.pontos.get(
            chave
        )

        if not ponto:
            messagebox.showwarning(
                "Ponto não capturado",
                "Capture esse ponto antes de testá-lo.",
                parent=self,
            )
            return

        try:
            pyautogui.moveTo(
                ponto["x"],
                ponto["y"],
                duration=0.7,
            )

        except pyautogui.FailSafeException:
            messagebox.showwarning(
                "Movimento interrompido",
                "O movimento foi interrompido pela proteção.",
                parent=self,
            )

    def salvar(self) -> None:
        """Salva a calibração no arquivo JSON."""

        try:
            dados = salvar_calibracao(
                self.pontos
            )

        except (
            ValueError,
            OSError,
        ) as erro:
            messagebox.showerror(
                "Não foi possível salvar",
                str(erro),
                parent=self,
            )
            return

        calculos = dados["calculos"]

        messagebox.showinfo(
            "Calibração salva",
            (
                "Calibração salva com sucesso.\n\n"
                f'Altura estimada da linha: '
                f'{calculos["altura_linha"]} pixels\n'
                f'Linhas visíveis estimadas: '
                f'{calculos["linhas_visiveis_estimadas"]}'
            ),
            parent=self,
        )


def main() -> None:
    ctk.set_appearance_mode(
        "light"
    )

    ctk.set_default_color_theme(
        "blue"
    )

    app = CalibrationWindow()
    app.mainloop()


if __name__ == "__main__":
    main()