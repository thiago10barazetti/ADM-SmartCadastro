import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pyautogui


CAMINHO_CALIBRACAO = (
    Path(__file__).resolve().parent
    / "calibration.json"
)

PONTOS_OBRIGATORIOS = (
    "mais_primeira_linha",
    "mais_segunda_linha",
    "limite_inferior_tabela",
    "aba_tributacao",
    "botao_salvar",
)


def carregar_calibracao() -> dict[str, Any]:
    """Carrega a calibração salva anteriormente."""

    if not CAMINHO_CALIBRACAO.exists():
        return {
            "pontos": {},
        }

    try:
        with CAMINHO_CALIBRACAO.open(
            "r",
            encoding="utf-8",
        ) as arquivo:
            dados = json.load(arquivo)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {
            "pontos": {},
        }

    if not isinstance(dados, dict):
        return {
            "pontos": {},
        }

    return dados


def validar_pontos(
    pontos: dict[str, dict[str, int]],
) -> None:
    """Valida se todos os pontos foram capturados."""

    faltantes = [
        ponto
        for ponto in PONTOS_OBRIGATORIOS
        if ponto not in pontos
    ]

    if faltantes:
        nomes = ", ".join(faltantes)

        raise ValueError(
            "Ainda faltam pontos de calibração: "
            f"{nomes}."
        )

    primeira = pontos["mais_primeira_linha"]
    segunda = pontos["mais_segunda_linha"]

    altura_linha = abs(
        segunda["y"] - primeira["y"]
    )

    if altura_linha < 5:
        raise ValueError(
            "A primeira e a segunda linha parecem estar "
            "na mesma posição. Capture novamente."
        )

    limite_tabela = pontos[
        "limite_inferior_tabela"
    ]

    if limite_tabela["y"] <= primeira["y"]:
        raise ValueError(
            "O limite inferior da tabela deve ficar abaixo "
            "da primeira linha."
        )


def salvar_calibracao(
    pontos: dict[str, dict[str, int]],
) -> dict[str, Any]:
    """Salva as coordenadas e cálculos da calibração."""

    validar_pontos(pontos)

    primeira = pontos["mais_primeira_linha"]
    segunda = pontos["mais_segunda_linha"]
    limite = pontos["limite_inferior_tabela"]

    altura_linha = abs(
        segunda["y"] - primeira["y"]
    )

    linhas_visiveis = (
        int(
            (
                limite["y"]
                - primeira["y"]
            )
            / altura_linha
        )
        + 1
    )

    tamanho_tela = pyautogui.size()

    dados = {
        "versao": 1,
        "salvo_em": datetime.now().isoformat(
            timespec="seconds"
        ),
        "tela": {
            "largura": tamanho_tela.width,
            "altura": tamanho_tela.height,
        },
        "pontos": pontos,
        "calculos": {
            "coluna_mais_x": round(
                (
                    primeira["x"]
                    + segunda["x"]
                )
                / 2
            ),
            "primeira_linha_y": primeira["y"],
            "altura_linha": altura_linha,
            "linhas_visiveis_estimadas": (
                linhas_visiveis
            ),
        },
    }

    with CAMINHO_CALIBRACAO.open(
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4,
        )

    return dados