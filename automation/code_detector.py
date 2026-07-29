from dataclasses import dataclass
from pathlib import Path
from statistics import median
from time import sleep
from typing import Any

import pyautogui
from PIL import Image


RAIZ_PROJETO = Path(__file__).resolve().parent.parent

SETAS_PARA_VOLTAR_AO_INICIO = 100

TEMPO_APOS_CLIQUE = 0.35
TEMPO_APOS_RETORNO = 0.40
TEMPO_ENTRE_SETAS = 0.05
TEMPO_APOS_SELECAO = 0.60


@dataclass(frozen=True)
class ResultadoCodigo:
    """Resultado da análise da coluna Código."""

    estado: str
    score_atual: float
    score_preenchido_modelo: float
    score_vazio_modelo: float
    limite_preenchido: float
    limite_vazio: float
    margem: float
    deslocamento_y: int
    caminho_captura: Path


def obter_geometria_tabela(
    calibracao: dict[str, Any],
) -> tuple[int, int, int]:
    """
    Retorna a posição da primeira linha, a altura
    das linhas e o limite inferior da tabela.
    """

    pontos = calibracao.get(
        "pontos",
        {},
    )

    primeira = pontos.get(
        "mais_primeira_linha"
    )

    segunda = pontos.get(
        "mais_segunda_linha"
    )

    limite = pontos.get(
        "limite_inferior_tabela"
    )

    if primeira is None or segunda is None:
        raise ValueError(
            "A calibração das linhas está incompleta."
        )

    primeira_y = int(
        primeira["y"]
    )

    segunda_y = int(
        segunda["y"]
    )

    altura_linha = abs(
        segunda_y - primeira_y
    )

    if altura_linha < 5:
        raise ValueError(
            "A altura calibrada das linhas é inválida."
        )

    if limite is not None:
        limite_y = int(
            limite["y"]
        )

    else:
        linhas_visiveis = int(
            calibracao.get(
                "calculos",
                {},
            ).get(
                "linhas_visiveis_estimadas",
                8,
            )
        )

        limite_y = (
            primeira_y
            + altura_linha
            * max(linhas_visiveis, 1)
        )

    return (
        primeira_y,
        altura_linha,
        limite_y,
    )


def resolver_caminho(
    caminho_salvo: str,
) -> Path:
    """Transforma um caminho relativo em absoluto."""

    caminho = Path(
        caminho_salvo
    )

    if caminho.is_absolute():
        return caminho

    return RAIZ_PROJETO / caminho


def recortar_area_interna(
    imagem: Image.Image,
    margem_x: int = 2,
    margem_y: int = 2,
) -> Image.Image:
    """Remove as bordas externas de uma captura."""

    imagem_rgb = imagem.convert(
        "RGB"
    )

    largura, altura = imagem_rgb.size

    if (
        largura > margem_x * 2
        and altura > margem_y * 2
    ):
        return imagem_rgb.crop(
            (
                margem_x,
                margem_y,
                largura - margem_x,
                altura - margem_y,
            )
        )

    return imagem_rgb


def obter_cor_fundo_selecao(
    modelo_preenchido: Image.Image,
    modelo_vazio: Image.Image,
) -> tuple[int, int, int]:
    """
    Descobre a cor real do fundo selecionado usando
    as duas capturas de calibração.
    """

    pixels: list[
        tuple[int, int, int]
    ] = []

    for imagem in (
        modelo_preenchido,
        modelo_vazio,
    ):
        area = recortar_area_interna(
            imagem,
            margem_x=2,
            margem_y=2,
        )

        pixels.extend(
            list(area.getdata())
        )

    if not pixels:
        raise ValueError(
            "As capturas de calibração estão vazias."
        )

    vermelho = round(
        median(
            pixel[0]
            for pixel in pixels
        )
    )

    verde = round(
        median(
            pixel[1]
            for pixel in pixels
        )
    )

    azul = round(
        median(
            pixel[2]
            for pixel in pixels
        )
    )

    return (
        vermelho,
        verde,
        azul,
    )


def cor_proxima(
    cor: tuple[int, int, int],
    referencia: tuple[int, int, int],
    tolerancia: int,
) -> bool:
    """Verifica se duas cores são semelhantes."""

    return max(
        abs(cor[0] - referencia[0]),
        abs(cor[1] - referencia[1]),
        abs(cor[2] - referencia[2]),
    ) <= tolerancia


def calcular_proporcao_fundo(
    imagem: Image.Image,
    cor_fundo: tuple[int, int, int],
) -> float:
    """
    Calcula qual parte da imagem possui a cor
    do fundo selecionado.
    """

    area = recortar_area_interna(
        imagem,
        margem_x=1,
        margem_y=1,
    )

    pixels = list(
        area.getdata()
    )

    if not pixels:
        return 0.0

    quantidade_fundo = sum(
        1
        for pixel in pixels
        if cor_proxima(
            pixel,
            cor_fundo,
            tolerancia=25,
        )
    )

    return (
        quantidade_fundo
        / len(pixels)
    )


