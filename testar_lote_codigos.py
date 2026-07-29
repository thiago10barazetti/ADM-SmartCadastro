import csv
import time
from datetime import datetime
from pathlib import Path

from automation.calibration_repository import (
    carregar_calibracao,
)
from automation.code_detector import (
    detectar_estado_codigo,
)


RAIZ_PROJETO = Path(__file__).resolve().parent

PASTA_RELATORIOS = (
    RAIZ_PROJETO
    / "logs"
    / "relatorios"
)

TOTAL_ITENS = 18


def traduzir_estado(
    estado: str,
) -> str:
    """Transforma o estado interno em texto legível."""

    estados = {
        "preenchido": "CADASTRADO",
        "vazio": "NÃO CADASTRADO",
        "incerto": "INCERTO",
    }

    return estados.get(
        estado,
        "ERRO",
    )


def mostrar_contagem_regressiva(
    segundos: int = 5,
) -> None:
    """Dá tempo para o usuário deixar o ADM visível."""

    print()
    print(
        "Deixe a nota aberta e totalmente visível no ADM."
    )
    print(
        "Não use o mouse ou o teclado durante o teste."
    )
    print()

    for restante in range(
        segundos,
        0,
        -1,
    ):
        print(
            f"Iniciando em {restante}...",
            flush=True,
        )

        time.sleep(1)

    print()
    print(
        "Teste iniciado."
    )
    print(
        "-" * 60
    )


def salvar_relatorio(
    resultados: list[dict[str, object]],
) -> Path:
    """Salva os resultados em um arquivo CSV."""

    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    horario = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    caminho = (
        PASTA_RELATORIOS
        / f"teste_codigos_{horario}.csv"
    )

    colunas = [
        "item",
        "resultado",
        "estado_interno",
        "score_atual",
        "modelo_preenchido",
        "modelo_vazio",
        "margem",
        "deslocamento_y",
        "captura",
        "erro",
    ]

    with caminho.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=colunas,
            delimiter=";",
        )

        escritor.writeheader()
        escritor.writerows(
            resultados
        )

    return caminho


def mostrar_resumo(
    resultados: list[dict[str, object]],
) -> None:
    """Apresenta o resumo final no terminal."""

    cadastrados = sum(
        1
        for resultado in resultados
        if resultado["resultado"]
        == "CADASTRADO"
    )

    nao_cadastrados = sum(
        1
        for resultado in resultados
        if resultado["resultado"]
        == "NÃO CADASTRADO"
    )

    incertos = sum(
        1
        for resultado in resultados
        if resultado["resultado"]
        == "INCERTO"
    )

    erros = sum(
        1
        for resultado in resultados
        if resultado["resultado"]
        == "ERRO"
    )

    print()
    print(
        "=" * 60
    )
    print(
        "RESUMO DO TESTE"
    )
    print(
        "=" * 60
    )
    print(
        f"Cadastrados:     {cadastrados}"
    )
    print(
        f"Não cadastrados: {nao_cadastrados}"
    )
    print(
        f"Incertos:        {incertos}"
    )
    print(
        f"Erros:           {erros}"
    )


def testar_item(
    calibracao: dict,
    numero_item: int,
) -> dict[str, object]:
    """Executa o teste visual de um único item."""

    try:
        resultado = detectar_estado_codigo(
            calibracao=calibracao,
            numero_item=numero_item,
        )

    except Exception as erro:
        return {
            "item": numero_item,
            "resultado": "ERRO",
            "estado_interno": "",
            "score_atual": "",
            "modelo_preenchido": "",
            "modelo_vazio": "",
            "margem": "",
            "deslocamento_y": "",
            "captura": "",
            "erro": str(erro),
        }

    return {
        "item": numero_item,
        "resultado": traduzir_estado(
            resultado.estado
        ),
        "estado_interno": resultado.estado,
        "score_atual": round(
            resultado.score_atual,
            6,
        ),
        "modelo_preenchido": round(
            resultado.score_preenchido_modelo,
            6,
        ),
        "modelo_vazio": round(
            resultado.score_vazio_modelo,
            6,
        ),
        "margem": round(
            resultado.margem,
            6,
        ),
        "deslocamento_y": (
            resultado.deslocamento_y
        ),
        "captura": str(
            resultado.caminho_captura
        ),
        "erro": "",
    }


def main() -> None:
    """Executa o teste completo dos 18 itens."""

    print(
        "=" * 60
    )
    print(
        "ADM SMARTCADASTRO — TESTE EM LOTE"
    )
    print(
        "=" * 60
    )
    print()
    print(
        f"Quantidade de itens: {TOTAL_ITENS}"
    )
    print(
        "Este teste é somente de leitura."
    )
    print(
        "Nenhum produto será cadastrado ou alterado."
    )

    try:
        calibracao = carregar_calibracao()

    except Exception as erro:
        print()
        print(
            f"Erro ao carregar a calibração: {erro}"
        )
        return

    if not calibracao.get(
        "codigo_produto"
    ):
        print()
        print(
            "A calibração da coluna Código "
            "não foi encontrada."
        )
        return

    input(
        "\nPressione ENTER e imediatamente "
        "deixe o ADM visível..."
    )

    mostrar_contagem_regressiva()

    resultados: list[
        dict[str, object]
    ] = []

    for numero_item in range(
        1,
        TOTAL_ITENS + 1,
    ):
        resultado = testar_item(
            calibracao=calibracao,
            numero_item=numero_item,
        )

        resultados.append(
            resultado
        )

        numero_formatado = str(
            numero_item
        ).zfill(2)

        texto_resultado = str(
            resultado["resultado"]
        )

        if texto_resultado == "ERRO":
            print(
                f"Item {numero_formatado} "
                f"→ ERRO: {resultado['erro']}"
            )

        else:
            print(
                f"Item {numero_formatado} "
                f"→ {texto_resultado}"
            )

    caminho_relatorio = salvar_relatorio(
        resultados
    )

    mostrar_resumo(
        resultados
    )

    print()
    print(
        f"Relatório salvo em:\n{caminho_relatorio}"
    )
    print()
    print(
        "Teste finalizado. Nenhum cadastro foi realizado."
    )


if __name__ == "__main__":
    main()