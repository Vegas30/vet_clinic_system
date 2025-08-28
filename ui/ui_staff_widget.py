# ui_staff_widget.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QComboBox, QGroupBox, QHeaderView, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

from database.database_models_pg import PostgresModels


class StaffDialog(QDialog):
    """Диалоговое окно для добавления/редактирования сотрудника"""

    def __init__(self, parent=None, staff_data=None, branches=None):
        super().__init__(parent)
        self.branches = branches or []
        self.setWindowTitle("Добавить сотрудника" if not staff_data else "Редактировать сотрудника")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Поля формы
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("ФИО сотрудника")
        form_layout.addRow("ФИО:", self.full_name_edit)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин для входа")
        form_layout.addRow("Логин:", self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Пароль:", self.password_edit)

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Подтверждение пароля")
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Подтверждение:", self.confirm_password_edit)

        # Роль сотрудника
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "doctor", "assistant"])
        form_layout.addRow("Роль:", self.role_combo)

        # Выбор филиала
        self.branch_combo = QComboBox()
        self.load_branches()
        form_layout.addRow("Филиал:", self.branch_combo)

        # Заполнение полей при редактировании
        if staff_data:
            self.full_name_edit.setText(staff_data.get('full_name', ''))
            self.login_edit.setText(staff_data.get('login', ''))
            self.role_combo.setCurrentText(staff_data.get('role', 'assistant'))

            # Для редактирования скрываем поля пароля
            self.password_edit.setVisible(False)
            self.confirm_password_edit.setVisible(False)
            form_layout.removeRow(2)  # Удаляем строку с подтверждением пароля
            form_layout.removeRow(2)  # Удаляем строку с паролем

            # Устанавливаем филиал
            branch_index = self.branch_combo.findData(staff_data.get('branch_id'))
            if branch_index >= 0:
                self.branch_combo.setCurrentIndex(branch_index)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_branches(self):
        """Загружает список филиалов в комбобокс"""
        self.branch_combo.clear()
        for branch in self.branches:
            self.branch_combo.addItem(f"{branch[1]} - {branch[2]}", branch[0])

    def get_data(self):
        """Возвращает введенные данные"""
        return {
            'full_name': self.full_name_edit.text().strip(),
            'login': self.login_edit.text().strip(),
            'password': self.password_edit.text(),
            'role': self.role_combo.currentText(),
            'branch_id': self.branch_combo.currentData()
        }

    def validate(self):
        """Валидация введенных данных"""
        data = self.get_data()

        if not data['full_name']:
            QMessageBox.warning(self, "Ошибка", "ФИО обязательно для заполнения")
            return False

        if not data['login']:
            QMessageBox.warning(self, "Ошибка", "Логин обязателен для заполнения")
            return False

        # Проверка пароля только при создании нового сотрудника
        if self.password_edit.isVisible():
            if not data['password']:
                QMessageBox.warning(self, "Ошибка", "Пароль обязателен")
                return False

            if data['password'] != self.confirm_password_edit.text():
                QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
                return False

            if len(data['password']) < 4:
                QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 4 символа")
                return False

        if not data['branch_id']:
            QMessageBox.warning(self, "Ошибка", "Необходимо выбрать филиал")
            return False

        return True


