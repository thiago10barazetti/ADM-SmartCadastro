import time
from collections.abc import Callable

import pyautogui
import pyperclip
from PIL import Image
from tkinter import messagebox

from automation.calibration_repository import (
    carregar_calibracao,
)
from automation.code_detector import (
    calcular_proporcao_fundo,
    detectar_estado_codigo,
    obter_cor_fundo_selecao,
    obter_geometria_tabela,
    resolver_caminho,
)


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


PONTOS_NECESSARIOS = (
    "mais_primeira_linha",
    "mais_segunda_linha",
    "aba_tributacao",
    "botao_salvar",
)


class CadastroAssistido:
    """
    Controla o cadastro assistido dos produtos no ADM.

    Fluxo:
    - verifica a coluna Código;
    - pula produtos já cadastrados;
    - prepara produtos com Código vazio;
    - interrompe em resultado incerto ou erro;
    - pede confirmação antes de cada salvamento.
    """

    def __init__(
        self,
        master,
        produtos: list,
        ao_atualizar_status: (
            Callable[[str, str], None] | None
        ) = None,
        ao_encerrar: (
            Callable[[str, dict], None] | None
        ) = None,
    ) -> None:
        self.master = master
        self.produtos = list(produtos)

        self.ao_atualizar_status = (
            ao_atualizar_status
        )
        self.ao_encerrar = ao_encerrar

        self.calibracao: dict = {}
        self.indice_atual = 0
        self.em_execucao = False

        self.itens_pulados: list[int] = []
        self.itens_salvos: list[int] = []

        self.cor_fundo_selecao: (
            tuple[int, int, int] | None
        ) = None
        self.proporcao_referencia = 0.0

    def iniciar(self) -> bool:
        """Valida o ambiente e inicia o cadastro."""

        if self.em_execucao:
            return False

        if not self.produtos:
            messagebox.showwarning(
                "Produtos necessários",
                "Nenhum produto foi carregado.",
                parent=self.master,
            )
            return False

        try:
            self.calibracao = carregar_calibracao()
            self.validar_calibracao()
            self.carregar_referencia_selecao()

        except (
            ValueError,
            FileNotFoundError,
            OSError,
            KeyError,
        ) as erro:
            messagebox.showerror(
                "Calibração inválida",
                str(erro),
                parent=self.master,
            )
            return False

        quantidade = len(self.produtos)

        confirmar = messagebox.askokcancel(
            "Confirmar cadastro",
            (
                f"Serão verificados {quantidade} produtos.\n\n"
                "• Produtos já cadastrados serão pulados.\n"
                "• Produtos não cadastrados serão preparados.\n"
                "• Antes de cada salvamento haverá confirmação.\n"
                "• Resultado incerto ou erro interromperá o processo.\n\n"
                "Confirme que o ADM está maximizado e que "
                "a mesma nota do XML está aberta.\n\n"
                "Emergência: mova o mouse para o canto "
                "superior esquerdo."
            ),
            parent=self.master,
        )

        if not confirmar:
            return False

        self.indice_atual = 0
        self.itens_pulados = []
        self.itens_salvos = []
        self.em_execucao = True

        self.atualizar_status(
            "Iniciando verificação dos produtos...",
            "#2563EB",
        )

        self.master.withdraw()
        self.master.after(
            600,
            self.verificar_item_atual,
        )
        return True

    def validar_calibracao(self) -> None:
        """Confere pontos, coluna Código e resolução."""

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
            raise ValueError(
                "Calibração incompleta. Pontos faltantes: "
                + ", ".join(faltantes)
            )

        if not self.calibracao.get(
            "codigo_produto"
        ):
            raise ValueError(
                "A calibração da coluna Código "
                "não foi encontrada."
            )

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
            raise ValueError(
                "A resolução atual é diferente "
                "da resolução usada na calibração."
            )

    def carregar_referencia_selecao(self) -> None:
        """Carrega a referência visual da célula selecionada."""

        configuracao = self.calibracao[
            "codigo_produto"
        ]

        caminho_preenchido = resolver_caminho(
            configuracao[
                "template_preenchido"
            ]
        )
        caminho_vazio = resolver_caminho(
            configuracao[
                "template_vazio"
            ]
        )

        if not caminho_preenchido.exists():
            raise FileNotFoundError(
                "Captura preenchida não encontrada: "
                f"{caminho_preenchido}"
            )

        if not caminho_vazio.exists():
            raise FileNotFoundError(
                "Captura vazia não encontrada: "
                f"{caminho_vazio}"
            )

        with Image.open(
            caminho_preenchido
        ) as imagem:
            modelo_preenchido = (
                imagem.convert("RGB").copy()
            )

        with Image.open(
            caminho_vazio
        ) as imagem:
            modelo_vazio = (
                imagem.convert("RGB").copy()
            )

        self.cor_fundo_selecao = (
            obter_cor_fundo_selecao(
                modelo_preenchido=(
                    modelo_preenchido
                ),
                modelo_vazio=modelo_vazio,
            )
        )

        proporcao_preenchido = (
            calcular_proporcao_fundo(
                modelo_preenchido,
                self.cor_fundo_selecao,
            )
        )
        proporcao_vazio = (
            calcular_proporcao_fundo(
                modelo_vazio,
                self.cor_fundo_selecao,
            )
        )

        self.proporcao_referencia = min(
            proporcao_preenchido,
            proporcao_vazio,
        )

        if self.proporcao_referencia <= 0:
            raise ValueError(
                "A referência visual da seleção é inválida."
            )

    def verificar_item_atual(self) -> None:
        """Verifica se o item atual já está cadastrado."""

        if not self.em_execucao:
            return

        if self.indice_atual >= len(
            self.produtos
        ):
            self.finalizar()
            return

        numero_item = self.indice_atual + 1

        self.atualizar_status(
            (
                f"Verificando item {numero_item} "
                f"de {len(self.produtos)}..."
            ),
            "#2563EB",
        )

        try:
            resultado = detectar_estado_codigo(
                calibracao=self.calibracao,
                numero_item=numero_item,
            )

        except pyautogui.FailSafeException:
            self.interromper_com_erro(
                "Cadastro interrompido pela proteção."
            )
            return

        except Exception as erro:
            self.interromper_com_erro(
                (
                    f"Erro ao verificar o item "
                    f"{numero_item}: {erro}"
                )
            )
            return

        if resultado.estado == "preenchido":
            self.itens_pulados.append(
                numero_item
            )
            self.indice_atual += 1

            self.master.after(
                450,
                self.verificar_item_atual,
            )
            return

        if resultado.estado == "incerto":
            self.interromper_com_erro(
                (
                    f"O item {numero_item} apresentou "
                    "resultado incerto na coluna Código.\n\n"
                    "O cadastro foi interrompido sem "
                    "abrir esse produto."
                )
            )
            return

        if resultado.estado != "vazio":
            self.interromper_com_erro(
                (
                    f"O item {numero_item} retornou "
                    f"um estado desconhecido: "
                    f"{resultado.estado}"
                )
            )
            return

        self.master.after(
            350,
            self.preparar_item_atual,
        )

    def localizar_y_linha_selecionada(
        self,
    ) -> int:
        """Localiza a posição vertical real da linha selecionada."""

        if self.cor_fundo_selecao is None:
            raise ValueError(
                "A referência visual da seleção "
                "não foi carregada."
            )

        configuracao = self.calibracao[
            "codigo_produto"
        ]

        coluna_x = int(
            configuracao["coluna_x"]
        )
        largura = int(
            configuracao.get(
                "largura_captura",
                36,
            )
        )
        altura = int(
            configuracao.get(
                "altura_captura",
                14,
            )
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
            topo = (
                centro_y - altura // 2
            )

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
                cor_fundo=(
                    self.cor_fundo_selecao
                ),
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
                "Não foi possível localizar "
                "a linha selecionada."
            )

        limite_faixa = (
            melhor_proporcao * 0.78
        )

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
        """Abre e prepara o cadastro do produto atual."""

        if not self.em_execucao:
            return

        numero_item = self.indice_atual + 1
        produto = self.produtos[
            self.indice_atual
        ]
        pontos = self.calibracao[
            "pontos"
        ]

        self.atualizar_status(
            (
                f"Preparando item {numero_item} "
                f"de {len(self.produtos)}..."
            ),
            "#2563EB",
        )

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
            self.interromper_com_erro(
                "Cadastro interrompido pela proteção."
            )
            return

        except Exception as erro:
            self.interromper_com_erro(
                (
                    f"Erro ao preparar o item "
                    f"{numero_item}: {erro}"
                )
            )
            return

        self.confirmar_item_atual()

    def confirmar_item_atual(self) -> None:
        """Pede confirmação antes do salvamento."""

        if not self.em_execucao:
            return

        numero_item = self.indice_atual + 1
        produto = self.produtos[
            self.indice_atual
        ]

        self.restaurar_janela()

        confirmar = messagebox.askyesno(
            "Confirmar salvamento",
            (
                f"Item {numero_item} de "
                f"{len(self.produtos)}\n\n"
                f"Referência: {produto.referencia}\n\n"
                f"Descrição:\n"
                f"{produto.descricao_final}\n\n"
                "Clique em Sim para salvar e continuar.\n"
                "Clique em Não para interromper."
            ),
            parent=self.master,
        )

        self.master.attributes(
            "-topmost",
            False,
        )

        if not confirmar:
            self.em_execucao = False

            self.atualizar_status(
                (
                    "Cadastro interrompido. O produto atual "
                    "permaneceu aberto sem salvar."
                ),
                "#B45309",
            )

            self.encerrar_callback(
                "interrompido"
            )
            return

        self.master.withdraw()
        self.master.after(
            700,
            self.salvar_item_atual,
        )

    def salvar_item_atual(self) -> None:
        """Salva o produto e avança para o próximo."""

        if not self.em_execucao:
            return

        numero_item = self.indice_atual + 1

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
            self.interromper_com_erro(
                "Salvamento interrompido pela proteção."
            )
            return

        except Exception as erro:
            self.interromper_com_erro(
                (
                    f"Erro ao salvar o item "
                    f"{numero_item}: {erro}"
                )
            )
            return

        self.itens_salvos.append(
            numero_item
        )
        self.indice_atual += 1

        self.master.after(
            500,
            self.verificar_item_atual,
        )

    def finalizar(self) -> None:
        """Finaliza o cadastro e mostra o resumo."""

        self.em_execucao = False
        self.restaurar_janela()

        total = len(self.produtos)
        salvos = len(self.itens_salvos)
        pulados = len(self.itens_pulados)

        self.atualizar_status(
            (
                f"Cadastro concluído: {salvos} salvos e "
                f"{pulados} já cadastrados."
            ),
            "#166534",
        )

        salvos_texto = self.formatar_itens(
            self.itens_salvos
        )
        pulados_texto = self.formatar_itens(
            self.itens_pulados
        )

        messagebox.showinfo(
            "Cadastro concluído",
            (
                f"Itens verificados: {total}\n"
                f"Itens salvos: {salvos}\n"
                f"Itens já cadastrados e pulados: {pulados}\n\n"
                f"Salvos: {salvos_texto}\n"
                f"Pulados: {pulados_texto}\n\n"
                "Confira no ADM os produtos processados."
            ),
            parent=self.master,
        )

        self.encerrar_callback(
            "concluido"
        )

    def interromper_com_erro(
        self,
        mensagem: str,
    ) -> None:
        """Interrompe o cadastro e mostra o erro."""

        self.em_execucao = False
        self.restaurar_janela()

        self.atualizar_status(
            mensagem,
            "#991B1B",
        )

        messagebox.showerror(
            "Erro no cadastro",
            mensagem,
            parent=self.master,
        )

        self.encerrar_callback(
            "erro"
        )

    def restaurar_janela(self) -> None:
        """Restaura a janela principal em primeiro plano."""

        self.master.deiconify()
        self.master.lift()
        self.master.focus_force()
        self.master.attributes(
            "-topmost",
            True,
        )
        self.master.update()

    def atualizar_status(
        self,
        texto: str,
        cor: str,
    ) -> None:
        """Envia uma atualização de status à interface."""

        if self.ao_atualizar_status is not None:
            self.ao_atualizar_status(
                texto,
                cor,
            )

    def encerrar_callback(
        self,
        resultado: str,
    ) -> None:
        """Informa à interface que o processo terminou."""

        if self.ao_encerrar is None:
            return

        resumo = {
            "total": len(self.produtos),
            "salvos": len(
                self.itens_salvos
            ),
            "pulados": len(
                self.itens_pulados
            ),
            "itens_salvos": list(
                self.itens_salvos
            ),
            "itens_pulados": list(
                self.itens_pulados
            ),
        }

        self.ao_encerrar(
            resultado,
            resumo,
        )

    @staticmethod
    def formatar_itens(
        itens: list[int],
    ) -> str:
        """Formata uma lista de números de itens."""

        if not itens:
            return "nenhum"

        return ", ".join(
            str(item)
            for item in itens
        )
