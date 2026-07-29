from tkinter import messagebox

import customtkinter as ctk
import pyautogui

from automation.calibration_repository import (
    carregar_calibracao,
)
from automation.link_detector import (
    detectar_estado_vinculo,
)


class LinkDetectionTestWindow(ctk.CTk):
    """Testa a identificação visual da coluna Vinc."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Teste de Identificação do Vínculo")
        self.geometry("650x510")
        self.resizable(False, False)
        self.configure(
            fg_color="#FFFFFF"
        )

        self.calibracao = carregar_calibracao()

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.criar_interface()
        self.validar_calibracao()

    def criar_interface(self) -> None:
        """Cria os componentes da janela."""

        titulo = ctk.CTkLabel(
            self,
            text="Identificação automática do vínculo",
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
                "Selecione manualmente no ADM a linha que deseja "
                "testar. Depois informe o número do item abaixo.\n\n"
                "O programa somente capturará a coluna Vinc. "
                "Nenhum clique ou alteração será realizado."
            ),
            anchor="w",
            justify="left",
            wraplength=585,
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
            pady=(0, 22),
            sticky="ew",
        )

        label_item = ctk.CTkLabel(
            self,
            text="Número do item selecionado no ADM:",
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

        self.quadro_resultado = ctk.CTkFrame(
            self,
            fg_color="#F3F4F6",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=4,
        )
        self.quadro_resultado.grid(
            row=4,
            column=0,
            padx=30,
            pady=22,
            sticky="ew",
        )

        self.label_resultado = ctk.CTkLabel(
            self.quadro_resultado,
            text="Aguardando teste",
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
            self.quadro_resultado,
            text=(
                "O resultado e as diferenças das imagens "
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

        self.botao_testar = ctk.CTkButton(
            self,
            text="Analisar vínculo selecionado",
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
        self.botao_testar.grid(
            row=6,
            column=0,
            padx=30,
            sticky="ew",
        )

        aviso = ctk.CTkLabel(
            self,
            text=(
                "A linha informada precisa estar visível "
                "e selecionada manualmente no ADM."
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
        """Valida a resolução e as capturas."""

        if not self.calibracao.get("vinculo"):
            self.label_status.configure(
                text=(
                    "Capturas de vínculo não encontradas. "
                    "Execute capturar_vinculos.py."
                ),
                text_color="#991B1B",
            )

            self.botao_testar.configure(
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

            self.botao_testar.configure(
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
        """Valida o item antes da captura."""

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
                "Item não visível",
                (
                    f"O item {numero_item} está fora da "
                    "área inicialmente calibrada.\n\n"
                    f"Linhas visíveis estimadas: "
                    f"{linhas_visiveis}."
                ),
                parent=self,
            )
            return

        confirmar = messagebox.askokcancel(
            "Preparar análise",
            (
                f"O programa analisará o item {numero_item}.\n\n"
                "Antes de continuar:\n\n"
                f"• selecione manualmente o item {numero_item};\n"
                "• mantenha a nota visível;\n"
                "• não cubra a coluna Vinc. com outra janela.\n\n"
                "Nenhum clique será realizado."
            ),
            parent=self,
        )

        if not confirmar:
            return

        self.numero_item = numero_item

        self.label_status.configure(
            text=(
                f"Analisando o item {numero_item}..."
            ),
            text_color="#2563EB",
        )

        self.withdraw()

        self.after(
            700,
            self.executar_teste,
        )

    def executar_teste(self) -> None:
        """Executa a captura e mostra o resultado."""

        try:
            resultado = detectar_estado_vinculo(
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

        distancia_ativo = (
            resultado.distancia_ativo * 100
        )

        distancia_inativo = (
            resultado.distancia_inativo * 100
        )

        margem = resultado.margem * 100

        if resultado.estado == "ativo":
            titulo = "PRODUTO JÁ CADASTRADO"
            cor = "#166534"

        elif resultado.estado == "inativo":
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
                f"Diferença para vínculo ativo: "
                f"{distancia_ativo:.2f}%\n"
                f"Diferença para vínculo inativo: "
                f"{distancia_inativo:.2f}%\n"
                f"Margem entre os resultados: "
                f"{margem:.2f}%"
            ),
            text_color="#1F2937",
        )

        self.label_status.configure(
            text=(
                f"Item {self.numero_item} analisado. "
                "A captura de diagnóstico foi salva em logs/vinculos."
            ),
            text_color=cor,
        )

        if resultado.estado == "incerto":
            messagebox.showwarning(
                "Resultado incerto",
                (
                    "As duas imagens ficaram muito parecidas.\n\n"
                    "Refaça as capturas do vínculo ativo e inativo, "
                    "posicionando o mouse exatamente no centro "
                    "do ícone."
                ),
                parent=self,
            )

    def mostrar_erro(
        self,
        mensagem: str,
    ) -> None:
        """Restaura a janela e mostra um erro."""

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

    app = LinkDetectionTestWindow()
    app.mainloop()


if __name__ == "__main__":
    main()