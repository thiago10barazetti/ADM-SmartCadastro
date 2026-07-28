import copy
import json

from abbreviation.defaults import CONFIGURACOES_PADRAO
from database.description_repository import conectar


def normalizar_item(texto: str) -> str:
    """Padroniza uma palavra ou expressão de configuração."""

    return " ".join(
        texto.upper().strip().split()
    )


def inicializar_configuracoes() -> None:
    """Cria a tabela e salva as configurações padrão."""

    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                atualizado_em TEXT
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        for chave, valor in CONFIGURACOES_PADRAO.items():
            valor_json = json.dumps(
                valor,
                ensure_ascii=False,
            )

            conexao.execute(
                """
                INSERT OR IGNORE INTO configuracoes (
                    chave,
                    valor
                )
                VALUES (?, ?)
                """,
                (
                    chave,
                    valor_json,
                ),
            )


def carregar_configuracoes() -> dict:
    """Carrega as configurações salvas no banco."""

    inicializar_configuracoes()

    configuracoes = copy.deepcopy(
        CONFIGURACOES_PADRAO
    )

    with conectar() as conexao:
        resultados = conexao.execute(
            """
            SELECT chave, valor
            FROM configuracoes
            """
        ).fetchall()

    for chave, valor_json in resultados:
        if chave not in configuracoes:
            continue

        try:
            configuracoes[chave] = json.loads(
                valor_json
            )

        except json.JSONDecodeError:
            continue

    return configuracoes


def salvar_configuracoes(
    configuracoes: dict,
) -> None:
    """Salva as configurações informadas pelo usuário."""

    with conectar() as conexao:
        for chave, valor in configuracoes.items():
            valor_json = json.dumps(
                valor,
                ensure_ascii=False,
            )

            conexao.execute(
                """
                INSERT INTO configuracoes (
                    chave,
                    valor,
                    atualizado_em
                )
                VALUES (?, ?, CURRENT_TIMESTAMP)

                ON CONFLICT(chave)
                DO UPDATE SET
                    valor = excluded.valor,
                    atualizado_em = CURRENT_TIMESTAMP
                """,
                (
                    chave,
                    valor_json,
                ),
            )


def adicionar_palavras_removidas(
    palavras: list[str],
) -> list[str]:
    """
    Adiciona palavras à lista global de remoção.

    Retorna somente as palavras realmente adicionadas.
    """

    configuracoes = carregar_configuracoes()

    palavras_atuais = [
        normalizar_item(palavra)
        for palavra in configuracoes[
            "palavras_removidas"
        ]
    ]

    palavras_adicionadas: list[str] = []

    for palavra in palavras:
        palavra_normalizada = normalizar_item(
            palavra
        )

        if not palavra_normalizada:
            continue

        if palavra_normalizada in palavras_atuais:
            continue

        palavras_atuais.append(
            palavra_normalizada
        )

        palavras_adicionadas.append(
            palavra_normalizada
        )

    if palavras_adicionadas:
        salvar_configuracoes(
            {
                "palavras_removidas": (
                    palavras_atuais
                )
            }
        )

    return palavras_adicionadas