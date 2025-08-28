# ui_animals_widget.py
import logging
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QListWidget, QListWidgetItem, QTextEdit, QDateEdit, QFileDialog,
    QComboBox, QGroupBox, QHeaderView, QTabWidget, QStyleOptionViewItem, QStyledItemDelegate, QMenu
)
from PyQt6.QtCore import Qt, QDate, QEvent, QRect, QUrl, QRegularExpression
from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices, QRegularExpressionValidator
from datetime import datetime
from database.database_models_mongo import MongoDBModels


class AnimalsWidget(QWidget):
    """Основной виджет для работы с карточками животных.

    Реализует функционал согласно ТЗ:
    - Поиск животных с фильтром (по ID, имени, хозяину или телефону)
    - Создание/редактирование карточек животных в MongoDB
    - Добавление медицинских записей и вложений
    - Просмотр полной истории болезни
    - Редактирование основной информации
    """

    def __init__(self):
        """Инициализация виджета работы с животными."""
        super().__init__()
        self.mongo_db = MongoDBModels()  # Подключение к MongoDB
        self.current_animal_id = None  # ID текущего выбранного животного
        self.attachments = []  # Список вложений для новой мед.записи

        self.init_ui()  # Инициализация интерфейса
        self.load_all_animals()  # Загрузка всех животных при старте

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("Учет животных") # Устанавливает заголовок окна приложения
        self.setMinimumSize(1200, 800)  # Задает минимальный размер окна в пикселях

        # Основной макет
        main_layout = QVBoxLayout() # Создает вертикальный макет для основного содержимого окна
        main_layout.setContentsMargins(10, 10, 10, 10) # Устанавливает отступы вокруг основного
        # макета в пикселях со всех сторон
        main_layout.setSpacing(10) # Задает расстояние между элементами в основном макете в пикселях

        # Верхняя панель с поиском и кнопками
        top_panel = QWidget() # Создает виджет для верхней панели
        top_layout = QHBoxLayout(top_panel) # Создает горизонтальный макет для верхней панели
        top_layout.setContentsMargins(0, 0, 0, 0) # Убирает отступы вокруг макета верхней панели

        # Левая часть панели - поиск
        search_group = QGroupBox("Поиск животного") # Создает группу с заголовком
        search_layout = QHBoxLayout(search_group) # Создает горизонтальный макет внутри группы

        # Выбор фильтра поиска
        self.filter_combo = QComboBox() # Создает выпадающий список для выбора фильтра
        self.filter_combo.addItems(["ID", "Имя", "Хозяин", "Телефон"]) # Добавляет варианты фильтров в выпадающий список

        # Поле поиска
        self.search_input = QLineEdit() # Создает поле ввода для поиска
        self.search_input.setPlaceholderText("Введите значение для поиска...") # Устанавливает подсказку в поле ввода
        self.search_input.setClearButtonEnabled(True) # Включает кнопку очистки в поле ввода

        # Кнопка поиска
        search_btn = QPushButton("Поиск") # Создает кнопку "Поиск"
        search_btn.setIcon(QIcon("assets/icons/search.png")) # Устанавливает иконку для кнопки поиска
        search_btn.clicked.connect(self.search_animals) # Подключает метод search_animals к нажатию кнопки

        # Кнопка сброса
        clear_btn = QPushButton("Сбросить") # Создает кнопку "Сбросить"
        clear_btn.setIcon(QIcon("assets/icons/clear.png")) # Устанавливает иконку для кнопки сброса
        clear_btn.clicked.connect(self.clear_search) # Подключает метод clear_search к нажатию кнопки

        # Добавляем элементы в группу поиска
        search_layout.addWidget(self.filter_combo) # Добавляет выпадающий список в макет поиска
        search_layout.addWidget(self.search_input) # Добавляет поле ввода в макет поиска
        search_layout.addWidget(search_btn) # Добавляет кнопку поиска в макет поиска
        search_layout.addWidget(clear_btn) # Добавляет кнопку сброса в макет поиска

        # Правая часть панели - кнопки управления
        buttons_group = QGroupBox("Действия") # Создает группу с заголовком "Действия"
        buttons_layout = QHBoxLayout(buttons_group) # Создает горизонтальный макет внутри группы действий

        # Кнопка добавления нового животного
        self.add_btn = QPushButton("Добавить") #  Создает кнопку "Добавить"
        self.add_btn.setIcon(QIcon("assets/icons/add.png")) # Устанавливает иконку для кнопки добавления
        self.add_btn.clicked.connect(self.show_add_animal_dialog) # Подключает метод show_add_animal_dialog
        # к нажатию кнопки
        self.add_btn.setToolTip("Добавить новое животное") # Устанавливает всплывающую подсказку для кнопки

        # Кнопки управления
        self.edit_btn = QPushButton("Редактировать") # Создает кнопку "Редактировать"
        self.edit_btn.setIcon(QIcon("assets/icons/edit.png")) # Устанавливает иконку для кнопки редактирования
        self.edit_btn.clicked.connect(self.edit_current_animal) # Подключает метод edit_current_animal к нажатию кнопки
        self.edit_btn.setToolTip("Редактировать выбранное животное") # Устанавливает всплывающую подсказку

        self.delete_btn = QPushButton("Удалить") #  Создает кнопку "Удалить"
        self.delete_btn.setIcon(QIcon("assets/icons/delete.png")) # Устанавливает иконку для кнопки удаления
        self.delete_btn.clicked.connect(self.delete_current_animal) # Подключает метод delete_current_animal
        # к нажатию кнопки
        self.delete_btn.setToolTip("Удалить выбранное животное") # Устанавливает всплывающую подсказку

        self.details_btn = QPushButton("Подробнее") # Создает кнопку "Подробнее"
        self.details_btn.setIcon(QIcon("assets/icons/details.png")) # Устанавливает иконку для кнопки подробностей
        self.details_btn.clicked.connect(self.show_current_animal_details) # Подключает метод show_current_animal_details
        # к нажатию кнопки
        self.details_btn.setToolTip("Просмотр подробной информации") # Устанавливает всплывающую подсказку

        # Добавляем кнопки в правую часть
        buttons_layout.addWidget(self.add_btn) # Добавляет кнопку добавления в макет действий
        buttons_layout.addWidget(self.edit_btn) # Добавляет кнопку редактирования в макет действий
        buttons_layout.addWidget(self.delete_btn) # Добавляет кнопку удаления в макет действий
        buttons_layout.addWidget(self.details_btn) # Добавляет кнопку подробностей в макет действий

        # Добавляем группы на верхнюю панель
        top_layout.addWidget(search_group) # Добавляет группу поиска в верхнюю панель
        top_layout.addWidget(buttons_group) # Добавляет группу действий в верхнюю панель

        # Таблица животных
        self.animals_table = QTableWidget() # Создает таблицу для отображения животных
        self.animals_table.setColumnCount(6)  # Устанавливает количество колонок в таблице - 6 колонок
        self.animals_table.setHorizontalHeaderLabels(["ID", "Имя", "Вид", "Порода", "Хозяин", "Телефон"]) #  Устанавливает
        # заголовки колонок таблицы

        # Настройка отображения таблицы
        self.animals_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)  # Равномерное растяжение
        self.animals_table.verticalHeader().setVisible(False) # Скрывает вертикальные заголовки (номера строк) в таблице
        self.animals_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) #выделяется вся строка, а не
        # только одна ячейка.
        self.animals_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection) # Разрешает выделять только одну
        # строку за раз (запрещает множественный выбор)
        self.animals_table.cellDoubleClicked.connect(self.show_animal_details) # Привязывает двойной клик по ячейке
        # таблицы к методу self.show_animal_details

        # Сборка основного интерфейса
        main_layout.addWidget(top_panel) # Добавляет верхнюю панель (с поиском и кнопками) в основной вертикальный макет
        main_layout.addWidget(self.animals_table) # Добавляет таблицу животных в основной вертикальный
        # макет (под верхней панелью)

        self.setLayout(main_layout) #  Устанавливает основной вертикальный макет (содержащий верхнюю панель и таблицу)
        # как главный макет для текущего виджета/окна

    def load_all_animals(self):
        """Загружает всех животных из базы данных и отображает их в таблице."""
        try:
            animals = self.mongo_db.get_all_animals()
            self.display_animals(animals)
        except Exception as e:
            logging.error(f"Ошибка при загрузке животных: {str(e)}")
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить данные о животных: {str(e)}"
            )

    def display_animals(self, animals):
        """Отображает список животных в таблице.

        Args:
            animals (list): Список словарей с данными животных
        """
        self.animals_table.setRowCount(len(animals))
        for row, animal in enumerate(animals):
            self.animals_table.setItem(row, 0, QTableWidgetItem(animal['_id']))
            self.animals_table.setItem(row, 1, QTableWidgetItem(animal.get('name', '')))
            self.animals_table.setItem(row, 2, QTableWidgetItem(animal.get('species', '')))
            self.animals_table.setItem(row, 3, QTableWidgetItem(animal.get('breed', '')))
            self.animals_table.setItem(row, 4, QTableWidgetItem(animal.get('owner_name', '')))
            self.animals_table.setItem(row, 5, QTableWidgetItem(animal.get('owner_phone', '')))

    def search_animals(self):
        """Выполняет поиск животных по выбранному фильтру."""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_all_animals()
            return

        filter_type = self.filter_combo.currentText()

        # Определяем критерии поиска в зависимости от выбранного фильтра
        if filter_type == "ID":
            criteria = {'_id': search_text}
        elif filter_type == "Имя":
            criteria = {'name': {'$regex': search_text, '$options': 'i'}}
        elif filter_type == "Хозяин":
            criteria = {'owner_name': {'$regex': search_text, '$options': 'i'}}
        else:  # По телефону
            criteria = {'owner_phone': {'$regex': '^' + search_text}}

        animals = self.mongo_db.search_animals(criteria)
        self.display_animals(animals)

    def clear_search(self):
        """Сбрасывает поиск и загружает всех животных."""
        self.search_input.clear()
        self.load_all_animals()

    def show_current_animal_details(self):
        """Отображает детальную информацию о выбранном животном."""
        try:
            selected_items = self.animals_table.selectedItems()

            # Проверяем, что выбрана хотя бы одна ячейка
            if not selected_items or len(selected_items) == 0:
                QMessageBox.warning(self, "Ошибка", "Выберите животное из таблицы")
                return

            # Получаем ID из первого столбца выбранной строки
            selected_row = self.animals_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Ошибка", "Не выбрана строка")
                return

            animal_id_item = self.animals_table.item(selected_row, 0)
            if not animal_id_item:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить ID животного")
                return

            animal_id = animal_id_item.text()
            if not animal_id:
                QMessageBox.warning(self, "Ошибка", "ID животного пуст")
                return

            self.show_animal_details(selected_row)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            print(f"Error in show_current_animal_details: {e}")

    def show_animal_details(self, row):
        """Открывает диалог с подробной информацией о животном."""
        try:
            animal_id_item = self.animals_table.item(row, 0)
            if not animal_id_item:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить ID животного")
                return

            animal_id = animal_id_item.text()
            animal = self.mongo_db.get_animal_by_id(animal_id)

            if not animal:
                QMessageBox.warning(self, "Ошибка", "Животное не найдено в базе данных")
                return

            # Создаем диалог с проверкой
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Карточка животного: {animal.get('name', 'Без имени')}")
            dialog.setMinimumSize(800, 600)

            # Добавляем защиту от ошибок при создании вкладок
            try:
                layout = QVBoxLayout()
                tabs = QTabWidget()

                # Вкладка "Общая информация"
                general_tab = QWidget()
                self.init_general_tab(general_tab, animal)
                tabs.addTab(general_tab, "Общая информация")

                # Вкладка "История болезни"
                medical_tab = QWidget()
                self.init_medical_tab(medical_tab, animal)
                tabs.addTab(medical_tab, "История болезни")

                layout.addWidget(tabs)
                close_btn = QPushButton("Закрыть")
                close_btn.clicked.connect(dialog.close)
                layout.addWidget(close_btn)

                dialog.setLayout(layout)
                dialog.exec()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при создании диалога: {str(e)}")
                print(f"Dialog creation error: {e}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            print(f"Error in show_animal_details: {e}")

    def init_general_tab(self, tab, animal):
        """Инициализирует вкладку с общей информацией о животном.

        Args:
            tab (QWidget): Виджет вкладки
            animal (dict): Данные животного
        """
        layout = QFormLayout()

        # Фото животного
        photo_label = QLabel()
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_label.setFixedSize(200, 200)
        photo_label.setStyleSheet("border: 1px solid #ccc;")

        photo_path = animal.get('photo_path', '')
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            photo_label.setPixmap(pixmap.scaled(
                200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            photo_label.setText("Фото отсутствует")

        # Основная информация
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"<b>Имя:</b> {animal.get('name', '')}"))
        info_layout.addWidget(QLabel(f"<b>Вид:</b> {animal.get('species', '')}"))
        info_layout.addWidget(QLabel(f"<b>Порода:</b> {animal.get('breed', '')}"))
        info_layout.addWidget(QLabel(f"<b>Дата рождения:</b> {animal.get('birth_date', '')}"))
        info_layout.addWidget(QLabel(f"<b>Пол:</b> {animal.get('sex', '')}"))
        info_layout.addWidget(QLabel(f"<b>Хозяин:</b> {animal.get('owner_name', '')}"))
        info_layout.addWidget(QLabel(f"<b>Телефон:</b> {animal.get('owner_phone', '')}"))

        # Кнопка изменения фото
        change_photo_btn = QPushButton("Изменить фото")
        change_photo_btn.clicked.connect(lambda: self.change_animal_photo(animal['_id'], photo_label))

        # Расположение элементов
        photo_layout = QHBoxLayout()
        photo_layout.addWidget(photo_label)
        photo_layout.addLayout(info_layout)

        layout.addRow(photo_layout)
        layout.addRow(change_photo_btn)
        tab.setLayout(layout)

    def init_medical_tab(self, tab, animal):
        """Инициализирует вкладку с историей болезни животного.

        Args:
            tab (QWidget): Виджет вкладки
            animal (dict): Данные животного
        """
        layout = QVBoxLayout()

        # Список медицинских записей
        medical_list = QListWidget()

        # Заполняем список записями
        for record in animal.get('medical_history', []):
            item = QListWidgetItem(f"{record.get('date', '')} - {record.get('diagnosis', '')}")
            item.setData(Qt.ItemDataRole.UserRole, record)
            medical_list.addItem(item)

        # Контекстное меню для вложений
        medical_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        medical_list.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, medical_list))

        # Кнопки управления
        btn_layout = QHBoxLayout()
        add_record_btn = QPushButton("Добавить запись")
        add_record_btn.clicked.connect(lambda: self.add_medical_record(animal['_id'], medical_list))
        view_record_btn = QPushButton("Просмотреть")
        view_record_btn.clicked.connect(lambda: self.show_medical_record(medical_list.currentItem()))

        btn_layout.addWidget(add_record_btn)
        btn_layout.addWidget(view_record_btn)

        layout.addWidget(medical_list)
        layout.addLayout(btn_layout)
        tab.setLayout(layout)

        attachments_list = QListWidget()
        delegate = AttachmentDelegate(attachments_list)
        attachments_list.setItemDelegate(delegate)
        attachments_list.viewport().setAttribute(Qt.WidgetAttribute.WA_Hover)

    def change_animal_photo(self, animal_id, photo_label):
        """Обновляет фото животного.

        Args:
            animal_id (str): ID животного
            photo_label (QLabel): Виджет для отображения фото
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Выберите фото", "", "Images (*.png *.jpg *.jpeg)")

        if file_path:
            # Сохраняем фото в папку uploads
            upload_dir = "assets/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            new_filename = f"{animal_id}_{os.path.basename(file_path)}"
            new_path = os.path.join(upload_dir, new_filename)

            try:
                # Копируем файл
                import shutil
                shutil.copy(file_path, new_path)

                # Обновляем в базе данных
                update_data = {'photo_path': new_path}
                self.mongo_db.update_animal(animal_id, update_data)

                # Обновляем отображение
                pixmap = QPixmap(new_path)
                photo_label.setPixmap(pixmap.scaled(
                    200, 200, Qt.AspectRatioMode.KeepAspectRatio))

                QMessageBox.information(self, "Успешно", "Фото обновлено")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить фото: {str(e)}")

    def show_medical_record(self, item):
        """Отображает детали медицинской записи.

        Args:
            item (QListWidgetItem): Элемент списка с данными записи
        """
        if not item:
            return

        record = item.data(Qt.ItemDataRole.UserRole)
        dialog = QDialog(self)
        dialog.setWindowTitle("Медицинская запись")
        dialog.setMinimumSize(600, 500)

        layout = QVBoxLayout()

        # Основная информация
        form_layout = QFormLayout()
        form_layout.addRow("Дата:", QLabel(record.get('date', '')))
        form_layout.addRow("Симптомы:", QLabel(record.get('symptoms', '')))
        form_layout.addRow("Диагноз:", QLabel(record.get('diagnosis', '')))
        form_layout.addRow("Лечение:", QLabel(record.get('treatment', '')))

        # Вложения
        attachments_group = QGroupBox("Вложения")
        attachments_layout = QVBoxLayout()
        # Вложения позволяют прикрепить к медицинской записи:
        # Результаты анализов (сканы лабораторных исследований, PDF-отчеты)
        # Рентгеновские снимки (изображения в форматах JPG, PNG, DICOM)
        # Рецепты (сканы или фото назначений врача)
        # Фото симптомов (например, кожных поражений, травм)
        # Выписки из истории болезни (документы Word/PDF)
        # Другие медицинские документы

        attachments_list = QListWidget()
        for attachment in record.get('attachments', []):
            item = QListWidgetItem(attachment)
            attachments_list.addItem(item)

        attachments_layout.addWidget(attachments_list)
        attachments_group.setLayout(attachments_layout)

        layout.addLayout(form_layout)
        layout.addWidget(attachments_group)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)

        layout.addWidget(close_btn)
        dialog.setLayout(layout)
        dialog.exec()

    def add_medical_record(self, animal_id, medical_list):
        """Добавляет новую медицинскую запись.

        Args:
            animal_id (str): ID животного
            medical_list (QListWidget): Виджет списка медицинских записей
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить медицинскую запись")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Форма для ввода данных
        form_layout = QFormLayout()

        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        symptoms_edit = QTextEdit()
        diagnosis_edit = QTextEdit()
        treatment_edit = QTextEdit()

        form_layout.addRow("Дата:", date_edit)
        form_layout.addRow("Симптомы:", symptoms_edit)
        form_layout.addRow("Диагноз:", diagnosis_edit)
        form_layout.addRow("Лечение:", treatment_edit)

        # Кнопка добавления вложений
        attachments_btn = QPushButton("Добавить вложение")
        attachments_btn.clicked.connect(self.add_attachment)

        layout.addLayout(form_layout)
        layout.addWidget(attachments_btn)

        # Кнопки сохранения/отмены
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_medical_record(
            animal_id, medical_list, dialog,
            date_edit.date().toString("yyyy-MM-dd"),
            symptoms_edit.toPlainText(),
            diagnosis_edit.toPlainText(),
            treatment_edit.toPlainText()
        ))
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def save_medical_record(self, animal_id, medical_list, dialog, date, symptoms, diagnosis, treatment):
        """Сохраняет новую медицинскую запись в базу данных.

        Args:
            animal_id (str): ID животного
            medical_list (QListWidget): Виджет списка записей
            dialog (QDialog): Диалоговое окно
            date (str): Дата записи
            symptoms (str): Симптомы
            diagnosis (str): Диагноз
            treatment (str): Лечение
        """
        if not diagnosis:
            QMessageBox.warning(self, "Ошибка", "Диагноз не может быть пустым")
            return

        record_data = {
            'date': date,
            'symptoms': symptoms,
            'diagnosis': diagnosis,
            'treatment': treatment,
            'attachments': self.attachments
        }

        if self.mongo_db.add_medical_record(animal_id, record_data):
            QMessageBox.information(self, "Успешно", "Запись добавлена")
            item = QListWidgetItem(f"{date} - {diagnosis}")
            item.setData(Qt.ItemDataRole.UserRole, record_data)
            medical_list.addItem(item)
            self.attachments = []  # Очищаем список вложений
            dialog.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить запись")

    def add_attachment(self):
        """Добавляет вложение к медицинской записи."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Выберите файл", "", "All Files (*)")

        if file_path:
            # Сохраняем файл в папку uploads
            upload_dir = "assets/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            new_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path)}"
            new_path = os.path.join(upload_dir, new_filename)

            try:
                import shutil
                shutil.copy(file_path, new_path)
                self.attachments.append(new_filename)
                QMessageBox.information(self, "Успешно", "Файл добавлен")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось добавить файл: {str(e)}")

    def show_add_animal_dialog(self):
        """Отображает диалог добавления нового животного."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить животное")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Форма для ввода данных
        form_layout = QFormLayout()

        name_edit = QLineEdit()
        species_edit = QLineEdit()
        breed_edit = QLineEdit()
        birth_date_edit = QDateEdit()
        birth_date_edit.setDate(QDate.currentDate())
        sex_combo = QComboBox()
        sex_combo.addItems(["М", "Ж"])
        owner_edit = QLineEdit()
        phone_edit = QLineEdit()

        phone_validator = QRegularExpressionValidator(
            QRegularExpression(r"\+7\d{10}")  # +7 и 10 цифр
        )
        phone_edit.setValidator(phone_validator)
        phone_edit.setText("+7")
        phone_edit.setPlaceholderText("+7XXXXXXXXXX")

        # Добавляем обработчик для проверки ввода 8
        phone_edit.textChanged.connect(lambda text: self.validate_phone_input(text, phone_edit))

        form_layout.addRow("Имя:", name_edit)
        form_layout.addRow("Вид:", species_edit)
        form_layout.addRow("Порода:", breed_edit)
        form_layout.addRow("Дата рождения:", birth_date_edit)
        form_layout.addRow("Пол:", sex_combo)
        form_layout.addRow("Хозяин:", owner_edit)
        form_layout.addRow("Телефон:", phone_edit)

        layout.addLayout(form_layout)

        # Кнопки сохранения/отмены
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_animal(
            dialog,
            name_edit.text(),
            species_edit.text(),
            breed_edit.text(),
            birth_date_edit.date().toString("yyyy-MM-dd"),
            sex_combo.currentText(),
            owner_edit.text(),
            phone_edit.text()
        ))
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def validate_phone_input(self, text, phone_edit):
        """Валидирует ввод телефона, проверяя на наличие 8 после +7."""
        # Блокируем сигнал чтобы избежать рекурсии
        phone_edit.blockSignals(True)

        try:
            # Проверяем, начинается ли введенный номер с 8 (после +7)
            if len(text) > 2 and text[2] == '8':
                QMessageBox.warning(
                    self,
                    "Некорректный ввод",
                    "Пожалуйста, введите телефон без 8. Используйте формат +7XXXXXXXXXX"
                )
                # Удаляем 8 из номера
                new_text = "+7" + text[3:].lstrip('8')  # Удаляем все 8 после +7
                phone_edit.setText(new_text)
                phone_edit.setCursorPosition(len(new_text))
            # Обеспечиваем, чтобы номер начинался с +7
            if not text.startswith("+7"):
                # Оставляем только цифры
                digits = ''.join(filter(str.isdigit, text))
                # Формируем новый текст
                new_text = "+7" + digits[:10]  # Ограничиваем 10 цифрами после +7
                phone_edit.setText(new_text)
                phone_edit.setCursorPosition(len(new_text))

        finally:
            # Всегда разблокируем сигнал
            phone_edit.blockSignals(False)


    def save_animal(self, dialog, name, species, breed, birth_date, sex, owner_name, owner_phone):
        """Сохраняет новое животное в базу данных.

        Args:
            dialog (QDialog): Диалоговое окно
            name (str): Имя животного
            species (str): Вид животного
            breed (str): Порода
            birth_date (str): Дата рождения
            sex (str): Пол
            owner_name (str): Имя владельца
            owner_phone (str): Телефон владельца
        """
        if not name or not owner_name:
            QMessageBox.warning(self, "Ошибка", "Имя животного и хозяина обязательны")
            return

        animal_data = {
            'name': name,
            'species': species,
            'breed': breed,
            'birth_date': birth_date,
            'sex': sex,
            'owner_name': owner_name,
            'owner_phone': owner_phone,
            'medical_history': []
        }

        if self.mongo_db.create_animal(animal_data):
            QMessageBox.information(self, "Успешно", "Животное добавлено")
            dialog.close()
            self.load_all_animals()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить животное")

    def edit_current_animal(self):
        """Отображает диалог редактирования выбранного животного."""
        selected = self.animals_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите животное")
            return

        animal_id = selected[0].text()
        animal = self.mongo_db.get_animal_by_id(animal_id)
        if not animal:
            QMessageBox.warning(self, "Ошибка", "Животное не найдено")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать животное")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Форма для редактирования
        form_layout = QFormLayout()

        name_edit = QLineEdit(animal.get('name', ''))
        species_edit = QLineEdit(animal.get('species', ''))
        breed_edit = QLineEdit(animal.get('breed', ''))
        birth_date_edit = QDateEdit(QDate.fromString(animal.get('birth_date', ''), "yyyy-MM-dd"))
        sex_combo = QComboBox()
        sex_combo.addItems(["М", "Ж"])
        sex_combo.setCurrentText(animal.get('sex', 'М'))
        owner_edit = QLineEdit(animal.get('owner_name', ''))
        phone_edit = QLineEdit(animal.get('owner_phone', ''))

        phone_validator = QRegularExpressionValidator(
            QRegularExpression(r"\+7\d{10}")  # +7 и 10 цифр
        )
        phone_edit.setValidator(phone_validator)
        phone_edit.textChanged.connect(lambda text: self.validate_phone_input(text, phone_edit))

        form_layout.addRow("Имя:", name_edit)
        form_layout.addRow("Вид:", species_edit)
        form_layout.addRow("Порода:", breed_edit)
        form_layout.addRow("Дата рождения:", birth_date_edit)
        form_layout.addRow("Пол:", sex_combo)
        form_layout.addRow("Хозяин:", owner_edit)
        form_layout.addRow("Телефон:", phone_edit)

        layout.addLayout(form_layout)

        # Кнопки сохранения/отмены
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.update_animal(
            animal['_id'], dialog,
            name_edit.text(),
            species_edit.text(),
            breed_edit.text(),
            birth_date_edit.date().toString("yyyy-MM-dd"),
            sex_combo.currentText(),
            owner_edit.text(),
            phone_edit.text()
        ))
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def update_animal(self, animal_id, dialog, name, species, breed, birth_date, sex, owner_name, owner_phone):
        """Обновляет данные животного в базе данных.

        Args:
            animal_id (str): ID животного
            dialog (QDialog): Диалоговое окно
            name (str): Имя животного
            species (str): Вид животного
            breed (str): Порода
            birth_date (str): Дата рождения
            sex (str): Пол
            owner_name (str): Имя владельца
            owner_phone (str): Телефон владельца
        """
        update_data = {
            'name': name,
            'species': species,
            'breed': breed,
            'birth_date': birth_date,
            'sex': sex,
            'owner_name': owner_name,
            'owner_phone': owner_phone
        }

        if self.mongo_db.update_animal(animal_id, update_data):
            QMessageBox.information(self, "Успешно", "Данные обновлены")
            dialog.close()
            self.load_all_animals()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные")

    def delete_current_animal(self):
        """Удаляет выбранное животное из базы данных."""
        selected = self.animals_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите животное")
            return

        animal_id = selected[0].text()
        animal_name = selected[1].text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить животное {animal_name}? Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.mongo_db.delete_animal(animal_id):
                QMessageBox.information(self, "Успешно", "Животное удалено")
                self.load_all_animals()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить животное")

    def show_context_menu(self, pos, list_widget):
        """
        Показывает контекстное меню для вложений.

        Args:
            pos (QPoint): Позиция курсора.
            list_widget (QListWidget): Виджет списка.
        """
        item = list_widget.itemAt(pos)
        if not item:
            return

        record = item.data(Qt.ItemDataRole.UserRole)
        if not record or 'attachments' not in record:
            return

        menu = QMenu()

        # Меню для каждого вложения
        for attachment in record.get('attachments', []):
            action = menu.addAction(f"Открыть: {attachment}")
            action.triggered.connect(
                lambda checked, a=attachment: self.open_attachment(a))

        menu.exec(list_widget.mapToGlobal(pos))

    def open_attachment(self, item_or_path):
        """
        Открывает вложение во внешней программе.

        Поддерживает:
        - QListWidgetItem (при двойном клике)
        - QModelIndex (при клике на кнопку в делегате)
        - str (при открытии из контекстного меню)

        Args:
            item_or_path: Объект с данными о файле или путь к файлу.
        """
        try:
            # Определяем путь к файлу в зависимости от типа входных данных
            if isinstance(item_or_path, str):
                file_name = item_or_path
            elif hasattr(item_or_path, 'data') and callable(item_or_path.data):
                file_name = item_or_path.data()
            elif hasattr(item_or_path, 'text'):
                file_name = item_or_path.text()
            else:
                raise ValueError("Неподдерживаемый тип данных для открытия")

            full_path = os.path.abspath(os.path.join("assets/uploads", file_name))

            # Проверка безопасности
            if not self.validate_file_path(full_path):
                return

            # Открытие файла
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(full_path)):
                QMessageBox.information(
                    self,
                    "Информация",
                    f"Файл можно открыть вручную:\n{full_path}"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось открыть файл:\n{str(e)}"
            )

    def validate_file_path(self, file_path):
        """
        Проверяет путь к файлу на безопасность.

        Args:
            file_path (str): Полный путь к файлу.

        Returns:
            bool: True если файл безопасен для открытия.
        """
        # Проверяем существование файла
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Ошибка", "Файл не найден")
            return False

        # Проверяем разрешенные расширения
        allowed_extensions = ('.pdf', '.jpg', '.jpeg', '.png',
                              '.doc', '.docx', '.txt', '.dicom')
        if not file_path.lower().endswith(allowed_extensions):
            QMessageBox.warning(
                self,
                "Ошибка",
                "Недопустимый тип файла. Разрешены только:\n" +
                ", ".join(allowed_extensions)
            )
            return False

        # Защита от path traversal
        upload_dir = os.path.abspath("assets/uploads")
        if not os.path.commonpath([upload_dir, file_path]) == upload_dir:
            QMessageBox.warning(self, "Ошибка", "Недопустимый путь к файлу")
            return False

        return True