def selecionar_item(
    primeira_y: int,
    coluna_x: int,
    numero_item: int,
) -> Image.Image:
    """
    Volta ao primeiro produto e desce até
    o produto solicitado.
    """

    pyautogui.click(
        x=coluna_x,
        y=primeira_y,
        duration=0.15,
    )

    sleep(
        TEMPO_APOS_CLIQUE
    )

    pyautogui.press(
        "up",
        presses=SETAS_PARA_VOLTAR_AO_INICIO,
        interval=0.01,
    )

    sleep(
        TEMPO_APOS_RETORNO
    )

    quantidade_para_descer = (
        numero_item - 1
    )

    if quantidade_para_descer > 0:
        pyautogui.press(
            "down",
            presses=quantidade_para_descer,
            interval=TEMPO_ENTRE_SETAS,
        )

    sleep(
        TEMPO_APOS_SELECAO
    )

    return pyautogui.screenshot()


def localizar_celula_selecionada(
    tela: Image.Image,
    calibracao: dict[str, Any],
    coluna_x: int,
    largura: int,
    altura: int,
    cor_fundo: tuple[int, int, int],
    proporcao_referencia: float,
) -> tuple[Image.Image, int, float]:
    """
    Procura a célula selecionada em toda a altura
    da tabela, sem presumir sua posição depois da rolagem.
    """

    (
        primeira_y,
        altura_linha,
        limite_y,
    ) = obter_geometria_tabela(
        calibracao
    )

    esquerda = max(
        0,
        coluna_x - largura // 2,
    )

    if esquerda + largura > tela.width:
        esquerda = (
            tela.width - largura
        )

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
            cor_fundo=cor_fundo,
        )

        resultados.append(
            (
                centro_y,
                proporcao,
            )
        )

    if not resultados:
        raise RuntimeError(
            "Não foi possível analisar a área da tabela."
        )

    melhor_y, melhor_proporcao = max(
        resultados,
        key=lambda resultado: resultado[1],
    )

    limite_minimo = max(
        0.08,
        proporcao_referencia * 0.30,
    )

    if melhor_proporcao < limite_minimo:
        pasta_logs = (
            RAIZ_PROJETO
            / "logs"
            / "codigos"
        )

        pasta_logs.mkdir(
            parents=True,
            exist_ok=True,
        )

        tela.save(
            pasta_logs
            / "tela_falha_localizacao.png"
        )

        raise RuntimeError(
            "Não foi possível localizar a célula "
            "selecionada na tabela. "
            f"Melhor resultado: {melhor_proporcao:.3f}."
        )

    # Encontra toda a faixa vertical que pertence
    # à mesma linha selecionada.
    limite_faixa = (
        melhor_proporcao * 0.78
    )

    candidatos_faixa = [
        centro_y
        for centro_y, proporcao in resultados
        if (
            proporcao >= limite_faixa
            and abs(
                centro_y - melhor_y
            ) <= altura_linha
        )
    ]

    if candidatos_faixa:
        linha_y_real = round(
            (
                min(candidatos_faixa)
                + max(candidatos_faixa)
            )
            / 2
        )

    else:
        linha_y_real = melhor_y

    topo = max(
        0,
        linha_y_real - altura // 2,
    )

    if topo + altura > tela.height:
        topo = (
            tela.height - altura
        )

    imagem_codigo = tela.crop(
        (
            esquerda,
            topo,
            esquerda + largura,
            topo + altura,
        )
    )

    indice_aproximado = round(
        (
            linha_y_real
            - primeira_y
        )
        / altura_linha
    )

    centro_grade = (
        primeira_y
        + indice_aproximado
        * altura_linha
    )

    deslocamento_y = (
        linha_y_real
        - centro_grade
    )

    return (
        imagem_codigo,
        deslocamento_y,
        melhor_proporcao,
    )


def pixel_eh_borda(
    vermelho: int,
    verde: int,
    azul: int,
) -> bool:
    """Identifica bordas pontilhadas e linhas da grade."""

    # Pontos pretos do foco.
    if (
        vermelho <= 30
        and verde <= 30
        and azul <= 30
    ):
        return True

    # Pontos laranja do foco.
    if (
        vermelho >= 210
        and 65 <= verde <= 190
        and azul <= 120
    ):
        return True

    # Linhas cinzas da grade.
    canais_parecidos = (
        abs(vermelho - verde) <= 12
        and abs(verde - azul) <= 12
    )

    if (
        canais_parecidos
        and 100 <= vermelho <= 220
    ):
        return True

    return False


