
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyautogui
from PIL import Image, ImageChops, ImageStat

from services.app_paths import (
    resolver_caminho_configuracao,
)

# O detector examinarÃ¡ pequenas variaÃ§Ãµes de posiÃ§Ã£o.
DESLOCAMENTOS_X = (-1, 0, 1)
DESLOCAMENTOS_Y = (-4, -3, -2, -1, 0, 1, 2, 3, 4)


@dataclass(frozen=True)
class ResultadoVinculo:
    """Resultado da identificaÃ§Ã£o visual do vÃ­nculo."""

    estado: str

    # Mantidos para compatibilidade com a tela de teste.
    distancia_ativo: float
    distancia_inativo: float
    margem: float

    percentual_verde: float
    percentual_verde_ativo_modelo: float
    percentual_verde_inativo_modelo: float
    limite_verde_ativo: float
    limite_verde_inativo: float
    pixels_verdes: int
    deslocamento_x: int
    deslocamento_y: int
    caminho_captura: Path | None


def calcular_posicao_linha(
    calibracao: dict[str, Any],
    numero_item: int,
) -> tuple[int, int]:
    """Calcula a posiÃ§Ã£o esperada da linha."""

    if numero_item < 1:
        raise ValueError(
            "O nÃºmero do item deve ser maior que zero."
        )

    pontos = calibracao.get("pontos", {})

    primeira = pontos.get("mais_primeira_linha")
    segunda = pontos.get("mais_segunda_linha")

    if primeira is None or segunda is None:
        raise ValueError(
            "A calibraÃ§Ã£o das linhas estÃ¡ incompleta."
        )

    primeira_y = int(primeira["y"])
    segunda_y = int(segunda["y"])

    altura_linha = abs(
        segunda_y - primeira_y
    )

    if altura_linha < 5:
        raise ValueError(
            "A altura calibrada da linha Ã© invÃ¡lida."
        )

    x = int(primeira["x"])

    y = (
        primeira_y
        + (numero_item - 1) * altura_linha
    )

    return x, y


def resolver_caminho_template(
    caminho_relativo: str,
) -> Path:
    """Transforma um caminho relativo em caminho completo."""

    caminho = Path(caminho_relativo)

    if caminho.is_absolute():
        return caminho

    return resolver_caminho_configuracao(
        caminho_relativo
    )


def pixel_eh_verde(
    vermelho: int,
    verde: int,
    azul: int,
) -> bool:
    """
    Verifica se um pixel pertence ao Ã­cone verde.

    A regra aceita diferentes tonalidades utilizadas
    pelo ADM, inclusive verdes mais escuros.
    """

    return (
        verde >= 55
        and verde >= vermelho + 14
        and verde >= azul + 3
    )


def contar_pixels_verdes(
    imagem: Image.Image,
) -> tuple[int, float]:
    """Conta a quantidade e o percentual de pixels verdes."""

    imagem_rgb = imagem.convert("RGB")

    quantidade_verdes = 0
    total_pixels = 0

    for vermelho, verde, azul in imagem_rgb.getdata():
        total_pixels += 1

        if pixel_eh_verde(
            vermelho,
            verde,
            azul,
        ):
            quantidade_verdes += 1

    if total_pixels == 0:
        return 0, 0.0

    percentual = (
        quantidade_verdes / total_pixels
    )

    return quantidade_verdes, percentual


def preparar_imagem_comparacao(
    imagem: Image.Image,
) -> Image.Image:
    """Prepara a imagem para comparaÃ§Ã£o auxiliar."""

    imagem_rgb = imagem.convert("RGB")

    return imagem_rgb.resize(
        (72, 48),
        Image.Resampling.LANCZOS,
    )


