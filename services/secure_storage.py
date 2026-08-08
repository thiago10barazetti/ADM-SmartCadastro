"""Proteção local de informações sensíveis no Windows."""

import base64
import ctypes
import sys
from ctypes import wintypes


CRYPTPROTECT_UI_FORBIDDEN = 0x01


class DATA_BLOB(ctypes.Structure):
    """Estrutura utilizada pela API de proteção de dados do Windows."""

    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


def _verificar_windows() -> None:
    """Garante que a proteção seja utilizada somente no Windows."""

    if sys.platform != "win32":
        raise RuntimeError(
            "A proteção de dados do ADM SmartCadastro "
            "está disponível somente no Windows."
        )


def _criar_blob(dados: bytes) -> tuple[DATA_BLOB, ctypes.Array]:
    """Cria uma estrutura DATA_BLOB a partir de bytes."""

    buffer = ctypes.create_string_buffer(dados)

    blob = DATA_BLOB(
        len(dados),
        ctypes.cast(
            buffer,
            ctypes.POINTER(ctypes.c_byte),
        ),
    )

    return blob, buffer


def proteger_texto(texto: str) -> str:
    """
    Protege um texto usando a DPAPI do Windows.

    Retorna o conteúdo protegido codificado em Base64
    para que possa ser armazenado no SQLite.
    """

    _verificar_windows()

    dados = texto.encode("utf-8")

    entrada, _buffer_entrada = _criar_blob(
        dados
    )

    saida = DATA_BLOB()

    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    resultado = crypt32.CryptProtectData(
        ctypes.byref(entrada),
        "ADM SmartCadastro",
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(saida),
    )

    if not resultado:
        erro = ctypes.get_last_error()

        raise OSError(
            erro,
            "Não foi possível proteger os dados.",
        )

    try:
        dados_protegidos = ctypes.string_at(
            saida.pbData,
            saida.cbData,
        )

        return base64.b64encode(
            dados_protegidos
        ).decode("ascii")

    finally:
        if saida.pbData:
            kernel32.LocalFree(
                saida.pbData
            )


def desproteger_texto(texto_protegido: str) -> str:
    """
    Recupera um texto anteriormente protegido pela DPAPI.
    """

    _verificar_windows()

    try:
        dados_protegidos = base64.b64decode(
            texto_protegido,
            validate=True,
        )

    except (ValueError, TypeError) as erro:
        raise ValueError(
            "Os dados protegidos possuem formato inválido."
        ) from erro

    entrada, _buffer_entrada = _criar_blob(
        dados_protegidos
    )

    saida = DATA_BLOB()

    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    resultado = crypt32.CryptUnprotectData(
        ctypes.byref(entrada),
        None,
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(saida),
    )

    if not resultado:
        erro = ctypes.get_last_error()

        raise OSError(
            erro,
            "Não foi possível recuperar os dados protegidos.",
        )

    try:
        dados = ctypes.string_at(
            saida.pbData,
            saida.cbData,
        )

        return dados.decode("utf-8")

    finally:
        if saida.pbData:
            kernel32.LocalFree(
                saida.pbData
            )