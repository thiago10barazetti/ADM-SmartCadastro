import sqlite3

from services.app_paths import CAMINHO_BANCO


def normalizar_texto(texto: str) -> str:
    """Padroniza o texto usado nas consultas do banco."""

    return " ".join(
        texto.upper().strip().split()
    )


def conectar() -> sqlite3.Connection:
    """Abre uma conexão com o banco persistente do usuário."""

    CAMINHO_BANCO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(
        CAMINHO_BANCO
    )


def inicializar_banco() -> None:
    """Cria as tabelas necessárias caso ainda não existam."""

    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS descricoes_aprendidas (
                descricao_original TEXT PRIMARY KEY,
                descricao_final TEXT NOT NULL,
                atualizado_em TEXT
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def buscar_descricao_aprendida(
    descricao_original: str,
) -> str | None:
    """Busca uma correção salva anteriormente."""

    descricao_normalizada = normalizar_texto(
        descricao_original
    )

    with conectar() as conexao:
        resultado = conexao.execute(
            """
            SELECT descricao_final
            FROM descricoes_aprendidas
            WHERE descricao_original = ?
            """,
            (descricao_normalizada,),
        ).fetchone()

    if resultado is None:
        return None

    return resultado[0]


def salvar_descricao_aprendida(
    descricao_original: str,
    descricao_final: str,
) -> None:
    """Salva ou atualiza uma descrição corrigida."""

    original_normalizada = normalizar_texto(
        descricao_original
    )

    final_normalizada = normalizar_texto(
        descricao_final
    )

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO descricoes_aprendidas (
                descricao_original,
                descricao_final,
                atualizado_em
            )
            VALUES (?, ?, CURRENT_TIMESTAMP)

            ON CONFLICT(descricao_original)
            DO UPDATE SET
                descricao_final = excluded.descricao_final,
                atualizado_em = CURRENT_TIMESTAMP
            """,
            (
                original_normalizada,
                final_normalizada,
            ),
        )
