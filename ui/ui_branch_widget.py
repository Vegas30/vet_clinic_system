import logging
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
        self.load_branches_data()  # Загрузка всех филиалов при старте

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
        search_btn.clicked.connect(self.search_branches)

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

        self.branches_table.setColumnCount(4)  # 4 колонки
        self.branches_table.setHorizontalHeaderLabels(["ID", "Название", "Адрес", "Телефон"])

        # Настройка отображения таблицы
        self.branches_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)  # Равномерное растяжение
        self.branches_table.verticalHeader().setVisible(False)
        self.branches_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.branches_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.branches_table.cellDoubleClicked.connect(self.show_current_branch_details)

        # Сборка основного интерфейса
        main_layout.addWidget(top_panel)
        main_layout.addWidget(self.branches_table)

        self.setLayout(main_layout)

    def load_branches_data(self):
        """Загружает всех животных из базы данных и отображает их в таблице."""
        branches = self.pSQL_db.get_all_branches()

        # Очищаем таблицу перед загрузкой новых данных
        self.branches_table.setRowCount(0)
        if not branches:
            QMessageBox.information(self, "Информация", "Нет доступных филиалов")
            return
        # Заполняем таблицу данными филиалов
        self.display_branches(branches)

    def display_branches(self, branches):
        """Отображает список филиалов в таблице.

        Args:
            branches (list): Список кортежей с данными филиалов (id, name, address, phone)
        """
        # Очищаем таблицу
        self.branches_table.setRowCount(0)

        self.branches_table.setRowCount(len(branches))

        for row, branch in enumerate(branches):

            # branch - это кортеж: (id, name, address, phone)
            self.branches_table.setItem(row, 0, QTableWidgetItem(str(branch[0])))
            self.branches_table.setItem(row, 1, QTableWidgetItem(branch[1] or ''))
            self.branches_table.setItem(row, 2, QTableWidgetItem(branch[2] or ''))
            self.branches_table.setItem(row, 3, QTableWidgetItem(branch[3] or ''))

    def search_branches(self):
        """Выполняет поиск филиалов по выбранному фильтру."""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_branches_data()
            return

        filter_type = self.filter_combo.currentText()

        # Определяем критерии поиска в зависимости от выбранного фильтра
        if filter_type == "ID":
            branches = self.pSQL_db.search_branches_by_id(search_text)
        elif filter_type == "Название":
            branches = self.pSQL_db.search_branches_by_name(search_text)
        elif filter_type == "Адрес":
            branches = self.pSQL_db.search_branches_by_address(search_text)
        else:  # По телефону
            branches = self.pSQL_db.search_branches_by_phone(search_text)

        self.display_branches(branches)

    def clear_search(self):
        """Сбрасывает поиск и загружает всех филиалов."""
        self.search_input.clear()
        self.load_branches_data()

    def show_current_branch_details(self):
        """Отображает детальную информацию о выбранном филиале."""
        try:
            selected_row = self.branches_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите филиал из таблицы")
                return

            branch_id_item = self.branches_table.item(selected_row, 0)
            if not branch_id_item:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить ID филиала")
                return

            branch_id = branch_id_item.text()
            if not branch_id:
                QMessageBox.warning(self, "Ошибка", "ID филиала пуст")
                return

            # Получаем данные филиала из базы данных
            branch = self.pSQL_db.get_branch_by_id(int(branch_id))
            if not branch:
                QMessageBox.warning(self, "Ошибка", "Филиал не найден")
                return

            # Используем ключи словаря вместо индексов
            details_text = f"""
            ID: {branch.get('id', 'N/A')}
            Название: {branch.get('name', 'Не указано')}
            Адрес: {branch.get('address', 'Не указан')}
            Телефон: {branch.get('phone', 'Не указан')}
            """

            QMessageBox.information(self, "Детали филиала", details_text)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            logging.error(f"Error in show_current_branch_details: {e}")

    def show_add_branch_dialog(self):
        """Отображает диалог добавления нового филиала."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить филиал")
        dialog.setMinimumSize(500, 300)

        layout = QVBoxLayout()

        # Форма для ввода данных
        form_layout = QFormLayout()

        name_edit = QLineEdit()
        address_edit = QLineEdit()
        phone_edit = QLineEdit()

        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Адрес:", address_edit)
        form_layout.addRow("Телефон:", phone_edit)

        layout.addLayout(form_layout)

        # Кнопки сохранения/отмены
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_branch(
            dialog,
            name_edit.text(),
            address_edit.text(),
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
            self.load_branches_data()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить филиал")

    def edit_current_branch(self):
        """Отображает диалог редактирования выбранного филиала."""
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
        dialog.setMinimumSize(500, 300)

        layout = QVBoxLayout()

        # Форма для редактирования
        form_layout = QFormLayout()

        # Используем ключи словаря вместо индексов
        name_edit = QLineEdit(branch.get('name', '') or '')
        address_edit = QLineEdit(branch.get('address', '') or '')
        phone_edit = QLineEdit(branch.get('phone', '') or '')

        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Адрес:", address_edit)
        form_layout.addRow("Телефон:", phone_edit)

        layout.addLayout(form_layout)

        # Кнопки сохранения/отмены
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.update_branch(
            branch.get('id'), dialog,
            name_edit.text(),
            address_edit.text(),
            phone_edit.text()
        ))
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def update_branch(self, branch_id, dialog, name, address, phone):
        """Обновляет данные филиала в базе данных.

        Args:
            branch_id (int): ID филиала
            dialog (QDialog): Диалоговое окно
            name (str): Название филиала
            address (str): Адрес филиала
            phone (str): Телефон филиала
        """
        update_data = {
            'name': name,
            'address': address,
            'phone': phone
        }

        if self.pSQL_db.update_branch(branch_id, update_data):
            QMessageBox.information(self, "Успешно", "Данные обновлены")
            dialog.close()
            self.load_branches_data()
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
            if self.pSQL_db.delete_branch(int(branch_id)):
                QMessageBox.information(self, "Успешно", "Филиал удалён")
                self.load_branches_data()
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
