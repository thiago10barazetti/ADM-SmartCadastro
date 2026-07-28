from database.description_repository import (
    inicializar_banco,
)
from interface.main_window import MainWindow


def main() -> None:
    inicializar_banco()

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()