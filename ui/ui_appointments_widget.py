# Приёмы

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QComboBox, QCompleter,  QDialog, QFormLayout,
    QMessageBox, QTimeEdit, QGroupBox, QAbstractItemView, QStyledItemDelegate, QCalendarWidget, QTextEdit
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QIcon
from database.database_models_pg import PostgresModels
from database.database_models_mongo import MongoDBModels
from datetime import datetime, timedelta
import logging


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

                # Заполняем строку таблицы
                self.appointments_table.setItem(row, 0, QTableWidgetItem(str(appt_id)))
                self.appointments_table.setItem(row, 1, QTableWidgetItem(date.strftime("%d.%m.%Y")))
                self.appointments_table.setItem(row, 2, QTableWidgetItem(time.strftime("%H:%M")))
                self.appointments_table.setItem(row, 3, QTableWidgetItem(animal_name))
                self.appointments_table.setItem(row, 4, QTableWidgetItem(vet_name))
                self.appointments_table.setItem(row, 5, QTableWidgetItem(service_name))
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
        print("DEBUG: Trying to open appointment dialog")
        try:
            dialog = AppointmentDialog(self.user_data, self.db_pg, self.db_mongo)
            print("DEBUG: Dialog created successfully")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_appointments()
        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог: {str(e)}")

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


class AppointmentDialog(QDialog):
    """Диалоговое окно для добавления/редактирования приёма."""

    def __init__(self, user_data, db_pg, db_mongo, appointment_id=None):
        super().__init__()
        self.user_data = user_data
        self.db_pg = db_pg
        self.db_mongo = db_mongo
        self.appointment_id = appointment_id
        self.is_edit_mode = appointment_id is not None

        self.setWindowTitle("Редактировать приём" if self.is_edit_mode else "Добавить приём")
        self.setMinimumSize(500, 400)

        self.init_ui()
        self.load_data()

        if self.is_edit_mode:
            self.load_appointment_data()

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        layout = QVBoxLayout()

        # Форма для ввода данных
        form_layout = QFormLayout()

        # Животное
        self.animal_combo = QComboBox()
        self.animal_combo.setEditable(True)
        self.animal_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        form_layout.addRow("Животное:", self.animal_combo)

        # Врач
        self.vet_combo = QComboBox()
        form_layout.addRow("Врач:", self.vet_combo)

        # Услуга
        self.service_combo = QComboBox()
        form_layout.addRow("Услуга:", self.service_combo)

        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Дата:", self.date_edit)

        # Время
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(9, 0))  # Начало рабочего дня
        self.time_edit.setDisplayFormat("HH:mm")
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

    def load_data(self):
        """Загружает данные для выпадающих списков."""
        try:
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
                self.service_combo.addItem(srv[1], srv[0])

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить данные: {str(e)}"
            )

    def load_appointment_data(self):
        """Загружает данные выбранного приёма для редактирования."""
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

    def save_appointment(self):
        """Сохраняет приём в базу данных."""
        try:
            # Получаем данные из формы
            animal_id = self.animal_combo.currentData()
            vet_id = self.vet_combo.currentData()
            service_id = self.service_combo.currentData()
            date = self.date_edit.date().toString("yyyy-MM-dd")
            time = self.time_edit.time().toString("HH:mm")
            status = self.status_combo.currentText()

            # Проверка данных
            if None in (animal_id, vet_id, service_id):
                # Уточняем, какое именно поле не заполнено
                missing = []
                if animal_id is None: missing.append("Животное")
                if vet_id is None: missing.append("Врач")
                if service_id is None: missing.append("Услуга")

                QMessageBox.warning(self, "Ошибка", f"Не заполнены обязательные поля: {', '.join(missing)}")
                return

            # Проверка доступности времени у врача
            if self.is_edit_mode:
                busy = self.db_pg.check_vet_availability(vet_id, date, time, self.appointment_id)
            else:
                busy = self.db_pg.check_vet_availability(vet_id, date, time)

            if busy:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Врач уже занят в это время. Выберите другое время."
                )
                return

            # Сохранение в базу данных
            if self.is_edit_mode:
                success = self.db_pg.update_appointment(
                    self.appointment_id,
                    animal_id,
                    vet_id,
                    date,
                    time,
                    service_id,
                    status,
                )
                action = "обновлён"
            else:
                appointment_id = self.db_pg.insert_appointment(
                    animal_id,
                    vet_id,
                    date,
                    time,
                    service_id,
                    status,
                )
                success = appointment_id is not None
                action = "добавлен"

            if success:
                QMessageBox.information(self, "Успех", f"Приём успешно {action}")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить приём")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить приём: {str(e)}"
            )


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

# TODO: Реализовать виджет для управления приёмами (PyQt5)