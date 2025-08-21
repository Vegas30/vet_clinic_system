# reports_widget.py
import logging

import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QDateEdit, QFileDialog, QGroupBox, QHeaderView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QColor
from datetime import datetime
from logic.logic_reports_generator import ReportsGenerator

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ReportsWidget(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.report_generator = ReportsGenerator()
        self.doctors_data = {}  # Инициализируем пустой словарь
        self.current_stats_data = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Отчеты")
        self.setMinimumSize(1000, 600)

        # Основной макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Верхняя панель с фильтрами и кнопками
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Группа фильтров
        filter_group = QGroupBox("Параметры отчета")
        filter_layout = QHBoxLayout(filter_group)

        # Левая часть - вертикальный layout с типом и параметром
        left_filter_layout = QVBoxLayout()

        # Выбор типа отчета
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип отчета:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Приемы за период",
            "Животные по диагнозу",
            "Услуги по врачу",
            "Финансы",
            "Статистика"
        ])
        type_layout.addWidget(self.report_type_combo)
        left_filter_layout.addLayout(type_layout)

        # Параметр отчета
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Параметр:"))
        self.param_combo = QComboBox()
        param_layout.addWidget(self.param_combo)
        left_filter_layout.addLayout(param_layout)

        filter_layout.addLayout(left_filter_layout)

        # Период отчета
        self.period_group = QGroupBox("Период")
        period_layout = QHBoxLayout(self.period_group)
        filter_layout.addWidget(self.period_group)

        # Создаем виджеты для периода
        self.create_period_widgets()

        # Подключаем сигналы после создания всех виджетов
        self.report_type_combo.currentTextChanged.connect(self.update_ui_for_report_type)
        top_layout.addWidget(filter_group)

        # Группа кнопок
        buttons_group = QGroupBox("Действия")
        buttons_layout = QHBoxLayout(buttons_group)

        self.generate_btn = QPushButton("Сформировать")
        self.generate_btn.setIcon(QIcon("assets/icons/refresh.png"))
        self.generate_btn.clicked.connect(self.generate_report)

        self.export_pdf_btn = QPushButton("Экспорт в PDF")
        self.export_pdf_btn.setIcon(QIcon("assets/icons/pdf.png"))
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)

        self.export_excel_btn = QPushButton("Экспорт в Excel")
        self.export_excel_btn.setIcon(QIcon("assets/icons/excel.png"))
        self.export_excel_btn.clicked.connect(self.export_to_excel)

        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.export_pdf_btn)
        buttons_layout.addWidget(self.export_excel_btn)

        top_layout.addWidget(buttons_group)
        main_layout.addWidget(top_panel)

        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(0)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.results_table)

        self.setLayout(main_layout)
        self.update_ui_for_report_type()

        # self.date_from = QDateEdit()
        # self.date_from.setDate(QDate.currentDate().addDays(-7))  # По умолчанию - неделя назад
        # self.date_from.setCalendarPopup(True)
        # self.date_from.setDisplayFormat("dd.MM.yyyy")
        #
        # self.date_to = QDateEdit()
        # self.date_to.setDate(QDate.currentDate())  # По умолчанию - сегодня
        # self.date_to.setCalendarPopup(True)
        # self.date_to.setDisplayFormat("dd.MM.yyyy")
        #
        # period_layout.addWidget(QLabel("С:"))
        # period_layout.addWidget(self.date_from)
        # period_layout.addWidget(QLabel("По:"))
        # period_layout.addWidget(self.date_to)

    def create_period_widgets(self):
        """Создает виджеты для выбора периода"""
        # Виджеты для статистики
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ])
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)

        # Комбобокс для выбора года
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        self.year_combo.addItems([str(y) for y in range(current_year - 5, current_year + 1)])
        self.year_combo.setCurrentText(str(current_year))

        # Виджеты для обычных отчетов
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        self.date_from.setDate(QDate.currentDate().addDays(-7))

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        self.date_to.setDate(QDate.currentDate())

    def update_ui_for_report_type(self):
        """Обновляет интерфейс в зависимости от выбранного типа отчета"""
        report_type = self.report_type_combo.currentText()
        param_label = self.findChild(QLabel, "Параметр:")

        # Очищаем группу периода
        period_layout = self.period_group.layout()
        while period_layout.count():
            item = period_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if report_type == "Статистика":
            # Настройка для статистики
            self.period_group.setTitle("Период для статистики")

            # Заполняем комбобокс параметров
            self.param_combo.clear()
            self.param_combo.addItems(["Месячная статистика", "Годовая статистика"])
            self.param_combo.currentTextChanged.connect(self.update_statistics_filters)

            # Показываем параметры для статистики
            self.param_combo.show()
            if param_label:
                param_label.show()

            # Определяем тип статистики
            is_monthly = self.param_combo.currentText() == "Месячная статистика"

            # Добавляем элементы в зависимости от типа статистики
            if is_monthly:
                # Для месячной статистики
                period_layout.addWidget(QLabel("Месяц:"))
                period_layout.addWidget(self.month_combo)
                period_layout.addWidget(QLabel("Год:"))
                period_layout.addWidget(self.year_combo)
            else:
                # Для годовой статистики
                period_layout.addWidget(QLabel("Год:"))
                period_layout.addWidget(self.year_combo)

            # Обновляем состояние виджетов
            self.month_combo.setVisible(is_monthly)
            self.month_combo.setEnabled(is_monthly)
            self.year_combo.setVisible(True)
            self.year_combo.setEnabled(True)

        else:
            # Настройка для других типов отчетов
            self.period_group.setTitle("Период")

            # Создаем виджеты дат если их нет
            if not hasattr(self, 'date_from'):
                self.date_from = QDateEdit()
                self.date_from.setCalendarPopup(True)
                self.date_from.setDisplayFormat("dd.MM.yyyy")
                self.date_from.setDate(QDate.currentDate().addDays(-7))

            if not hasattr(self, 'date_to'):
                self.date_to = QDateEdit()
                self.date_to.setCalendarPopup(True)
                self.date_to.setDisplayFormat("dd.MM.yyyy")
                self.date_to.setDate(QDate.currentDate())

            # Добавляем виджеты дат
            period_layout.addWidget(QLabel("С:"))
            period_layout.addWidget(self.date_from)
            period_layout.addWidget(QLabel("По:"))
            period_layout.addWidget(self.date_to)

            # Скрываем комбобоксы статистики
            if hasattr(self, 'month_combo'):
                self.month_combo.hide()
                self.year_combo.hide()

            # Настройка параметров отчета
            if report_type == "Животные по диагнозу":
                self.load_diagnoses()
                self.param_combo.show()
                if param_label: param_label.show()
            elif report_type == "Услуги по врачу":
                self.load_doctors()
                self.param_combo.show()
                if param_label: param_label.show()
            else:
                self.param_combo.hide()
                if param_label: param_label.hide()

        # Обновляем фильтры статистики после изменения интерфейса
        # if report_type == "Статистика":
        #     self.update_statistics_filters()

    def setup_statistics_ui(self):
        """Настройка интерфейса для отчета Статистика"""
        try:
            # Очищаем и настраиваем комбобокс параметров
            self.param_combo.clear()
            self.param_combo.addItems(["Месячная статистика", "Годовая статистика"])
            self.param_combo.currentTextChanged.connect(self.update_statistics_filters)

            # Создаем виджеты для выбора периода, если их нет
            if not hasattr(self, 'month_combo'):
                self.create_period_widgets()

            # Обновляем видимость элементов
            self.update_statistics_filters()

        except Exception as e:
            logging.error(f"Ошибка настройки интерфейса статистики: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось настроить интерфейс: {str(e)}")

    def update_statistics_filters(self):
        """Обновляет активность фильтров для статистики"""
        if not hasattr(self, 'month_combo') or not hasattr(self, 'year_combo'):
            return

        if self.report_type_combo.currentText() != "Статистика":
            return

        is_monthly = self.param_combo.currentText() == "Месячная статистика"

        # Обновляем видимость и активность виджетов
        self.month_combo.setVisible(is_monthly)
        self.month_combo.setEnabled(is_monthly)
        self.year_combo.setVisible(True)
        self.year_combo.setEnabled(True)

    def load_diagnoses(self):
        """Загружает список диагнозов для комбобокса"""
        try:
            self.param_combo.clear()
            diagnoses = self.report_generator.db_mongo.get_all_diagnoses()
            self.param_combo.addItems(diagnoses)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить диагнозы: {str(e)}")

    def load_doctors(self):
        """Загружает список ветеринаров для комбобокса"""
        try:
            self.param_combo.clear()
            doctors = self.report_generator.db_pg.get_all_doctors()

            if not doctors:
                QMessageBox.warning(self, "Предупреждение", "Нет данных о врачах")
                return
            # Сохраняем данные врачей в словарь для быстрого доступа
            self.doctors_data.clear()  # Очищаем существующий словарь
            self.doctors_data = {doctor[1]: doctor[0] for doctor in doctors}  # {ФИО: id}

            # Заполняем комбобокс только ФИО врачей
            self.param_combo.addItems(self.doctors_data.keys())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить врачей: {str(e)}")

    def update_finance_date_inputs(self):
        """Обновляет поля дат для финансового отчета"""
        if not hasattr(self, 'param_combo'):
            return

        period_type = self.param_combo.currentText()
        is_custom = period_type == "произвольный"

        self.date_from.setVisible(is_custom)
        self.date_to.setVisible(is_custom)

        # Устанавливаем текущую дату, если период произвольный
        if is_custom:
            self.date_from.setDate(QDate.currentDate().addDays(-7))
            self.date_to.setDate(QDate.currentDate())

    def generate_report(self):
        """Генерация отчета по выбранным параметрам"""
        report_type = self.report_type_combo.currentText()
        headers = []
        data = []  # Инициализируем переменную data

        try:
            if report_type == "Статистика":
                stat_type = self.param_combo.currentText()
                selected_year = int(self.year_combo.currentText()) if hasattr(self, 'year_combo') else None
                selected_month = self.month_combo.currentIndex() + 1 if hasattr(self,
                                'month_combo') and self.month_combo.isVisible() else None
                if stat_type == "Месячная статистика":
                    headers, data = self.report_generator.generate_monthly_stats_report(year=selected_year,
                    month=selected_month)
                elif stat_type == "Годовая статистика":
                    headers, data = self.report_generator.generate_monthly_stats_report(year=selected_year)

                if data:  # Проверяем, что данные есть
                    self.current_stats_data = data
                    if hasattr(self, 'show_chart_btn'):
                        self.show_chart_btn.setEnabled(True)
            elif report_type == "Приемы за период":
                date_from = self.date_from.date().toString("yyyy-MM-dd")
                date_to = self.date_to.date().toString("yyyy-MM-dd")
                headers, data = self.report_generator.generate_appointments_report(date_from, date_to)
            elif report_type == "Животные по диагнозу":
                diagnosis = self.param_combo.currentText()
                headers, data = self.report_generator.generate_animals_by_diagnosis(diagnosis)
            elif report_type == "Услуги по врачу":
                doctor_name = self.param_combo.currentText()
                doctor_id = self.doctors_data.get(doctor_name)
                if doctor_id is None:
                    QMessageBox.warning(self, "Ошибка", "Не удалось определить ID врача")
                    return

                date_from = self.date_from.date().toString("yyyy-MM-dd")
                date_to = self.date_to.date().toString("yyyy-MM-dd")
                headers, data = self.report_generator.generate_services_by_doctor(doctor_id, date_from, date_to)
            elif report_type == "Финансы":
                date_from = self.date_from.date().toString("yyyy-MM-dd")
                date_to = self.date_to.date().toString("yyyy-MM-dd")
                headers, data = self.report_generator.generate_finance_report(date_from, date_to)

            # Отображаем отчет только если есть данные
            if headers and data:
                self.display_report(headers, data)
            else:
                QMessageBox.information(self, "Информация", "Нет данных для отображения")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчет:\n{str(e)}")
            logging.error(f"Ошибка формирования отчета: {str(e)}")

    # def generate_monthly_stats(self):
    #     """Генерация месячной статистики"""
    #     try:
    #         selected_year = int(self.year_combo.currentText())
    #         selected_month = self.month_combo.currentIndex() + 1
    #
    #         # Получаем данные из БД
    #         result = self.report_generator.generate_monthly_stats_report(
    #             year=selected_year,
    #             month=selected_month
    #         )
    #
    #         # Проверяем структуру полученных данных
    #         if not result or len(result) != 2 or not result[1]:
    #             return ["Месяц", "Количество приемов", "Доход"], [["Нет данных за выбранный период"]]
    #
    #         headers, raw_data = result
    #         data = []
    #
    #         # Форматируем данные для отображения
    #         for row in raw_data:
    #             try:
    #                 # Проверяем, что строка содержит достаточно элементов
    #                 if len(row) < 3:
    #                     continue
    #
    #                 month_name = str(row[0]).strip() if row[0] else "Неизвестно"
    #                 appointments = int(row[1]) if row[1] else 0
    #
    #                 # Обрабатываем доход (может быть числом или строкой "1000.00 ₽")
    #                 income = 0.0
    #                 if isinstance(row[2], str):
    #                     try:
    #                         income_str = row[2].replace('₽', '').strip()
    #                         income = float(income_str)
    #                     except (ValueError, AttributeError):
    #                         income = 0.0
    #                 elif isinstance(row[2], (int, float)):
    #                     income = float(row[2])
    #
    #                 data.append([month_name, appointments, f"{income:.2f} ₽"])
    #             except Exception as e:
    #                 logging.error(f"Ошибка обработки строки данных: {row}. Ошибка: {str(e)}")
    #                 continue
    #
    #         if not data:
    #             return ["Месяц", "Количество приемов", "Доход"], [["Нет данных за выбранный период"]]
    #
    #         return ["Месяц", "Количество приемов", "Доход"], data
    #
    #     except Exception as e:
    #         logging.error(f"Ошибка генерации месячной статистики: {str(e)}")
    #         return ["Ошибка"], [[f"Не удалось сформировать отчет: {str(e)}"]]

    def generate_yearly_stats(self):
        """Генерация годовой статистики"""
        try:
            selected_year = int(self.year_combo.currentText())

            # Получаем данные из БД
            result = self.report_generator.generate_yearly_stats_report(
                year=selected_year
            )

            # Проверяем структуру полученных данных
            if not result or len(result) != 2 or not result[1]:
                return ["Год", "Количество приемов", "Доход"], [["Нет данных за выбранный период"]]

            headers, raw_data = result
            data = []

            # Форматируем данные для отображения
            for row in raw_data:
                try:
                    # Проверяем, что строка содержит достаточно элементов
                    if len(row) < 3:
                        continue

                    year = str(row[0]) if row[0] else "Неизвестно"
                    appointments = int(row[1]) if row[1] else 0

                    # Обрабатываем доход (может быть числом или строкой "10000.00 ₽")
                    income = 0.0
                    if isinstance(row[2], str):
                        try:
                            income_str = row[2].replace('₽', '').strip()
                            income = float(income_str)
                        except (ValueError, AttributeError):
                            income = 0.0
                    elif isinstance(row[2], (int, float)):
                        income = float(row[2])

                    data.append([year, appointments, f"{income:.2f} ₽"])
                except Exception as e:
                    logging.error(f"Ошибка обработки строки данных: {row}. Ошибка: {str(e)}")
                    continue

            if not data:
                return ["Год", "Количество приемов", "Доход"], [["Нет данных за выбранный период"]]

            return ["Год", "Количество приемов", "Доход"], data

        except Exception as e:
            logging.error(f"Ошибка генерации годовой статистики: {str(e)}")
            return ["Ошибка"], [[f"Не удалось сформировать отчет: {str(e)}"]]

    # def show_statistics_chart(self):
    #     """Показывает график статистики"""
    #     if not hasattr(self, 'current_stats_data') or not self.current_stats_data:
    #         return
    #
    #     # Создаем график
    #     fig = Figure(figsize=(8, 4))
    #     canvas = FigureCanvas(fig)
    #
    #     # Определяем тип статистики (месячная/годовая)
    #     is_monthly = self.param_combo.currentText() == "Месячная статистика"
    #
    #     if is_monthly:
    #         self.draw_monthly_chart(fig, self.current_stats_data)
    #     else:
    #         self.draw_yearly_chart(fig, self.current_stats_data)
    #
    #     # Создаем окно для графика
    #     chart_window = QWidget()
    #     chart_window.setWindowTitle("График статистики")
    #     layout = QVBoxLayout()
    #     layout.addWidget(canvas)
    #     chart_window.setLayout(layout)
    #     chart_window.resize(800, 500)
    #     chart_window.show()

    # def draw_monthly_chart(self, fig, data):
    #     """Рисует график месячной статистики"""
    #     months = [row[0] for row in data]
    #     appointments = [row[1] for row in data]
    #     incomes = [float(row[2].split()[0]) for row in data]  # Извлекаем числа из строк "1000.00 ₽"
    #
    #     ax1 = fig.add_subplot(211)
    #     ax1.bar(months, appointments, color='skyblue')
    #     ax1.set_title('Количество приемов по месяцам')
    #     ax1.set_ylabel('Количество')
    #
    #     ax2 = fig.add_subplot(212)
    #     ax2.plot(months, incomes, marker='o', color='green')
    #     ax2.set_title('Доход по месяцам')
    #     ax2.set_ylabel('Сумма (₽)')
    #
    #     fig.tight_layout()

    # def draw_yearly_chart(self, fig, data):
    #     """Рисует график годовой статистики"""
    #     years = [str(row[0]) for row in data]
    #     appointments = [row[1] for row in data]
    #     incomes = [float(row[2].split()[0]) for row in data]  # Извлекаем числа из строк "10000.00 ₽"
    #
    #     ax1 = fig.add_subplot(211)
    #     ax1.bar(years, appointments, color='skyblue')
    #     ax1.set_title('Количество приемов по годам')
    #     ax1.set_ylabel('Количество')
    #
    #     ax2 = fig.add_subplot(212)
    #     ax2.plot(years, incomes, marker='o', color='green')
    #     ax2.set_title('Доход по годам')
    #     ax2.set_ylabel('Сумма (₽)')
    #
    #     fig.tight_layout()


    def display_report(self, headers, data):
        """Отображает отчет в таблице с улучшенным форматированием"""
        try:
            # Очищаем таблицу перед заполнением
            self.results_table.clear()

            # Устанавливаем количество колонок и строк
            self.results_table.setColumnCount(len(headers))
            self.results_table.setRowCount(len(data))

            # Устанавливаем заголовки
            self.results_table.setHorizontalHeaderLabels(headers)

            # Настраиваем поведение заголовков
            header = self.results_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setDefaultSectionSize(150)  # Значение по умолчанию

            # Заполняем таблицу данными
            for row_idx, row_data in enumerate(data):
                for col_idx, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))

                    # Выравнивание для числовых данных и денежных значений
                    if isinstance(col_data, (int, float)) or '₽' in str(col_data):
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                    # Особое форматирование для финансовых данных
                    if '₽' in str(col_data):
                        item.setForeground(QColor(0, 100, 0))  # Темно-зеленый для сумм

                    # Форматирование заголовков и разделителей
                    if (headers[0] == "Показатель" and col_idx == 0 and
                            (row_data[0] in ["Услуги", "Врачи"] or row_data[0] == "")):
                        item.setBackground(QColor(240, 240, 240))  # Серый фон
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

                    self.results_table.setItem(row_idx, col_idx, item)

            # Настраиваем ширину колонок
            self.results_table.resizeColumnsToContents()

            # Дополнительные настройки для таблицы
            self.results_table.verticalHeader().setVisible(False)
            self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

            # Особые настройки для финансового отчета
            if headers[0] == "Показатель":
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            else:
                # Для других отчетов - равномерное растяжение
                header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            # if headers[0] == "Месяц":
            #     self.show_monthly_chart(data)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отобразить отчет:\n{str(e)}")
            logging.error(f"Ошибка отображения отчета: {str(e)}")

    # def show_monthly_chart(self, data):
    #     """Показывает график месячной статистики"""
    #     try:
    #         from matplotlib.figure import Figure
    #         from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    #
    #         # Создаем окно для графика
    #         chart_window = QWidget()
    #         chart_window.setWindowTitle("График месячной статистики")
    #         layout = QVBoxLayout(chart_window)
    #
    #         # Создаем график
    #         fig = Figure(figsize=(8, 6))
    #         canvas = FigureCanvasQTAgg(fig)
    #         layout.addWidget(canvas)
    #
    #         # Подготовка данных
    #         months = [row[0] for row in data]
    #         appointments = [row[1] for row in data]
    #         incomes = [float(row[2].replace('₽', '').strip()) for row in data]
    #
    #         # Создаем графики
    #         ax1 = fig.add_subplot(211)
    #         ax1.bar(months, appointments, color='skyblue')
    #         ax1.set_title('Количество приемов по месяцам')
    #         ax1.set_ylabel('Количество')
    #
    #         ax2 = fig.add_subplot(212)
    #         ax2.plot(months, incomes, marker='o', color='green')
    #         ax2.set_title('Доход по месяцам')
    #         ax2.set_ylabel('Сумма (₽)')
    #
    #         fig.tight_layout()
    #         chart_window.show()
    #
    #     except ImportError:
    #         QMessageBox.warning(self, "Ошибка",
    #                             "Для отображения графиков требуется установить matplotlib")
    #     except Exception as e:
    #         logging.error(f"Ошибка при создании графика: {str(e)}")
    #         QMessageBox.critical(self, "Ошибка",
    #                              f"Не удалось отобразить график:\n{str(e)}")
    def export_to_pdf(self):
        """Экспорт текущего отчета в PDF"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return

        report_type = self.report_type_combo.currentText()
        default_name = f"{report_type}_{datetime.now().strftime('%Y%m%d')}.pdf"

        PDFExporter.export_to_pdf(
            self,
            self.results_table,
            default_name,
            f"Отчет: {report_type}"
        )

    def export_to_excel(self):
        """Экспорт текущего отчета в Excel"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return

        report_type = self.report_type_combo.currentText()
        default_name = f"{report_type}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        ExcelExporter.export_to_excel(
            self,
            self.results_table,
            default_name,
            report_type
        )


