from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox
from database.database_models_pg import PostgresModels
import bcrypt

class StaffWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pg_models = PostgresModels()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Вкладка Сотрудники
        self.staff_tab = QWidget()
        self.tab_widget.addTab(self.staff_tab, "Сотрудники")
        self.init_staff_tab()

        # Вкладка Услуги
        self.services_tab = QWidget()
        self.tab_widget.addTab(self.services_tab, "Услуги")
        self.init_services_tab()

        self.setLayout(main_layout)

    def init_staff_tab(self):
        layout = QVBoxLayout()

        # Элементы управления для сотрудников
        staff_controls_layout = QHBoxLayout()
        self.add_staff_button = QPushButton("Добавить сотрудника", self)
        self.add_staff_button.clicked.connect(self.add_staff)
        staff_controls_layout.addWidget(self.add_staff_button)

        self.edit_staff_button = QPushButton("Редактировать сотрудника", self)
        self.edit_staff_button.clicked.connect(self.edit_staff)
        staff_controls_layout.addWidget(self.edit_staff_button)

        self.delete_staff_button = QPushButton("Удалить сотрудника", self)
        self.delete_staff_button.clicked.connect(self.delete_staff)
        staff_controls_layout.addWidget(self.delete_staff_button)

        layout.addLayout(staff_controls_layout)

        # Таблица сотрудников
        self.staff_table = QTableWidget(self)
        self.staff_table.setColumnCount(5) # id, full_name, login, role, branch_id
        self.staff_table.setHorizontalHeaderLabels(["ID", "Полное имя", "Логин", "Роль", "ID филиала"])
        self.staff_table.horizontalHeader().setStretchLastSection(True)
        self.staff_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.staff_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.staff_table)

        self.staff_tab.setLayout(layout)
        self.load_staff()

    def load_staff(self):
        employees = self.pg_models.get_all_employees()
        self.staff_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            # emp: (id, full_name, login, password_hash, role, branch_id)
            self.staff_table.setItem(row, 0, QTableWidgetItem(str(emp[0])))
            self.staff_table.setItem(row, 1, QTableWidgetItem(emp[1]))
            self.staff_table.setItem(row, 2, QTableWidgetItem(emp[2]))
            self.staff_table.setItem(row, 3, QTableWidgetItem(emp[4]))
            self.staff_table.setItem(row, 4, QTableWidgetItem(str(emp[5])))

    def add_staff(self):
        dialog = AddEditStaffDialog(self.pg_models, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_staff()

    def edit_staff(self):
        selected_row = self.staff_table.currentRow()
        if selected_row >= 0:
            staff_id = int(self.staff_table.item(selected_row, 0).text())
            staff_data = self.pg_models.get_employee_by_id(staff_id)
            if staff_data:
                dialog = AddEditStaffDialog(self.pg_models, self, staff_data=staff_data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_staff()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные сотрудника.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите сотрудника для редактирования.")

    def delete_staff(self):
        selected_row = self.staff_table.currentRow()
        if selected_row >= 0:
            staff_id = int(self.staff_table.item(selected_row, 0).text())
            reply = QMessageBox.question(self, "Удалить сотрудника", f"Вы уверены, что хотите удалить сотрудника с ID {staff_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                if self.pg_models.delete_employee(staff_id):
                    QMessageBox.information(self, "Успех", "Сотрудник успешно удален.")
                    self.load_staff()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить сотрудника.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите сотрудника для удаления.")

    def init_services_tab(self):
        layout = QVBoxLayout()

        # Элементы управления для услуг
        service_controls_layout = QHBoxLayout()
        self.add_service_button = QPushButton("Добавить услугу", self)
        self.add_service_button.clicked.connect(self.add_service)
        service_controls_layout.addWidget(self.add_service_button)

        self.edit_service_button = QPushButton("Редактировать услугу", self)
        self.edit_service_button.clicked.connect(self.edit_service)
        service_controls_layout.addWidget(self.edit_service_button)

        self.delete_service_button = QPushButton("Удалить услугу", self)
        self.delete_service_button.clicked.connect(self.delete_service)
        service_controls_layout.addWidget(self.delete_service_button)

        layout.addLayout(service_controls_layout)

        # Таблица услуг
        self.services_table = QTableWidget(self)
        self.services_table.setColumnCount(4) # id, title, description, price
        self.services_table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Цена"])
        self.services_table.horizontalHeader().setStretchLastSection(True)
        self.services_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.services_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.services_table)

        self.services_tab.setLayout(layout)
        self.load_services()

    def load_services(self):
        services = self.pg_models.get_all_services()
        self.services_table.setRowCount(len(services))
        for row, svc in enumerate(services):
            self.services_table.setItem(row, 0, QTableWidgetItem(str(svc[0])))
            self.services_table.setItem(row, 1, QTableWidgetItem(svc[1]))
            self.services_table.setItem(row, 2, QTableWidgetItem(svc[2] if svc[2] else ""))
            self.services_table.setItem(row, 3, QTableWidgetItem(str(svc[3])))

    def add_service(self):
        dialog = AddEditServiceDialog(self.pg_models, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_services()

    def edit_service(self):
        selected_row = self.services_table.currentRow()
        if selected_row >= 0:
            service_id = int(self.services_table.item(selected_row, 0).text())
            service_data = self.pg_models.get_service_by_id(service_id)
            if service_data:
                dialog = AddEditServiceDialog(self.pg_models, self, service_data=service_data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_services()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные услуги.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите услугу для редактирования.")

    def delete_service(self):
        selected_row = self.services_table.currentRow()
        if selected_row >= 0:
            service_id = int(self.services_table.item(selected_row, 0).text())
            reply = QMessageBox.question(self, "Удалить услугу", f"Вы уверены, что хотите удалить услугу с ID {service_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                if self.pg_models.delete_service(service_id):
                    QMessageBox.information(self, "Успех", "Услуга успешно удалена.")
                    self.load_services()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить услугу.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите услугу для удаления.")


class AddEditStaffDialog(QDialog):
    def __init__(self, pg_models, parent=None, staff_data=None):
        super().__init__(parent)
        self.pg_models = pg_models
        self.staff_data = staff_data
        self.setWindowTitle("Редактировать сотрудника" if staff_data else "Добавить нового сотрудника")
        self.init_ui()
        self.load_branches()
        if self.staff_data:
            self.load_staff_data()

    def init_ui(self):
        layout = QFormLayout()

        self.full_name_input = QLineEdit(self)
        layout.addRow("Полное имя:", self.full_name_input)

        self.login_input = QLineEdit(self)
        layout.addRow("Логин:", self.login_input)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Пароль (оставьте пустым для сохранения текущего):", self.password_input)

        self.role_combo = QComboBox(self)
        self.role_combo.addItems(["Администратор", "Врач", "Регистратор", "Менеджер"])
        layout.addRow("Роль:", self.role_combo)

        self.branch_combo = QComboBox(self)
        layout.addRow("Филиал:", self.branch_combo)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_staff)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def load_branches(self):
        branches = self.pg_models.get_all_branches()
        if branches:
            for branch_id, name, _, _ in branches:
                self.branch_combo.addItem(f"{name} (ID: {branch_id})", branch_id)

    def load_staff_data(self):
        # staff_data: (id, full_name, login, password_hash, role, branch_id)
        self.full_name_input.setText(self.staff_data[1])
        self.login_input.setText(self.staff_data[2])
        # Пароль не загружается по соображениям безопасности, пользователь должен ввести его повторно или оставить пустым.
        self.role_combo.setCurrentText(self.staff_data[4])
        branch_index = self.branch_combo.findData(self.staff_data[5])
        if branch_index >= 0: 
            self.branch_combo.setCurrentIndex(branch_index)

    def save_staff(self):
        full_name = self.full_name_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        branch_id = self.branch_combo.currentData()

        if not all([full_name, login, role, branch_id]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        hashed_password = None
        if password: # Если пароль предоставлен, хешируем его
            # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') # Хеширование закомментировано
            hashed_password = password # Используем пароль в чистом виде
        elif self.staff_data: # Если редактируем и поле пароля пустое, сохраняем текущий хеш пароля
            hashed_password = self.staff_data[3] # Используем существующий хеш пароля
        else: # Новый сотрудник должен иметь пароль
            QMessageBox.warning(self, "Ошибка", "Для нового сотрудника пароль обязателен.")
            return

        if self.staff_data: # Редактирование существующего сотрудника
            success = self.pg_models.update_employee(self.staff_data[0], full_name, login, hashed_password, role, branch_id)
            if success:
                QMessageBox.information(self, "Успех", "Информация о сотруднике успешно обновлена.")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить информацию о сотруднике.")
        else: # Добавление нового сотрудника
            success = self.pg_models.insert_employee(full_name, login, hashed_password, role, branch_id)
            if success:
                QMessageBox.information(self, "Успех", "Сотрудник успешно добавлен.")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить сотрудника.")


class AddEditServiceDialog(QDialog):
    def __init__(self, pg_models, parent=None, service_data=None):
        super().__init__(parent)
        self.pg_models = pg_models
        self.service_data = service_data
        self.setWindowTitle("Редактировать услугу" if service_data else "Добавить новую услугу")
        self.init_ui()
        if self.service_data:
            self.load_service_data()

    def init_ui(self):
        layout = QFormLayout()

        self.title_input = QLineEdit(self)
        layout.addRow("Название:", self.title_input)

        self.description_input = QLineEdit(self)
        layout.addRow("Описание:", self.description_input)

        self.price_input = QLineEdit(self)
        layout.addRow("Цена:", self.price_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_service)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def load_service_data(self):
        # service_data: (id, title, description, price)
        self.title_input.setText(self.service_data[1])
        self.description_input.setText(self.service_data[2] if self.service_data[2] else "")
        self.price_input.setText(str(self.service_data[3]))

    def save_service(self):
        title = self.title_input.text().strip()
        description = self.description_input.text().strip()
        price_str = self.price_input.text().strip()

        if not all([title, price_str]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните название и цену.")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError("Цена не может быть отрицательной.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Неверный формат цены: {e}")
            return

        if self.service_data: # Редактирование существующей услуги
            success = self.pg_models.update_service(self.service_data[0], title, description, price)
            if success:
                QMessageBox.information(self, "Успех", "Услуга успешно обновлена.")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить услугу.")
        else: # Добавление новой услуги
            success = self.pg_models.insert_service(title, description, price)
            if success:
                QMessageBox.information(self, "Успех", "Услуга успешно добавлена.")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить услугу.")