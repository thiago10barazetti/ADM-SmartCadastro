import json
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
import pyautogui

from automation.calibration_repository import (
    CAMINHO_CALIBRACAO,
    carregar_calibracao,
)


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


LARGURA_CAPTURA = 18
ALTURA_CAPTURA = 12

PASTA_ICONES = (
    Path(__file__).resolve().parent
    / "assets"
    / "icons"
)

ARQUIVOS = {
    "ativo": PASTA_ICONES / "vinculo_ativo.png",
    "inativo": PASTA_ICONES / "vinculo_inativo.png",
}


class LinkCaptureWindow(ctk.CTk):
    """Captura os estados ativo e inativo do vínculo."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Captura dos Vínculos")
        self.geometry("680x500")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")

        PASTA_ICONES.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.capturas: dict[
            str,
            dict[str, int | str],
        ] = {}

        self.tipo_em_captura: str | None = None

        self.grid_columnconfigure(0, weight=1)

        self.criar_interface()

    def criar_interface(self) -> None:
        """Cria os elementos da janela."""

        titulo = ctk.CTkLabel(
            self,
            text="Captura da coluna Vinc.",
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
                "Vamos capturar a pequena área da coluna Vinc. "
                "em dois estados.\n\n"
                "Ao clicar em Capturar, esta janela desaparecerá. "
                "Você terá 4 segundos para posicionar o mouse "
                "no centro do vínculo da linha selecionada."
            ),
            anchor="w",
            justify="left",
            wraplength=610,
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
            tipo="ativo",
            titulo="Vínculo ativo",
            descricao=(
                "Selecione no ADM uma linha já cadastrada. "
                "Posicione o mouse no centro do ícone verde "
                "da coluna Vinc."
            ),
        )

        self.criar_cartao(
            linha=3,
            tipo="inativo",
            titulo="Vínculo inativo",
            descricao=(
                "Selecione no ADM uma linha ainda não cadastrada. "
                "Posicione o mouse no centro do ícone inativo ou "
                "no centro do espaço vazio da coluna Vinc."
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
            text="Salvar capturas",
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
                "Nenhum clique será realizado no ADM. "
                "A ferramenta apenas tira uma pequena captura da tela."
            ),
            text_color="#166534",
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

        frame.grid_columnconfigure(0, weight=1)

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
            wraplength=430,
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

        if tipo == "ativo":
            self.label_ativo = label_resultado
        else:
            self.label_inativo = label_resultado

    def iniciar_captura(
        self,
        tipo: str,
    ) -> None:
        """Esconde a janela e inicia a espera."""

        self.tipo_em_captura = tipo

        nome = (
            "vínculo ativo"
            if tipo == "ativo"
            else "vínculo inativo"
        )

        self.label_status.configure(
            text=(
                f"Preparando captura do {nome}. "
                "Posicione o mouse no local indicado."
            ),
            text_color="#2563EB",
        )

        self.after(
            400,
            self.ocultar_janela,
        )

    def ocultar_janela(self) -> None:
        """Oculta a janela durante a captura."""

        self.withdraw()

        self.after(
            4000,
            self.finalizar_captura,
        )

    def finalizar_captura(self) -> None:
        """Captura uma pequena região em volta do mouse."""

        tipo = self.tipo_em_captura

        if tipo is None:
            self.deiconify()
            return

        posicao = pyautogui.position()
        tamanho_tela = pyautogui.size()

        esquerda = max(
            0,
            int(posicao.x - LARGURA_CAPTURA / 2),
        )

        topo = max(
            0,
            int(posicao.y - ALTURA_CAPTURA / 2),
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

        imagem.save(caminho)

        self.capturas[tipo] = {
            "x": int(posicao.x),
            "y": int(posicao.y),
            "arquivo": caminho.as_posix(),
        }

        label = (
            self.label_ativo
            if tipo == "ativo"
            else self.label_inativo
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
                f"Captura salva em: "
                f"{caminho.name}"
            ),
            text_color="#166534",
        )

        self.tipo_em_captura = None

    def salvar(self) -> None:
        """Salva os dados no arquivo de calibração."""

        if "ativo" not in self.capturas:
            messagebox.showwarning(
                "Captura necessária",
                "Capture primeiro o vínculo ativo.",
                parent=self,
            )
            return

        if "inativo" not in self.capturas:
            messagebox.showwarning(
                "Captura necessária",
                "Capture também o vínculo inativo.",
                parent=self,
            )
            return

        ativo = self.capturas["ativo"]
        inativo = self.capturas["inativo"]

        diferenca_x = abs(
            int(ativo["x"])
            - int(inativo["x"])
        )

        if diferenca_x > 20:
            continuar = messagebox.askyesno(
                "Posições diferentes",
                (
                    "As duas capturas possuem uma diferença "
                    "horizontal maior que 20 pixels.\n\n"
                    "Isso pode indicar que uma delas não foi feita "
                    "na mesma coluna Vinc.\n\n"
                    "Deseja salvar mesmo assim?"
                ),
                parent=self,
            )

            if not continuar:
                return

        dados = carregar_calibracao()

        dados["vinculo"] = {
            "coluna_x": round(
                (
                    int(ativo["x"])
                    + int(inativo["x"])
                )
                / 2
            ),
            "largura_captura": LARGURA_CAPTURA,
            "altura_captura": ALTURA_CAPTURA,
            "template_ativo": (
                "assets/icons/vinculo_ativo.png"
            ),
            "template_inativo": (
                "assets/icons/vinculo_inativo.png"
            ),
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
            "Capturas salvas",
            (
                "Os estados do vínculo foram salvos.\n\n"
                "Agora poderemos testar a identificação "
                "automática de produtos cadastrados."
            ),
            parent=self,
        )


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = LinkCaptureWindow()
    app.mainloop()


if __name__ == "__main__":
    main()