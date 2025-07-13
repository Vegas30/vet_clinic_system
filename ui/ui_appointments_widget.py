from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QCalendarWidget, QDialog, QFormLayout, QLineEdit, QLabel, QComboBox, QMessageBox
from PyQt6.QtCore import Qt, QDate
from database.database_models_pg import PostgresModels
from database.database_models_mongo import MongoDBModels # Используется для получения animal_id по имени животного
from logic.logic_calendar_utils import CalendarUtils

class AppointmentsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pg_models = PostgresModels()
        self.mongo_models = MongoDBModels()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Календарь и кнопка добавления приема
        calendar_layout = QHBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.load_appointments_for_selected_date)
        calendar_layout.addWidget(self.calendar)

        add_appointment_button = QPushButton("Добавить приём", self)
        add_appointment_button.clicked.connect(self.add_appointment)
        calendar_layout.addWidget(add_appointment_button)

        main_layout.addLayout(calendar_layout)

        # Таблица приемов
        self.appointments_table = QTableWidget(self)
        self.appointments_table.setColumnCount(6) # appointment_id, animal_name, vet_name, date, time, service_title, status
        self.appointments_table.setHorizontalHeaderLabels(["ID Приёма", "Животное", "Врач", "Дата", "Время", "Услуга", "Статус"])
        self.appointments_table.horizontalHeader().setStretchLastSection(True)
        self.appointments_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.appointments_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.appointments_table)

        self.setLayout(main_layout)

        # Загрузка приемов на сегодня по умолчанию
        self.load_appointments_for_selected_date()

    def load_appointments_for_selected_date(self):
        selected_date = self.calendar.selectedDate().toPyDate()
        
        # Получаем всех сотрудников и сопоставляем ID с именами для отображения
        employees = self.pg_models.get_all_employees()
        vet_names = {emp[0]: emp[1] for emp in employees} if employees else {}

        # Получаем все услуги и сопоставляем ID с названиями для отображения
        services = self.pg_models.get_all_services()
        service_titles = {svc[0]: svc[1] for svc in services} if services else {}

        # Для демонстрации, получаем все приемы независимо от ветеринара, затем фильтруем по дате.
        # В реальном приложении может быть отдельный метод для получения приемов только по дате.
        all_appointments = []
        for emp in employees:
            appointments_for_vet = self.pg_models.get_appointments_by_vet_and_date(emp[0], CalendarUtils.format_date(selected_date))
            if appointments_for_vet:
                all_appointments.extend(appointments_for_vet)

        self.appointments_table.setRowCount(len(all_appointments))
        for row, appt in enumerate(all_appointments):
            # appt: (id, animal_id, vet_id, date, time, service_id, status)
            animal_info = self.mongo_models.get_animal_by_id(appt[1])
            animal_name = animal_info.get("name", "Неизвестно") if animal_info else "Неизвестно"

            vet_name = vet_names.get(appt[2], "Неизвестно")
            service_title = service_titles.get(appt[5], "Неизвестно")

            self.appointments_table.setItem(row, 0, QTableWidgetItem(str(appt[0])))
            self.appointments_table.setItem(row, 1, QTableWidgetItem(animal_name))
            self.appointments_table.setItem(row, 2, QTableWidgetItem(vet_name))
            self.appointments_table.setItem(row, 3, QTableWidgetItem(CalendarUtils.format_date(appt[3])))
            self.appointments_table.setItem(row, 4, QTableWidgetItem(CalendarUtils.format_time(appt[4])))
            self.appointments_table.setItem(row, 5, QTableWidgetItem(service_title))
            self.appointments_table.setItem(row, 6, QTableWidgetItem(appt[6])) # Статус

    def add_appointment(self):
        dialog = AddAppointmentDialog(self.pg_models, self.mongo_models, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_appointments_for_selected_date() # Перезагружаем приемы после добавления


class AddAppointmentDialog(QDialog):
    def __init__(self, pg_models, mongo_models, parent=None):
        super().__init__(parent)
        self.pg_models = pg_models
        self.mongo_models = mongo_models
        self.setWindowTitle("Добавить новый приём")
        self.init_ui()
        self.load_combobox_data()

    def init_ui(self):
        layout = QFormLayout()

        self.animal_name_input = QLineEdit(self)
        layout.addRow("Имя животного:", self.animal_name_input)

        self.vet_combo = QComboBox(self)
        layout.addRow("Врач:", self.vet_combo)

        self.date_input = QLineEdit(self)
        self.date_input.setPlaceholderText(CalendarUtils.format_date(QDate.currentDate().toPyDate()))
        layout.addRow("Дата (ГГГГ-ММ-ДД):", self.date_input)

        self.time_input = QLineEdit(self)
        self.time_input.setPlaceholderText("ЧЧ:ММ")
        layout.addRow("Время (ЧЧ:ММ):", self.time_input)

        self.service_combo = QComboBox(self)
        layout.addRow("Услуга:", self.service_combo)

        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["запланирован", "завершен", "отменен"])
        layout.addRow("Статус:", self.status_combo)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_appointment)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def load_combobox_data(self):
        # Загрузка ветеринаров
        employees = self.pg_models.get_all_employees()
        if employees:
            for emp_id, full_name, _, _, role, _ in employees:
                # Добавляем в комбобокс только сотрудников с ролью 'Врач'
                if role == 'Врач':
                    self.vet_combo.addItem(f"{full_name} (ID: {emp_id})", emp_id)

        # Загрузка услуг
        services = self.pg_models.get_all_services()
        if services:
            for service_id, title, _, _ in services:
                self.service_combo.addItem(f"{title} (ID: {service_id})", service_id)

    def save_appointment(self):
        animal_name = self.animal_name_input.text().strip()
        vet_id = self.vet_combo.currentData()
        date_str = self.date_input.text().strip()
        time_str = self.time_input.text().strip()
        service_id = self.service_combo.currentData()
        status = self.status_combo.currentText()

        if not all([animal_name, vet_id, date_str, time_str, service_id, status]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        # Получаем animal_id по имени животного с использованием MongoDBModels
        animals = self.mongo_models.get_animals_by_criteria({"name": animal_name})
        animal_id = None
        if animals:
            animal_id = animals[0].get("_id") # Берем первое совпадение
        else:
            QMessageBox.warning(self, "Ошибка", f"Животное с именем '{animal_name}' не найдено.")
            return

        # Разбор даты и времени
        parsed_date = CalendarUtils.parse_date_str(date_str)
        parsed_time = CalendarUtils.parse_time_str(time_str)

        if not parsed_date or not parsed_time:
            QMessageBox.warning(self, "Ошибка", "Неверный формат даты или времени. Используйте ГГГГ-ММ-ДД и ЧЧ:ММ.")
            return

        success = self.pg_models.insert_appointment(animal_id, vet_id, parsed_date, parsed_time, service_id, status)
        if success:
            QMessageBox.information(self, "Успех", "Приём успешно добавлен.")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить приём. Проверьте данные или соединение с БД.")