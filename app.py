from database.description_repository import (
    inicializar_banco,
)
from database.settings_repository import (
    inicializar_configuracoes,
)
from interface.main_window import MainWindow


def main() -> None:
    inicializar_banco()
    inicializar_configuracoes()

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()