import time
from tkinter import messagebox

import customtkinter as ctk
import pyautogui
import pyperclip

from automation.calibration_repository import (
    carregar_calibracao,
)


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


PONTOS_NECESSARIOS = (
    "mais_primeira_linha",
    "mais_segunda_linha",
    "aba_tributacao",
    "botao_salvar",
)


class TestAutomationWindow(ctk.CTk):
    """Executa um teste de cadastro sem salvar o produto."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Teste da Automação")
        self.geometry("640x520")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")

        self.calibracao = carregar_calibracao()

        self.descricao_teste = ""
        self.numero_item_teste = 3

        self.grid_columnconfigure(0, weight=1)

        self.criar_interface()
        self.verificar_calibracao()

    def criar_interface(self) -> None:
        """Cria os elementos da janela."""

        titulo = ctk.CTkLabel(
            self,
            text="Teste assistido da automação",
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
            sticky="w",
        )

        explicacao = ctk.CTkLabel(
            self,
            text=(
                "Neste teste, os dois primeiros itens serão "
                "considerados já cadastrados.\n\n"
                "A automação abrirá o terceiro item, preencherá "
                "a descrição e a tributação, mas não clicará em Salvar."
            ),
            justify="left",
            anchor="w",
            wraplength=570,
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
            ),
        )
        explicacao.grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="ew",
        )

        label_item = ctk.CTkLabel(
            self,
            text="Número do item que será testado:",
            anchor="w",
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
        )
        label_item.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 7),
            sticky="ew",
        )

        self.campo_item = ctk.CTkEntry(
            self,
            width=120,
            height=40,
            fg_color="#FFFFFF",
            text_color="#1F2937",
            border_color="#D1D5DB",
            border_width=1,
            corner_radius=4,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
            ),
        )
        self.campo_item.grid(
            row=3,
            column=0,
            padx=30,
            sticky="w",
        )
        self.campo_item.insert(0, "3")

        label_descricao = ctk.CTkLabel(
            self,
            text="Descrição final do terceiro produto:",
            anchor="w",
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
        )
        label_descricao.grid(
            row=4,
            column=0,
            padx=30,
            pady=(18, 7),
            sticky="ew",
        )

        self.campo_descricao = ctk.CTkEntry(
            self,
            height=42,
            fg_color="#FFFFFF",
            text_color="#1F2937",
            border_color="#D1D5DB",
            border_width=1,
            corner_radius=4,
            placeholder_text=(
                "Exemplo: CALCA SARJA SLIM (AFX)"
            ),
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
            ),
        )
        self.campo_descricao.grid(
            row=5,
            column=0,
            padx=30,
            sticky="ew",
        )

        self.label_status = ctk.CTkLabel(
            self,
            text="Verificando calibração...",
            anchor="w",
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        self.label_status.grid(
            row=6,
            column=0,
            padx=30,
            pady=(12, 18),
            sticky="ew",
        )

        self.botao_executar = ctk.CTkButton(
            self,
            text="Executar teste no terceiro item",
            height=42,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
            command=self.preparar_teste,
        )
        self.botao_executar.grid(
            row=7,
            column=0,
            padx=30,
            sticky="ew",
        )

        aviso = ctk.CTkLabel(
            self,
            text=(
                "Emergência: mova rapidamente o mouse para o "
                "canto superior esquerdo da tela."
            ),
            text_color="#991B1B",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        aviso.grid(
            row=8,
            column=0,
            padx=30,
            pady=(16, 20),
        )

    def verificar_calibracao(self) -> None:
        """Verifica os pontos e a resolução calibrada."""

        pontos = self.calibracao.get(
            "pontos",
            {},
        )

        faltantes = [
            ponto
            for ponto in PONTOS_NECESSARIOS
            if ponto not in pontos
        ]

        if faltantes:
            self.label_status.configure(
                text=(
                    "Calibração incompleta. Execute novamente "
                    "o arquivo calibrar.py."
                ),
                text_color="#991B1B",
            )

            self.botao_executar.configure(
                state="disabled"
            )
            return

        tela_calibrada = self.calibracao.get(
            "tela",
            {},
        )

        tela_atual = pyautogui.size()

        if (
            tela_calibrada.get("largura")
            != tela_atual.width
            or tela_calibrada.get("altura")
            != tela_atual.height
        ):
            self.label_status.configure(
                text=(
                    "A resolução atual é diferente da resolução "
                    "usada na calibração."
                ),
                text_color="#991B1B",
            )

            self.botao_executar.configure(
                state="disabled"
            )
            return

        self.label_status.configure(
            text=(
                f"Calibração válida: "
                f"{tela_atual.width} x {tela_atual.height}."
            ),
            text_color="#166534",
        )

    def preparar_teste(self) -> None:
        """Valida os dados antes de começar."""

        texto_item = self.campo_item.get().strip()

        try:
            numero_item = int(texto_item)
        except ValueError:
            messagebox.showwarning(
                "Número inválido",
                "O número do item deve ser um número inteiro.",
                parent=self,
            )
            return

        if numero_item < 1:
            messagebox.showwarning(
                "Número inválido",
                "O número do item deve ser maior que zero.",
                parent=self,
            )
            return

        calculos = self.calibracao.get(
            "calculos",
            {},
        )

        linhas_visiveis = calculos.get(
            "linhas_visiveis_estimadas",
            0,
        )

        if (
            linhas_visiveis
            and numero_item > linhas_visiveis
        ):
            messagebox.showwarning(
                "Item não visível",
                (
                    f"O item {numero_item} pode não estar "
                    "visível na tela.\n\n"
                    f"A calibração estimou "
                    f"{linhas_visiveis} linhas visíveis."
                ),
                parent=self,
            )
            return

        descricao = " ".join(
            self.campo_descricao.get().upper().split()
        )

        if not descricao:
            messagebox.showwarning(
                "Descrição necessária",
                "Digite a descrição final do produto.",
                parent=self,
            )
            return

        if len(descricao) > 35:
            messagebox.showwarning(
                "Descrição muito longa",
                (
                    f"A descrição possui {len(descricao)} "
                    "caracteres.\n\n"
                    "O limite atual é de 35 caracteres, "
                    "incluindo o código secreto."
                ),
                parent=self,
            )
            return

        confirmar = messagebox.askokcancel(
            "Confirmar teste",
            (
                f"O teste será executado no item {numero_item}.\n\n"
                "Confirme que:\n\n"
                "• o ADM está maximizado;\n"
                "• a nota está aberta;\n"
                "• a janela de cadastro está fechada;\n"
                f"• o item {numero_item} possui o botão +;\n"
                "• os itens anteriores não precisam ser cadastrados.\n\n"
                "O programa não clicará em Salvar."
            ),
            parent=self,
        )

        if not confirmar:
            return

        self.numero_item_teste = numero_item
        self.descricao_teste = descricao

        pyperclip.copy(
        self.descricao_teste
        )

        self.label_status.configure(
            text=(
                f"Executando teste no item "
                f"{self.numero_item_teste}..."
            ),
            text_color="#2563EB",
        )

        self.withdraw()

        self.after(
            500,
            self.executar_fluxo,
        )

    def calcular_posicao_item(
        self,
        numero_item: int,
    ) -> tuple[int, int]:
        """Calcula a posição do ícone de uma linha."""

        pontos = self.calibracao["pontos"]

        primeira = pontos[
            "mais_primeira_linha"
        ]

        segunda = pontos[
            "mais_segunda_linha"
        ]

        altura_linha = abs(
            segunda["y"] - primeira["y"]
        )

        posicao_x = primeira["x"]

        posicao_y = (
            primeira["y"]
            + (
                numero_item - 1
            )
            * altura_linha
        )

        return posicao_x, posicao_y

    def executar_fluxo(self) -> None:
        """Executa o teste automatizado sem salvar."""

        pontos = self.calibracao["pontos"]

        try:
            posicao_x, posicao_y = (
                self.calcular_posicao_item(
                    self.numero_item_teste
                )
            )

            # Primeiro mostra o ponto que será clicado.
            pyautogui.moveTo(
                posicao_x,
                posicao_y,
                duration=0.8,
            )

            time.sleep(1.5)

            # O primeiro clique seleciona a linha
            # e o segundo abre o cadastro.
            pyautogui.doubleClick(
               posicao_x,
               posicao_y,
               interval=0.20,
            )

            time.sleep(1.7)

            # Referência até Descrição.
            pyautogui.press(
                "tab",
                presses=4,
                interval=0.20,
            )

            # Seleciona a descrição atual.
            pyautogui.hotkey(
                "ctrl",
                "a",
            )

            time.sleep(0.4)

            # Copia novamente para garantir que o texto
            # ainda está disponível na área de transferência.
            pyperclip.copy(
            self.descricao_teste
            )

            time.sleep(0.3)

            # Cola a nova descrição.
            pyautogui.hotkey(
                "ctrl",
                "v",
            )

            time.sleep(1.0)

            ponto_tributacao = pontos[
                "aba_tributacao"
            ]

            pyautogui.click(
                ponto_tributacao["x"],
                ponto_tributacao["y"],
            )

            time.sleep(0.7)

            # Terceiro Tab sai do CSOSN e preenche CSOSN PR.
            pyautogui.press(
                "tab",
                presses=3,
                interval=0.30,
            )

            time.sleep(0.7)

            ponto_salvar = pontos[
                "botao_salvar"
            ]

            pyautogui.moveTo(
                ponto_salvar["x"],
                ponto_salvar["y"],
                duration=0.8,
            )

        except pyautogui.FailSafeException:
            self.mostrar_erro(
                "O teste foi interrompido pela proteção "
                "de emergência."
            )
            return

        except Exception as erro:
            self.mostrar_erro(
                f"Erro durante o teste: {erro}"
            )
            return

        print(
            f"Teste concluído no item "
            f"{self.numero_item_teste}. "
            "Nenhum clique foi realizado em Salvar."
        )

        self.deiconify()

        self.label_status.configure(
            text=(
                f"Teste concluído no item "
                f"{self.numero_item_teste}. "
                "Confira a descrição e o CSOSN PR no ADM."
            ),
            text_color="#166534",
        )

        # Mantém o ADM visível para conferência.
        self.iconify()

    def mostrar_erro(
        self,
        mensagem: str,
    ) -> None:
        """Restaura a janela e apresenta um erro."""

        self.deiconify()
        self.lift()
        self.focus_force()

        self.label_status.configure(
            text=mensagem,
            text_color="#991B1B",
        )

        messagebox.showerror(
            "Erro no teste",
            mensagem,
            parent=self,
        )


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = TestAutomationWindow()
    app.mainloop()


if __name__ == "__main__":
    main()