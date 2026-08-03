import sys

from calibrar import main as abrir_calibrador
from capturar_codigos import main as abrir_captura_codigos
from criar_vinculos import main as abrir_captura_vinculos
from database.description_repository import (
    inicializar_banco,
)
from database.settings_repository import (
    inicializar_configuracoes,
)
from interface.main_window import MainWindow
from services.app_paths import (
    inicializar_estrutura_usuario,
)


MODO_CALIBRAR = "--calibrar"
MODO_CAPTURAR_CODIGOS = "--capturar-codigos"
MODO_CAPTURAR_VINCULOS = "--capturar-vinculos"


def abrir_aplicativo_principal() -> None:
    """Abre a janela principal."""

    inicializar_banco()
    inicializar_configuracoes()

    app = MainWindow()
    app.mainloop()


def main() -> None:
    """Cria a estrutura limpa e abre a janela solicitada."""

    inicializar_estrutura_usuario()
    argumentos = set(sys.argv[1:])

    if MODO_CALIBRAR in argumentos:
        abrir_calibrador()
        return

    if MODO_CAPTURAR_CODIGOS in argumentos:
        abrir_captura_codigos()
        return

    if MODO_CAPTURAR_VINCULOS in argumentos:
        abrir_captura_vinculos()
        return

    abrir_aplicativo_principal()


if __name__ == "__main__":
    main()
