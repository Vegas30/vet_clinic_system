# ui_services_widget.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QDoubleSpinBox, QTextEdit, QDialogButtonBox, QGroupBox, QComboBox, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from database.database_models_pg import PostgresModels


class ServiceDialog(QDialog):
    """Диалоговое окно для добавления/редактирования услуги"""

    def __init__(self, parent=None, service_data=None):
        super().__init__(parent)
        # Установка заголовка в зависимости от режима
        self.setWindowTitle("Добавить услугу" if not service_data else "Редактировать услугу")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # Модальное окно
        self.resize(500, 400)  # Размер окна

        layout = QVBoxLayout()  # Основной макет
        form_layout = QFormLayout()  # Макет формы

        # Поля формы
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Название услуги")
        form_layout.addRow("Услуга:", self.title_edit)

        # Поле ввода цены
        self.price_edit = QDoubleSpinBox()
        self.price_edit.setMinimum(0.01)  # Минимальное значение
        self.price_edit.setMaximum(999999.99)  # Максимальное значение
        self.price_edit.setDecimals(2)  # 2 знака после запятой
        self.price_edit.setPrefix("₽ ")  # Префикс валюты
        form_layout.addRow("Стоимость:", self.price_edit)

        # Поле ввода описания
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Описание услуги...")
        form_layout.addRow("Описание:", self.desc_edit)

        # Кнопки OK и Cancel
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)  # Обработчик OK
        button_box.rejected.connect(self.reject)  # Обработчик Cancel

        # Заполнение полей при редактировании
        if service_data:
            self.title_edit.setText(service_data.get('title', ''))
            self.price_edit.setValue(service_data.get('price', 0))
            self.desc_edit.setPlainText(service_data.get('description', ''))

        # Сборка интерфейса
        layout.addLayout(form_layout)  # Добавление формы
        layout.addWidget(button_box)  # Добавление кнопок
        self.setLayout(layout)  # Установка макета

    def get_data(self):
        """Возвращает введённые данные"""
        return {
            'title': self.title_edit.text().strip(),  # Название без пробелов
            'price': self.price_edit.value(), # Числовое значение цены
            'description': self.desc_edit.toPlainText().strip() # Описание без пробелов
        }


