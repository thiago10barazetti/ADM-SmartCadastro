from tkinter import messagebox

import customtkinter as ctk
import pyautogui

from automation.calibration_repository import (
    carregar_calibracao,
)
from automation.code_detector import (
    detectar_estado_codigo,
)


class CodeDetectionTestWindow(ctk.CTk):
    """Testa a identificação da coluna Código."""

    def __init__(self) -> None:
        super().__init__()

        self.title(
            "Teste da Coluna Código"
        )
        self.geometry(
            "660x540"
        )
        self.resizable(
            False,
            False,
        )
        self.configure(
            fg_color="#FFFFFF"
        )

        self.calibracao = carregar_calibracao()
        self.numero_item = 1

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.criar_interface()
        self.validar_calibracao()

    def criar_interface(self) -> None:
        """Cria a interface."""

        titulo = ctk.CTkLabel(
            self,
            text=(
                "Identificação pela coluna Código"
            ),
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
                "Informe o número do item que deseja analisar.\n\n"
                "O programa verificará se existe um número na "
                "coluna Código. Nenhum clique será realizado."
            ),
            anchor="w",
            justify="left",
            wraplength=590,
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
        self.campo_item.insert(
            0,
            "1",
        )

        quadro = ctk.CTkFrame(
            self,
            fg_color="#F3F4F6",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=4,
        )
        quadro.grid(
            row=4,
            column=0,
            padx=30,
            pady=22,
            sticky="ew",
        )

        self.label_resultado = ctk.CTkLabel(
            quadro,
            text="Aguardando análise",
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=19,
                weight="bold",
            ),
        )
        self.label_resultado.pack(
            pady=(20, 6),
        )

        self.label_detalhes = ctk.CTkLabel(
            quadro,
            text=(
                "Os valores de diagnóstico "
                "aparecerão aqui."
            ),
            justify="left",
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        self.label_detalhes.pack(
            pady=(0, 20),
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
            row=5,
            column=0,
            padx=30,
            pady=(0, 14),
            sticky="ew",
        )

        self.botao_analisar = ctk.CTkButton(
            self,
            text="Analisar coluna Código",
            height=42,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
            command=self.preparar_analise,
        )
        self.botao_analisar.grid(
            row=6,
            column=0,
            padx=30,
            sticky="ew",
        )

        aviso = ctk.CTkLabel(
            self,
            text=(
                "Mantenha a nota visível e não cubra "
                "a tabela com outra janela."
            ),
            text_color="#B45309",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        aviso.grid(
            row=7,
            column=0,
            padx=30,
            pady=(15, 20),
        )

    def validar_calibracao(self) -> None:
        """Valida a calibração e a resolução."""

        if not self.calibracao.get(
            "codigo_produto"
        ):
            self.label_status.configure(
                text=(
                    "Calibração da coluna Código "
                    "não encontrada."
                ),
                text_color="#991B1B",
            )

            self.botao_analisar.configure(
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
                    "A resolução atual é diferente "
                    "da resolução calibrada."
                ),
                text_color="#991B1B",
            )

            self.botao_analisar.configure(
                state="disabled"
            )
            return

        self.label_status.configure(
            text=(
                f"Calibração válida: "
                f"{tela_atual.width} x "
                f"{tela_atual.height}."
            ),
            text_color="#166534",
        )

    def preparar_analise(self) -> None:
        """Valida o item antes da análise."""

        try:
            numero_item = int(
                self.campo_item.get().strip()
            )

        except ValueError:
            messagebox.showwarning(
                "Número inválido",
                "Informe um número inteiro.",
                parent=self,
            )
            return

        if numero_item < 1:
            messagebox.showwarning(
                "Número inválido",
                "O número deve ser maior que zero.",
                parent=self,
            )
            return

        linhas_visiveis = int(
            self.calibracao.get(
                "calculos",
                {},
            ).get(
                "linhas_visiveis_estimadas",
                0,
            )
        )

        if (
            linhas_visiveis
            and numero_item > linhas_visiveis
        ):
            messagebox.showwarning(
                "Item fora da área visível",
                (
                    f"O item {numero_item} pode não estar "
                    "visível na tabela."
                ),
                parent=self,
            )
            return

        self.numero_item = numero_item

        self.label_status.configure(
            text=(
                f"Analisando item {numero_item}..."
            ),
            text_color="#2563EB",
        )

        self.withdraw()

        self.after(
            700,
            self.executar_analise,
        )

    def executar_analise(self) -> None:
        """Executa a análise da coluna."""

        try:
            resultado = detectar_estado_codigo(
                calibracao=self.calibracao,
                numero_item=self.numero_item,
            )

        except (
            ValueError,
            FileNotFoundError,
            OSError,
        ) as erro:
            self.mostrar_erro(
                str(erro)
            )
            return

        except Exception as erro:
            self.mostrar_erro(
                f"Erro inesperado: {erro}"
            )
            return

        self.deiconify()
        self.lift()
        self.focus_force()

        if resultado.estado == "preenchido":
            titulo = "PRODUTO JÁ CADASTRADO"
            cor = "#166534"

        elif resultado.estado == "vazio":
            titulo = "PRODUTO NÃO CADASTRADO"
            cor = "#B45309"

        else:
            titulo = "RESULTADO INCERTO"
            cor = "#991B1B"

        self.label_resultado.configure(
            text=titulo,
            text_color=cor,
        )

        self.label_detalhes.configure(
            text=(
                f"Valor atual: "
                f"{resultado.score_atual:.4f}\n"
                f"Modelo preenchido: "
                f"{resultado.score_preenchido_modelo:.4f}\n"
                f"Modelo vazio: "
                f"{resultado.score_vazio_modelo:.4f}\n"
                f"Limite preenchido: "
                f"{resultado.limite_preenchido:.4f}\n"
                f"Deslocamento vertical: "
                f"{resultado.deslocamento_y:+d}px"
            ),
            text_color="#1F2937",
        )

        self.label_status.configure(
            text=(
                f"Item {self.numero_item} analisado. "
                "Captura salva em logs/codigos."
            ),
            text_color=cor,
        )

        if resultado.estado == "incerto":
            messagebox.showwarning(
                "Resultado incerto",
                (
                    "A célula ficou entre os modelos vazio "
                    "e preenchido.\n\n"
                    "Não cadastre automaticamente este item "
                    "até ajustarmos a captura."
                ),
                parent=self,
            )

    def mostrar_erro(
        self,
        mensagem: str,
    ) -> None:
        """Mostra um erro da análise."""

        self.deiconify()
        self.lift()
        self.focus_force()

        self.label_status.configure(
            text=mensagem,
            text_color="#991B1B",
        )

        messagebox.showerror(
            "Erro na análise",
            mensagem,
            parent=self,
        )


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = CodeDetectionTestWindow()
    app.mainloop()


if __name__ == "__main__":
    main()