def calcular_score_texto(
    imagem: Image.Image,
    cor_fundo: tuple[int, int, int],
) -> float:
    """
    Mede a quantidade de caracteres na célula
    selecionada.
    """

    area = recortar_area_interna(
        imagem,
        margem_x=2,
        margem_y=3,
    )

    pixels = list(
        area.getdata()
    )

    if not pixels:
        return 0.0

    quantidade_texto = 0

    for vermelho, verde, azul in pixels:
        pixel = (
            vermelho,
            verde,
            azul,
        )

        if cor_proxima(
            pixel,
            cor_fundo,
            tolerancia=28,
        ):
            continue

        if pixel_eh_borda(
            vermelho,
            verde,
            azul,
        ):
            continue

        quantidade_texto += 1

    return (
        quantidade_texto
        / len(pixels)
    )


def detectar_estado_codigo(
    calibracao: dict[str, Any],
    numero_item: int,
) -> ResultadoCodigo:
    """Identifica se a coluna Código está preenchida."""

    if numero_item < 1:
        raise ValueError(
            "O número do item deve ser maior que zero."
        )

    configuracao = calibracao.get(
        "codigo_produto"
    )

    if not configuracao:
        raise ValueError(
            "A coluna Código ainda não foi calibrada."
        )

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
            "Captura do código preenchido "
            f"não encontrada: {caminho_preenchido}"
        )

    if not caminho_vazio.exists():
        raise FileNotFoundError(
            "Captura do código vazio "
            f"não encontrada: {caminho_vazio}"
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

    cor_fundo = obter_cor_fundo_selecao(
        modelo_preenchido=(
            modelo_preenchido
        ),
        modelo_vazio=modelo_vazio,
    )

    proporcao_preenchido = (
        calcular_proporcao_fundo(
            modelo_preenchido,
            cor_fundo,
        )
    )

    proporcao_vazio = (
        calcular_proporcao_fundo(
            modelo_vazio,
            cor_fundo,
        )
    )

    proporcao_referencia = min(
        proporcao_preenchido,
        proporcao_vazio,
    )

    score_preenchido = calcular_score_texto(
        imagem=modelo_preenchido,
        cor_fundo=cor_fundo,
    )

    score_vazio = calcular_score_texto(
        imagem=modelo_vazio,
        cor_fundo=cor_fundo,
    )

    diferenca_modelos = abs(
        score_preenchido
        - score_vazio
    )

    if diferenca_modelos <= 0.005:
        raise ValueError(
            "As capturas preenchida e vazia "
            "ficaram muito parecidas."
        )

    (
        primeira_y,
        _,
        _,
    ) = obter_geometria_tabela(
        calibracao
    )

    tela = selecionar_item(
        primeira_y=primeira_y,
        coluna_x=coluna_x,
        numero_item=numero_item,
    )

    (
        imagem_atual,
        deslocamento_y,
        _,
    ) = localizar_celula_selecionada(
        tela=tela,
        calibracao=calibracao,
        coluna_x=coluna_x,
        largura=largura,
        altura=altura,
        cor_fundo=cor_fundo,
        proporcao_referencia=(
            proporcao_referencia
        ),
    )

    score_atual = calcular_score_texto(
        imagem=imagem_atual,
        cor_fundo=cor_fundo,
    )

    pasta_logs = (
        RAIZ_PROJETO
        / "logs"
        / "codigos"
    )

    pasta_logs.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho_captura = (
        pasta_logs
        / f"ultima_captura_item_{numero_item}.png"
    )

    imagem_atual.save(
        caminho_captura
    )

    distancia_preenchido = abs(
        score_atual
        - score_preenchido
    )

    distancia_vazio = abs(
        score_atual
        - score_vazio
    )

    faixa_incerteza = max(
        diferenca_modelos * 0.12,
        0.002,
    )

    diferenca_distancias = abs(
        distancia_preenchido
        - distancia_vazio
    )

    if diferenca_distancias <= faixa_incerteza:
        estado = "incerto"

    elif (
        distancia_preenchido
        < distancia_vazio
    ):
        estado = "preenchido"

    else:
        estado = "vazio"

    centro = (
        score_preenchido
        + score_vazio
    ) / 2

    limite_vazio = (
        centro - faixa_incerteza
    )

    limite_preenchido = (
        centro + faixa_incerteza
    )

    return ResultadoCodigo(
        estado=estado,
        score_atual=score_atual,
        score_preenchido_modelo=(
            score_preenchido
        ),
        score_vazio_modelo=(
            score_vazio
        ),
        limite_preenchido=(
            limite_preenchido
        ),
        limite_vazio=limite_vazio,
        margem=diferenca_distancias,
        deslocamento_y=deslocamento_y,
        caminho_captura=caminho_captura,
    )