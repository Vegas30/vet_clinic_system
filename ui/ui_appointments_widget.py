# Приёмы

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QComboBox, QCompleter, QDialog, QFormLayout,
    QMessageBox, QTimeEdit, QGroupBox, QAbstractItemView, QStyledItemDelegate, QCalendarWidget, QTextEdit, QLineEdit
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette
from database.database_models_pg import PostgresModels
from database.database_models_mongo import MongoDBModels
from datetime import datetime, timedelta
import logging
from logic.logic_calendar_utils import CalendarUtils

class AppointmentsWidget(QWidget):
    """Виджет для управления приёмами в ветеринарной клинике."""

    # Сигнал об обновлении данных
    data_updated = pyqtSignal()

    def __init__(self, user_data):
        """
        Инициализация виджета приёмов.

        Args:
            user_data (dict): Данные текущего пользователя
        """
        super().__init__()
        self.user_data = user_data
        self.db_pg = PostgresModels()
        self.db_mongo = MongoDBModels()
        self.selected_date = QDate.currentDate()
        self.init_ui()
        self.load_appointments()
        self.calendar_utils = CalendarUtils()

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Панель управления
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # Группа фильтров
        filter_group = QGroupBox("Фильтры")
        filter_layout = QHBoxLayout(filter_group)

        # Выбор даты
        date_label = QLabel("Дата:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(self.selected_date)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self.date_changed)

        # Фильтр по статусу
        status_label = QLabel("Статус:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Все", "запланирован", "завершен", "отменен"])
        self.status_combo.currentIndexChanged.connect(self.load_appointments)

        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_edit)
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_combo)

        # Группа действий
        action_group = QGroupBox("Действия")
        action_layout = QHBoxLayout(action_group)

        # Кнопки управления
        self.add_btn = QPushButton("Добавить")
        self.add_btn.setIcon(QIcon("assets/icons/add.png"))
        self.add_btn.clicked.connect(self.add_appointment)

        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.setIcon(QIcon("assets/icons/edit.png"))
        self.edit_btn.clicked.connect(self.edit_appointment)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setIcon(QIcon("assets/icons/delete.png"))
        self.delete_btn.clicked.connect(self.delete_appointment)

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.setIcon(QIcon("assets/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.load_appointments)

        action_layout.addWidget(self.add_btn)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addWidget(self.refresh_btn)

        # Добавляем группы на панель управления
        control_layout.addWidget(filter_group)
        control_layout.addWidget(action_group)

        # Таблица приёмов
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(7)  # ID, Дата, Время, Животное, Врач, Услуга, Статус
        self.appointments_table.setHorizontalHeaderLabels([
            "ID", "Дата", "Время", "Животное", "Врач", "Услуга", "Статус"
        ])

        # Настройка таблицы
        self.appointments_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.appointments_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.appointments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.appointments_table.verticalHeader().setVisible(False)
        self.appointments_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Устанавливаем делегат для цветового выделения статуса
        self.appointments_table.setItemDelegate(StatusDelegate())

        # Сборка основного интерфейса
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.appointments_table)

        self.setLayout(main_layout)

    def date_changed(self, date):
        """Обработчик изменения даты."""
        self.selected_date = date
        self.load_appointments()

    def load_appointments(self):
        """Загружает приёмы из базы данных и отображает их в таблице."""
        if not self.db_pg or not self.db_mongo:
            logging.error("Нет подключения к базе данных")
            return

        try:
            # Получаем выбранный статус
            status_filter = self.status_combo.currentText()
            status = None if status_filter == "Все" else status_filter

            # Получаем приёмы из PostgreSQL
            appointments = self.db_pg.get_appointments_by_date(
                self.selected_date.toString('yyyy-MM-dd'),
                status
            )

            # Очищаем таблицу
            self.appointments_table.setRowCount(0)

            if not appointments:
                return

            # Заполняем таблицу
            self.appointments_table.setRowCount(len(appointments))

            for row, appt in enumerate(appointments):
                appt_id, animal_id, vet_id, date, time, service_id, status = appt[:7]

                # Получаем данные животного из MongoDB
                animal = self.db_mongo.get_animal_by_id(animal_id)
                animal_name = animal.get('name', 'Неизвестно') if animal else "Животное не найдено"

                # Получаем данные врача
                vet = self.db_pg.get_employee_by_id(vet_id)
                vet_name = vet[1] if vet else "Врач не найден"

                # Получаем данные услуги
                service = self.db_pg.get_service_by_id(service_id)
                service_name = service[1] if service else "Услуга не найдена"
                service_price = f"{service[3]:.2f} ₽" if service else "0.00 ₽"

                # Изменяем отображение названия услуги
                service_display = f"{service_name}"

                # Заполняем строку таблицы
                self.appointments_table.setItem(row, 0, QTableWidgetItem(str(appt_id)))
                self.appointments_table.setItem(row, 1, QTableWidgetItem(date.strftime("%d.%m.%Y")))
                self.appointments_table.setItem(row, 2, QTableWidgetItem(time.strftime("%H:%M")))
                self.appointments_table.setItem(row, 3, QTableWidgetItem(animal_name))
                self.appointments_table.setItem(row, 4, QTableWidgetItem(vet_name))
                self.appointments_table.setItem(row, 5, QTableWidgetItem(service_display))
                self.appointments_table.setItem(row, 6, QTableWidgetItem(status))


                # Сохраняем ID приёма в пользовательские данные
                for col in range(self.appointments_table.columnCount()):
                    item = self.appointments_table.item(row, col)
                    if item:
                        item.setData(Qt.ItemDataRole.UserRole, appt_id)

            # Сортируем по времени
            self.appointments_table.sortItems(2, Qt.SortOrder.AscendingOrder)

        except Exception as e:
            logging.error(f"Ошибка при загрузке приёмов: {str(e)}")
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить данные о приёмах: {str(e)}"
            )

    def get_selected_appointment_id(self):
        """Возвращает ID выбранного приёма или None."""
        selected_items = self.appointments_table.selectedItems()
        if not selected_items:
            return None

        # ID хранится в UserData первого элемента строки
        return selected_items[0].data(Qt.ItemDataRole.UserRole)

    def add_appointment(self):
        """Открывает диалог для добавления нового приёма."""
        try:
            dialog = AppointmentDialog(self.user_data, self.db_pg, self.db_mongo)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_appointments()
                self.data_updated.emit()
        except Exception as e:
            logging.error(f"Ошибка при открытии диалога добавления приёма: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог добавления приёма: {str(e)}")

    def edit_appointment(self):
        """Открывает диалог для редактирования выбранного приёма"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            QMessageBox.warning(self, "Ошибка", "Выберите приём для редактирования")
            return

        dialog = AppointmentDialog(
            self.user_data,
            self.db_pg,
            self.db_mongo,
            appointment_id
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_appointments()
            self.data_updated.emit()

    def delete_appointment(self):
        """Удаляет выбранный приём"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            QMessageBox.warning(self, "Ошибка", "Выберите приём для удаления")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этот приём?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db_pg.delete_appointment(appointment_id):
                    QMessageBox.information(self, "Успешно", "Приём удалён")
                    self.load_appointments()
                    self.data_updated.emit()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить приём")
            except Exception as e:
                logging.error(f"Ошибка при удалении приёма: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить приём: {str(e)}"
                )

    def date_changed(self, date):
        """Обработчик изменения даты"""
        if not self.calendar_utils.is_working_day(date):
            QMessageBox.information(self, "Выходной", "В выбранный день клиника не работает")
            self.date_edit.setDate(QDate.currentDate())
        else:
            self.selected_date = date
            self.load_appointments()


