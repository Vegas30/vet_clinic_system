# Окно входа
"""
Модуль окна авторизации.
Обеспечивает интерфейс для входа пользователей в систему.
"""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from logic.logic_auth_manager import AuthManager


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)  # Сигнал об успешной авторизации с данными пользователя

    def __init__(self):
        super().__init__()

        # Инициализация менеджера аутентификации
        self.auth_manager = AuthManager()

        # Инициализация UI
        self.init_ui()

    def init_ui(self):
        # Настройка основных параметров окна
        self.setWindowTitle("Ветеринарная клиника - Авторизация")
        self.setFixedSize(400, 350)

        # Основной вертикальный контейнер
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Заголовок ---
        title_label = QLabel("Ветеринарная клиника")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Подзаголовок
        subtitle_label = QLabel("Авторизация в системе")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Форма входа ---
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Поле логина
        login_label = QLabel("Логин:")
        login_label.setFont(QFont("Arial", 10))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите ваш логин")
        self.login_input.setMinimumHeight(35)
        self.login_input.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)

        # Поле пароля
        password_label = QLabel("Пароль:")
        password_label.setFont(QFont("Arial", 10))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setMinimumHeight(35)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self.login_input.styleSheet())

        # Собираем форму
        form_layout.addWidget(login_label)
        form_layout.addWidget(self.login_input)
        form_layout.addSpacing(10)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        # --- Кнопка входа ---
        login_button = QPushButton("Войти")
        login_button.setMinimumHeight(40)
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        login_button.clicked.connect(self.attempt_login)

        # Подсказка по нажатию Enter
        self.login_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)

        # --- Сборка основного интерфейса ---
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addSpacing(20)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(login_button)

        # Устанавливаем основной макет
        self.setLayout(main_layout)

    def attempt_login(self):
        """
        Попытка аутентификации пользователя
        """
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        # Проверка заполненности полей
        if not login or not password:
            self.show_error("Логин и пароль не могут быть пустыми")
            return

        # Попытка аутентификации
        user_data = self.auth_manager.authenticate(login, password)

        if user_data:
            # Успешная авторизация
            QMessageBox.information(
                self,
                "Успешный вход",
                f"Добро пожаловать, {user_data['full_name']}!"
            )
            self.login_success.emit(user_data)
        else:
            # Неудачная попытка входа
            self.show_error("Неверный логин или пароль")
            self.password_input.clear()

    def show_error(self, message: str):
        """Отображение сообщения об ошибке"""
        QMessageBox.critical(
            self,
            "Ошибка авторизации",
            message,
            buttons=QMessageBox.StandardButton.Ok,
            defaultButton=QMessageBox.StandardButton.Ok
        )

    def clear_fields(self):
        """Очистка полей ввода"""
        self.login_input.clear()
        self.password_input.clear()

# TODO: Реализовать окно входа (PyQt5)