def calcular_distancia(
    imagem_atual: Image.Image,
    imagem_modelo: Image.Image,
) -> float:
    """
    Calcula a diferenÃ§a visual entre duas imagens.

    Essa informaÃ§Ã£o Ã© apenas auxiliar. A decisÃ£o principal
    Ã© feita pela quantidade de verde.
    """

    atual = preparar_imagem_comparacao(
        imagem_atual
    )

    modelo = preparar_imagem_comparacao(
        imagem_modelo
    )

    diferenca = ImageChops.difference(
        atual,
        modelo,
    )

    estatisticas = ImageStat.Stat(
        diferenca
    )

    media = sum(
        estatisticas.mean
    ) / len(estatisticas.mean)

    return media / 255


def limitar_regiao(
    esquerda: int,
    topo: int,
    largura: int,
    altura: int,
    largura_tela: int,
    altura_tela: int,
) -> tuple[int, int, int, int]:
    """MantÃ©m a regiÃ£o dentro dos limites da tela."""

    esquerda = max(0, esquerda)
    topo = max(0, topo)

    if esquerda + largura > largura_tela:
        esquerda = largura_tela - largura

    if topo + altura > altura_tela:
        topo = altura_tela - altura

    return (
        esquerda,
        topo,
        largura,
        altura,
    )


def encontrar_melhor_captura(
    tela: Image.Image,
    coluna_x: int,
    linha_y: int,
    largura: int,
    altura: int,
) -> tuple[Image.Image, int, float, int, int]:
    """
    Procura o Ã­cone alguns pixels ao redor da posiÃ§Ã£o esperada.

    Retorna a regiÃ£o com a maior quantidade de verde.
    """

    largura_tela, altura_tela = tela.size

    melhor_imagem: Image.Image | None = None
    melhor_pixels = -1
    melhor_percentual = 0.0
    melhor_dx = 0
    melhor_dy = 0

    for deslocamento_y in DESLOCAMENTOS_Y:
        for deslocamento_x in DESLOCAMENTOS_X:
            centro_x = (
                coluna_x + deslocamento_x
            )

            centro_y = (
                linha_y + deslocamento_y
            )

            esquerda = (
                centro_x - largura // 2
            )

            topo = (
                centro_y - altura // 2
            )

            regiao = limitar_regiao(
                esquerda=esquerda,
                topo=topo,
                largura=largura,
                altura=altura,
                largura_tela=largura_tela,
                altura_tela=altura_tela,
            )

            imagem = tela.crop(
                (
                    regiao[0],
                    regiao[1],
                    regiao[0] + regiao[2],
                    regiao[1] + regiao[3],
                )
            )

            pixels, percentual = (
                contar_pixels_verdes(imagem)
            )

            if pixels > melhor_pixels:
                melhor_imagem = imagem
                melhor_pixels = pixels
                melhor_percentual = percentual
                melhor_dx = deslocamento_x
                melhor_dy = deslocamento_y

    if melhor_imagem is None:
        raise RuntimeError(
            "NÃ£o foi possÃ­vel capturar a regiÃ£o do vÃ­nculo."
        )

    return (
        melhor_imagem,
        melhor_pixels,
        melhor_percentual,
        melhor_dx,
        melhor_dy,
    )