class PDFExporter:
    """Класс для экспорта данных таблицы в PDF-формат.

    Предоставляет функционал для генерации PDF-документов с табличными данными.

    Attributes:
        Все методы класса являются статическими.

    Methods:
        export_to_pdf: Основной метод экспорта данных
        prepare_data: Подготовка данных таблицы
        create_styles: Создание стилей документа
        create_table_style: Настройка стилей таблицы
        register_fonts: Регистрация шрифтов
        calculate_column_widths: Расчет ширины колонок

    Пример использования:
        PDFExporter.export_to_pdf(parent_window, table, "report.pdf", "Отчет")
    """
    @staticmethod
    def export_to_pdf(parent, table_widget, default_filename, document_title):
        """Экспортирует данные таблицы в PDF-файл.

        Args:
            parent (QWidget): Родительское окно для диалогов
            table_widget (QTableWidget): Таблица с данными для экспорта
            default_filename (str): Имя файла по умолчанию
            document_title (str): Заголовок документа

        Raises:
            PermissionError: При отсутствии прав записи
            Exception: Общие ошибки генерации PDF

        Process:
            1. Проверка наличия данных
            2. Настройка шрифтов и стилей
            3. Подготовка данных таблицы
            4. Показ диалога сохранения
            5. Генерация PDF-документа
        """

        try:
            if table_widget.rowCount() == 0:
                QMessageBox.warning(parent, "Ошибка", "Нет данных для экспорта")
                return

            # Регистрация шрифтов
            font_name = PDFExporter.register_fonts()

            # Создание стилей
            styles = PDFExporter.create_styles(font_name)

            # Подготовка данных с форматированием
            headers, table_data = PDFExporter.prepare_data(table_widget, styles)

            # Диалог сохранения
            file_path, _ = QFileDialog.getSaveFileName(
                parent,
                "Экспорт в PDF",
                default_filename,
                "PDF Files (*.pdf)"
            )
            if not file_path:
                return

            # Создание документа
            doc = SimpleDocTemplate(
                file_path,
                pagesize=landscape(A4),
                leftMargin=10 * mm,
                rightMargin=10 * mm,
                topMargin=15 * mm,
                bottomMargin=15 * mm
            )

            elements = []

            # Добавление заголовка
            elements.append(Paragraph(document_title, styles['Title']))
            elements.append(Spacer(1, 0.2 * 25.4))

            # Создание и настройка таблицы
            table = Table(
                table_data,
                colWidths=PDFExporter.calculate_column_widths(len(headers))
            )
            table.setStyle(PDFExporter.create_table_style(font_name))

            elements.append(table)
            doc.build(elements)

            QMessageBox.information(
                parent,
                "Успех",
                f"PDF-документ успешно сохранен:\n{file_path}"
            )

        except PermissionError:
            error_msg = "Нет прав для записи в выбранную директорию"
            logging.error(error_msg)
            QMessageBox.critical(parent, "Ошибка", error_msg)
        except Exception as e:
            logging.error(f"PDF Export Error: {str(e)}")
            QMessageBox.critical(parent, "Ошибка", f"Не удалось создать PDF:\n{str(e)}")

    @staticmethod
    def prepare_data(table_widget, styles):
        """Подготавливает данные таблицы для вставки в PDF.

        Args:
            table_widget (QTableWidget): Исходная таблица
            styles (dict): Словарь стилей ReportLab

        Returns:
            tuple: Кортеж содержащий:
                - headers (list): Список заголовков
                - table_data (list): Данные для ReportLab Table

        Notes:
            - Форматирует заголовки жирным начертанием
            - Центрирует содержимое ячеек
            - Заменяет пустые ячейки на пустые строки
        """

        def format_text(text, is_header=False):
            """Форматирование текста ячейки"""
            style = styles['Header'] if is_header else styles['Body']
            text = str(text).strip() if text else ""
            return Paragraph(f"<b>{text}</b>" if is_header else text, style)

        # Получение заголовков
        headers = [
            table_widget.horizontalHeaderItem(i).text()
            for i in range(table_widget.columnCount())
        ]

        # Форматирование данных
        table_data = []
        if headers:
            table_data.append([format_text(h, True) for h in headers])

        # Обработка строк данных
        for row in range(table_widget.rowCount()):
            formatted_row = []
            for col in range(table_widget.columnCount()):
                item = table_widget.item(row, col)
                text = item.text() if item else ""
                formatted_row.append(format_text(text))
            table_data.append(formatted_row)

        return headers, table_data

    @staticmethod
    def create_styles(font_name):
        """Создает набор стилей для элементов PDF.

        Args:
            font_name (str): Имя зарегистрированного шрифта

        Returns:
            dict: Словарь стилей с ключами:
                - 'Header': Стиль заголовков таблицы
                - 'Body': Стиль тела таблицы
                - 'Title': Стиль заголовка документа

        Notes:
            Размеры шрифтов:
                - Заголовок документа: 14pt
                - Заголовки таблицы: 9pt
                - Тело таблицы: 8pt
        """
        styles = getSampleStyleSheet()

        # Стиль для заголовков таблицы
        styles.add(ParagraphStyle(
            name='Header',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=11,
            alignment=1,  # Центрирование
            textColor=colors.white,
            spaceBefore=2,
            spaceAfter=2
        ))

        # Стиль для тела таблицы
        styles.add(ParagraphStyle(
            name='Body',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            leading=10,
            alignment=1,  # Центрирование
            textColor=colors.black,
            spaceBefore=2,
            spaceAfter=2
        ))

        # Стиль для заголовка документа
        styles['Title'].fontName = font_name
        styles['Title'].fontSize = 14
        styles['Title'].alignment = 1  # Центрирование

        return styles

    @staticmethod
    def create_table_style(font_name):
        """Генерирует стили оформления таблицы.

        Args:
            font_name (str): Имя используемого шрифта

        Returns:
            TableStyle: Объект стилей таблицы ReportLab

        Notes:
            Применяет:
                - Синий фон заголовков (#2c3e50)
                - Серую сетку таблицы (#bdc3c7)
                - Чередующийся фон строк (#f8f9fa)
        """
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ])

    @staticmethod
    def register_fonts():
        """Регистрирует шрифты для поддержки кириллицы.

        Returns:
            str: Имя зарегистрированного шрифта

        Notes:
            Приоритет шрифтов:
                1. DejaVuSans
                2. Arial
                3. Helvetica (по умолчанию)
        """
        font_name = 'Helvetica'
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            font_name = 'DejaVuSans'
        except:
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
                font_name = 'Arial'
            except:
                logging.warning("Используется стандартный шрифт")
        return font_name

    @staticmethod
    def calculate_column_widths(columns_count):
        """Рассчитывает ширину колонок таблицы.

        Args:
            columns_count (int): Количество колонок в таблице

        Returns:
            list: Список значений ширины для каждой колонки

        Notes:
            Ширина рассчитывается с учетом:
                - Размера страницы A4 в альбомной ориентации
                - Отступов по краям документа
        """
        page_width = landscape(A4)[0] - 20 * mm
        return [page_width / columns_count * 0.95] * columns_count




