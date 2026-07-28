import time
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyautogui
import pyperclip

from automation.calibration_repository import (
    carregar_calibracao,
)
from database.settings_repository import (
    carregar_configuracoes,
)
from services.preparacao_produtos import (
    preparar_produtos,
)
from xml_reader.nfe_reader import (
    ler_produtos_xml,
)


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


PONTOS_NECESSARIOS = (
    "mais_primeira_linha",
    "mais_segunda_linha",
    "aba_tributacao",
    "botao_salvar",
)


class BatchTestWindow(ctk.CTk):
    """Executa um pequeno lote com confirmação individual."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Teste de Lote Assistido")
        self.geometry("720x650")
        self.minsize(680, 610)
        self.configure(fg_color="#FFFFFF")

        self.calibracao = carregar_calibracao()
        self.configuracoes = carregar_configuracoes()

        self.limite_descricao = int(
            self.configuracoes.get(
                "limite_descricao",
                35,
            )
        )

        self.caminho_xml: Path | None = None
        self.produtos = []
        self.itens_lote = []
        self.indice_atual = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.criar_interface()
        self.verificar_calibracao()

    def criar_interface(self) -> None:
        """Cria a interface do teste."""

        titulo = ctk.CTkLabel(
            self,
            text="Teste de lote assistido",
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
            pady=(25, 5),
            sticky="ew",
        )

        explicacao = ctk.CTkLabel(
            self,
            text=(
                "Selecione o mesmo XML importado no ADM. "
                "O programa preparará alguns produtos consecutivos "
                "e pedirá confirmação antes de salvar cada um."
            ),
            anchor="w",
            justify="left",
            wraplength=650,
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
            pady=(0, 18),
            sticky="ew",
        )

        area_xml = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
        )
        area_xml.grid(
            row=2,
            column=0,
            padx=30,
            sticky="ew",
        )
        area_xml.grid_columnconfigure(1, weight=1)

        botao_xml = ctk.CTkButton(
            area_xml,
            text="Selecionar XML",
            width=145,
            height=38,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.selecionar_xml,
        )
        botao_xml.grid(
            row=0,
            column=0,
            padx=(0, 12),
        )

        self.label_xml = ctk.CTkLabel(
            area_xml,
            text="Nenhum XML selecionado",
            anchor="w",
            text_color="#6B7280",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
            ),
        )
        self.label_xml.grid(
            row=0,
            column=1,
            sticky="ew",
        )

        area_opcoes = ctk.CTkFrame(
            self,
            fg_color="#F3F4F6",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=4,
        )
        area_opcoes.grid(
            row=3,
            column=0,
            padx=30,
            pady=18,
            sticky="ew",
        )

        label_inicio = ctk.CTkLabel(
            area_opcoes,
            text="Item inicial",
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
        )
        label_inicio.grid(
            row=0,
            column=0,
            padx=(18, 8),
            pady=16,
        )

        self.campo_inicio = ctk.CTkEntry(
            area_opcoes,
            width=80,
            height=36,
            corner_radius=4,
        )
        self.campo_inicio.grid(
            row=0,
            column=1,
            padx=(0, 25),
            pady=16,
        )
        self.campo_inicio.insert(0, "1")

        label_quantidade = ctk.CTkLabel(
            area_opcoes,
            text="Quantidade",
            text_color="#1F2937",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
        )
        label_quantidade.grid(
            row=0,
            column=2,
            padx=(0, 8),
            pady=16,
        )

        self.campo_quantidade = ctk.CTkEntry(
            area_opcoes,
            width=80,
            height=36,
            corner_radius=4,
        )
        self.campo_quantidade.grid(
            row=0,
            column=3,
            padx=(0, 18),
            pady=16,
        )
        self.campo_quantidade.insert(0, "3")

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
            row=4,
            column=0,
            padx=30,
            pady=(0, 8),
            sticky="ew",
        )

        self.campo_resumo = ctk.CTkTextbox(
            self,
            fg_color="#FFFFFF",
            text_color="#1F2937",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=4,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
            ),
        )
        self.campo_resumo.grid(
            row=5,
            column=0,
            padx=30,
            pady=(0, 18),
            sticky="nsew",
        )
        self.campo_resumo.insert(
            "1.0",
            "Selecione o XML para visualizar os produtos.",
        )
        self.campo_resumo.configure(
            state="disabled"
        )

        self.botao_executar = ctk.CTkButton(
            self,
            text="Iniciar lote assistido",
            height=42,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
            command=self.preparar_lote,
        )
        self.botao_executar.grid(
            row=6,
            column=0,
            padx=30,
            sticky="ew",
        )

        aviso = ctk.CTkLabel(
            self,
            text=(
                "Emergência: mova o mouse para o canto "
                "superior esquerdo da tela."
            ),
            text_color="#991B1B",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        aviso.grid(
            row=7,
            column=0,
            padx=30,
            pady=(14, 20),
        )

    def verificar_calibracao(self) -> None:
        """Confere os pontos e a resolução."""

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
                text="Calibração incompleta.",
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
                    "A resolução atual é diferente "
                    "da calibração."
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

    def selecionar_xml(self) -> None:
        """Seleciona e prepara os produtos do XML."""

        caminho = filedialog.askopenfilename(
            title="Selecionar XML de teste",
            filetypes=[
                ("Arquivos XML", "*.xml"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not caminho:
            return

        try:
            produtos = ler_produtos_xml(
                Path(caminho)
            )
            preparar_produtos(produtos)

        except (
            ValueError,
            FileNotFoundError,
            OSError,
        ) as erro:
            messagebox.showerror(
                "Erro ao abrir XML",
                str(erro),
                parent=self,
            )
            return

        self.caminho_xml = Path(caminho)
        self.produtos = produtos

        self.label_xml.configure(
            text=(
                f"{self.caminho_xml.name} "
                f"({len(self.produtos)} produtos)"
            ),
            text_color="#1F2937",
        )

        self.atualizar_resumo()

    def atualizar_resumo(self) -> None:
        """Mostra os produtos preparados."""

        linhas = []

        for numero, produto in enumerate(
            self.produtos,
            start=1,
        ):
            quantidade = len(
                produto.descricao_final
            )

            linhas.append(
                f"{numero:02d}. "
                f"{produto.referencia} | "
                f"{produto.descricao_final} | "
                f"{quantidade}/{self.limite_descricao}"
            )

        self.campo_resumo.configure(
            state="normal"
        )
        self.campo_resumo.delete(
            "1.0",
            "end",
        )
        self.campo_resumo.insert(
            "1.0",
            "\n".join(linhas),
        )
        self.campo_resumo.configure(
            state="disabled"
        )

    def preparar_lote(self) -> None:
        """Valida o lote antes da execução."""

        if not self.produtos:
            messagebox.showwarning(
                "XML necessário",
                "Selecione o XML importado no ADM.",
                parent=self,
            )
            return

        try:
            item_inicial = int(
                self.campo_inicio.get().strip()
            )
            quantidade = int(
                self.campo_quantidade.get().strip()
            )

        except ValueError:
            messagebox.showwarning(
                "Valores inválidos",
                "Informe números inteiros.",
                parent=self,
            )
            return

        if item_inicial < 1 or quantidade < 1:
            messagebox.showwarning(
                "Valores inválidos",
                "Os valores devem ser maiores que zero.",
                parent=self,
            )
            return

        if quantidade > 5:
            messagebox.showwarning(
                "Lote muito grande",
                (
                    "Neste primeiro teste, use no máximo "
                    "5 produtos."
                ),
                parent=self,
            )
            return

        item_final = (
            item_inicial + quantidade - 1
        )

        if item_final > len(self.produtos):
            messagebox.showwarning(
                "Lote inválido",
                "O lote ultrapassa os produtos do XML.",
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
            and item_final > linhas_visiveis
        ):
            messagebox.showwarning(
                "Itens fora da área visível",
                (
                    "Neste teste, todos os produtos precisam "
                    "estar visíveis sem rolar a tabela.\n\n"
                    f"Linhas visíveis estimadas: "
                    f"{linhas_visiveis}."
                ),
                parent=self,
            )
            return

        selecionados = []

        for numero_item in range(
            item_inicial,
            item_final + 1,
        ):
            produto = self.produtos[
                numero_item - 1
            ]

            if (
                len(produto.descricao_final)
                > self.limite_descricao
            ):
                messagebox.showwarning(
                    "Descrição inválida",
                    (
                        f"O item {numero_item} ultrapassa "
                        f"{self.limite_descricao} caracteres:\n\n"
                        f"{produto.descricao_final}"
                    ),
                    parent=self,
                )
                return

            selecionados.append(
                (numero_item, produto)
            )

        confirmar = messagebox.askokcancel(
            "Confirmar lote assistido",
            (
                f"Serão preparados {quantidade} produtos, "
                f"do item {item_inicial} ao {item_final}.\n\n"
                "Antes de cada salvamento haverá uma "
                "confirmação individual.\n\n"
                "Confirme que o ADM está maximizado, "
                "a nota está aberta e todos esses itens "
                "possuem o botão +."
            ),
            parent=self,
        )

        if not confirmar:
            return

        self.itens_lote = selecionados
        self.indice_atual = 0

        self.label_status.configure(
            text="Iniciando lote assistido...",
            text_color="#2563EB",
        )

        self.withdraw()
        self.after(
            500,
            self.preparar_item_atual,
        )

    def calcular_posicao_item(
        self,
        numero_item: int,
    ) -> tuple[int, int]:
        """Calcula a posição da linha escolhida."""

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

        x = primeira["x"]
        y = (
            primeira["y"]
            + (numero_item - 1) * altura_linha
        )

        return x, y

    def preparar_item_atual(self) -> None:
        """Preenche o produto atual até o salvamento."""

        numero_item, produto = (
            self.itens_lote[
                self.indice_atual
            ]
        )

        pontos = self.calibracao["pontos"]

        try:
            x, y = self.calcular_posicao_item(
                numero_item
            )

            pyautogui.moveTo(
                x,
                y,
                duration=0.6,
            )
            time.sleep(0.7)

            pyautogui.doubleClick(
                x,
                y,
                interval=0.20,
            )
            time.sleep(1.7)

            pyautogui.press(
                "tab",
                presses=4,
                interval=0.20,
            )

            pyautogui.hotkey(
                "ctrl",
                "a",
            )
            time.sleep(0.3)

            pyperclip.copy(
                produto.descricao_final
            )
            time.sleep(0.2)

            pyautogui.hotkey(
                "ctrl",
                "v",
            )
            time.sleep(0.8)

            tributacao = pontos[
                "aba_tributacao"
            ]

            pyautogui.click(
                tributacao["x"],
                tributacao["y"],
            )
            time.sleep(0.6)

            pyautogui.press(
                "tab",
                presses=3,
                interval=0.30,
            )
            time.sleep(0.7)

            salvar = pontos[
                "botao_salvar"
            ]

            pyautogui.moveTo(
                salvar["x"],
                salvar["y"],
                duration=0.6,
            )

        except pyautogui.FailSafeException:
            self.mostrar_erro(
                "Lote interrompido pela proteção."
            )
            return

        except Exception as erro:
            self.mostrar_erro(
                f"Erro ao preparar item: {erro}"
            )
            return

        self.confirmar_item_atual()

    def confirmar_item_atual(self) -> None:
        """Pede confirmação antes do salvamento."""

        numero_item, produto = (
            self.itens_lote[
                self.indice_atual
            ]
        )

        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.update()

        confirmar = messagebox.askyesno(
            "Confirmar salvamento",
            (
                f"Item {numero_item} de "
                f"{self.itens_lote[-1][0]}\n\n"
                f"Referência: {produto.referencia}\n\n"
                f"Descrição:\n"
                f"{produto.descricao_final}\n\n"
                "Clique em Sim para salvar e continuar.\n"
                "Clique em Não para interromper o lote."
            ),
            parent=self,
        )

        self.attributes("-topmost", False)

        if not confirmar:
            self.label_status.configure(
                text=(
                    "Lote interrompido. O cadastro atual "
                    "permaneceu aberto sem salvar."
                ),
                text_color="#B45309",
            )
            return

        self.withdraw()
        self.after(
            700,
            self.salvar_item_atual,
        )

    def salvar_item_atual(self) -> None:
        """Salva o produto e avança para o próximo."""

        salvar = self.calibracao[
            "pontos"
        ]["botao_salvar"]

        try:
            pyautogui.click(
                salvar["x"],
                salvar["y"],
            )

            time.sleep(2.8)

        except pyautogui.FailSafeException:
            self.mostrar_erro(
                "Salvamento interrompido pela proteção."
            )
            return

        except Exception as erro:
            self.mostrar_erro(
                f"Erro ao salvar item: {erro}"
            )
            return

        self.indice_atual += 1

        if self.indice_atual >= len(
            self.itens_lote
        ):
            self.finalizar_lote()
            return

        self.after(
            400,
            self.preparar_item_atual,
        )

    def finalizar_lote(self) -> None:
        """Finaliza o teste assistido."""

        self.deiconify()
        self.lift()
        self.focus_force()

        quantidade = len(
            self.itens_lote
        )

        self.label_status.configure(
            text=(
                f"Lote concluído: {quantidade} "
                "produtos processados."
            ),
            text_color="#166534",
        )

        messagebox.showinfo(
            "Lote concluído",
            (
                f"O teste processou {quantidade} produtos.\n\n"
                "Confira no ADM se todas as linhas receberam "
                "código, descrição de cadastro e vínculo."
            ),
            parent=self,
        )

    def mostrar_erro(
        self,
        mensagem: str,
    ) -> None:
        """Restaura a janela e mostra o erro."""

        self.deiconify()
        self.lift()
        self.focus_force()

        self.label_status.configure(
            text=mensagem,
            text_color="#991B1B",
        )

        messagebox.showerror(
            "Erro no lote",
            mensagem,
            parent=self,
        )


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = BatchTestWindow()
    app.mainloop()


if __name__ == "__main__":
    main()