class AppointmentDialog(QDialog):
    """Диалоговое окно для добавления/редактирования приёма."""

    def __init__(self, user_data, db_pg, db_mongo, appointment_id=None):
        super().__init__()
        self.calendar_utils = CalendarUtils()
        self.user_data = user_data
        self.db_pg = db_pg
        self.db_mongo = db_mongo
        self.appointment_id = appointment_id
        self.is_edit_mode = appointment_id is not None

        self.setWindowTitle("Добавить приём" if not self.is_edit_mode else "Редактировать приём")
        self.setMinimumSize(500, 400)

        self.init_ui()
        self.load_data()

        # Устанавливаем текущего ветеринара по умолчанию, если это не редактирование
        if not self.is_edit_mode:
            self.set_default_values()
        else:
            self.load_appointment_data()  # Загружаем данные при редактировании

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        layout = QVBoxLayout()

        # Форма для ввода данных
        form_layout = QFormLayout()

        # Животное
        animal_layout = QHBoxLayout()
        self.animal_combo = QComboBox()
        self.animal_combo.setEditable(True)
        self.animal_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        add_animal_btn = QPushButton("Добавить")
        add_animal_btn.clicked.connect(self.show_add_animal_dialog)
        animal_layout.addWidget(self.animal_combo)
        animal_layout.addWidget(add_animal_btn)
        form_layout.addRow("Животное:", animal_layout)

        # Врач
        self.vet_combo = QComboBox()
        form_layout.addRow("Врач:", self.vet_combo)

        # Услуга
        self.service_combo = QComboBox()
        self.service_combo.currentIndexChanged.connect(self.update_service_price)
        form_layout.addRow("Услуга:", self.service_combo)

        # Цена услуги
        self.price_label = QLabel("0.00 ₽")
        self.price_label.setStyleSheet("font-weight: bold; color: #2a5caa;")
        form_layout.addRow("Стоимость:", self.price_label)

        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Дата:", self.date_edit)

        # Время
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(9, 0))  # Начало рабочего дня
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.timeChanged.connect(self.validate_time)
        form_layout.addRow("Время:", self.time_edit)

        # Статус
        self.status_combo = QComboBox()
        self.status_combo.addItems(["запланирован", "завершен", "отменен"])
        form_layout.addRow("Статус:", self.status_combo)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_appointment)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def validate_time(self, time):
        """Валидирует введённое время"""
        if isinstance(time, str):
            time = QTime.fromString(time, 'HH:mm')

        if not self.calendar_utils.is_within_working_hours(time):
            palette = self.time_edit.palette()
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.red)
            self.time_edit.setPalette(palette)
            self.time_edit.setToolTip("Рабочее время с 9:00 до 18:00")
        else:
            self.time_edit.setPalette(QPalette())
            self.time_edit.setToolTip("")

    def update_service_price(self):
        """Обновляет отображение цены при изменении выбранной услуги."""
        service_id = self.service_combo.currentData()
        if service_id:
            try:
                service = self.db_pg.get_service_by_id(service_id)
                if service:
                    price = service[3]  # Предполагаем, что цена находится в 4-м поле (индекс 3)
                    self.price_label.setText(f"{price:.2f} ₽")
                else:
                    self.price_label.setText("0.00 ₽")
            except Exception as e:
                logging.error(f"Ошибка при получении цены услуги: {str(e)}")
                self.price_label.setText("0.00 ₽")
        else:
            self.price_label.setText("0.00 ₽")

    def show_add_animal_dialog(self):
        """Отображает диалог добавления нового животного."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить животное")
        dialog.setMinimumSize(400, 300)

        layout = QFormLayout()

        # Поля для ввода данных
        self.name_edit = QLineEdit()
        self.species_edit = QLineEdit()
        self.breed_edit = QLineEdit()
        self.owner_edit = QLineEdit()
        self.phone_edit = QLineEdit()

        layout.addRow("Имя:", self.name_edit)
        layout.addRow("Вид:", self.species_edit)
        layout.addRow("Порода:", self.breed_edit)
        layout.addRow("Хозяин:", self.owner_edit)
        layout.addRow("Телефон:", self.phone_edit)

        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_new_animal(dialog))
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def save_new_animal(self, dialog):
        """Сохраняет новое животное в базу данных."""
        name = self.name_edit.text().strip()
        species = self.species_edit.text().strip()
        breed = self.breed_edit.text().strip()
        owner = self.owner_edit.text().strip()
        phone = self.phone_edit.text().strip()

        if not name or not owner:
            QMessageBox.warning(self, "Ошибка", "Имя животного и хозяина обязательны")
            return

        animal_data = {
            'name': name,
            'species': species,
            'breed': breed,
            'owner_name': owner,
            'owner_phone': phone,
            'medical_history': []
        }

        try:
            animal_id = self.db_mongo.create_animal(animal_data)
            if animal_id:
                # Добавляем новое животное в комбобокс
                self.animal_combo.addItem(
                    f"{name} ({owner})",
                    animal_id
                )
                # Выбираем только что добавленное животное
                self.animal_combo.setCurrentIndex(self.animal_combo.count() - 1)
                dialog.accept()
                QMessageBox.information(self, "Успех", "Животное успешно добавлено")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить животное")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить животное: {str(e)}"
            )

    def set_default_values(self):
        """Устанавливает значения по умолчанию для нового приема"""
        # Используем метод из calendar_utils
        self.time_edit.setTime(self.calendar_utils.get_next_available_time())

        # Устанавливаем пустые значения
        self.animal_combo.setCurrentIndex(0)  # "Выберите животное"
        self.service_combo.setCurrentIndex(0)  # "Выберите услугу"

        # Устанавливаем текущего пользователя как ветеринара, если он врач
        if self.user_data['role'] == 'vet':
            vet_index = self.vet_combo.findData(self.user_data['id'])
            if vet_index >= 0:
                self.vet_combo.setCurrentIndex(vet_index)
        else:
            self.vet_combo.setCurrentIndex(0)  # "Выберите врача"

        # Устанавливаем текущую дату и ближайшее доступное время
        self.date_edit.setDate(QDate.currentDate())

        # Устанавливаем ближайшее рабочее время
        now = datetime.now()
        current_time = QTime(now.hour, now.minute)

        if not self.calendar_utils.is_within_working_hours(current_time):
            # Если сейчас нерабочее время, устанавливаем начало следующего рабочего дня
            self.time_edit.setTime(QTime(9, 0))
        else:
            # Иначе ближайшие 30 минут
            self.time_edit.setTime(self.calendar_utils.get_next_available_time())

        # Устанавливаем статус "запланирован"
        self.status_combo.setCurrentText("запланирован")

    def update_available_times(self):
        """Обновляет доступное время при изменении даты или врача"""
        vet_id = self.vet_combo.currentData()
        date = self.date_edit.date()

        if vet_id and date.isValid():
            available_slots = self.calendar_utils.get_available_slots(
                vet_id,
                date,
                self.db_pg
            )

    def load_data(self):
        """Загружает данные для выпадающих списков."""
        try:
            # Очищаем списки перед загрузкой
            self.animal_combo.clear()
            self.vet_combo.clear()
            self.service_combo.clear()

            # Добавляем пустой элемент в начало списка животных
            self.animal_combo.addItem("Выберите животное или добавьте новое", None)

            # Для врачей и услуг оставляем обязательный выбор
            self.vet_combo.addItem("Выберите врача", None)
            self.service_combo.addItem("Выберите услугу", None)

            # Загрузка животных
            animals = self.db_mongo.get_all_animals()
            for animal in animals:
                self.animal_combo.addItem(
                    f"{animal.get('name', 'Без имени')} ({animal.get('owner_name', 'Без хозяина')})",
                    animal['_id']
                )

            # Загрузка ветеринаров
            employees = self.db_pg.get_all_employees()
            for emp in employees:
                self.vet_combo.addItem(emp[1], emp[0])

            # Загрузка услуг
            services = self.db_pg.get_all_services()
            for srv in services:
                self.service_combo.addItem(
                    f"{srv[1]}",  # Название
                    srv[0]  # ID услуги
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить данные: {str(e)}"
            )

    def load_appointment_data(self):
        """Загружает данные выбранного приёма для редактирования."""
        if not self.appointment_id:
            return  # Если нет ID приема, ничего не загружаем

        try:
            appointment = self.db_pg.get_appointment_by_id(self.appointment_id)
            if not appointment:
                QMessageBox.warning(self, "Ошибка", "Приём не найден")
                self.reject()
                return

            _, animal_id, vet_id, date, time, service_id, status = appointment

            # Устанавливаем животное
            animal_index = self.animal_combo.findData(animal_id)
            if animal_index >= 0:
                self.animal_combo.setCurrentIndex(animal_index)

            # Устанавливаем врача
            vet_index = self.vet_combo.findData(vet_id)
            if vet_index >= 0:
                self.vet_combo.setCurrentIndex(vet_index)

            # Устанавливаем услугу
            service_index = self.service_combo.findData(service_id)
            if service_index >= 0:
                self.service_combo.setCurrentIndex(service_index)
                # Обновляем цену
                self.update_service_price()

            # Устанавливаем дату и время
            self.date_edit.setDate(date)
            self.time_edit.setTime(QTime(time.hour, time.minute))

            # Устанавливаем статус
            status_index = self.status_combo.findText(status)
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить данные приёма: {str(e)}"
            )
            self.reject()

    def save_appointment(self):
        """Сохраняет приём в базу данных."""
        try:
            # Получаем данные из формы
            animal_id = self.animal_combo.currentData()
            vet_id = self.vet_combo.currentData()
            service_id = self.service_combo.currentData()
            date = self.date_edit.date()  # QDate object
            time = self.time_edit.time()  # QTime object
            status = self.status_combo.currentText()

            # Проверка обязательных полей
            missing_fields = []
            if not animal_id: missing_fields.append("Животное")
            if not vet_id: missing_fields.append("Врач")
            if not service_id: missing_fields.append("Услуга")

            if missing_fields:
                QMessageBox.warning(self, "Ошибка", f"Не заполнены поля: {', '.join(missing_fields)}")
                return

            # Проверка рабочего времени
            if not self.calendar_utils.is_within_working_hours(time):
                QMessageBox.warning(self, "Ошибка", "Запись возможна только с 9:00 до 18:00")
                return

            # Проверка доступности врача
            if not self.calendar_utils.validate_appointment_time(
                    vet_id,
                    date,
                    time,
                    self.db_pg,
                    self.appointment_id if self.is_edit_mode else None
            ):
                QMessageBox.warning(self, "Ошибка", "Врач уже занят в это время")
                return

            # Сохранение в базу данных
            if self.is_edit_mode:
                success = self.db_pg.update_appointment(
                    self.appointment_id,
                    animal_id,
                    vet_id,
                    date.toString('yyyy-MM-dd'),
                    time.toString('HH:mm'),
                    service_id,
                    status
                )
                action = "обновлён"
            else:
                appointment_id = self.db_pg.insert_appointment(
                    animal_id,
                    vet_id,
                    date.toString('yyyy-MM-dd'),
                    time.toString('HH:mm'),
                    service_id,
                    status
                )
                success = appointment_id is not None
                action = "добавлен"

            if success:
                QMessageBox.information(self, "Успех", f"Приём успешно {action}")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить приём")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить приём: {str(e)}")
            logging.error(f"Ошибка сохранения приёма: {str(e)}")


class StatusDelegate(QStyledItemDelegate):
    """Делегат для цветового выделения статуса приёма."""

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        # Получаем текст статуса
        status = index.data(Qt.ItemDataRole.DisplayRole)

        # Устанавливаем цвет фона в зависимости от статуса
        if status == "запланирован":
            option.backgroundBrush = Qt.GlobalColor.yellow
        elif status == "завершен":
            option.backgroundBrush = Qt.GlobalColor.green
        elif status == "отменен":
            option.backgroundBrush = Qt.GlobalColor.red

