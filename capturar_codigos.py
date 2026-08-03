import json
from time import sleep
from tkinter import messagebox

import customtkinter as ctk
import pyautogui

from automation.calibration_repository import (
    CAMINHO_CALIBRACAO,
    carregar_calibracao,
)
from services.app_paths import PASTA_TEMPLATES


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


LARGURA_CAPTURA = 36
ALTURA_CAPTURA = 14

PASTA_CAPTURAS = PASTA_TEMPLATES

ARQUIVOS = {
    "preenchido": (
        PASTA_CAPTURAS
        / "codigo_preenchido.png"
    ),
    "vazio": (
        PASTA_CAPTURAS
        / "codigo_vazio.png"
    ),
}


class CodeCaptureWindow(ctk.CTk):
    """Captura células selecionadas da coluna Código."""

    def __init__(self) -> None:
        super().__init__()

        self.title(
            "Captura da Coluna Código"
        )
        self.geometry(
            "700x520"
        )
        self.resizable(
            False,
            False,
        )
        self.configure(
            fg_color="#FFFFFF"
        )

        PASTA_CAPTURAS.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.capturas: dict[
            str,
            dict[str, int | str],
        ] = {}

        self.tipo_em_captura: str | None = None

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.criar_interface()

    def criar_interface(self) -> None:
        """Cria a interface."""

        titulo = ctk.CTkLabel(
            self,
            text="Calibração da coluna Código",
            anchor="w",
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=24,
                weight="bold",
            ),
        )
        titulo.grid(
            row=0,
            column=0,
            padx=30,
            pady=(28, 6),
            sticky="ew",
        )

        explicacao = ctk.CTkLabel(
            self,
            text=(
                "O programa capturará uma célula preenchida "
                "e uma célula vazia.\n\n"
                "Depois de clicar em Capturar, posicione o mouse "
                "no centro da célula Código. O programa dará um "
                "único clique para selecionar a linha e fará "
                "a captura automaticamente."
            ),
            anchor="w",
            justify="left",
            wraplength=630,
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
            ),
        )
        explicacao.grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="ew",
        )

        self.criar_cartao(
            linha=2,
            tipo="preenchido",
            titulo="Código preenchido",
            descricao=(
                "Use o item 1. Posicione o mouse no centro "
                "da célula da coluna Código que contém o número."
            ),
        )

        self.criar_cartao(
            linha=3,
            tipo="vazio",
            titulo="Código vazio",
            descricao=(
                "Use o item 4. Posicione o mouse exatamente "
                "na mesma coluna, dentro da célula vazia."
            ),
        )

        self.label_status = ctk.CTkLabel(
            self,
            text="Nenhuma captura realizada.",
            anchor="w",
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        self.label_status.grid(
            row=4,
            column=0,
            padx=30,
            pady=(18, 12),
            sticky="ew",
        )

        botao_salvar = ctk.CTkButton(
            self,
            text="Salvar calibração dos códigos",
            height=42,
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
            row=5,
            column=0,
            padx=30,
            sticky="ew",
        )

        aviso = ctk.CTkLabel(
            self,
            text=(
                "Não clique no ADM durante a contagem. "
                "A seleção será feita automaticamente."
            ),
            text_color="#B45309",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        aviso.grid(
            row=6,
            column=0,
            padx=30,
            pady=(15, 20),
        )

    def criar_cartao(
        self,
        linha: int,
        tipo: str,
        titulo: str,
        descricao: str,
    ) -> None:
        """Cria um cartão de captura."""

        frame = ctk.CTkFrame(
            self,
            fg_color="#F3F4F6",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=4,
        )
        frame.grid(
            row=linha,
            column=0,
            padx=30,
            pady=6,
            sticky="ew",
        )

        frame.grid_columnconfigure(
            0,
            weight=1,
        )

        label_titulo = ctk.CTkLabel(
            frame,
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
            padx=16,
            pady=(13, 3),
            sticky="ew",
        )

        label_descricao = ctk.CTkLabel(
            frame,
            text=descricao,
            anchor="w",
            justify="left",
            wraplength=450,
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        label_descricao.grid(
            row=1,
            column=0,
            padx=16,
            pady=(0, 13),
            sticky="ew",
        )

        label_resultado = ctk.CTkLabel(
            frame,
            text="Não capturado",
            width=105,
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        label_resultado.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=8,
        )

        botao = ctk.CTkButton(
            frame,
            text="Capturar",
            width=105,
            height=36,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
            command=lambda: self.iniciar_captura(
                tipo
            ),
        )
        botao.grid(
            row=0,
            column=2,
            rowspan=2,
            padx=(4, 15),
        )

        if tipo == "preenchido":
            self.label_preenchido = (
                label_resultado
            )
        else:
            self.label_vazio = (
                label_resultado
            )

    def iniciar_captura(
        self,
        tipo: str,
    ) -> None:
        """Inicia a contagem para captura."""

        self.tipo_em_captura = tipo

        nome = (
            "código preenchido"
            if tipo == "preenchido"
            else "código vazio"
        )

        self.label_status.configure(
            text=(
                f"Preparando captura do {nome}..."
            ),
            text_color="#2563EB",
        )

        self.after(
            300,
            self.ocultar_para_captura,
        )

    def ocultar_para_captura(self) -> None:
        """Esconde a janela."""

        self.withdraw()

        self.after(
            4000,
            self.finalizar_captura,
        )

    def finalizar_captura(self) -> None:
        """Seleciona a célula e realiza a captura."""

        tipo = self.tipo_em_captura

        if tipo is None:
            self.deiconify()
            return

        posicao = pyautogui.position()

        # O clique garante que o ADM e a linha estejam
        # no mesmo estado visual usado pelo detector.
        pyautogui.click(
            x=posicao.x,
            y=posicao.y,
            duration=0.15,
        )

        sleep(0.6)

        tamanho_tela = pyautogui.size()

        esquerda = max(
            0,
            posicao.x - LARGURA_CAPTURA // 2,
        )

        topo = max(
            0,
            posicao.y - ALTURA_CAPTURA // 2,
        )

        if (
            esquerda + LARGURA_CAPTURA
            > tamanho_tela.width
        ):
            esquerda = (
                tamanho_tela.width
                - LARGURA_CAPTURA
            )

        if (
            topo + ALTURA_CAPTURA
            > tamanho_tela.height
        ):
            topo = (
                tamanho_tela.height
                - ALTURA_CAPTURA
            )

        imagem = pyautogui.screenshot(
            region=(
                esquerda,
                topo,
                LARGURA_CAPTURA,
                ALTURA_CAPTURA,
            )
        )

        caminho = ARQUIVOS[tipo]

        imagem.save(
            caminho
        )

        self.capturas[tipo] = {
            "x": int(posicao.x),
            "y": int(posicao.y),
            "arquivo": caminho.as_posix(),
        }

        label = (
            self.label_preenchido
            if tipo == "preenchido"
            else self.label_vazio
        )

        label.configure(
            text=(
                f"X: {posicao.x}\n"
                f"Y: {posicao.y}"
            ),
            text_color="#166534",
        )

        self.deiconify()
        self.lift()
        self.focus_force()

        self.label_status.configure(
            text=(
                f"Captura salva: {caminho.name}"
            ),
            text_color="#166534",
        )

        self.tipo_em_captura = None

    def salvar(self) -> None:
        """Salva a calibração."""

        if "preenchido" not in self.capturas:
            messagebox.showwarning(
                "Captura necessária",
                "Capture o código preenchido.",
                parent=self,
            )
            return

        if "vazio" not in self.capturas:
            messagebox.showwarning(
                "Captura necessária",
                "Capture o código vazio.",
                parent=self,
            )
            return

        preenchido = self.capturas[
            "preenchido"
        ]

        vazio = self.capturas[
            "vazio"
        ]

        diferenca_x = abs(
            int(preenchido["x"])
            - int(vazio["x"])
        )

        if diferenca_x > 10:
            messagebox.showwarning(
                "Posições diferentes",
                (
                    "As capturas não estão na mesma "
                    "posição horizontal.\n\n"
                    "Capture novamente usando exatamente "
                    "a mesma coluna."
                ),
                parent=self,
            )
            return

        dados = carregar_calibracao()

        dados["codigo_produto"] = {
            "coluna_x": round(
                (
                    int(preenchido["x"])
                    + int(vazio["x"])
                )
                / 2
            ),
            "largura_captura": (
                LARGURA_CAPTURA
            ),
            "altura_captura": (
                ALTURA_CAPTURA
            ),
            "template_preenchido": (
                "codigo_preenchido.png"
            ),
            "template_vazio": (
                "codigo_vazio.png"
            ),
            "captura_com_linha_selecionada": True,
        }

        try:
            with CAMINHO_CALIBRACAO.open(
                "w",
                encoding="utf-8",
            ) as arquivo:
                json.dump(
                    dados,
                    arquivo,
                    ensure_ascii=False,
                    indent=4,
                )

        except OSError as erro:
            messagebox.showerror(
                "Erro ao salvar",
                str(erro),
                parent=self,
            )
            return

        messagebox.showinfo(
            "Calibração salva",
            (
                "As duas células foram capturadas "
                "com a linha selecionada."
            ),
            parent=self,
        )


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = CodeCaptureWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
