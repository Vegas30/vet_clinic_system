from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QDialog, QFormLayout, QMessageBox, QTextEdit
from PyQt6.QtCore import Qt
from database.database_models_mongo import MongoDBModels
import os

class AnimalsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mongo_models = MongoDBModels()
        self.init_ui()
        self.load_animals()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Элементы управления поиска и добавления
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Поиск по имени или владельцу")
        self.search_input.textChanged.connect(self.filter_animals)
        search_layout.addWidget(self.search_input)

        self.add_button = QPushButton("Добавить животное", self)
        self.add_button.clicked.connect(self.add_animal)
        search_layout.addWidget(self.add_button)

        main_layout.addLayout(search_layout)

        # Таблица животных
        self.animals_table = QTableWidget(self)
        self.animals_table.setColumnCount(7)  # _id, name, species, breed, birth_date, sex, owner_name, owner_phone, photo_path, medical_history
        self.animals_table.setHorizontalHeaderLabels(["ID", "Имя", "Вид", "Порода", "Дата рождения", "Пол", "Владелец"])
        self.animals_table.horizontalHeader().setStretchLastSection(True)
        self.animals_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.animals_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.animals_table.doubleClicked.connect(self.view_animal_details)
        main_layout.addWidget(self.animals_table)

        # Кнопки действий
        action_layout = QHBoxLayout()
        self.edit_button = QPushButton("Редактировать", self)
        self.edit_button.clicked.connect(self.edit_animal)
        action_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.clicked.connect(self.delete_animal)
        action_layout.addWidget(self.delete_button)

        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    def load_animals(self, query=None):
        animals = self.mongo_models.get_animals_by_criteria(query)
        self.animals_table.setRowCount(len(animals))
        for row, animal in enumerate(animals):
            self.animals_table.setItem(row, 0, QTableWidgetItem(animal.get("_id", "")))
            self.animals_table.setItem(row, 1, QTableWidgetItem(animal.get("name", "")))
            self.animals_table.setItem(row, 2, QTableWidgetItem(animal.get("species", "")))
            self.animals_table.setItem(row, 3, QTableWidgetItem(animal.get("breed", "")))
            self.animals_table.setItem(row, 4, QTableWidgetItem(animal.get("birth_date", "")))
            self.animals_table.setItem(row, 5, QTableWidgetItem(animal.get("sex", "")))
            self.animals_table.setItem(row, 6, QTableWidgetItem(animal.get("owner_name", "")))

    def filter_animals(self):
        search_text = self.search_input.text().strip()
        if search_text:
            query = {
                "$or": [
                    {"name": {"$regex": search_text, "$options": "i"}},
                    {"owner_name": {"$regex": search_text, "$options": "i"}}
                ]
            }
            self.load_animals(query)
        else:
            self.load_animals()

    def add_animal(self):
        dialog = AddEditAnimalDialog(self.mongo_models, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_animals() # Перезагрузка данных после добавления нового животного

    def edit_animal(self):
        selected_row = self.animals_table.currentRow()
        if selected_row >= 0:
            animal_id = self.animals_table.item(selected_row, 0).text()
            animal_data = self.mongo_models.get_animal_by_id(animal_id)
            if animal_data:
                dialog = AddEditAnimalDialog(self.mongo_models, self, animal_data=animal_data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_animals()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные животного.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите животное для редактирования.")

    def delete_animal(self):
        selected_row = self.animals_table.currentRow()
        if selected_row >= 0:
            animal_id = self.animals_table.item(selected_row, 0).text()
            reply = QMessageBox.question(self, "Удалить животное", f"Вы уверены, что хотите удалить животное с ID {animal_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                if self.mongo_models.delete_animal(animal_id):
                    QMessageBox.information(self, "Успех", "Животное успешно удалено.")
                    self.load_animals()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить животное.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите животное для удаления.")

    def view_animal_details(self):
        selected_row = self.animals_table.currentRow()
        if selected_row >= 0:
            animal_id = self.animals_table.item(selected_row, 0).text()
            animal_data = self.mongo_models.get_animal_by_id(animal_id)
            if animal_data:
                details_dialog = AnimalDetailsDialog(animal_data, self.mongo_models, self)
                details_dialog.exec()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить детали животного.")


class AddEditAnimalDialog(QDialog):
    def __init__(self, mongo_models, parent=None, animal_data=None):
        super().__init__(parent)
        self.mongo_models = mongo_models
        self.animal_data = animal_data
        self.setWindowTitle("Редактировать животное" if animal_data else "Добавить новое животное")
        self.init_ui()
        if self.animal_data:
            self.load_animal_data()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit(self)
        layout.addRow("Имя:", self.name_input)

        self.species_input = QLineEdit(self)
        layout.addRow("Вид:", self.species_input)

        self.breed_input = QLineEdit(self)
        layout.addRow("Порода:", self.breed_input)

        self.birth_date_input = QLineEdit(self)
        self.birth_date_input.setPlaceholderText("ГГГГ-ММ-ДД")
        layout.addRow("Дата рождения:", self.birth_date_input)

        self.sex_input = QLineEdit(self)
        self.sex_input.setPlaceholderText("М/Ж")
        layout.addRow("Пол:", self.sex_input)

        self.owner_name_input = QLineEdit(self)
        layout.addRow("Имя владельца:", self.owner_name_input)

        self.owner_phone_input = QLineEdit(self)
        layout.addRow("Телефон владельца:", self.owner_phone_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_animal)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def load_animal_data(self):
        self.name_input.setText(self.animal_data.get("name", ""))
        self.species_input.setText(self.animal_data.get("species", ""))
        self.breed_input.setText(self.animal_data.get("breed", ""))
        self.birth_date_input.setText(self.animal_data.get("birth_date", ""))
        self.sex_input.setText(self.animal_data.get("sex", ""))
        self.owner_name_input.setText(self.animal_data.get("owner_name", ""))
        self.owner_phone_input.setText(self.animal_data.get("owner_phone", ""))

    def save_animal(self):
        name = self.name_input.text()
        species = self.species_input.text()
        breed = self.breed_input.text()
        birth_date = self.birth_date_input.text()
        sex = self.sex_input.text()
        owner_name = self.owner_name_input.text()
        owner_phone = self.owner_phone_input.text()

        if not all([name, species, owner_name]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните обязательные поля (Имя, Вид, Имя владельца).")
            return

        animal_data_to_save = {
            "name": name,
            "species": species,
            "breed": breed,
            "birth_date": birth_date,
            "sex": sex,
            "owner_name": owner_name,
            "owner_phone": owner_phone,
        }

        if self.animal_data: # Редактирование существующего животного
            success = self.mongo_models.update_animal_info(self.animal_data["_id"], animal_data_to_save)
            if success:
                QMessageBox.information(self, "Успех", "Информация о животном успешно обновлена.")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить информацию о животном.")
        else: # Добавление нового животного
            success = self.mongo_models.insert_animal(
                name, species, breed, birth_date, sex, owner_name, owner_phone
            )
            if success:
                QMessageBox.information(self, "Успех", "Животное успешно добавлено.")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить животное.")


class AnimalDetailsDialog(QDialog):
    def __init__(self, animal_data, mongo_models, parent=None):
        super().__init__(parent)
        self.animal_data = animal_data
        self.mongo_models = mongo_models
        self.setWindowTitle(f"Детали животного: {animal_data.get('name', '')}")
        self.setGeometry(200, 200, 600, 500)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Общая информация
        general_info_layout = QFormLayout()
        general_info_layout.addRow("Имя:", QLabel(self.animal_data.get("name", "")))
        general_info_layout.addRow("Вид:", QLabel(self.animal_data.get("species", "")))
        general_info_layout.addRow("Порода:", QLabel(self.animal_data.get("breed", "")))
        general_info_layout.addRow("Дата рождения:", QLabel(self.animal_data.get("birth_date", "")))
        general_info_layout.addRow("Пол:", QLabel(self.animal_data.get("sex", "")))
        general_info_layout.addRow("Владелец:", QLabel(self.animal_data.get("owner_name", "")))
        general_info_layout.addRow("Телефон владельца:", QLabel(self.animal_data.get("owner_phone", "")))
        main_layout.addLayout(general_info_layout)

        # История болезни
        main_layout.addWidget(QLabel("\nИстория болезни:"))
        self.medical_history_table = QTableWidget(self)
        self.medical_history_table.setColumnCount(5) # date, symptoms, diagnosis, treatment, attachments
        self.medical_history_table.setHorizontalHeaderLabels(["Дата", "Симптомы", "Диагноз", "Лечение", "Вложения"])
        self.medical_history_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.medical_history_table)
        self.load_medical_history()

        # Кнопка добавления записи в историю болезни
        add_medical_entry_button = QPushButton("Добавить запись в историю болезни", self)
        add_medical_entry_button.clicked.connect(self.add_medical_entry)
        main_layout.addWidget(add_medical_entry_button)

        self.setLayout(main_layout)

    def load_medical_history(self):
        history = self.animal_data.get("medical_history", [])
        self.medical_history_table.setRowCount(len(history))
        for row, entry in enumerate(history):
            self.medical_history_table.setItem(row, 0, QTableWidgetItem(entry.get("date", "")))
            self.medical_history_table.setItem(row, 1, QTableWidgetItem(entry.get("symptoms", "")))
            self.medical_history_table.setItem(row, 2, QTableWidgetItem(entry.get("diagnosis", "")))
            self.medical_history_table.setItem(row, 3, QTableWidgetItem(entry.get("treatment", "")))
            attachments_str = ", ".join(entry.get("attachments", []))
            self.medical_history_table.setItem(row, 4, QTableWidgetItem(attachments_str))

    def add_medical_entry(self):
        dialog = AddMedicalEntryDialog(self.mongo_models, self.animal_data["_id"], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Перезагрузка данных животного и обновление таблицы истории болезни
            self.animal_data = self.mongo_models.get_animal_by_id(self.animal_data["_id"])
            self.load_medical_history()


class AddMedicalEntryDialog(QDialog):
    def __init__(self, mongo_models, animal_id, parent=None):
        super().__init__(parent)
        self.mongo_models = mongo_models
        self.animal_id = animal_id
        self.setWindowTitle("Добавить запись в историю болезни")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.date_input = QLineEdit(self)
        self.date_input.setPlaceholderText("ГГГГ-ММ-ДД")
        layout.addRow("Дата:", self.date_input)

        self.symptoms_input = QTextEdit(self)
        layout.addRow("Симптомы:", self.symptoms_input)

        self.diagnosis_input = QTextEdit(self)
        layout.addRow("Диагноз:", self.diagnosis_input)

        self.treatment_input = QTextEdit(self)
        layout.addRow("Лечение:", self.treatment_input)

        self.attachments_input = QLineEdit(self) # Для простоты, имена файлов через запятую
        self.attachments_input.setPlaceholderText("файл1.jpg, файл2.pdf (через запятую)")
        layout.addRow("Вложения:", self.attachments_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_entry)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def save_entry(self):
        date = self.date_input.text()
        symptoms = self.symptoms_input.toPlainText()
        diagnosis = self.diagnosis_input.toPlainText()
        treatment = self.treatment_input.toPlainText()
        attachments_str = self.attachments_input.text()
        attachments = [f.strip() for f in attachments_str.split(',') if f.strip()] if attachments_str else []

        if not all([date, symptoms, diagnosis, treatment]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return

        success = self.mongo_models.add_medical_history_entry(
            self.animal_id, date, symptoms, diagnosis, treatment, attachments
        )

        if success:
            QMessageBox.information(self, "Успех", "Запись успешно добавлена.")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить запись.")