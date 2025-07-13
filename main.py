# Точка входа в приложение ветклиники
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.ui_main_window import MainWindow

def main():
    # TODO: Инициализация приложения, запуск UI, подключение к БД и т.д.
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":


    main()
