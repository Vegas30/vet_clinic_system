import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QListWidget, QListWidgetItem, QTextEdit, QDateEdit, QFileDialog,
    QComboBox, QGroupBox, QHeaderView, QTabWidget, QStyleOptionViewItem, QStyledItemDelegate, QMenu
)
from PyQt6.QtCore import Qt, QDate, QEvent, QRect, QUrl
from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
from datetime import datetime
from database.database_models_pg import PostgresModels


class BranchWidget(QWidget):
    """Основной виджет для работы с филиалами.

    Реализует функционал согласно ТЗ:
    - Поиск филиалов с фильтром (по ID, названию, адресу или телефону)
    - Создание/редактирование филиалов в postgreSQL
    - Удаление филиалов
    """

    def __init__(self):
        """Инициализация виджета работы с филиалами."""
        super().__init__()
        self.pSQL_db = PostgresModels()  # Подключение к postgreSQL базе данных
        self.current_branch_id = None  # ID текущего филиала
        # self.attachments = []  # Список вложений для новой мед.записи

        self.init_ui()  # Инициализация интерфейса
        self.get_all_branches()  # Загрузка всех филиалов при старте

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("Управление филиалами")
        self.setMinimumSize(1200, 800)  # Увеличим минимальный размер окна

        # Основной макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Верхняя панель с поиском и кнопками
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Левая часть панели - поиск
        search_group = QGroupBox("Поиск филиала")
        search_layout = QHBoxLayout(search_group)

        # Выбор фильтра поиска
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ID", "Название", "Адрес", "Телефон"])

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите значение для поиска...")
        self.search_input.setClearButtonEnabled(True)

        # Кнопка поиска
        search_btn = QPushButton("Поиск")
        search_btn.setIcon(QIcon("assets/icons/search.png"))
        search_btn.clicked.connect(self.search_branch)

        # Кнопка сброса
        clear_btn = QPushButton("Сбросить")
        clear_btn.setIcon(QIcon("assets/icons/clear.png"))
        clear_btn.clicked.connect(self.clear_search)

        # Добавляем элементы в группу поиска
        search_layout.addWidget(self.filter_combo)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)

        # Правая часть панели - кнопки управления
        buttons_group = QGroupBox("Действия")
        buttons_layout = QHBoxLayout(buttons_group)

        # Кнопка добавления нового животного
        self.add_btn = QPushButton("Добавить")
        self.add_btn.setIcon(QIcon("assets/icons/add.png"))
        self.add_btn.clicked.connect(self.show_add_branch_dialog)
        self.add_btn.setToolTip("Добавить новый филиал")

        # Кнопки управления
        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.setIcon(QIcon("assets/icons/edit.png"))
        self.edit_btn.clicked.connect(self.edit_current_branch)
        self.edit_btn.setToolTip("Редактировать выбранный филиал")

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setIcon(QIcon("assets/icons/delete.png"))
        self.delete_btn.clicked.connect(self.delete_current_branch)
        self.delete_btn.setToolTip("Удалить выбранный филиал")

        self.details_btn = QPushButton("Подробнее")
        self.details_btn.setIcon(QIcon("assets/icons/details.png"))
        self.details_btn.clicked.connect(self.show_current_branch_details)
        self.details_btn.setToolTip("Просмотр подробной информации")

        # Добавляем кнопки в правую часть
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.details_btn)

        # Добавляем группы на верхнюю панель
        top_layout.addWidget(search_group)
        top_layout.addWidget(buttons_group)

        # Таблица филиалов
        self.branches_table = QTableWidget()
        self.branches_table.setColumnCount(6)  # 6 колонок
        self.branches_table.setHorizontalHeaderLabels(["ID", "Имя", "Вид", "Порода", "Хозяин", "Телефон"])

        # Настройка отображения таблицы
        self.branches_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)  # Равномерное растяжение
        self.branches_table.verticalHeader().setVisible(False)
        self.branches_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.branches_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.branches_table.cellDoubleClicked.connect(self.show_branch_details)

        # Сборка основного интерфейса
        main_layout.addWidget(top_panel)
        main_layout.addWidget(self.branches_table)

        self.setLayout(main_layout)

    def get_all_branches(self):
        """Загружает всех животных из базы данных и отображает их в таблице."""
        branches = self.pSQL_db.get_all_branches()
        self.display_branches(branches)

    def display_branches(self, branches):
        """Отображает список филиалов в таблице.

        Args:
            branches (list): Список словарей с данными филиалов
        """
        self.branches_table.setRowCount(len(branches))
        for row, branch in enumerate(branches):
            self.branches_table.setItem(row, 0, QTableWidgetItem(branch['id']))
            self.branches_table.setItem(row, 1, QTableWidgetItem(branch.get('name', '')))
            self.branches_table.setItem(row, 2, QTableWidgetItem(branch.get('address', '')))
            self.branches_table.setItem(row, 3, QTableWidgetItem(branch.get('phone', '')))


    def search_branches(self):
        """Выполняет поиск животных по выбранному фильтру."""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.get_all_branches()
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

        branches = self.pSQL_db.search_branches(criteria)
        self.display_branches(branches)

    def clear_search(self):
        """Сбрасывает поиск и загружает всех животных."""
        self.search_input.clear()
        self.load_all_branches()

    def show_current_branch_details(self):
        """Отображает детальную информацию о выбранном животном."""
        try:
            selected_items = self.branches_table.selectedItems()

            # Проверяем, что выбрана хотя бы одна ячейка
            if not selected_items or len(selected_items) == 0:
                QMessageBox.warning(self, "Ошибка", "Выберите филиал из таблицы")
                return

            # Получаем ID из первого столбца выбранной строки
            selected_row = self.branches_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Ошибка", "Не выбрана строка")
                return

            branch_id_item = self.branches_table.item(selected_row, 0)
            if not branch_id_item:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить ID животного")
                return

            branch_id = branch_id_item.text()
            if not branch_id:
                QMessageBox.warning(self, "Ошибка", "ID животного пуст")
                return

            self.show_branch_details(selected_row)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            print(f"Error in show_current_branch_details: {e}")

    def show_branch_details(self, row):
        """Открывает диалог с подробной информацией о животном."""
        try:
            branch_id_item = self.branches_table.item(row, 0)
            if not branch_id_item:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить ID животного")
                return

            branch_id = branch_id_item.text()
            branch = self.pSQL_db.get_branch_by_id(branch_id)

            if not branch:
                QMessageBox.warning(self, "Ошибка", "Филиал не найден в базе данных")
                return

            # Создаем диалог с проверкой
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Карточка животного: {branch.get('name', 'Без имени')}")
            dialog.setMinimumSize(800, 600)

            # Добавляем защиту от ошибок при создании вкладок
            try:
                layout = QVBoxLayout()
                tabs = QTabWidget()

                # Вкладка "Общая информация"
                general_tab = QWidget()
                self.init_general_tab(general_tab, branch)
                tabs.addTab(general_tab, "Общая информация")

                # Вкладка "История болезни"
                medical_tab = QWidget()
                self.init_medical_tab(medical_tab, branch)
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
            print(f"Error in show_branch_details: {e}")

    def init_general_tab(self, tab, branch):
        """Инициализирует вкладку с общей информацией о животном.

        Args:
            tab (QWidget): Виджет вкладки
            branch (dict): Данные животного
        """
        layout = QFormLayout()

        # Фото животного
        photo_label = QLabel()
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_label.setFixedSize(200, 200)
        photo_label.setStyleSheet("border: 1px solid #ccc;")

        photo_path = branch.get('photo_path', '')
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            photo_label.setPixmap(pixmap.scaled(
                200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            photo_label.setText("Фото отсутствует")

        # Основная информация
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"<b>Имя:</b> {branch.get('name', '')}"))
        info_layout.addWidget(QLabel(f"<b>Вид:</b> {branch.get('species', '')}"))
        info_layout.addWidget(QLabel(f"<b>Порода:</b> {branch.get('breed', '')}"))
        info_layout.addWidget(QLabel(f"<b>Дата рождения:</b> {branch.get('birth_date', '')}"))
        info_layout.addWidget(QLabel(f"<b>Пол:</b> {branch.get('sex', '')}"))
        info_layout.addWidget(QLabel(f"<b>Хозяин:</b> {branch.get('owner_name', '')}"))
        info_layout.addWidget(QLabel(f"<b>Телефон:</b> {branch.get('owner_phone', '')}"))

        # Кнопка изменения фото
        change_photo_btn = QPushButton("Изменить фото")
        change_photo_btn.clicked.connect(lambda: self.change_branch_photo(branch['_id'], photo_label))

        # Расположение элементов
        photo_layout = QHBoxLayout()
        photo_layout.addWidget(photo_label)
        photo_layout.addLayout(info_layout)

        layout.addRow(photo_layout)
        layout.addRow(change_photo_btn)
        tab.setLayout(layout)

    def init_medical_tab(self, tab, branch):
        """Инициализирует вкладку с историей болезни животного.

        Args:
            tab (QWidget): Виджет вкладки
            branch (dict): Данные животного
        """
        layout = QVBoxLayout()

        # Список медицинских записей
        medical_list = QListWidget()

        # Заполняем список записями
        for record in branch.get('medical_history', []):
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
        add_record_btn.clicked.connect(lambda: self.add_medical_record(branch['_id'], medical_list))
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

    def change_branch_photo(self, branch_id, photo_label):
        """Обновляет фото животного.

        Args:
            branch_id (str): ID животного
            photo_label (QLabel): Виджет для отображения фото
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Выберите фото", "", "Images (*.png *.jpg *.jpeg)")

        if file_path:
            # Сохраняем фото в папку uploads
            upload_dir = "assets/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            new_filename = f"{branch_id}_{os.path.basename(file_path)}"
            new_path = os.path.join(upload_dir, new_filename)

            try:
                # Копируем файл
                import shutil
                shutil.copy(file_path, new_path)

                # Обновляем в базе данных
                update_data = {'photo_path': new_path}
                self.pSQL_db.update_branch(branch_id, update_data)

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

    def add_medical_record(self, branch_id, medical_list):
        """Добавляет новую медицинскую запись.

        Args:
            branch_id (str): ID животного
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
            branch_id, medical_list, dialog,
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

    def save_medical_record(self, branch_id, medical_list, dialog, date, symptoms, diagnosis, treatment):
        """Сохраняет новую медицинскую запись в базу данных.

        Args:
            branch_id (str): ID животного
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

        if self.pSQL_db.add_medical_record(branch_id, record_data):
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

    def show_add_branch_dialog(self):
        """Отображает диалог добавления нового животного."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить филиал")
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
        save_btn.clicked.connect(lambda: self.save_branch(
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

    def save_branch(self, dialog, name, address, phone):
        """Сохраняет новый филиал в базу данных.

        Args:
            dialog (QDialog): Диалоговое окно
            name (str): Название филиала
            address (str): Адрес филиала
            phone (str): Телефон филиала

        """
        if not name or not phone:
            QMessageBox.warning(self, "Ошибка", "Название филиала и телефон не могут быть пустыми")
            return

        branch_data = {
            'name': name,
            'address': address,
            'phone': phone,
        }

        if self.pSQL_db.insert_branch(branch_data):
            QMessageBox.information(self, "Успешно", "Филиал добавлен")
            dialog.close()
            self.get_all_branches()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить филиал")

    def edit_current_branch(self):
        """Отображает диалог редактирования выбранного животного."""
        selected = self.branches_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите филиал")
            return

        branch_id = selected[0].text()
        branch = self.pSQL_db.get_branch_by_id(int(branch_id))
        if not branch:
            QMessageBox.warning(self, "Ошибка", "Филиал не найден")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать филиал")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Форма для редактирования
        form_layout = QFormLayout()

        name_edit = QLineEdit(branch.get('name', ''))
        species_edit = QLineEdit(branch.get('species', ''))
        breed_edit = QLineEdit(branch.get('breed', ''))
        birth_date_edit = QDateEdit(QDate.fromString(branch.get('birth_date', ''), "yyyy-MM-dd"))
        sex_combo = QComboBox()
        sex_combo.addItems(["М", "Ж"])
        sex_combo.setCurrentText(branch.get('sex', 'М'))
        owner_edit = QLineEdit(branch.get('owner_name', ''))
        phone_edit = QLineEdit(branch.get('owner_phone', ''))

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
        save_btn.clicked.connect(lambda: self.update_branch(
            branch['_id'], dialog,
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

    def update_branch(self, _id, dialog, name, species, breed, birth_date, sex, owner_name, owner_phone):
        """Обновляет данные животного в базе данных.

        Args:
            _id (int): ID животного
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

        if self.pSQL_db.update_branch(_id, update_data):
            QMessageBox.information(self, "Успешно", "Данные обновлены")
            dialog.close()
            self.get_all_branches()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные")

    def delete_current_branch(self):
        """Удаляет выбранный филиал из базы данных."""
        selected = self.branches_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите филиал")
            return

        branch_id = selected[0].text()
        branch_name = selected[1].text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить филиал {branch_name}? Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.pSQL_db.delete_branch(branch_id):
                QMessageBox.information(self, "Успешно", "Филиал удалён")
                self.get_all_branches()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить филиал")

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