class ExcelExporter:
    @staticmethod
    def export_to_excel(parent, table_widget, default_filename, sheet_name="Данные"):
        """
        "кспорт в Excel
        """
        try:
            if table_widget.rowCount() == 0:
                QMessageBox.warning(parent, "Ошибка", "Нет данных для экспорта")
                return

            # Получение заголовков
            headers = [
                table_widget.horizontalHeaderItem(i).text()
                for i in range(table_widget.columnCount())
            ]

            # Сбор данных
            data = []
            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            # Создание DataFrame
            df = pd.DataFrame(data, columns=headers)

            # Диалог сохранения файла
            file_path, _ = QFileDialog.getSaveFileName(
                parent,
                "Экспорт в Excel",
                default_filename,
                "Excel Files (*.xlsx)"
            )

            if not file_path:
                return

            # Cохранение без форматирования
            df.to_excel(file_path, sheet_name=sheet_name, index=False)

            QMessageBox.information(
                parent,
                "Успех",
                f"Данные успешно экспортированы в файл:\n{file_path}"
            )

        except PermissionError:
            error_msg = "Нет прав для записи в выбранную директорию"
            logging.error(error_msg)
            QMessageBox.critical(parent, "Ошибка", error_msg)
        except Exception as e:
            logging.error(f"Excel Export Error: {str(e)}")
            QMessageBox.critical(
                parent,
                "Ошибка",
                f"Не удалось экспортировать данные:\n{str(e)}"
            )
