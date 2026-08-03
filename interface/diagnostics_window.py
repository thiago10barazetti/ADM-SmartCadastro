import subprocess
import sys
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
import pyautogui
from PIL import Image

from automation.calibration_repository import (
    carregar_calibracao,
)
from automation.code_detector import (
    detectar_estado_codigo,
    resolver_caminho,
)
from interface.styles import (
    COR_AZUL,
    COR_AZUL_HOVER,
    COR_BORDA,
    COR_BORDA_ESCURA,
    COR_ERRO_TEXTO,
    COR_FUNDO,
    COR_FUNDO_SECUNDARIO,
    COR_TEXTO,
    COR_TEXTO_BOTAO,
    COR_TEXTO_SECUNDARIO,
    FONTE_PRINCIPAL,
    TAMANHO_BOTAO,
    TAMANHO_SUBTITULO,
    TAMANHO_TEXTO,
    TAMANHO_TEXTO_DESTAQUE,
    TAMANHO_TITULO,
)


PONTOS_NECESSARIOS = (
    "mais_primeira_linha",
    "mais_segunda_linha",
    "limite_inferior_tabela",
    "aba_tributacao",
    "botao_salvar",
)


class DiagnosticsWindow(ctk.CTkToplevel):
    """Exibe o diagnóstico da calibração e do detector."""

    def __init__(
        self,
        master,
    ) -> None:
        super().__init__(master)

        self.title("Diagnóstico e calibração")
        self.geometry("1040x760")
        self.minsize(900, 650)
        self.configure(fg_color=COR_FUNDO)

        self.calibracao: dict = {}
        self.diagnostico_pronto = False

        self.imagem_preenchido: (
            ctk.CTkImage | None
        ) = None
        self.imagem_vazio: (
            ctk.CTkImage | None
        ) = None

        self.grid_columnconfigure(
            0,
            weight=1,
        )
        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self.criar_cabecalho()
        self.criar_conteudo()
        self.atualizar_diagnostico()

        self.after(
            150,
            self.lift,
        )

    def criar_cabecalho(self) -> None:
        """Cria o cabeçalho da janela."""

        cabecalho = ctk.CTkFrame(
            self,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        cabecalho.grid(
            row=0,
            column=0,
            padx=28,
            pady=(22, 14),
            sticky="ew",
        )
        cabecalho.grid_columnconfigure(
            0,
            weight=1,
        )

        titulo = ctk.CTkLabel(
            cabecalho,
            text="Diagnóstico e calibração",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TITULO,
                weight="bold",
            ),
        )
        titulo.grid(
            row=0,
            column=0,
            sticky="w",
        )

        subtitulo = ctk.CTkLabel(
            cabecalho,
            text=(
                "Confira a resolução, os pontos calibrados, "
                "as imagens do detector e faça uma leitura de teste."
            ),
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_SUBTITULO,
            ),
        )
        subtitulo.grid(
            row=1,
            column=0,
            pady=(3, 0),
            sticky="w",
        )

        botao_atualizar = ctk.CTkButton(
            cabecalho,
            text="Atualizar",
            width=110,
            height=36,
            corner_radius=4,
            fg_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            text_color=COR_TEXTO_BOTAO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
                weight="bold",
            ),
            command=self.atualizar_diagnostico,
        )
        botao_atualizar.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=(14, 0),
            sticky="e",
        )

    def criar_conteudo(self) -> None:
        """Cria os cartões e detalhes do diagnóstico."""

        self.area_rolagem = ctk.CTkScrollableFrame(
            self,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        self.area_rolagem.grid(
            row=1,
            column=0,
            padx=28,
            pady=(0, 24),
            sticky="nsew",
        )
        self.area_rolagem.grid_columnconfigure(
            0,
            weight=1,
        )

        area_status = ctk.CTkFrame(
            self.area_rolagem,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        area_status.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        for coluna in range(4):
            area_status.grid_columnconfigure(
                coluna,
                weight=1,
            )

        (
            self.valor_status_geral,
            self.detalhe_status_geral,
        ) = self.criar_cartao(
            area_status,
            coluna=0,
            titulo="Status geral",
        )

        (
            self.valor_resolucao,
            self.detalhe_resolucao,
        ) = self.criar_cartao(
            area_status,
            coluna=1,
            titulo="Resolução",
        )

        (
            self.valor_pontos,
            self.detalhe_pontos,
        ) = self.criar_cartao(
            area_status,
            coluna=2,
            titulo="Pontos",
        )

        (
            self.valor_detector,
            self.detalhe_detector,
        ) = self.criar_cartao(
            area_status,
            coluna=3,
            titulo="Detector",
        )

        self.criar_secao_pontos()
        self.criar_secao_detector()
        self.criar_secao_teste()
        self.criar_secao_calibrador()

    def criar_cartao(
        self,
        master,
        coluna: int,
        titulo: str,
    ) -> tuple[ctk.CTkLabel, ctk.CTkLabel]:
        """Cria um cartão de resumo."""

        cartao = ctk.CTkFrame(
            master,
            fg_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=5,
        )
        cartao.grid(
            row=0,
            column=coluna,
            padx=(
                0 if coluna == 0 else 6,
                0 if coluna == 3 else 6,
            ),
            sticky="nsew",
        )

        label_titulo = ctk.CTkLabel(
            cartao,
            text=titulo,
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        label_titulo.grid(
            row=0,
            column=0,
            padx=14,
            pady=(12, 2),
            sticky="ew",
        )

        label_valor = ctk.CTkLabel(
            cartao,
            text="Verificando...",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO_DESTAQUE,
                weight="bold",
            ),
        )
        label_valor.grid(
            row=1,
            column=0,
            padx=14,
            sticky="ew",
        )

        label_detalhe = ctk.CTkLabel(
            cartao,
            text="",
            anchor="w",
            justify="left",
            wraplength=195,
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        label_detalhe.grid(
            row=2,
            column=0,
            padx=14,
            pady=(3, 12),
            sticky="ew",
        )

        return label_valor, label_detalhe

    def criar_secao_pontos(self) -> None:
        """Cria a seção com os pontos calibrados."""

        secao = ctk.CTkFrame(
            self.area_rolagem,
            fg_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=5,
        )
        secao.grid(
            row=1,
            column=0,
            pady=(16, 0),
            sticky="ew",
        )
        secao.grid_columnconfigure(
            0,
            weight=1,
        )

        titulo = ctk.CTkLabel(
            secao,
            text="Pontos e cálculos da tabela",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO_DESTAQUE,
                weight="bold",
            ),
        )
        titulo.grid(
            row=0,
            column=0,
            padx=16,
            pady=(14, 8),
            sticky="ew",
        )

        self.texto_pontos = ctk.CTkTextbox(
            secao,
            height=165,
            fg_color=COR_FUNDO,
            text_color=COR_TEXTO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=4,
            font=ctk.CTkFont(
                family="Consolas",
                size=12,
            ),
        )
        self.texto_pontos.grid(
            row=1,
            column=0,
            padx=16,
            pady=(0, 16),
            sticky="ew",
        )
        self.texto_pontos.configure(
            state="disabled"
        )

    def criar_secao_detector(self) -> None:
        """Cria a seção das imagens do detector."""

        secao = ctk.CTkFrame(
            self.area_rolagem,
            fg_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=5,
        )
        secao.grid(
            row=2,
            column=0,
            pady=(16, 0),
            sticky="ew",
        )
        secao.grid_columnconfigure(
            0,
            weight=1,
        )
        secao.grid_columnconfigure(
            1,
            weight=1,
        )

        titulo = ctk.CTkLabel(
            secao,
            text="Referências visuais da coluna Código",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO_DESTAQUE,
                weight="bold",
            ),
        )
        titulo.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=16,
            pady=(14, 8),
            sticky="ew",
        )

        self.label_imagem_preenchido = (
            self.criar_preview_detector(
                secao,
                coluna=0,
                titulo="Código preenchido",
            )
        )
        self.label_imagem_vazio = (
            self.criar_preview_detector(
                secao,
                coluna=1,
                titulo="Código vazio",
            )
        )

        self.label_dados_detector = ctk.CTkLabel(
            secao,
            text="Aguardando a calibração...",
            anchor="w",
            justify="left",
            wraplength=900,
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        self.label_dados_detector.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=16,
            pady=(4, 16),
            sticky="ew",
        )

    def criar_preview_detector(
        self,
        master,
        coluna: int,
        titulo: str,
    ) -> ctk.CTkLabel:
        """Cria um quadro de pré-visualização."""

        quadro = ctk.CTkFrame(
            master,
            fg_color=COR_FUNDO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=4,
        )
        quadro.grid(
            row=1,
            column=coluna,
            padx=(
                16 if coluna == 0 else 8,
                8 if coluna == 0 else 16,
            ),
            pady=(0, 10),
            sticky="nsew",
        )

        label_titulo = ctk.CTkLabel(
            quadro,
            text=titulo,
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
                weight="bold",
            ),
        )
        label_titulo.grid(
            row=0,
            column=0,
            padx=12,
            pady=(10, 5),
        )

        label_imagem = ctk.CTkLabel(
            quadro,
            text="Imagem não encontrada",
            width=300,
            height=100,
            fg_color="#E5E7EB",
            corner_radius=3,
            text_color=COR_TEXTO_SECUNDARIO,
        )
        label_imagem.grid(
            row=1,
            column=0,
            padx=12,
            pady=(0, 12),
            sticky="ew",
        )

        return label_imagem

    def criar_secao_teste(self) -> None:
        """Cria o teste de leitura da coluna Código."""

        secao = ctk.CTkFrame(
            self.area_rolagem,
            fg_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=5,
        )
        secao.grid(
            row=3,
            column=0,
            pady=(16, 0),
            sticky="ew",
        )
        secao.grid_columnconfigure(
            1,
            weight=1,
        )

        titulo = ctk.CTkLabel(
            secao,
            text="Teste de leitura — somente leitura",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO_DESTAQUE,
                weight="bold",
            ),
        )
        titulo.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=16,
            pady=(14, 4),
            sticky="ew",
        )

        explicacao = ctk.CTkLabel(
            secao,
            text=(
                "O teste apenas seleciona o item e analisa a célula Código. "
                "Ele não abre cadastro e não salva alterações."
            ),
            anchor="w",
            justify="left",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        explicacao.grid(
            row=1,
            column=0,
            columnspan=3,
            padx=16,
            pady=(0, 12),
            sticky="ew",
        )

        label_item = ctk.CTkLabel(
            secao,
            text="Número do item",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
                weight="bold",
            ),
        )
        label_item.grid(
            row=2,
            column=0,
            padx=(16, 8),
            pady=(0, 14),
        )

        self.campo_item = ctk.CTkEntry(
            secao,
            width=90,
            height=36,
            corner_radius=4,
        )
        self.campo_item.grid(
            row=2,
            column=1,
            pady=(0, 14),
            sticky="w",
        )
        self.campo_item.insert(
            0,
            "1",
        )

        self.botao_testar = ctk.CTkButton(
            secao,
            text="Testar leitura",
            width=150,
            height=36,
            corner_radius=4,
            fg_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            text_color=COR_TEXTO_BOTAO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
                weight="bold",
            ),
            command=self.preparar_teste_leitura,
        )
        self.botao_testar.grid(
            row=2,
            column=2,
            padx=16,
            pady=(0, 14),
            sticky="e",
        )

        self.label_resultado_teste = ctk.CTkLabel(
            secao,
            text="Nenhum teste executado.",
            anchor="w",
            justify="left",
            wraplength=900,
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        self.label_resultado_teste.grid(
            row=3,
            column=0,
            columnspan=3,
            padx=16,
            pady=(0, 14),
            sticky="ew",
        )

    def criar_secao_calibrador(self) -> None:
        """Cria a seção com as três etapas de calibração."""

        secao = ctk.CTkFrame(
            self.area_rolagem,
            fg_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=5,
        )
        secao.grid(
            row=4,
            column=0,
            pady=(16, 0),
            sticky="ew",
        )

        for coluna in range(3):
            secao.grid_columnconfigure(
                coluna,
                weight=1,
            )

        titulo = ctk.CTkLabel(
            secao,
            text="Configurar este computador",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO_DESTAQUE,
                weight="bold",
            ),
        )
        titulo.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=16,
            pady=(14, 4),
            sticky="ew",
        )

        explicacao = ctk.CTkLabel(
            secao,
            text=(
                "Cada computador começa sem calibração. Execute as "
                "três etapas abaixo depois de abrir o Cadastro de "
                "Produtos no ADM. O SmartCadastro será fechado ao "
                "abrir uma ferramenta."
            ),
            anchor="w",
            justify="left",
            wraplength=850,
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        explicacao.grid(
            row=1,
            column=0,
            columnspan=3,
            padx=16,
            pady=(0, 12),
            sticky="ew",
        )

        botoes = (
            (
                "1. Calibrar pontos",
                "--calibrar",
                "calibração dos pontos",
            ),
            (
                "2. Capturar códigos",
                "--capturar-codigos",
                "captura da coluna Código",
            ),
            (
                "3. Capturar vínculos",
                "--capturar-vinculos",
                "captura da coluna Vinc.",
            ),
        )

        for coluna, (
            texto,
            argumento,
            nome,
        ) in enumerate(botoes):
            botao = ctk.CTkButton(
                secao,
                text=texto,
                height=38,
                corner_radius=4,
                fg_color=(
                    COR_AZUL
                    if coluna == 0
                    else COR_FUNDO
                ),
                hover_color=(
                    COR_AZUL_HOVER
                    if coluna == 0
                    else COR_FUNDO_SECUNDARIO
                ),
                border_width=(
                    0
                    if coluna == 0
                    else 1
                ),
                border_color=COR_BORDA_ESCURA,
                text_color=(
                    COR_TEXTO_BOTAO
                    if coluna == 0
                    else COR_TEXTO
                ),
                font=ctk.CTkFont(
                    family=FONTE_PRINCIPAL,
                    size=TAMANHO_BOTAO,
                    weight="bold",
                ),
                command=lambda arg=argumento, titulo=nome: (
                    self.abrir_ferramenta_calibracao(
                        arg,
                        titulo,
                    )
                ),
            )
            botao.grid(
                row=2,
                column=coluna,
                padx=(
                    (16, 5)
                    if coluna == 0
                    else (
                        (5, 5)
                        if coluna == 1
                        else (5, 16)
                    )
                ),
                pady=(0, 14),
                sticky="ew",
            )

    def atualizar_diagnostico(self) -> None:
        """Recarrega e avalia a calibração."""

        problemas: list[str] = []

        try:
            self.calibracao = carregar_calibracao()

        except Exception as erro:
            self.calibracao = {}
            problemas.append(
                f"Não foi possível carregar a calibração: {erro}"
            )

        tela_atual = pyautogui.size()
        tela_calibrada = self.calibracao.get(
            "tela",
            {},
        )

        largura_calibrada = tela_calibrada.get(
            "largura"
        )
        altura_calibrada = tela_calibrada.get(
            "altura"
        )

        resolucao_ok = (
            largura_calibrada == tela_atual.width
            and altura_calibrada == tela_atual.height
        )

        if resolucao_ok:
            self.configurar_status(
                self.valor_resolucao,
                self.detalhe_resolucao,
                "Compatível",
                (
                    f"Atual e calibrada: "
                    f"{tela_atual.width} × {tela_atual.height}"
                ),
                True,
            )
        else:
            problemas.append(
                "A resolução atual não corresponde à calibração."
            )
            calibrada_texto = (
                f"{largura_calibrada} × {altura_calibrada}"
                if largura_calibrada and altura_calibrada
                else "não encontrada"
            )
            self.configurar_status(
                self.valor_resolucao,
                self.detalhe_resolucao,
                "Incompatível",
                (
                    f"Atual: {tela_atual.width} × {tela_atual.height}\n"
                    f"Calibrada: {calibrada_texto}"
                ),
                False,
            )

        pontos = self.calibracao.get(
            "pontos",
            {},
        )
        faltantes = [
            nome
            for nome in PONTOS_NECESSARIOS
            if nome not in pontos
        ]

        pontos_ok = not faltantes

        if pontos_ok:
            self.configurar_status(
                self.valor_pontos,
                self.detalhe_pontos,
                "Completos",
                (
                    f"{len(PONTOS_NECESSARIOS)}/"
                    f"{len(PONTOS_NECESSARIOS)} necessários"
                ),
                True,
            )
        else:
            problemas.append(
                "Existem pontos obrigatórios não calibrados."
            )
            self.configurar_status(
                self.valor_pontos,
                self.detalhe_pontos,
                "Incompletos",
                (
                    "Faltando: "
                    + ", ".join(faltantes)
                ),
                False,
            )

        detector_ok = self.atualizar_detector(
            problemas
        )
        self.atualizar_texto_pontos(
            pontos,
            faltantes,
        )

        self.diagnostico_pronto = (
            resolucao_ok
            and pontos_ok
            and detector_ok
        )

        if self.diagnostico_pronto:
            self.configurar_status(
                self.valor_status_geral,
                self.detalhe_status_geral,
                "Pronto",
                "Ambiente aprovado para uso.",
                True,
            )
            self.botao_testar.configure(
                state="normal"
            )
        else:
            self.configurar_status(
                self.valor_status_geral,
                self.detalhe_status_geral,
                "Atenção",
                (
                    problemas[0]
                    if problemas
                    else "Verifique os detalhes abaixo."
                ),
                False,
            )
            self.botao_testar.configure(
                state="disabled"
            )

    def atualizar_detector(
        self,
        problemas: list[str],
    ) -> bool:
        """Avalia e mostra as referências do detector."""

        configuracao = self.calibracao.get(
            "codigo_produto",
            {},
        )

        if not configuracao:
            problemas.append(
                "A configuração da coluna Código não foi encontrada."
            )
            self.configurar_status(
                self.valor_detector,
                self.detalhe_detector,
                "Ausente",
                "Execute a captura da coluna Código.",
                False,
            )
            self.limpar_previews()
            self.label_dados_detector.configure(
                text="Configuração do detector não encontrada."
            )
            return False

        try:
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

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as erro:
            problemas.append(
                f"Configuração inválida do detector: {erro}"
            )
            self.configurar_status(
                self.valor_detector,
                self.detalhe_detector,
                "Inválido",
                str(erro),
                False,
            )
            self.limpar_previews()
            return False

        preenchido_ok = caminho_preenchido.exists()
        vazio_ok = caminho_vazio.exists()
        detector_ok = preenchido_ok and vazio_ok

        if detector_ok:
            self.configurar_status(
                self.valor_detector,
                self.detalhe_detector,
                "Disponível",
                "As duas referências foram encontradas.",
                True,
            )
        else:
            problemas.append(
                "Uma ou mais imagens do detector não foram encontradas."
            )
            faltando = []

            if not preenchido_ok:
                faltando.append(
                    "preenchido"
                )

            if not vazio_ok:
                faltando.append(
                    "vazio"
                )

            self.configurar_status(
                self.valor_detector,
                self.detalhe_detector,
                "Incompleto",
                "Faltando: " + ", ".join(faltando),
                False,
            )

        self.carregar_preview(
            caminho_preenchido,
            self.label_imagem_preenchido,
            "preenchido",
        )
        self.carregar_preview(
            caminho_vazio,
            self.label_imagem_vazio,
            "vazio",
        )

        self.label_dados_detector.configure(
            text=(
                f"Coluna X: {configuracao.get('coluna_x', '—')} | "
                f"Captura: "
                f"{configuracao.get('largura_captura', '—')} × "
                f"{configuracao.get('altura_captura', '—')}\n"
                f"Preenchido: {caminho_preenchido}\n"
                f"Vazio: {caminho_vazio}"
            )
        )

        return detector_ok

    def atualizar_texto_pontos(
        self,
        pontos: dict,
        faltantes: list[str],
    ) -> None:
        """Mostra as coordenadas e os cálculos."""

        linhas = []

        for nome in PONTOS_NECESSARIOS:
            valor = pontos.get(
                nome
            )

            if isinstance(valor, dict):
                linhas.append(
                    f"[OK] {nome:<25} "
                    f"x={valor.get('x', '—'):<5} "
                    f"y={valor.get('y', '—')}"
                )
            else:
                linhas.append(
                    f"[FALTA] {nome}"
                )

        calculos = self.calibracao.get(
            "calculos",
            {},
        )

        linhas.extend(
            [
                "",
                "Cálculos:",
                (
                    "altura_linha: "
                    f"{calculos.get('altura_linha', '—')}"
                ),
                (
                    "linhas_visiveis_estimadas: "
                    f"{calculos.get('linhas_visiveis_estimadas', '—')}"
                ),
            ]
        )

        if faltantes:
            linhas.extend(
                [
                    "",
                    (
                        "Pontos faltantes: "
                        + ", ".join(faltantes)
                    ),
                ]
            )

        self.texto_pontos.configure(
            state="normal"
        )
        self.texto_pontos.delete(
            "1.0",
            "end",
        )
        self.texto_pontos.insert(
            "1.0",
            "\n".join(linhas),
        )
        self.texto_pontos.configure(
            state="disabled"
        )

    def carregar_preview(
        self,
        caminho: Path,
        label: ctk.CTkLabel,
        tipo: str,
    ) -> None:
        """Carrega uma imagem de referência ampliada."""

        if not caminho.exists():
            label.configure(
                image=None,
                text="Imagem não encontrada",
            )
            return

        try:
            with Image.open(caminho) as imagem:
                imagem_rgb = imagem.convert("RGB").copy()

            largura_destino = 300
            altura_destino = 100

            imagem_ampliada = imagem_rgb.resize(
                (
                    largura_destino,
                    altura_destino,
                ),
                Image.Resampling.NEAREST,
            )

            imagem_ctk = ctk.CTkImage(
                light_image=imagem_ampliada,
                dark_image=imagem_ampliada,
                size=(
                    largura_destino,
                    altura_destino,
                ),
            )

            label.configure(
                image=imagem_ctk,
                text="",
            )

            if tipo == "preenchido":
                self.imagem_preenchido = imagem_ctk
            else:
                self.imagem_vazio = imagem_ctk

        except (
            OSError,
            ValueError,
        ) as erro:
            label.configure(
                image=None,
                text=f"Erro ao abrir imagem:\n{erro}",
            )

    def limpar_previews(self) -> None:
        """Limpa as imagens do detector."""

        self.imagem_preenchido = None
        self.imagem_vazio = None

        self.label_imagem_preenchido.configure(
            image=None,
            text="Imagem não encontrada",
        )
        self.label_imagem_vazio.configure(
            image=None,
            text="Imagem não encontrada",
        )

    def configurar_status(
        self,
        label_valor: ctk.CTkLabel,
        label_detalhe: ctk.CTkLabel,
        valor: str,
        detalhe: str,
        correto: bool,
    ) -> None:
        """Configura um cartão de status."""

        label_valor.configure(
            text=valor,
            text_color=(
                "#166534"
                if correto
                else COR_ERRO_TEXTO
            ),
        )
        label_detalhe.configure(
            text=detalhe
        )

    def preparar_teste_leitura(self) -> None:
        """Valida e confirma o teste de leitura."""

        if not self.diagnostico_pronto:
            messagebox.showwarning(
                "Diagnóstico incompleto",
                (
                    "Corrija os itens indicados antes "
                    "de executar o teste."
                ),
                parent=self,
            )
            return

        try:
            numero_item = int(
                self.campo_item.get().strip()
            )

        except ValueError:
            messagebox.showwarning(
                "Item inválido",
                "Informe um número inteiro.",
                parent=self,
            )
            return

        if numero_item < 1:
            messagebox.showwarning(
                "Item inválido",
                "O número deve ser maior que zero.",
                parent=self,
            )
            return

        confirmar = messagebox.askokcancel(
            "Confirmar teste de leitura",
            (
                f"O detector analisará o item {numero_item}.\n\n"
                "Confirme que o ADM está maximizado e que "
                "uma nota está aberta.\n\n"
                "Nenhum cadastro será aberto ou salvo."
            ),
            parent=self,
        )

        if not confirmar:
            return

        self.botao_testar.configure(
            state="disabled",
            text="Testando...",
        )
        self.label_resultado_teste.configure(
            text=(
                f"Analisando o item {numero_item}..."
            ),
            text_color=COR_AZUL,
        )

        self.withdraw()
        self.master.withdraw()

        self.after(
            650,
            lambda: self.executar_teste_leitura(
                numero_item
            ),
        )

    def executar_teste_leitura(
        self,
        numero_item: int,
    ) -> None:
        """Executa o detector e mostra o resultado."""

        try:
            resultado = detectar_estado_codigo(
                calibracao=self.calibracao,
                numero_item=numero_item,
            )

        except pyautogui.FailSafeException:
            self.restaurar_apos_teste()

            self.label_resultado_teste.configure(
                text=(
                    "Teste interrompido pela proteção "
                    "do PyAutoGUI."
                ),
                text_color=COR_ERRO_TEXTO,
            )

            messagebox.showerror(
                "Teste interrompido",
                (
                    "A proteção foi acionada. "
                    "Mantenha o mouse longe dos cantos."
                ),
                parent=self,
            )
            return

        except Exception as erro:
            self.restaurar_apos_teste()

            self.label_resultado_teste.configure(
                text=f"Erro no teste: {erro}",
                text_color=COR_ERRO_TEXTO,
            )

            messagebox.showerror(
                "Erro no teste",
                str(erro),
                parent=self,
            )
            return

        self.restaurar_apos_teste()

        mapa_estado = {
            "preenchido": "CADASTRADO",
            "vazio": "NÃO CADASTRADO",
            "incerto": "INCERTO",
        }

        estado_exibicao = mapa_estado.get(
            resultado.estado,
            resultado.estado.upper(),
        )

        texto = (
            f"Item {numero_item}: {estado_exibicao}\n"
            f"Score atual: {resultado.score_atual:.4f} | "
            f"Limite preenchido: {resultado.limite_preenchido:.4f} | "
            f"Limite vazio: {resultado.limite_vazio:.4f} | "
            f"Margem: {resultado.margem:.4f}"
        )

        cor = (
            "#166534"
            if resultado.estado in {
                "preenchido",
                "vazio",
            }
            else COR_ERRO_TEXTO
        )

        self.label_resultado_teste.configure(
            text=texto,
            text_color=cor,
        )

        messagebox.showinfo(
            "Resultado do teste",
            texto,
            parent=self,
        )

    def restaurar_apos_teste(self) -> None:
        """Restaura as janelas depois do teste."""

        self.master.deiconify()
        self.master.lift()

        self.deiconify()
        self.lift()
        self.focus_force()

        self.botao_testar.configure(
            state=(
                "normal"
                if self.diagnostico_pronto
                else "disabled"
            ),
            text="Testar leitura",
        )

    def abrir_ferramenta_calibracao(
        self,
        argumento: str,
        nome: str,
    ) -> None:
        """Fecha o aplicativo e abre uma ferramenta de calibração."""

        confirmar = messagebox.askyesno(
            "Abrir ferramenta",
            (
                f"O ADM SmartCadastro será fechado e a {nome} "
                "será aberta.\n\n"
                "Depois de concluir esta etapa, abra novamente "
                "o programa principal.\n\n"
                "Deseja continuar?"
            ),
            parent=self,
        )

        if not confirmar:
            return

        if getattr(sys, "frozen", False):
            comando = [
                sys.executable,
                argumento,
            ]
            pasta_execucao = (
                Path(sys.executable).resolve().parent
            )

        else:
            raiz_projeto = (
                Path(__file__).resolve().parents[1]
            )
            comando = [
                sys.executable,
                str(raiz_projeto / "app.py"),
                argumento,
            ]
            pasta_execucao = raiz_projeto

        try:
            subprocess.Popen(
                comando,
                cwd=str(pasta_execucao),
            )

        except OSError as erro:
            messagebox.showerror(
                "Erro ao abrir ferramenta",
                str(erro),
                parent=self,
            )
            return

        self.master.destroy()
