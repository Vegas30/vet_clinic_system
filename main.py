# main
import locale
import sys
from PyQt6.QtWidgets import QApplication, QDialog
import logging
from datetime import datetime

from ui.ui_main_window import MainWindow
from ui.ui_login_window import LoginWindow

from database.database_models_pg import PostgresModels
from database.database_models_mongo import MongoDBModels

logging.basicConfig(
    filename=f'app_errors_{datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
except locale.Error:
    print("Warning: Russian locale not available, fallback to system default", file=sys.stderr)

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.pg_models = PostgresModels()
            self.mongo_models = MongoDBModels()
            logging.info("Database connections initialized successfully")
        except Exception as e:
            logging.critical(f"Database initialization failed: {e}")
            raise

    def get_pg_models(self):
        return self.pg_models

    def get_mongo_models(self):
        return self.mongo_models

    def close_connections(self):
        try:
            if hasattr(self, 'pg_models') and hasattr(self.pg_models, 'db'):
                self.pg_models.db.close_all()
            if hasattr(self, 'mongo_models') and hasattr(self.mongo_models, 'client'):
                self.mongo_models.client.close()
        except Exception as e:
            logging.error(f"Error closing connections: {e}")

    def log_connection_stats(self):
        stats = {
            'postgres': self.pg_models.db.get_pool_stats(),
            'mongo': self.mongo_models.client.server_info()
        }
        logging.info(f"Connection stats: {stats}")


def main():
    try:
        # Инициализация менеджера баз данных
        db_manager = DatabaseManager()

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

        # Корректный выход - закрываем соединения
        db_manager.close_connections()
        sys.exit(exit_code)

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}", exc_info=True)
        if 'db_manager' in locals():
            db_manager.close_connections()
        sys.exit(1)

if __name__ == "__main__":
    main()
