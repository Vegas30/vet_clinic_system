# Точка входа в приложение ветклиники
import sys

from PyQt6.QtWidgets import QApplication, QDialog
import logging
from datetime import datetime

from ui.ui_main_window import MainWindow
from ui.ui_login_window import LoginWindow

logging.basicConfig(
    filename=f'app_errors_{datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def create_test_user():
    """Создание тестового пользователя для отладки"""
    from database.database_models_pg import PostgresModels
    db = PostgresModels()
    db.insert_employee(
        full_name="Тестовый Пользователь",
        login="test",
        password_hash="test",  # Пароль в открытом виде
        role="admin",
        branch_id=1
    )
    print("Тестовый пользователь создан: login='test', password='test'")


def add(a, b):
    return a + b


def subtract(a, b):
    return (a - b)


def main():
    try:
        # Для отладки можно раскомментировать создание тестового пользователя
        create_test_user()

        # Создание приложения
        app = QApplication(sys.argv)
        print("Приложение создано")

        # Создаем окно авторизации
        login_window = LoginWindow()
        login_window.show()
        print("Окно авторизации показано")

        # Создаем переменную для главного окна (пока None)
        main_window = None

        # Обработчик успешного входа
        def on_login_success(user_data):
            nonlocal main_window
            print(f"Получены данные пользователя: {user_data}")

            if not user_data or 'role' not in user_data or 'full_name' not in user_data:
                print("Ошибка: некорректные данные пользователя")
                return

            try:
                main_window = MainWindow(user_data)
                main_window.show()
                login_window.close()
                print("Главное окно успешно показано")
            except Exception as e:
                print(f"Ошибка при создании главного окна: {e}")

        # Подключаем сигнал успешного входа
        login_window.login_success.connect(on_login_success)

        # Запускаем цикл событий
        exit_code = app.exec()

        # Корректный выход
        sys.exit(exit_code)

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
