import time
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyautogui
import pyperclip
from PIL import Image

from automation.calibration_repository import carregar_calibracao
from automation.code_detector import (
    calcular_proporcao_fundo,
    detectar_estado_codigo,
    obter_cor_fundo_selecao,
    obter_geometria_tabela,
    resolver_caminho,
)
from database.settings_repository import carregar_configuracoes
from services.preparacao_produtos import preparar_produtos
from xml_reader.nfe_reader import ler_produtos_xml


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15

PONTOS_NECESSARIOS = (
    "mais_primeira_linha",
    "mais_segunda_linha",
    "aba_tributacao",
    "botao_salvar",
)

MAXIMO_ITENS_TESTE = 5


class BatchTestWindow(ctk.CTk):
    """Executa lote assistido, pulando produtos já cadastrados."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Teste de Lote Assistido")
        self.geometry("740x680")
        self.minsize(700, 630)
        self.configure(fg_color="#FFFFFF")

        self.calibracao = carregar_calibracao()
        self.configuracoes = carregar_configuracoes()
        self.limite_descricao = int(
            self.configuracoes.get("limite_descricao", 35)
        )

        self.caminho_xml: Path | None = None
        self.produtos = []
        self.itens_lote = []
        self.indice_atual = 0
        self.itens_pulados: list[int] = []
        self.itens_salvos: list[int] = []

        self.cor_fundo_selecao: tuple[int, int, int] | None = None
        self.proporcao_referencia = 0.0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.criar_interface()
        self.verificar_calibracao()

    def criar_interface(self) -> None:
        titulo = ctk.CTkLabel(
            self,
            text="Teste de lote assistido com detecção",
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
                "O programa verificará cada item pela coluna Código.\n\n"
                "Itens já cadastrados serão pulados. Itens não cadastrados "
                "serão preparados e pedirão confirmação antes do salvamento."
            ),
            anchor="w",
            justify="left",
            wraplength=670,
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
        self.campo_quantidade.insert(0, "5")

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
        self.campo_resumo.configure(state="disabled")

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
        pontos = self.calibracao.get("pontos", {})

        faltantes = [
            ponto
            for ponto in PONTOS_NECESSARIOS
            if ponto not in pontos
        ]

        if faltantes:
            self.desabilitar_por_erro(
                "Calibração incompleta. Pontos faltantes: "
                + ", ".join(faltantes)
            )
            return

        if not self.calibracao.get("codigo_produto"):
            self.desabilitar_por_erro(
                "A calibração da coluna Código não foi encontrada."
            )
            return

        tela_calibrada = self.calibracao.get("tela", {})
        tela_atual = pyautogui.size()

        if (
            tela_calibrada.get("largura") != tela_atual.width
            or tela_calibrada.get("altura") != tela_atual.height
        ):
            self.desabilitar_por_erro(
                "A resolução atual é diferente da calibração."
            )
            return

        try:
            self.carregar_referencia_selecao()

        except (
            ValueError,
            FileNotFoundError,
            OSError,
        ) as erro:
            self.desabilitar_por_erro(
                f"Erro na calibração da coluna Código: {erro}"
            )
            return

        self.label_status.configure(
            text=(
                f"Calibração válida: "
                f"{tela_atual.width} x {tela_atual.height}."
            ),
            text_color="#166534",
        )

    def desabilitar_por_erro(self, mensagem: str) -> None:
        self.label_status.configure(
            text=mensagem,
            text_color="#991B1B",
        )
        self.botao_executar.configure(state="disabled")

    def carregar_referencia_selecao(self) -> None:
        configuracao = self.calibracao["codigo_produto"]

        caminho_preenchido = resolver_caminho(
            configuracao["template_preenchido"]
        )
        caminho_vazio = resolver_caminho(
            configuracao["template_vazio"]
        )

        if not caminho_preenchido.exists():
            raise FileNotFoundError(
                f"Captura preenchida não encontrada: "
                f"{caminho_preenchido}"
            )

        if not caminho_vazio.exists():
            raise FileNotFoundError(
                f"Captura vazia não encontrada: "
                f"{caminho_vazio}"
            )

        with Image.open(caminho_preenchido) as imagem:
            modelo_preenchido = imagem.convert("RGB").copy()

        with Image.open(caminho_vazio) as imagem:
            modelo_vazio = imagem.convert("RGB").copy()

        self.cor_fundo_selecao = obter_cor_fundo_selecao(
            modelo_preenchido=modelo_preenchido,
            modelo_vazio=modelo_vazio,
        )

        proporcao_preenchido = calcular_proporcao_fundo(
            modelo_preenchido,
            self.cor_fundo_selecao,
        )
        proporcao_vazio = calcular_proporcao_fundo(
            modelo_vazio,
            self.cor_fundo_selecao,
        )

        self.proporcao_referencia = min(
            proporcao_preenchido,
            proporcao_vazio,
        )

        if self.proporcao_referencia <= 0:
            raise ValueError(
                "A referência visual da seleção é inválida."
            )

    def selecionar_xml(self) -> None:
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
            produtos = ler_produtos_xml(Path(caminho))
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
        linhas = []

        for numero, produto in enumerate(
            self.produtos,
            start=1,
        ):
            quantidade = len(produto.descricao_final)

            linhas.append(
                f"{numero:02d}. "
                f"{produto.referencia} | "
                f"{produto.descricao_final} | "
                f"{quantidade}/{self.limite_descricao}"
            )

        self.campo_resumo.configure(state="normal")
        self.campo_resumo.delete("1.0", "end")
        self.campo_resumo.insert(
            "1.0",
            "\n".join(linhas),
        )
        self.campo_resumo.configure(state="disabled")

    def preparar_lote(self) -> None:
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

        if quantidade > MAXIMO_ITENS_TESTE:
            messagebox.showwarning(
                "Lote muito grande",
                (
                    "Neste primeiro teste integrado, use no máximo "
                    f"{MAXIMO_ITENS_TESTE} produtos."
                ),
                parent=self,
            )
            return

        item_final = item_inicial + quantidade - 1

        if item_final > len(self.produtos):
            messagebox.showwarning(
                "Lote inválido",
                "O lote ultrapassa os produtos do XML.",
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
                f"Serão verificados {quantidade} produtos, "
                f"do item {item_inicial} ao {item_final}.\n\n"
                "• Produtos já cadastrados serão pulados.\n"
                "• Produtos não cadastrados serão preparados.\n"
                "• Antes de cada salvamento haverá confirmação.\n"
                "• Resultado incerto ou erro interromperá o lote.\n\n"
                "Confirme que o ADM está maximizado e que "
                "a mesma nota do XML está aberta."
            ),
            parent=self,
        )

        if not confirmar:
            return

        self.itens_lote = selecionados
        self.indice_atual = 0
        self.itens_pulados = []
        self.itens_salvos = []

        self.label_status.configure(
            text="Iniciando lote assistido...",
            text_color="#2563EB",
        )

        self.withdraw()
        self.after(
            600,
            self.verificar_item_atual,
        )

    def verificar_item_atual(self) -> None:
        if self.indice_atual >= len(
            self.itens_lote
        ):
            self.finalizar_lote()
            return

        numero_item, _ = self.itens_lote[
            self.indice_atual
        ]

        try:
            resultado = detectar_estado_codigo(
                calibracao=self.calibracao,
                numero_item=numero_item,
            )

        except pyautogui.FailSafeException:
            self.mostrar_erro(
                "Lote interrompido pela proteção."
            )
            return

        except Exception as erro:
            self.mostrar_erro(
                f"Erro ao verificar o item {numero_item}: {erro}"
            )
            return

        if resultado.estado == "preenchido":
            self.itens_pulados.append(numero_item)
            self.indice_atual += 1
            self.after(
                450,
                self.verificar_item_atual,
            )
            return

        if resultado.estado == "incerto":
            self.mostrar_erro(
                (
                    f"O item {numero_item} apresentou resultado "
                    "incerto na coluna Código.\n\n"
                    "O lote foi interrompido sem abrir o cadastro."
                )
            )
            return

        if resultado.estado != "vazio":
            self.mostrar_erro(
                (
                    f"O item {numero_item} retornou um estado "
                    f"desconhecido: {resultado.estado}"
                )
            )
            return

        self.after(
            350,
            self.preparar_item_atual,
        )

    def localizar_y_linha_selecionada(self) -> int:
        if self.cor_fundo_selecao is None:
            raise ValueError(
                "A referência visual da seleção não foi carregada."
            )

        configuracao = self.calibracao["codigo_produto"]
        coluna_x = int(configuracao["coluna_x"])
        largura = int(
            configuracao.get("largura_captura", 36)
        )
        altura = int(
            configuracao.get("altura_captura", 14)
        )

        (
            primeira_y,
            altura_linha,
            limite_y,
        ) = obter_geometria_tabela(
            self.calibracao
        )

        tela = pyautogui.screenshot()

        esquerda = max(
            0,
            coluna_x - largura // 2,
        )

        if esquerda + largura > tela.width:
            esquerda = tela.width - largura

        inicio_busca = max(
            altura // 2,
            primeira_y - altura_linha,
        )
        fim_busca = min(
            tela.height - altura // 2,
            limite_y,
        )

        resultados: list[
            tuple[int, float]
        ] = []

        for centro_y in range(
            inicio_busca,
            fim_busca + 1,
        ):
            topo = centro_y - altura // 2

            imagem = tela.crop(
                (
                    esquerda,
                    topo,
                    esquerda + largura,
                    topo + altura,
                )
            )

            proporcao = calcular_proporcao_fundo(
                imagem=imagem,
                cor_fundo=self.cor_fundo_selecao,
            )

            resultados.append(
                (centro_y, proporcao)
            )

        if not resultados:
            raise RuntimeError(
                "Não foi possível analisar a tabela."
            )

        melhor_y, melhor_proporcao = max(
            resultados,
            key=lambda resultado: resultado[1],
        )

        limite_minimo = max(
            0.08,
            self.proporcao_referencia * 0.30,
        )

        if melhor_proporcao < limite_minimo:
            raise RuntimeError(
                "Não foi possível localizar a linha selecionada."
            )

        limite_faixa = melhor_proporcao * 0.78

        candidatos = [
            centro_y
            for centro_y, proporcao in resultados
            if (
                proporcao >= limite_faixa
                and abs(
                    centro_y - melhor_y
                ) <= altura_linha
            )
        ]

        if candidatos:
            return round(
                (
                    min(candidatos)
                    + max(candidatos)
                )
                / 2
            )

        return melhor_y

    def preparar_item_atual(self) -> None:
        numero_item, produto = self.itens_lote[
            self.indice_atual
        ]
        pontos = self.calibracao["pontos"]

        try:
            linha_y = (
                self.localizar_y_linha_selecionada()
            )

            x_mais = int(
                pontos[
                    "mais_primeira_linha"
                ]["x"]
            )

            pyautogui.moveTo(
                x_mais,
                linha_y,
                duration=0.55,
            )
            time.sleep(0.5)

            pyautogui.doubleClick(
                x_mais,
                linha_y,
                interval=0.20,
            )
            time.sleep(1.7)

            pyautogui.press(
                "tab",
                presses=4,
                interval=0.20,
            )

            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.3)

            pyperclip.copy(
                produto.descricao_final
            )
            time.sleep(0.2)

            pyautogui.hotkey("ctrl", "v")
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
                (
                    f"Erro ao preparar o item "
                    f"{numero_item}: {erro}"
                )
            )
            return

        self.confirmar_item_atual()

    def confirmar_item_atual(self) -> None:
        numero_item, produto = self.itens_lote[
            self.indice_atual
        ]

        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.update()

        confirmar = messagebox.askyesno(
            "Confirmar salvamento",
            (
                f"Item {numero_item}\n\n"
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
        numero_item, _ = self.itens_lote[
            self.indice_atual
        ]

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
                f"Erro ao salvar o item {numero_item}: {erro}"
            )
            return

        self.itens_salvos.append(numero_item)
        self.indice_atual += 1

        self.after(
            500,
            self.verificar_item_atual,
        )

    def finalizar_lote(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()

        total = len(self.itens_lote)
        salvos = len(self.itens_salvos)
        pulados = len(self.itens_pulados)

        self.label_status.configure(
            text=(
                f"Lote concluído: {salvos} salvos e "
                f"{pulados} já cadastrados."
            ),
            text_color="#166534",
        )

        salvos_texto = (
            ", ".join(
                str(item)
                for item in self.itens_salvos
            )
            if self.itens_salvos
            else "nenhum"
        )

        pulados_texto = (
            ", ".join(
                str(item)
                for item in self.itens_pulados
            )
            if self.itens_pulados
            else "nenhum"
        )

        messagebox.showinfo(
            "Lote concluído",
            (
                f"Itens verificados: {total}\n"
                f"Itens salvos: {salvos}\n"
                f"Itens já cadastrados e pulados: {pulados}\n\n"
                f"Salvos: {salvos_texto}\n"
                f"Pulados: {pulados_texto}\n\n"
                "Confira no ADM os produtos salvos."
            ),
            parent=self,
        )

    def mostrar_erro(
        self,
        mensagem: str,
    ) -> None:
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
