import time
from tkinter import messagebox

import customtkinter as ctk
import pyautogui
import pyperclip

from automation.calibration_repository import (
    carregar_calibracao,
)
from database.settings_repository import (
    carregar_configuracoes,
)


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


PONTOS_NECESSARIOS = (
    "mais_primeira_linha",
    "mais_segunda_linha",
    "aba_tributacao",
    "botao_salvar",
)


class RealRegistrationTestWindow(ctk.CTk):
    """Executa o cadastro real de apenas um produto."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Teste de Cadastro Real")
        self.geometry("660x560")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")

        self.calibracao = carregar_calibracao()
        self.configuracoes = carregar_configuracoes()

        self.limite_descricao = int(
            self.configuracoes.get(
                "limite_descricao",
                35,
            )
        )

        self.numero_item = 3
        self.descricao = ""

        self.grid_columnconfigure(0, weight=1)

        self.criar_interface()
        self.verificar_calibracao()

    def criar_interface(self) -> None:
        """Cria os componentes da janela."""

        titulo = ctk.CTkLabel(
            self,
            text="Primeiro cadastro real",
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
                "Este teste fará o cadastro real de apenas um produto.\n\n"
                "Os dois primeiros itens serão ignorados e o terceiro "
                "item será aberto. Antes de clicar em Salvar, o sistema "
                "pedirá uma confirmação final."
            ),
            anchor="w",
            justify="left",
            wraplength=590,
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
            text="Número do item:",
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
            text="Descrição final, incluindo o código secreto:",
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
            placeholder_text="Exemplo: CALCA SLIM SETTA (AGA)",
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

        self.label_contagem = ctk.CTkLabel(
            self,
            text=f"0/{self.limite_descricao} caracteres",
            anchor="e",
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        self.label_contagem.grid(
            row=6,
            column=0,
            padx=30,
            pady=(5, 0),
            sticky="ew",
        )

        self.campo_descricao.bind(
            "<KeyRelease>",
            self.atualizar_contagem,
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
            row=7,
            column=0,
            padx=30,
            pady=(12, 18),
            sticky="ew",
        )

        self.botao_executar = ctk.CTkButton(
            self,
            text="Preparar cadastro real",
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
            row=8,
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
            row=9,
            column=0,
            padx=30,
            pady=(16, 20),
        )

    def atualizar_contagem(self, _evento=None) -> None:
        """Atualiza a quantidade de caracteres digitados."""

        descricao = " ".join(
            self.campo_descricao.get().upper().split()
        )

        quantidade = len(descricao)

        if quantidade > self.limite_descricao:
            cor = "#991B1B"
        else:
            cor = "#6B7280"

        self.label_contagem.configure(
            text=(
                f"{quantidade}/"
                f"{self.limite_descricao} caracteres"
            ),
            text_color=cor,
        )

    def verificar_calibracao(self) -> None:
        """Valida os pontos e a resolução utilizada."""

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
                    "utilizada na calibração."
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
        """Valida as informações antes da execução."""

        try:
            numero_item = int(
                self.campo_item.get().strip()
            )

        except ValueError:
            messagebox.showwarning(
                "Número inválido",
                "O número do item deve ser inteiro.",
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

        linhas_visiveis = int(
            calculos.get(
                "linhas_visiveis_estimadas",
                0,
            )
        )

        if (
            linhas_visiveis > 0
            and numero_item > linhas_visiveis
        ):
            messagebox.showwarning(
                "Item não visível",
                (
                    f"O item {numero_item} não está dentro "
                    "da área visível calibrada.\n\n"
                    f"Linhas visíveis estimadas: "
                    f"{linhas_visiveis}."
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

        if len(descricao) > self.limite_descricao:
            messagebox.showwarning(
                "Descrição muito longa",
                (
                    f"A descrição possui {len(descricao)} "
                    f"caracteres.\n\n"
                    f"O limite configurado é de "
                    f"{self.limite_descricao} caracteres."
                ),
                parent=self,
            )
            return

        confirmar = messagebox.askokcancel(
            "Preparar cadastro real",
            (
                f"O item {numero_item} será aberto e preparado.\n\n"
                "Confirme que:\n\n"
                "• o ADM está maximizado;\n"
                "• a nota correta está aberta;\n"
                "• a janela de cadastro está fechada;\n"
                f"• o item {numero_item} possui o botão + verde;\n"
                "• ninguém usará o mouse ou teclado durante o teste.\n\n"
                "Ainda haverá outra confirmação antes de Salvar."
            ),
            parent=self,
        )

        if not confirmar:
            return

        self.numero_item = numero_item
        self.descricao = descricao

        pyperclip.copy(
            self.descricao
        )

        self.label_status.configure(
            text=(
                f"Preparando o cadastro do item "
                f"{self.numero_item}..."
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
        """Calcula a coordenada do botão + do item."""

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
        """Prepara o cadastro até o botão Salvar."""

        pontos = self.calibracao["pontos"]

        try:
            posicao_x, posicao_y = (
                self.calcular_posicao_item(
                    self.numero_item
                )
            )

            pyautogui.moveTo(
                posicao_x,
                posicao_y,
                duration=0.8,
            )

            time.sleep(1.2)

            # Primeiro clique seleciona a linha.
            # Segundo clique abre o cadastro.
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

            pyautogui.hotkey(
                "ctrl",
                "a",
            )

            time.sleep(0.4)

            pyperclip.copy(
                self.descricao
            )

            time.sleep(0.3)

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

            # O terceiro Tab sai do CSOSN
            # e provoca o preenchimento do CSOSN PR.
            pyautogui.press(
                "tab",
                presses=3,
                interval=0.30,
            )

            time.sleep(0.8)

            ponto_salvar = pontos[
                "botao_salvar"
            ]

            pyautogui.moveTo(
                ponto_salvar["x"],
                ponto_salvar["y"],
                duration=0.8,
            )

            time.sleep(1.0)

        except pyautogui.FailSafeException:
            self.mostrar_erro(
                "A execução foi interrompida pela proteção "
                "de emergência."
            )
            return

        except Exception as erro:
            self.mostrar_erro(
                f"Erro durante a preparação: {erro}"
            )
            return

        self.confirmar_salvamento()

    def confirmar_salvamento(self) -> None:
        """Pede autorização antes de clicar em Salvar."""

        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.update()

        confirmar = messagebox.askyesno(
            "Confirmação final",
            (
                f"O cadastro do item {self.numero_item} "
                "está preparado.\n\n"
                f"Descrição:\n{self.descricao}\n\n"
                "Clique em Sim para realizar o clique em Salvar.\n"
                "Clique em Não para deixar o cadastro aberto "
                "sem salvar."
            ),
            parent=self,
        )

        self.attributes("-topmost", False)

        if not confirmar:
            self.label_status.configure(
                text=(
                    "O cadastro foi preparado, mas não foi salvo. "
                    "Revise ou feche manualmente no ADM."
                ),
                text_color="#B45309",
            )
            return

        self.withdraw()
        self.update()

        time.sleep(0.8)

        ponto_salvar = self.calibracao[
            "pontos"
        ]["botao_salvar"]

        try:
            pyautogui.moveTo(
                ponto_salvar["x"],
                ponto_salvar["y"],
                duration=0.5,
            )

            pyautogui.click(
                ponto_salvar["x"],
                ponto_salvar["y"],
            )

            # Não executamos nenhuma outra ação após salvar.
            time.sleep(3.0)

        except pyautogui.FailSafeException:
            self.mostrar_erro(
                "O clique em Salvar foi interrompido "
                "pela proteção de emergência."
            )
            return

        except Exception as erro:
            self.mostrar_erro(
                f"Erro ao clicar em Salvar: {erro}"
            )
            return

        self.deiconify()
        self.lift()
        self.focus_force()

        self.label_status.configure(
            text=(
                f"O clique em Salvar foi executado no item "
                f"{self.numero_item}. Confira o resultado no ADM."
            ),
            text_color="#166534",
        )

        messagebox.showinfo(
            "Teste concluído",
            (
                "O clique em Salvar foi executado.\n\n"
                "Agora confira no ADM se:\n\n"
                "• a janela de cadastro foi fechada;\n"
                "• a linha correta continua selecionada;\n"
                "• o botão + foi substituído pelo vínculo;\n"
                "• a descrição cadastrada está correta.\n\n"
                "A automação não avançou para outro produto."
            ),
            parent=self,
        )

    def mostrar_erro(
        self,
        mensagem: str,
    ) -> None:
        """Restaura a janela e apresenta o erro."""

        self.deiconify()
        self.lift()
        self.focus_force()

        self.label_status.configure(
            text=mensagem,
            text_color="#991B1B",
        )

        messagebox.showerror(
            "Erro na automação",
            mensagem,
            parent=self,
        )


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = RealRegistrationTestWindow()
    app.mainloop()


if __name__ == "__main__":
    main()