class AttachmentDelegate(QStyledItemDelegate):
    """
    Кастомный делегат для отображения кнопки открытия при наведении на вложение.

    Attributes:
        _hovered_row (int): Индекс строки, над которой находится курсор.
    """

    def __init__(self, parent=None):
        """
        Инициализация делегата.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._hovered_row = -1

    def paint(self, painter, option, index):
        """
        Отрисовка элемента списка с кнопкой при наведении.

        Args:
            painter (QPainter): Объект для отрисовки.
            option (QStyleOptionViewItem): Параметры отображения.
            index (QModelIndex): Индекс элемента.
        """
        super().paint(painter, option, index)

        # Рисуем иконку открытия при наведении
        if option.state & QStyleOptionViewItem.StateFlag.State_MouseOver:
            button_rect = QRect(
                option.rect.right() - 30,
                option.rect.top() + 2,
                25,
                option.rect.height() - 4
            )

            painter.save()
            painter.setPen(Qt.GlobalColor.blue)
            painter.drawText(button_rect, Qt.AlignmentFlag.AlignCenter, "📂")
            painter.restore()

    def editorEvent(self, event, model, option, index):
        """
        Обработка событий для клика по кнопке открытия.

        Args:
            event (QEvent): Событие.
            model: Модель данных.
            option (QStyleOptionViewItem): Параметры отображения.
            index (QModelIndex): Индекс элемента.

        Returns:
            bool: True если событие обработано, иначе False.
        """
        if (event.type() == QEvent.Type.MouseButtonRelease and
                option.rect.right() - 30 <= event.pos().x() <= option.rect.right()):
            self.parent().open_attachment(index)
            return True
        return super().editorEvent(event, model, option, index)

