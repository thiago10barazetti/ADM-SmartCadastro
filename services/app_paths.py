"""Caminhos persistentes do ADM SmartCadastro."""

from __future__ import annotations

import os
import sys
from pathlib import Path


NOME_APLICATIVO = "ADM SmartCadastro"


def obter_raiz_recursos() -> Path:
    """Retorna a pasta dos recursos do projeto ou do PyInstaller."""

    raiz_pyinstaller = getattr(
        sys,
        "_MEIPASS",
        None,
    )

    if raiz_pyinstaller:
        return Path(raiz_pyinstaller)

    return Path(__file__).resolve().parents[1]


def obter_raiz_dados() -> Path:
    """Retorna a pasta gravável exclusiva do usuário."""

    local_app_data = os.environ.get(
        "LOCALAPPDATA"
    )

    if local_app_data:
        return (
            Path(local_app_data)
            / NOME_APLICATIVO
        )

    return (
        Path.home()
        / ".adm_smartcadastro"
    )


RAIZ_RECURSOS = obter_raiz_recursos()
RAIZ_DADOS = obter_raiz_dados()

PASTA_DADOS = RAIZ_DADOS / "data"
PASTA_CALIBRACAO = RAIZ_DADOS / "calibration"
PASTA_TEMPLATES = PASTA_CALIBRACAO / "templates"
PASTA_RELATORIOS = RAIZ_DADOS / "reports"
PASTA_LOGS = RAIZ_DADOS / "logs"
PASTA_LOGS_CODIGOS = PASTA_LOGS / "codigos"
PASTA_LOGS_VINCULOS = PASTA_LOGS / "vinculos"

CAMINHO_BANCO = (
    PASTA_DADOS
    / "adm_smartcadastro.db"
)
CAMINHO_CALIBRACAO = (
    PASTA_CALIBRACAO
    / "calibration.json"
)


def criar_pastas_usuario() -> None:
    """Cria apenas as pastas vazias da instalação atual."""

    for pasta in (
        PASTA_DADOS,
        PASTA_CALIBRACAO,
        PASTA_TEMPLATES,
        PASTA_RELATORIOS,
        PASTA_LOGS_CODIGOS,
        PASTA_LOGS_VINCULOS,
    ):
        pasta.mkdir(
            parents=True,
            exist_ok=True,
        )


def inicializar_estrutura_usuario() -> None:
    """Prepara uma instalação nova, sem importar dados."""

    criar_pastas_usuario()


def resolver_caminho_configuracao(
    caminho_salvo: str,
) -> Path:
    """Resolve o caminho de um template salvo na calibração."""

    caminho = Path(caminho_salvo)

    if caminho.is_absolute():
        if caminho.exists():
            return caminho

        template_local = (
            PASTA_TEMPLATES
            / caminho.name
        )

        if template_local.exists():
            return template_local

        return caminho

    candidatos = (
        PASTA_TEMPLATES / caminho.name,
        RAIZ_DADOS / caminho,
        RAIZ_RECURSOS / caminho,
    )

    for candidato in candidatos:
        if candidato.exists():
            return candidato

    return PASTA_TEMPLATES / caminho.name