class StaffDetailsDialog(QDialog):
    """Диалог просмотра детальной информации о сотруднике"""

    def __init__(self, staff_data, branch_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Информация о сотруднике: {staff_data[1]}")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Отображение информации
        form_layout.addRow("ID:", QLabel(str(staff_data[0])))
        form_layout.addRow("ФИО:", QLabel(staff_data[1]))
        form_layout.addRow("Логин:", QLabel(staff_data[2]))
        form_layout.addRow("Роль:", QLabel(staff_data[4]))
        form_layout.addRow("Филиал:", QLabel(branch_name or "Не указан"))

        layout.addLayout(form_layout)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class StaffWidget(QWidget):
    """Виджет для управления сотрудниками ветеринарной клиники"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = PostgresModels()
        self.current_staff_id = None
        self.branches = []

        self.init_ui()
        self.load_staff_data()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Управление сотрудниками")
        self.setMinimumSize(1000, 600)

        # Основной макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Верхняя панель с поиском и кнопками
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Группа поиска
        search_group = QGroupBox("Поиск сотрудника")
        search_layout = QHBoxLayout(search_group)

        # Выбор фильтра поиска
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ФИО", "Логин", "Роль", "Филиал"])

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите значение для поиска...")
        self.search_input.setClearButtonEnabled(True)

        # Кнопка поиска
        search_btn = QPushButton("Поиск")
        search_btn.setIcon(QIcon("assets/icons/search.png"))
        search_btn.clicked.connect(self.search_staff)

        # Кнопка сброса
        clear_btn = QPushButton("Сбросить")
        clear_btn.setIcon(QIcon("assets/icons/clear.png"))
        clear_btn.clicked.connect(self.clear_search)

        search_layout.addWidget(self.filter_combo)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)

        # Группа кнопок управления
        buttons_group = QGroupBox("Действия")
        buttons_layout = QHBoxLayout(buttons_group)

        # Кнопка добавления нового сотрудника
        self.add_btn = QPushButton("Добавить")
        self.add_btn.setIcon(QIcon("assets/icons/add.png"))
        self.add_btn.clicked.connect(self.show_add_staff_dialog)
        self.add_btn.setToolTip("Добавить нового сотрудника")

        # Кнопки управления
        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.setIcon(QIcon("assets/icons/edit.png"))
        self.edit_btn.clicked.connect(self.edit_current_staff)
        self.edit_btn.setToolTip("Редактировать выбранного сотрудника")

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setIcon(QIcon("assets/icons/delete.png"))
        self.delete_btn.clicked.connect(self.delete_current_staff)
        self.delete_btn.setToolTip("Удалить выбранного сотрудника")

        self.details_btn = QPushButton("Подробнее")
        self.details_btn.setIcon(QIcon("assets/icons/details.png"))
        self.details_btn.clicked.connect(self.show_current_staff_details)
        self.details_btn.setToolTip("Просмотр подробной информации")

        # Проверка прав доступа
        if self.user_data['role'] != 'admin':
            self.add_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.details_btn)

        # Добавляем группы на верхнюю панель
        top_layout.addWidget(search_group)
        top_layout.addWidget(buttons_group)

        # Таблица сотрудников
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(5)
        self.staff_table.setHorizontalHeaderLabels(["ID", "ФИО", "Логин", "Роль", "Филиал"])

        # Настройка отображения таблицы
        self.staff_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.staff_table.verticalHeader().setVisible(False)
        self.staff_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.staff_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.staff_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.staff_table.cellDoubleClicked.connect(self.show_current_staff_details)

        # Сборка основного интерфейса
        main_layout.addWidget(top_panel)
        main_layout.addWidget(self.staff_table)

        self.setLayout(main_layout)

    def load_staff_data(self):
        """Загружает всех сотрудников из базы данных"""
        try:
            # Загрузка филиалов для отображения в комбобоксах
            self.branches = self.db.get_all_branches()

            # Загрузка сотрудников
            staff_data = self.db.get_all_employees()
            self.display_staff(staff_data)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные сотрудников: {str(e)}")

    def display_staff(self, staff_data):
        """Отображает список сотрудников в таблице"""
        self.staff_table.setRowCount(len(staff_data))

        for row, staff in enumerate(staff_data):
            # staff: (id, full_name, login, password_hash, role, branch_id)
            self.staff_table.setItem(row, 0, QTableWidgetItem(str(staff[0])))
            self.staff_table.setItem(row, 1, QTableWidgetItem(staff[1]))
            self.staff_table.setItem(row, 2, QTableWidgetItem(staff[2]))
            self.staff_table.setItem(row, 3, QTableWidgetItem(staff[4]))

            # Получаем название филиала
            branch_name = self.get_branch_name(staff[5])
            self.staff_table.setItem(row, 4, QTableWidgetItem(branch_name))

    def get_branch_name(self, branch_id):
        """Возвращает название филиала по ID"""
        for branch in self.branches:
            if branch[0] == branch_id:
                return branch[1]  # Название филиала
        return "Неизвестно"

    def search_staff(self):
        """Выполняет поиск сотрудников по выбранному фильтру"""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_staff_data()
            return

        filter_type = self.filter_combo.currentText()
        staff_data = self.db.get_all_employees()
        filtered_staff = []

        for staff in staff_data:
            if filter_type == "ФИО" and search_text.lower() in staff[1].lower():
                filtered_staff.append(staff)
            elif filter_type == "Логин" and search_text.lower() in staff[2].lower():
                filtered_staff.append(staff)
            elif filter_type == "Роль" and search_text.lower() in staff[4].lower():
                filtered_staff.append(staff)
            elif filter_type == "Филиал":
                branch_name = self.get_branch_name(staff[5])
                if search_text.lower() in branch_name.lower():
                    filtered_staff.append(staff)

        self.display_staff(filtered_staff)

    def clear_search(self):
        """Сбрасывает поиск и загружает всех сотрудников"""
        self.search_input.clear()
        self.load_staff_data()

    def get_selected_staff(self):
        """Возвращает данные выбранного сотрудника"""
        selected_row = self.staff_table.currentRow()
        if selected_row >= 0:
            staff_id = int(self.staff_table.item(selected_row, 0).text())
            staff_data = self.db.get_employee_by_id(staff_id)
            return staff_data
        return None

    def show_add_staff_dialog(self):
        """Отображает диалог добавления нового сотрудника"""
        dialog = StaffDialog(self, branches=self.branches)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.validate():
            data = dialog.get_data()
            self.add_staff(data)

    def add_staff(self, staff_data):
        """Добавляет нового сотрудника в базу данных"""
        try:
            # Хеширование пароля (в реальном приложении используйте bcrypt или подобное)
            # Здесь упрощенная реализация - в production используйте безопасное хеширование
            password_hash = staff_data['password']  # В реальном приложении: hash_password(staff_data['password'])

            employee_data = {
                "full_name": staff_data['full_name'],
                "login": staff_data['login'],
                "password_hash": password_hash,
                "role": staff_data['role'],
                "branch_id": staff_data['branch_id']
            }

            staff_id = self.db.insert_employee(employee_data)
            if staff_id:
                QMessageBox.information(self, "Успешно", "Сотрудник добавлен")
                self.load_staff_data()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить сотрудника")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении сотрудника: {str(e)}")

    def edit_current_staff(self):
        """Редактирует выбранного сотрудника"""
        if self.user_data['role'] != 'admin':
            QMessageBox.warning(self, "Ошибка", "Только администраторы могут редактировать сотрудников")
            return

        staff_data = self.get_selected_staff()
        if not staff_data:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника для редактирования")
            return

        # Преобразуем в словарь для диалога
        staff_dict = {
            'full_name': staff_data[1],
            'login': staff_data[2],
            'role': staff_data[4],
            'branch_id': staff_data[5]
        }

        dialog = StaffDialog(self, staff_data=staff_dict, branches=self.branches)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.validate():
            data = dialog.get_data()
            self.update_staff(staff_data[0], data)

    def update_staff(self, staff_id, staff_data):
        """Обновляет данные сотрудника"""
        try:
            success = self.db.update_employee(
                staff_id,
                staff_data['full_name'],
                staff_data['login'],
                staff_data.get('password', ''),  # Пароль только если изменен
                staff_data['role'],
                staff_data['branch_id']
            )

            if success:
                QMessageBox.information(self, "Успешно", "Данные сотрудника обновлены")
                self.load_staff_data()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные сотрудника")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении сотрудника: {str(e)}")

    def delete_current_staff(self):
        """Удаляет выбранного сотрудника"""
        if self.user_data['role'] != 'admin':
            QMessageBox.warning(self, "Ошибка", "Только администраторы могут удалять сотрудников")
            return

        staff_data = self.get_selected_staff()
        if not staff_data:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника для удаления")
            return

        # Нельзя удалить самого себя
        if staff_data[0] == self.user_data['id']:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить собственный аккаунт")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить сотрудника {staff_data[1]}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db.delete_employee(staff_data[0]):
                    QMessageBox.information(self, "Успешно", "Сотрудник удален")
                    self.load_staff_data()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить сотрудника")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении сотрудника: {str(e)}")

    def show_current_staff_details(self):
        """Показывает детальную информацию о выбранном сотруднике"""
        staff_data = self.get_selected_staff()
        if not staff_data:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника")
            return

        branch_name = self.get_branch_name(staff_data[5])
        dialog = StaffDetailsDialog(staff_data, branch_name, self)
        dialog.exec()