class ServicesWidget(QWidget):
    """Виджет для работы с услугами ветеринарной клиники.

    Реализует функционал:
    - Поиск услуг с фильтром (по ID, названию, описанию или цене)
    - Создание/редактирование услуг
    - Удаление услуг
    - Просмотр детальной информации
    """

    data_updated = pyqtSignal()  # Добавляем сигнал

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data  # Данные текущего пользователя
        self.db = PostgresModels()  # Подключение к PostgreSQL
        self.current_service_id = None  # ID текущей выбранной услуги
        self.all_services = []  # Список всех услуг

        self.init_ui()  # Инициализация интерфейса
        self.load_services()  # Загрузка всех услуг при старте

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("Управление услугами")  # Устанавливает заголовок окна
        self.setMinimumSize(1000, 600)  # Задает минимальный размер окна

        # Основной макет - вертикальное расположение элементов
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Отступы от краев окна
        main_layout.setSpacing(10)  # Расстояние между элементами

        # Верхняя панель с поиском и кнопками
        top_panel = QWidget()  # Создает контейнер для верхней панели
        top_layout = QHBoxLayout(top_panel)  # Горизонтальное расположение элементов
        top_layout.setContentsMargins(0, 0, 0, 0)  # Без отступов внутри панели

        # Группа поиска
        search_group = QGroupBox("Поиск услуги")  # Группирующий элемент с рамкой
        search_layout = QHBoxLayout(search_group)  # Горизонтальное расположение

        # Выбор фильтра поиска
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ID", "Название", "Описание", "Цена"])

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите значение для поиска...")
        self.search_input.setClearButtonEnabled(True) # Кнопка очистки

        # Кнопка поиска
        search_btn = QPushButton("Поиск")
        search_btn.setIcon(QIcon("assets/icons/search.png")) # Иконка лупы
        search_btn.clicked.connect(self.search_services) # Обработчик нажатия

        # Кнопка сброса
        clear_btn = QPushButton("Сбросить")
        clear_btn.setIcon(QIcon("assets/icons/clear.png"))  # Иконка крестика
        clear_btn.clicked.connect(self.clear_search)  # Обработчик нажатия

        # Добавляем элементы в группу поиска
        search_layout.addWidget(self.filter_combo)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)

        # Группа кнопок управления
        buttons_group = QGroupBox("Действия")
        buttons_layout = QHBoxLayout(buttons_group)

        # Кнопка добавления новой услуги
        self.add_btn = QPushButton("Добавить")
        self.add_btn.setIcon(QIcon("assets/icons/add.png"))
        self.add_btn.clicked.connect(self.add_service)
        self.add_btn.setToolTip("Добавить новую услугу")

        # Кнопка редактирования услуги
        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.setIcon(QIcon("assets/icons/edit.png"))
        self.edit_btn.clicked.connect(self.edit_service)
        self.edit_btn.setToolTip("Редактировать выбранную услугу")

        # Кнопка удаления услуги
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setIcon(QIcon("assets/icons/delete.png"))
        self.delete_btn.clicked.connect(self.delete_service)
        self.delete_btn.setToolTip("Удалить выбранную услугу")

        # Кнопка просмотра деталей
        self.details_btn = QPushButton("Подробнее")
        self.details_btn.setIcon(QIcon("assets/icons/details.png"))
        self.details_btn.clicked.connect(self.show_service_details)
        self.details_btn.setToolTip("Просмотр подробной информации")

        # проверка ролей для ограничения функционала
        if self.user_data['role'] != 'admin':
            self.add_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

        # Добавляем кнопки в группу
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.details_btn)

        # Добавляем группы на верхнюю панель
        top_layout.addWidget(search_group)
        top_layout.addWidget(buttons_group)

        # Таблица услуг
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(4) # 4 колонки
        self.services_table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Цена"])

        # Настройка отображения таблицы
        self.services_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch)  # Равномерное растяжение
        self.services_table.verticalHeader().setVisible(False) # Скрыть нумерацию строк
        # Настройка выделения строк
        self.services_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.services_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        # Запрет редактирования ячеек напрямую
        self.services_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Обработчик двойного клика по строке
        self.services_table.cellDoubleClicked.connect(self.show_service_details)

        # Сборка основного интерфейса
        main_layout.addWidget(top_panel)  # Добавление верхней панели
        main_layout.addWidget(self.services_table)  # Добавление таблицы

        self.setLayout(main_layout)  # Установка основного макета

    def load_services(self):
        """Загрузка всех услуг из базы данных."""
        try:
            self.all_services = self.db.get_all_services() # Получение всех услуг
            self.update_services_table(self.all_services) # Обновление таблицы
            self.data_updated.emit()  # Сигнализируем об обновлении
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить услуги:\n{str(e)}")

    def update_services_table(self, services):
        """Обновление таблицы услуг."""
        self.services_table.setRowCount(len(services)) # Установка количества строк

        for row, service in enumerate(services):
            self.services_table.setItem(row, 0, QTableWidgetItem(str(service[0])))  # ID
            self.services_table.setItem(row, 1, QTableWidgetItem(service[1]))  # Название
            self.services_table.setItem(row, 2, QTableWidgetItem(service[2] or ""))  # Описание
            self.services_table.setItem(row, 3, QTableWidgetItem(f"{service[3]:.2f} ₽"))  # Цена

    def search_services(self):
        """Поиск услуг по выбранному фильтру."""
        search_text = self.search_input.text().strip()  # Текст для поиска
        filter_type = self.filter_combo.currentText()  # Выбранный фильтр

        if not search_text:  # Если строка поиска пустая
            self.update_services_table(self.all_services)  # Показать все услуги
            return

        try:
            filtered_services = []  # Результаты поиска
            for service in self.all_services:
                # Поиск по ID (точное совпадение)
                if filter_type == "ID" and search_text == str(service[0]):
                    filtered_services.append(service)
                # Поиск по названию (частичное совпадение без учета регистра)
                elif filter_type == "Название" and search_text.lower() in service[1].lower():
                    filtered_services.append(service)
                # Поиск по описанию (частичное совпадение без учета регистра)
                elif filter_type == "Описание" and service[2] and search_text.lower() in service[2].lower():
                    filtered_services.append(service)
                # Поиск по цене (точное совпадение)
                elif filter_type == "Цена" and search_text in f"{service[3]:.2f}":
                    filtered_services.append(service)

            self.update_services_table(filtered_services)  # Обновление таблицы

        except Exception as e:
            QMessageBox.warning(self, "Ошибка поиска", f"Ошибка при выполнении поиска:\n{str(e)}")

    def clear_search(self):
        """Очистка поиска и отображение всех услуг."""
        self.search_input.clear()  # Очистка поля ввода
        self.update_services_table(self.all_services)  # Показать все услуги

    def get_selected_service(self):
        """Возвращает данные выбранной услуги."""
        selected_row = self.services_table.currentRow() # Индекс выбранной строки
        if selected_row >= 0: # Если строка выбрана
            service_id = int(self.services_table.item(selected_row, 0).text())  # Получение ID
            return next((s for s in self.all_services if s[0] == service_id), None) # Поиск услуги в общем списке
        return None # Если ничего не выбрано

    def add_service(self):
        """Добавление новой услуги."""
        dialog = ServiceDialog(self) # Создание диалогового окна
        if dialog.exec() == QDialog.DialogCode.Accepted: # Если нажата OK
            data = dialog.get_data() # Получение данных из формы

            if not data['title']: # Проверка обязательного поля
                QMessageBox.warning(self, "Ошибка", "Название услуги обязательно!")
                return

            try:
                # Добавление услуги в базу данных
                service_id = self.db.insert_service(
                    title=data['title'],
                    description=data['description'],
                    price=data['price']
                )

                if service_id: # Если добавление успешно
                    QMessageBox.information(self, "Успешно", "Услуга добавлена!")
                    self.load_services() # Обновление списка
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить услугу:\n{str(e)}")

    def edit_service(self):
        """Редактирование выбранной услуги."""
        service = self.get_selected_service() # Получение выбранной услуги
        if not service:
            QMessageBox.warning(self, "Ошибка", "Выберите услугу для редактирования")
            return

        # Создание диалога с текущими данными
        dialog = ServiceDialog(self, {
            'title': service[1],
            'description': service[2],
            'price': service[3]
        })

        if dialog.exec() == QDialog.DialogCode.Accepted:  # Если нажата OK
            data = dialog.get_data()  # Получение новых данных

            if not data['title']:  # Проверка обязательного поля
                QMessageBox.warning(self, "Ошибка", "Название услуги обязательно!")
                return

            try:
                # Обновление услуги в базе данных
                if self.db.update_service(
                        service_id=service[0],
                        title=data['title'],
                        description=data['description'],
                        price=data['price']
                ):
                    QMessageBox.information(self, "Успешно", "Данные услуги обновлены!")
                    self.load_services()  # Обновление списка
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить услугу:\n{str(e)}")

    def delete_service(self):
        """Удаление выбранной услуги."""
        service = self.get_selected_service()
        if not service:
            QMessageBox.warning(self, "Ошибка", "Выберите услугу для удаления")
            return

        # Диалог подтверждения удаления
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы действительно хотите удалить услугу '{service[1]}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes: # Если подтверждено
            try:
                if self.db.delete_service(service[0]):  # Удаление из базы
                    QMessageBox.information(self, "Успешно", "Услуга удалена!")
                    self.load_services() # Обновление списка
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка",
                    f"Не удалось удалить услугу. Возможно, она используется в приёмах.\n{str(e)}"
                )

    def show_service_details(self):
        """Просмотр детальной информации об услуге."""
        service = self.get_selected_service() # Получение выбранной услуги
        if not service:
            QMessageBox.warning(self, "Ошибка", "Выберите услугу для просмотра")
            return

        dialog = ServiceDetailsDialog(service, self)  # Создание диалога деталей
        dialog.exec() # Показ диалога


