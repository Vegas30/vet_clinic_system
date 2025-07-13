from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QMessageBox, QFileDialog
from logic.logic_reports_generator import ReportsGenerator
from database.database_models_pg import PostgresModels
from logic.logic_calendar_utils import CalendarUtils
from PyQt6.QtCore import QDate

class ReportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.reports_generator = ReportsGenerator()
        self.pg_models = PostgresModels()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Отчет 1: Животные по диагнозу
        diagnosis_report_group = QVBoxLayout()
        diagnosis_report_group.addWidget(QLabel("Отчет: Животные по диагнозу"))
        
        diagnosis_input_layout = QHBoxLayout()
        self.diagnosis_input = QLineEdit(self)
        self.diagnosis_input.setPlaceholderText("Введите диагноз")
        diagnosis_input_layout.addWidget(self.diagnosis_input)
        
        self.generate_diagnosis_csv_button = QPushButton("Сгенерировать CSV", self)
        self.generate_diagnosis_csv_button.clicked.connect(self.generate_animals_by_diagnosis_csv)
        diagnosis_input_layout.addWidget(self.generate_diagnosis_csv_button)
        
        diagnosis_report_group.addLayout(diagnosis_input_layout)
        main_layout.addLayout(diagnosis_report_group)
        
        main_layout.addStretch(1) # Добавляем растяжку для выравнивания содержимого вверх

        # Отчет 2: Приёмы по врачу и дате
        appointments_report_group = QVBoxLayout()
        appointments_report_group.addWidget(QLabel("Отчет: Приёмы по врачу и дате"))

        vet_selection_layout = QHBoxLayout()
        self.vet_combo = QComboBox(self)
        vet_selection_layout.addWidget(QLabel("Врач:"))
        vet_selection_layout.addWidget(self.vet_combo)
        self.load_vets_to_combobox()
        appointments_report_group.addLayout(vet_selection_layout)

        date_input_layout = QHBoxLayout()
        self.appointment_date_input = QLineEdit(self)
        self.appointment_date_input.setPlaceholderText(CalendarUtils.format_date(QDate.currentDate().toPyDate()))
        date_input_layout.addWidget(QLabel("Дата (ГГГГ-ММ-ДД):"))
        date_input_layout.addWidget(self.appointment_date_input)
        appointments_report_group.addLayout(date_input_layout)

        self.generate_appointments_csv_button = QPushButton("Сгенерировать CSV", self)
        self.generate_appointments_csv_button.clicked.connect(self.generate_appointments_by_vet_date_csv)
        appointments_report_group.addWidget(self.generate_appointments_csv_button)

        main_layout.addLayout(appointments_report_group)

        self.setLayout(main_layout)

    def load_vets_to_combobox(self):
        employees = self.pg_models.get_all_employees()
        if employees:
            for emp_id, full_name, _, _, role, _ in employees:
                if role == 'Врач':
                    self.vet_combo.addItem(f"{full_name} (ID: {emp_id})", emp_id)

    def generate_animals_by_diagnosis_csv(self):
        diagnosis = self.diagnosis_input.text().strip()
        if not diagnosis:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите диагноз.")
            return

        options = QFileDialog.Option.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "animals_by_diagnosis.csv", "CSV Files (*.csv)", options=options)
        if filename:
            if self.reports_generator.generate_animals_by_diagnosis_csv(diagnosis, filename):
                QMessageBox.information(self, "Успех", f"Отчет по животным с диагнозом '{diagnosis}' успешно сгенерирован: {filename}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сгенерировать отчет.")

    def generate_appointments_by_vet_date_csv(self):
        vet_id = self.vet_combo.currentData()
        date_str = self.appointment_date_input.text().strip()

        if not vet_id or not date_str:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите врача и введите дату.")
            return

        parsed_date = CalendarUtils.parse_date_str(date_str)
        if not parsed_date:
            QMessageBox.warning(self, "Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
            return

        options = QFileDialog.Option.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "appointments_report.csv", "CSV Files (*.csv)", options=options)
        if filename:
            if self.reports_generator.generate_appointments_by_vet_date_csv(vet_id, CalendarUtils.format_date(parsed_date), filename):
                QMessageBox.information(self, "Успех", f"Отчет по приёмам для врача ID {vet_id} на дату {date_str} успешно сгенерирован: {filename}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сгенерировать отчет.")