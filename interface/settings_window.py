from collections.abc import Callable
from tkinter import messagebox

import customtkinter as ctk

from abbreviation.defaults import CONFIGURACOES_PADRAO
from database.settings_repository import (
    carregar_configuracoes,
    salvar_configuracoes,
)
from interface.styles import (
    COR_AZUL,
    COR_AZUL_HOVER,
    COR_BORDA,
    COR_FUNDO,
    COR_FUNDO_SECUNDARIO,
    COR_TEXTO,
    COR_TEXTO_BOTAO,
    COR_TEXTO_SECUNDARIO,
    FONTE_PRINCIPAL,
    TAMANHO_BOTAO,
    TAMANHO_SUBTITULO,
    TAMANHO_TEXTO,
    TAMANHO_TITULO,
)


class SettingsWindow(ctk.CTkToplevel):
    """Janela de configurações do motor de abreviação."""

    def __init__(
        self,
        master,
        ao_salvar: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master)

        self.ao_salvar = ao_salvar
        self.configuracoes = carregar_configuracoes()

        self.title("Configurações - ADM SmartCadastro")
        self.geometry("1080x700")
        self.minsize(920, 600)
        self.configure(fg_color=COR_FUNDO)

        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.criar_cabecalho()
        self.criar_abas()
        self.criar_botoes()
        self.carregar_campos()

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
            padx=25,
            pady=(20, 10),
            sticky="ew",
        )

        titulo = ctk.CTkLabel(
            cabecalho,
            text="Configurações",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TITULO,
                weight="bold",
            ),
        )
        titulo.pack(anchor="w")

        subtitulo = ctk.CTkLabel(
            cabecalho,
            text=(
                "Edite as regras utilizadas para preparar "
                "as descrições dos produtos."
            ),
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_SUBTITULO,
            ),
        )
        subtitulo.pack(
            anchor="w",
            pady=(4, 0),
        )

    def criar_abas(self) -> None:
        """Cria as abas de configurações."""

        self.abas = ctk.CTkTabview(
            self,
            fg_color=COR_FUNDO_SECUNDARIO,
            segmented_button_fg_color="#E5E7EB",
            segmented_button_selected_color=COR_AZUL,
            segmented_button_selected_hover_color=COR_AZUL_HOVER,
            segmented_button_unselected_color="#E5E7EB",
            segmented_button_unselected_hover_color="#D1D5DB",
            text_color=COR_TEXTO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=4,
        )
        self.abas.grid(
            row=1,
            column=0,
            padx=25,
            pady=10,
            sticky="nsew",
        )

        nomes_abas = (
            "Palavras removidas",
            "Substituições",
            "Abreviações",
            "Tamanhos",
            "Cores",
            "Código secreto",
            "Limite",
        )

        for nome in nomes_abas:
            self.abas.add(nome)

        self.campo_palavras = self.criar_campo_texto(
            nome_aba="Palavras removidas",
            explicacao=(
                "Digite uma palavra por linha. Essas palavras "
                "serão retiradas da descrição."
            ),
        )

        self.campo_substituicoes = self.criar_campo_texto(
            nome_aba="Substituições",
            explicacao=(
                "Digite uma regra por linha usando o formato:\n"
                "EXPRESSÃO ORIGINAL = EXPRESSÃO FINAL"
            ),
        )

        self.campo_abreviacoes = self.criar_campo_texto(
            nome_aba="Abreviações",
            explicacao=(
                "Digite uma abreviação por linha usando o formato:\n"
                "PALAVRA ORIGINAL = ABREVIAÇÃO"
            ),
        )

        self.campo_tamanhos = self.criar_campo_texto(
            nome_aba="Tamanhos",
            explicacao=(
                "Digite um tamanho por linha. Esses valores "
                "serão mantidos nas descrições."
            ),
        )

        self.campo_cores = self.criar_campo_texto(
            nome_aba="Cores",
            explicacao=(
                "Digite uma cor principal por linha. O sistema "
                "manterá a cor e removerá sua variante posterior."
            ),
        )

        self.criar_campo_codigo_secreto()
        self.campo_limite = self.criar_campo_limite()

    def criar_campo_texto(
        self,
        nome_aba: str,
        explicacao: str,
    ) -> ctk.CTkTextbox:
        """Cria um campo de texto dentro de uma aba."""

        aba = self.abas.tab(nome_aba)
        aba.configure(
            fg_color=COR_FUNDO_SECUNDARIO
        )

        aba.grid_columnconfigure(0, weight=1)
        aba.grid_rowconfigure(1, weight=1)

        label = ctk.CTkLabel(
            aba,
            text=explicacao,
            justify="left",
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        label.grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 10),
            sticky="ew",
        )

        campo = ctk.CTkTextbox(
            aba,
            fg_color=COR_FUNDO,
            text_color=COR_TEXTO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=3,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        campo.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )

        return campo

    def criar_campo_codigo_secreto(self) -> None:
        """Cria a aba de configuração do código secreto."""

        aba = self.abas.tab("Código secreto")
        aba.configure(
            fg_color=COR_FUNDO_SECUNDARIO
        )

        aba.grid_columnconfigure(0, weight=1)
        aba.grid_rowconfigure(2, weight=1)

        topo = ctk.CTkFrame(
            aba,
            fg_color=COR_FUNDO_SECUNDARIO,
            corner_radius=0,
        )
        topo.grid(
            row=0,
            column=0,
            padx=18,
            pady=(16, 8),
            sticky="ew",
        )
        topo.grid_columnconfigure(0, weight=1)

        textos = ctk.CTkFrame(
            topo,
            fg_color=COR_FUNDO_SECUNDARIO,
            corner_radius=0,
        )
        textos.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        titulo = ctk.CTkLabel(
            textos,
            text="Código secreto de custo",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=16,
                weight="bold",
            ),
        )
        titulo.pack(anchor="w")

        explicacao = ctk.CTkLabel(
            textos,
            text=(
                "Ative ou desative o código e defina o símbolo "
                "correspondente a cada número do custo inteiro."
            ),
            anchor="w",
            justify="left",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        explicacao.pack(
            anchor="w",
            pady=(3, 0),
        )

        self.variavel_codigo_ativo = ctk.BooleanVar(
            value=True
        )

        self.switch_codigo_ativo = ctk.CTkSwitch(
            topo,
            text="Ativar código secreto",
            variable=self.variavel_codigo_ativo,
            onvalue=True,
            offvalue=False,
            command=self.atualizar_estado_codigo,
            text_color=COR_TEXTO,
            progress_color=COR_AZUL,
            button_color=COR_AZUL,
            button_hover_color=COR_AZUL_HOVER,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
                weight="bold",
            ),
        )
        self.switch_codigo_ativo.grid(
            row=0,
            column=1,
            padx=(18, 0),
            sticky="e",
        )

        self.label_estado_codigo = ctk.CTkLabel(
            aba,
            text="",
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=12,
            ),
        )
        self.label_estado_codigo.grid(
            row=1,
            column=0,
            padx=18,
            sticky="ew",
        )

        area_configuracao = ctk.CTkFrame(
            aba,
            fg_color=COR_FUNDO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=4,
        )
        area_configuracao.grid(
            row=2,
            column=0,
            padx=18,
            pady=(8, 12),
            sticky="nsew",
        )
        area_configuracao.grid_columnconfigure(
            0,
            weight=1,
        )

        area_delimitadores = ctk.CTkFrame(
            area_configuracao,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        area_delimitadores.grid(
            row=0,
            column=0,
            padx=16,
            pady=(14, 8),
            sticky="ew",
        )
        area_delimitadores.grid_columnconfigure(
            4,
            weight=1,
        )

        label_prefixo = ctk.CTkLabel(
            area_delimitadores,
            text="Símbolo inicial",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
                weight="bold",
            ),
        )
        label_prefixo.grid(
            row=0,
            column=0,
            padx=(0, 8),
        )

        self.campo_codigo_prefixo = ctk.CTkEntry(
            area_delimitadores,
            width=58,
            height=36,
            justify="center",
            fg_color=COR_FUNDO_SECUNDARIO,
            text_color=COR_TEXTO,
            border_color=COR_BORDA,
            border_width=1,
            corner_radius=4,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=16,
                weight="bold",
            ),
        )
        self.campo_codigo_prefixo.grid(
            row=0,
            column=1,
            padx=(0, 22),
        )

        label_sufixo = ctk.CTkLabel(
            area_delimitadores,
            text="Símbolo final",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
                weight="bold",
            ),
        )
        label_sufixo.grid(
            row=0,
            column=2,
            padx=(0, 8),
        )

        self.campo_codigo_sufixo = ctk.CTkEntry(
            area_delimitadores,
            width=58,
            height=36,
            justify="center",
            fg_color=COR_FUNDO_SECUNDARIO,
            text_color=COR_TEXTO,
            border_color=COR_BORDA,
            border_width=1,
            corner_radius=4,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=16,
                weight="bold",
            ),
        )
        self.campo_codigo_sufixo.grid(
            row=0,
            column=3,
        )

        botao_restaurar = ctk.CTkButton(
            area_delimitadores,
            text="Restaurar padrão",
            width=145,
            height=34,
            corner_radius=4,
            fg_color=COR_FUNDO,
            hover_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
            ),
            command=self.restaurar_codigo_padrao,
        )
        botao_restaurar.grid(
            row=0,
            column=5,
            sticky="e",
        )

        label_mapeamento = ctk.CTkLabel(
            area_configuracao,
            text="Símbolo de cada número",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
                weight="bold",
            ),
        )
        label_mapeamento.grid(
            row=1,
            column=0,
            padx=16,
            pady=(4, 6),
            sticky="ew",
        )

        grade_simbolos = ctk.CTkFrame(
            area_configuracao,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        grade_simbolos.grid(
            row=2,
            column=0,
            padx=16,
            sticky="ew",
        )

        for coluna in range(5):
            grade_simbolos.grid_columnconfigure(
                coluna,
                weight=1,
            )

        self.campos_codigo_simbolos: dict[
            str,
            ctk.CTkEntry,
        ] = {}

        for indice, numero in enumerate(
            "0123456789"
        ):
            linha = indice // 5
            coluna = indice % 5

            cartao = ctk.CTkFrame(
                grade_simbolos,
                fg_color=COR_FUNDO_SECUNDARIO,
                border_width=1,
                border_color=COR_BORDA,
                corner_radius=4,
            )
            cartao.grid(
                row=linha,
                column=coluna,
                padx=(
                    0 if coluna == 0 else 5,
                    0 if coluna == 4 else 5,
                ),
                pady=5,
                sticky="ew",
            )
            cartao.grid_columnconfigure(
                1,
                weight=1,
            )

            label_numero = ctk.CTkLabel(
                cartao,
                text=f"{numero} =",
                text_color=COR_TEXTO,
                font=ctk.CTkFont(
                    family=FONTE_PRINCIPAL,
                    size=TAMANHO_TEXTO,
                    weight="bold",
                ),
            )
            label_numero.grid(
                row=0,
                column=0,
                padx=(10, 5),
                pady=9,
            )

            campo = ctk.CTkEntry(
                cartao,
                width=52,
                height=32,
                justify="center",
                fg_color=COR_FUNDO,
                text_color=COR_TEXTO,
                border_color=COR_BORDA,
                border_width=1,
                corner_radius=4,
                font=ctk.CTkFont(
                    family=FONTE_PRINCIPAL,
                    size=15,
                    weight="bold",
                ),
            )
            campo.grid(
                row=0,
                column=1,
                padx=(0, 10),
                pady=7,
                sticky="e",
            )
            campo.bind(
                "<KeyRelease>",
                self.atualizar_previa_codigo,
            )

            self.campos_codigo_simbolos[
                numero
            ] = campo

        self.campo_codigo_prefixo.bind(
            "<KeyRelease>",
            self.atualizar_previa_codigo,
        )
        self.campo_codigo_sufixo.bind(
            "<KeyRelease>",
            self.atualizar_previa_codigo,
        )

        area_previa = ctk.CTkFrame(
            area_configuracao,
            fg_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=4,
        )
        area_previa.grid(
            row=3,
            column=0,
            padx=16,
            pady=(12, 14),
            sticky="ew",
        )
        area_previa.grid_columnconfigure(
            1,
            weight=1,
        )

        label_previa = ctk.CTkLabel(
            area_previa,
            text="Prévia para o custo 159:",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        label_previa.grid(
            row=0,
            column=0,
            padx=(12, 8),
            pady=10,
        )

        self.label_previa_codigo = ctk.CTkLabel(
            area_previa,
            text="(AEI)",
            anchor="w",
            text_color=COR_AZUL,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=17,
                weight="bold",
            ),
        )
        self.label_previa_codigo.grid(
            row=0,
            column=1,
            padx=(0, 12),
            pady=10,
            sticky="w",
        )

    def carregar_codigo_secreto(self) -> None:
        """Carrega o código secreto salvo nos campos."""

        padrao = CONFIGURACOES_PADRAO[
            "codigo_secreto"
        ]
        configuracao = self.configuracoes.get(
            "codigo_secreto",
            {},
        )

        ativo = configuracao.get(
            "ativo",
            padrao["ativo"],
        )

        simbolos = dict(
            padrao["simbolos"]
        )
        simbolos_salvos = configuracao.get(
            "simbolos"
        )

        if isinstance(simbolos_salvos, dict):
            simbolos.update(
                {
                    str(numero): str(simbolo)
                    for numero, simbolo
                    in simbolos_salvos.items()
                    if str(numero) in simbolos
                }
            )

        prefixo = configuracao.get(
            "prefixo",
            padrao["prefixo"],
        )
        sufixo = configuracao.get(
            "sufixo",
            padrao["sufixo"],
        )

        self.variavel_codigo_ativo.set(
            bool(ativo)
        )

        self.campo_codigo_prefixo.delete(
            0,
            "end",
        )
        self.campo_codigo_prefixo.insert(
            0,
            str(prefixo),
        )

        self.campo_codigo_sufixo.delete(
            0,
            "end",
        )
        self.campo_codigo_sufixo.insert(
            0,
            str(sufixo),
        )

        for numero, campo in (
            self.campos_codigo_simbolos.items()
        ):
            campo.delete(
                0,
                "end",
            )
            campo.insert(
                0,
                simbolos[numero],
            )

        self.atualizar_estado_codigo()

    def restaurar_codigo_padrao(self) -> None:
        """Restaura o mapeamento padrão do código."""

        padrao = CONFIGURACOES_PADRAO[
            "codigo_secreto"
        ]

        self.variavel_codigo_ativo.set(
            padrao["ativo"]
        )

        self.campo_codigo_prefixo.configure(
            state="normal"
        )
        self.campo_codigo_sufixo.configure(
            state="normal"
        )

        self.campo_codigo_prefixo.delete(
            0,
            "end",
        )
        self.campo_codigo_prefixo.insert(
            0,
            padrao["prefixo"],
        )

        self.campo_codigo_sufixo.delete(
            0,
            "end",
        )
        self.campo_codigo_sufixo.insert(
            0,
            padrao["sufixo"],
        )

        for numero, campo in (
            self.campos_codigo_simbolos.items()
        ):
            campo.configure(
                state="normal"
            )
            campo.delete(
                0,
                "end",
            )
            campo.insert(
                0,
                padrao["simbolos"][numero],
            )

        self.atualizar_estado_codigo()

    def atualizar_estado_codigo(self) -> None:
        """Ativa ou bloqueia os campos do código."""

        ativo = self.variavel_codigo_ativo.get()
        estado = (
            "normal"
            if ativo
            else "disabled"
        )

        self.campo_codigo_prefixo.configure(
            state=estado
        )
        self.campo_codigo_sufixo.configure(
            state=estado
        )

        for campo in (
            self.campos_codigo_simbolos.values()
        ):
            campo.configure(
                state=estado
            )

        self.label_estado_codigo.configure(
            text=(
                "Ativado: o código será acrescentado "
                "ao final da descrição."
                if ativo
                else (
                    "Desativado: nenhum código de custo "
                    "será acrescentado à descrição."
                )
            ),
            text_color=(
                "#166534"
                if ativo
                else COR_TEXTO_SECUNDARIO
            ),
        )

        self.atualizar_previa_codigo()

    def atualizar_previa_codigo(
        self,
        _evento=None,
    ) -> None:
        """Atualiza a prévia do código configurado."""

        if not self.variavel_codigo_ativo.get():
            self.label_previa_codigo.configure(
                text="Código desativado",
                text_color=COR_TEXTO_SECUNDARIO,
            )
            return

        prefixo = (
            self.campo_codigo_prefixo.get()
            or "?"
        )
        sufixo = (
            self.campo_codigo_sufixo.get()
            or "?"
        )

        simbolos = {
            numero: (
                campo.get().strip().upper()
                or "?"
            )
            for numero, campo in (
                self.campos_codigo_simbolos.items()
            )
        }

        previa = (
            f"{prefixo}"
            f"{simbolos['1']}"
            f"{simbolos['5']}"
            f"{simbolos['9']}"
            f"{sufixo}"
        )

        self.label_previa_codigo.configure(
            text=previa,
            text_color=COR_AZUL,
        )

    def ler_codigo_secreto(self) -> dict:
        """Lê e valida as configurações do código."""

        prefixo = (
            self.campo_codigo_prefixo
            .get()
            .strip()
        )
        sufixo = (
            self.campo_codigo_sufixo
            .get()
            .strip()
        )

        if len(prefixo) != 1:
            raise ValueError(
                "O símbolo inicial do código secreto "
                "deve possuir exatamente um caractere."
            )

        if len(sufixo) != 1:
            raise ValueError(
                "O símbolo final do código secreto "
                "deve possuir exatamente um caractere."
            )

        if prefixo.isspace() or sufixo.isspace():
            raise ValueError(
                "Os símbolos inicial e final não podem "
                "ser espaços."
            )

        if prefixo == sufixo:
            raise ValueError(
                "Os símbolos inicial e final devem "
                "ser diferentes."
            )

        simbolos: dict[str, str] = {}

        for numero, campo in (
            self.campos_codigo_simbolos.items()
        ):
            simbolo = (
                campo.get()
                .strip()
                .upper()
            )

            if len(simbolo) != 1:
                raise ValueError(
                    f"O símbolo do número {numero} deve "
                    "possuir exatamente um caractere."
                )

            if simbolo.isspace():
                raise ValueError(
                    f"O símbolo do número {numero} não "
                    "pode ser um espaço."
                )

            simbolos[numero] = simbolo

        valores = list(
            simbolos.values()
        )

        if len(set(valores)) != len(valores):
            raise ValueError(
                "Cada número deve possuir um símbolo "
                "diferente no código secreto."
            )

        return {
            "ativo": bool(
                self.variavel_codigo_ativo.get()
            ),
            "simbolos": simbolos,
            "prefixo": prefixo,
            "sufixo": sufixo,
        }

    def criar_campo_limite(self) -> ctk.CTkEntry:
        """Cria o campo do limite da descrição."""

        aba = self.abas.tab("Limite")
        aba.configure(
            fg_color=COR_FUNDO_SECUNDARIO
        )

        aba.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            aba,
            text="Limite máximo da descrição",
            anchor="w",
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=16,
                weight="bold",
            ),
        )
        titulo.grid(
            row=0,
            column=0,
            padx=20,
            pady=(25, 5),
            sticky="ew",
        )

        explicacao = ctk.CTkLabel(
            aba,
            text=(
                "O limite conta todos os caracteres da descrição, "
                "incluindo espaços, parênteses e o código secreto.\n\n"
                "Descrições acima do limite serão destacadas em "
                "vermelho e impedirão o início do cadastro."
            ),
            justify="left",
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_TEXTO,
            ),
        )
        explicacao.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="ew",
        )

        campo = ctk.CTkEntry(
            aba,
            width=180,
            height=40,
            fg_color=COR_FUNDO,
            text_color=COR_TEXTO,
            border_color=COR_BORDA,
            border_width=1,
            corner_radius=4,
            placeholder_text="35",
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=15,
            ),
        )
        campo.grid(
            row=2,
            column=0,
            padx=20,
            sticky="w",
        )

        observacao = ctk.CTkLabel(
            aba,
            text="Valor permitido: de 10 até 100 caracteres.",
            anchor="w",
            text_color=COR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=12,
            ),
        )
        observacao.grid(
            row=3,
            column=0,
            padx=20,
            pady=(8, 0),
            sticky="w",
        )

        return campo

    def criar_botoes(self) -> None:
        """Cria os botões da janela."""

        area_botoes = ctk.CTkFrame(
            self,
            fg_color=COR_FUNDO,
            corner_radius=0,
        )
        area_botoes.grid(
            row=2,
            column=0,
            padx=25,
            pady=(10, 20),
            sticky="ew",
        )
        area_botoes.grid_columnconfigure(0, weight=1)

        botao_cancelar = ctk.CTkButton(
            area_botoes,
            text="Cancelar",
            width=120,
            height=38,
            corner_radius=4,
            fg_color=COR_FUNDO,
            hover_color=COR_FUNDO_SECUNDARIO,
            border_width=1,
            border_color=COR_BORDA,
            text_color=COR_TEXTO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
            ),
            command=self.destroy,
        )
        botao_cancelar.grid(
            row=0,
            column=1,
            padx=(0, 10),
        )

        botao_salvar = ctk.CTkButton(
            area_botoes,
            text="Salvar configurações",
            width=180,
            height=38,
            corner_radius=4,
            fg_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            text_color=COR_TEXTO_BOTAO,
            font=ctk.CTkFont(
                family=FONTE_PRINCIPAL,
                size=TAMANHO_BOTAO,
                weight="bold",
            ),
            command=self.salvar,
        )
        botao_salvar.grid(
            row=0,
            column=2,
        )

    def carregar_campos(self) -> None:
        """Carrega as configurações nos campos."""

        self.inserir_lista(
            self.campo_palavras,
            self.configuracoes["palavras_removidas"],
        )

        self.inserir_mapeamento(
            self.campo_substituicoes,
            self.configuracoes[
                "substituicoes_expressoes"
            ],
        )

        self.inserir_mapeamento(
            self.campo_abreviacoes,
            self.configuracoes["abreviacoes"],
        )

        self.inserir_lista(
            self.campo_tamanhos,
            self.configuracoes["tamanhos_validos"],
        )

        self.inserir_lista(
            self.campo_cores,
            self.configuracoes["cores_base"],
        )

        self.carregar_codigo_secreto()

        self.campo_limite.delete(0, "end")
        self.campo_limite.insert(
            0,
            str(
                self.configuracoes.get(
                    "limite_descricao",
                    35,
                )
            ),
        )

    @staticmethod
    def inserir_lista(
        campo: ctk.CTkTextbox,
        valores: list[str],
    ) -> None:
        campo.delete("1.0", "end")
        campo.insert(
            "1.0",
            "\n".join(valores),
        )

    @staticmethod
    def inserir_mapeamento(
        campo: ctk.CTkTextbox,
        valores: dict[str, str],
    ) -> None:
        linhas = [
            f"{original} = {resultado}"
            for original, resultado in valores.items()
        ]

        campo.delete("1.0", "end")
        campo.insert(
            "1.0",
            "\n".join(linhas),
        )

    @staticmethod
    def ler_lista(
        campo: ctk.CTkTextbox,
    ) -> list[str]:
        texto = campo.get(
            "1.0",
            "end",
        )

        valores = []

        for linha in texto.splitlines():
            valor = " ".join(
                linha.upper().split()
            )

            if valor and valor not in valores:
                valores.append(valor)

        return valores

    @staticmethod
    def ler_mapeamento(
        campo: ctk.CTkTextbox,
        nome_configuracao: str,
    ) -> dict[str, str]:
        texto = campo.get(
            "1.0",
            "end",
        )

        resultado: dict[str, str] = {}

        for numero_linha, linha in enumerate(
            texto.splitlines(),
            start=1,
        ):
            linha = linha.strip()

            if not linha:
                continue

            if "=" not in linha:
                raise ValueError(
                    f'Erro em "{nome_configuracao}", '
                    f"linha {numero_linha}: use o símbolo =."
                )

            original, substituicao = linha.split(
                "=",
                1,
            )

            original = " ".join(
                original.upper().split()
            )

            substituicao = " ".join(
                substituicao.upper().split()
            )

            if not original or not substituicao:
                raise ValueError(
                    f'Erro em "{nome_configuracao}", '
                    f"linha {numero_linha}: informe "
                    "os dois lados da regra."
                )

            resultado[original] = substituicao

        return resultado

    def ler_limite(self) -> int:
        """Lê e valida o limite da descrição."""

        texto = self.campo_limite.get().strip()

        try:
            limite = int(texto)
        except ValueError as erro:
            raise ValueError(
                "O limite da descrição deve ser um número inteiro."
            ) from erro

        if limite < 10 or limite > 100:
            raise ValueError(
                "O limite da descrição deve estar entre "
                "10 e 100 caracteres."
            )

        return limite

    def salvar(self) -> None:
        """Valida e salva as configurações."""

        try:
            configuracoes = {
                "palavras_removidas": self.ler_lista(
                    self.campo_palavras
                ),

                "substituicoes_expressoes": (
                    self.ler_mapeamento(
                        self.campo_substituicoes,
                        "Substituições",
                    )
                ),

                "abreviacoes": self.ler_mapeamento(
                    self.campo_abreviacoes,
                    "Abreviações",
                ),

                "tamanhos_validos": self.ler_lista(
                    self.campo_tamanhos
                ),

                "cores_base": self.ler_lista(
                    self.campo_cores
                ),

                "codigo_secreto": (
                    self.ler_codigo_secreto()
                ),

                "limite_descricao": self.ler_limite(),
            }

            salvar_configuracoes(
                configuracoes
            )

        except ValueError as erro:
            messagebox.showerror(
                "Configuração inválida",
                str(erro),
                parent=self,
            )
            return

        if self.ao_salvar is not None:
            self.ao_salvar()

        messagebox.showinfo(
            "Configurações salvas",
            "As configurações foram atualizadas com sucesso.",
            parent=self,
        )

        self.destroy()