class ServiceDetailsDialog(QDialog):
    """Диалоговое окно для просмотра детальной информации об услуге."""

    def __init__(self, service, parent=None):
        super().__init__(parent)
        # Заголовок с названием услуги
        self.setWindowTitle(f"Детали услуги: {service[1]}")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # Модальное окно
        self.resize(500, 400)  # Размер окна

        layout = QVBoxLayout()  # Основной макет
        form_layout = QFormLayout()  # Макет формы

        # Отображение данных об услуге
        form_layout.addRow("ID:", QLabel(str(service[0])))  # ID услуги
        form_layout.addRow("Название:", QLabel(service[1]))  # Название
        form_layout.addRow("Стоимость:", QLabel(f"{service[3]:.2f} ₽"))  # Цена

        # Поле описания (только для чтения)
        desc_label = QTextEdit()
        desc_label.setPlainText(service[2] or "Нет описания")  # Текст или заглушка
        desc_label.setReadOnly(True)  # Запрет редактирования
        form_layout.addRow("Описание:", desc_label)

        # Кнопка закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)  # Обработчик закрытия

        # Сборка интерфейса
        layout.addLayout(form_layout)  # Добавление формы
        layout.addWidget(button_box)  # Добавление кнопки
        self.setLayout(layout)  # Установка макета