def detectar_estado_vinculo(
    calibracao: dict[str, Any],
    numero_item: int,
) -> ResultadoVinculo:
    """Captura e identifica o vÃ­nculo do item informado."""

    configuracao_vinculo = calibracao.get(
        "vinculo"
    )

    if not configuracao_vinculo:
        raise ValueError(
            "As imagens dos vÃ­nculos ainda nÃ£o foram calibradas."
        )

    _, linha_y = calcular_posicao_linha(
        calibracao=calibracao,
        numero_item=numero_item,
    )

    coluna_x = int(
        configuracao_vinculo["coluna_x"]
    )

    largura = int(
        configuracao_vinculo.get(
            "largura_captura",
            18,
        )
    )

    altura = int(
        configuracao_vinculo.get(
            "altura_captura",
            12,
        )
    )

    # Impede uma captura grande o suficiente
    # para alcanÃ§ar o botÃ£o + da coluna vizinha.
    largura = max(
        16,
        min(largura, 20),
    )

    altura = max(
        10,
        min(altura, 14),
    )

    caminho_ativo = resolver_caminho_template(
        configuracao_vinculo[
            "template_ativo"
        ]
    )

    caminho_inativo = resolver_caminho_template(
        configuracao_vinculo[
            "template_inativo"
        ]
    )

    if not caminho_ativo.exists():
        raise FileNotFoundError(
            "Imagem do vÃ­nculo ativo nÃ£o encontrada: "
            f"{caminho_ativo}"
        )

    if not caminho_inativo.exists():
        raise FileNotFoundError(
            "Imagem do vÃ­nculo inativo nÃ£o encontrada: "
            f"{caminho_inativo}"
        )

    with Image.open(
        caminho_ativo
    ) as modelo_ativo_aberto:
        modelo_ativo = (
            modelo_ativo_aberto
            .convert("RGB")
            .copy()
        )

    with Image.open(
        caminho_inativo
    ) as modelo_inativo_aberto:
        modelo_inativo = (
            modelo_inativo_aberto
            .convert("RGB")
            .copy()
        )

    _, percentual_ativo_modelo = (
        contar_pixels_verdes(
            modelo_ativo
        )
    )

    _, percentual_inativo_modelo = (
        contar_pixels_verdes(
            modelo_inativo
        )
    )

    diferenca_modelos = (
        percentual_ativo_modelo
        - percentual_inativo_modelo
    )

    if diferenca_modelos <= 0.005:
        raise ValueError(
            "As capturas ativa e inativa possuem quase "
            "a mesma quantidade de verde. RefaÃ§a a captura "
            "dos vÃ­nculos."
        )

    # Utiliza uma parte pequena da diferenÃ§a porque
    # o Ã­cone pode ficar alguns pixels fora do centro.
    limite_verde_ativo = (
        percentual_inativo_modelo
        + diferenca_modelos * 0.08
    )

    limite_verde_inativo = (
        percentual_inativo_modelo
        + diferenca_modelos * 0.025
    )

    # Uma Ãºnica captura da tela Ã© usada para todas
    # as pequenas tentativas de posiÃ§Ã£o.
    tela = pyautogui.screenshot()

    (
        imagem_atual,
        pixels_verdes,
        percentual_verde,
        deslocamento_x,
        deslocamento_y,
    ) = encontrar_melhor_captura(
        tela=tela,
        coluna_x=coluna_x,
        linha_y=linha_y,
        largura=largura,
        altura=altura,
    )

    # A imagem atual existe somente em memória.
    # Nenhuma captura de execução é salva automaticamente.
    caminho_captura = None

    distancia_ativo = calcular_distancia(
        imagem_atual,
        modelo_ativo,
    )

    distancia_inativo = calcular_distancia(
        imagem_atual,
        modelo_inativo,
    )

    margem = abs(
        distancia_ativo
        - distancia_inativo
    )

    if percentual_verde >= limite_verde_ativo:
        estado = "ativo"

    elif percentual_verde <= limite_verde_inativo:
        estado = "inativo"

    else:
        estado = "incerto"

    return ResultadoVinculo(
        estado=estado,
        distancia_ativo=distancia_ativo,
        distancia_inativo=distancia_inativo,
        margem=margem,
        percentual_verde=percentual_verde,
        percentual_verde_ativo_modelo=(
            percentual_ativo_modelo
        ),
        percentual_verde_inativo_modelo=(
            percentual_inativo_modelo
        ),
        limite_verde_ativo=limite_verde_ativo,
        limite_verde_inativo=limite_verde_inativo,
        pixels_verdes=pixels_verdes,
        deslocamento_x=deslocamento_x,
        deslocamento_y=deslocamento_y,
        caminho_captura=caminho_captura,
    )
