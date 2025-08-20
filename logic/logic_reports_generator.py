# logic_reports_generator.py
from datetime import datetime, timedelta
from PyQt6.QtCore import QDate
from database.database_models_pg import PostgresModels
from database.database_models_mongo import MongoDBModels
import logging


class ReportsGenerator:
    def __init__(self):
        self.db_pg = PostgresModels()
        self.db_mongo = MongoDBModels()

    def get_date_range(self, period_type, custom_date_from=None, custom_date_to=None):
        """Возвращает даты начала и конца периода в формате строк"""
        today = datetime.now().date()

        if period_type == "day":
            date_from = date_to = today
        elif period_type == "week":
            date_from = today - timedelta(days=today.weekday())
            date_to = date_from + timedelta(days=6)
        elif period_type == "month":
            date_from = today.replace(day=1)
            next_month = date_from.replace(day=28) + timedelta(days=4)
            date_to = next_month - timedelta(days=next_month.day)
        elif period_type == "custom" and custom_date_from and custom_date_to:
            date_from = custom_date_from
            date_to = custom_date_to
        else:
            raise ValueError("Invalid period type or custom dates")

        return date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")

    def generate_appointments_report(self, date_from, date_to):
        """Генерация отчета по приемам за период с использованием агрегации"""
        try:
            query = """
                SELECT 
                    a.id, 
                    a.date, 
                    a.time, 
                    a.animal_id,
                    e.full_name AS vet_name,
                    s.title AS service_name,
                    a.status
                FROM Приёмы a
                JOIN Сотрудники e ON a.vet_id = e.id
                JOIN Услуги s ON a.service_id = s.id
                WHERE a.date BETWEEN %s AND %s
                ORDER BY a.date, a.time
            """

            conn = self.db_pg.db.connect()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (date_from, date_to))
                    appointments = cursor.fetchall()

            # Получаем данные животных одним запросом
            animal_ids = [str(appt[3]) for appt in appointments]
            animals_data = {}
            if animal_ids:
                animals = self.db_mongo.collection.find(
                    {'_id': {'$in': animal_ids}},
                    {'_id': 1, 'name': 1, 'species': 1, 'breed': 1, 'owner_name': 1, 'owner_phone': 1}
                )
                animals_data = {str(a['_id']): a for a in animals}

            # Форматируем данные для отображения
            report_data = []
            for appt in appointments:
                animal = animals_data.get(appt[3], {})
                report_data.append([
                    str(appt[0]),
                    appt[1].strftime("%d.%m.%Y"),
                    appt[2].strftime("%H:%M"),
                    animal.get('name', 'Неизвестно'),
                    appt[4],  # vet_name
                    appt[5],  # service_name
                    appt[6]  # status
                ])

            headers = ["ID", "Дата", "Время", "Животное", "Врач", "Услуга", "Статус"]
            return headers, report_data

        except Exception as e:
            logging.error(f"Ошибка генерации отчета по приемам: {str(e)}")
            raise

    def generate_animals_by_diagnosis(self, diagnosis):
        """Генерация отчета по животным с определенным диагнозом с агрегацией"""
        try:
            # Используем агрегацию MongoDB для получения животных с диагнозом
            pipeline = [
                {"$match": {"medical_history.diagnosis": diagnosis}},
                {"$project": {
                    "_id": 1,
                    "name": 1,
                    "species": 1,
                    "breed": 1,
                    "owner_name": 1,
                    "owner_phone": 1
                }}
            ]

            animals = list(self.db_mongo.collection.aggregate(pipeline))

            report_data = []
            for animal in animals:
                report_data.append([
                    animal['_id'],
                    animal.get('name', ''),
                    animal.get('species', ''),
                    animal.get('breed', ''),
                    animal.get('owner_name', ''),
                    animal.get('owner_phone', '')
                ])

            headers = ["ID", "Имя", "Вид", "Порода", "Хозяин", "Телефон"]
            return headers, report_data

        except Exception as e:
            logging.error(f"Ошибка генерации отчета по животным: {str(e)}")
            raise

    def generate_services_by_doctor(self, vet_id, date_from, date_to):
        """Генерация отчета по услугам врача с агрегацией на стороне БД"""
        try:
            # Используем агрегирующий запрос для получения статистики по услугам
            query = """
                SELECT 
                    s.title AS service_name,
                    COUNT(a.id) AS service_count,
                    SUM(s.price) AS service_total
                FROM Приёмы a
                JOIN Услуги s ON a.service_id = s.id
                WHERE a.vet_id = %s 
                    AND a.date BETWEEN %s AND %s
                    AND a.status = 'завершен'
                GROUP BY s.title
                ORDER BY service_count DESC
            """

            conn = self.db_pg.db.connect()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (vet_id, date_from, date_to))
                    services = cursor.fetchall()

            # Форматируем для отчета
            report_data = []
            for service in services:
                report_data.append([
                    service[0],  # service_name
                    str(service[1]),  # count
                    f"{float(service[2]):.2f} ₽"  # total
                ])

            headers = ["Услуга", "Количество", "Сумма"]
            return headers, report_data

        except Exception as e:
            logging.error(f"Ошибка генерации отчета по услугам: {str(e)}")
            raise

    def generate_finance_report(self, date_from, date_to):
        """Генерация финансового отчета за период с агрегацией"""

        conn = None

        try:
            conn = self.db_pg.db.connect()
            if not conn:
                raise Exception("Не удалось подключиться к базе данных")

            # Основные показатели с агрегацией в одном запросе
            main_query = """
                   SELECT 
                       COUNT(*) as total_count,
                       COALESCE(SUM(s.price), 0) as total_income,
                       COUNT(DISTINCT a.vet_id) as doctors_count
                   FROM Приёмы a
                   JOIN Услуги s ON a.service_id = s.id
                   WHERE a.status = 'завершен' 
                       AND a.date BETWEEN %s AND %s
               """

            # Статистика по услугам с агрегацией
            services_query = """
                   SELECT 
                       s.title as service_name,
                       COUNT(*) as service_count,
                       COALESCE(SUM(s.price), 0) as service_income
                   FROM Приёмы a
                   JOIN Услуги s ON a.service_id = s.id
                   WHERE a.status = 'завершен' 
                       AND a.date BETWEEN %s AND %s
                   GROUP BY s.title
                   ORDER BY service_count DESC
               """

            # Статистика по врачам с агрегацией
            doctors_query = """
                   SELECT 
                       e.full_name as doctor_name,
                       COUNT(*) as appointment_count,
                       COALESCE(SUM(s.price), 0) as doctor_income
                   FROM Приёмы a
                   JOIN Услуги s ON a.service_id = s.id
                   JOIN Сотрудники e ON a.vet_id = e.id
                   WHERE a.status = 'завершен' 
                       AND a.date BETWEEN %s AND %s
                   GROUP BY e.full_name
                   ORDER BY appointment_count DESC
               """

            # Выполняем все запросы в рамках одного соединения
            with conn.cursor() as cursor:
                cursor.execute(main_query, (date_from, date_to))
                main_stats = cursor.fetchone()

                cursor.execute(services_query, (date_from, date_to))
                services = cursor.fetchall()

                cursor.execute(doctors_query, (date_from, date_to))
                doctors = cursor.fetchall()

            if not main_stats:
                return ["Период", "Данные"], [["Нет данных за выбранный период"]]

            headers = ["Категория", "Значение"]
            data = [
                ["Период отчета", f"{date_from} - {date_to}"],
                ["Всего завершенных приемов", str(main_stats[0])],
                ["Общий доход", f"{float(main_stats[1]):.2f} ₽"],
                ["Количество работавших врачей", str(main_stats[2])],
                ["", ""],  # Разделитель
                ["Статистика по услугам", ""]
            ]

            # Добавляем данные по услугам
            for service in services:
                data.append([
                    service[0],
                    f"{service[1]} приемов на {float(service[2]):.2f} ₽"
                ])

            data.append(["", ""])  # Разделитель
            data.append(["Статистика по врачам", ""])

            # Добавляем данные по врачам
            for doctor in doctors:
                data.append([
                    doctor[0],
                    f"{doctor[1]} приемов на {float(doctor[2]):.2f} ₽"
                ])

            return headers, data

        except Exception as e:
            logging.error(f"Ошибка генерации финансового отчета: {str(e)}")
            return ["Ошибка", "Детали"], [[f"Не удалось сформировать отчет", str(e)]]
        finally:
            if conn:
                self.db_pg.db.disconnect()

    def generate_monthly_stats_report(self, year=None, month=None):
        """Генерация месячной статистики с агрегацией"""
        try:
            # Основной агрегирующий запрос
            query = """
                SELECT
                    EXTRACT(MONTH FROM date) AS month,
                    COUNT(*) FILTER (WHERE status = 'завершен') AS completed_count,
                    COALESCE(SUM(s.price), 0) AS income
                FROM Приёмы a
                JOIN Услуги s ON a.service_id = s.id
                WHERE status = 'завершен'
            """

            params = []

            if year:
                query += " AND EXTRACT(YEAR FROM date) = %s"
                params.append(year)
            if month:
                query += " AND EXTRACT(MONTH FROM date) = %s"
                params.append(month)

            query += " GROUP BY month ORDER BY month;"

            conn = self.db_pg.db.connect()
            if not conn:
                raise Exception("Не удалось подключиться к базе данных")

            with conn.cursor() as cursor:
                cursor.execute(query, tuple(params))
                stats = cursor.fetchall()

            month_names = [
                "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
            ]

            # Форматируем данные для отчета
            data = []
            for row in stats:
                try:
                    month_num = int(row[0]) if row[0] else 1
                    count = int(row[1]) if row[1] else 0
                    income = float(row[2]) if row[2] else 0.0

                    month_name = month_names[month_num - 1] if 1 <= month_num <= 12 else "Неизвестно"
                    data.append([month_name, count, f"{income:.2f} ₽"])
                except (IndexError, ValueError) as e:
                    logging.error(f"Ошибка обработки данных: {row}. Ошибка: {str(e)}")
                    continue

            headers = ["Месяц", "Завершенных приемов", "Доход"]
            return headers, data

        except Exception as e:
            logging.error(f"Ошибка генерации месячного отчета: {str(e)}", exc_info=True)
            return ["Ошибка"], [[f"Ошибка формирования отчета: {str(e)}"]]

    # def generate_yearly_stats_report(self, year=None):
    #     """Генерация годовой статистики с фильтрацией по году"""
    #     try:
    #         conn = self.db_pg.connect()
    #         with conn.cursor() as cur:
    #             query = """
    #                 SELECT
    #                     EXTRACT(YEAR FROM date) AS year,
    #                     COUNT(*) AS total_appointments,
    #                     COALESCE(SUM(s.price), 0) AS total_income
    #                 FROM Приёмы a
    #                 JOIN Услуги s ON a.service_id = s.id
    #                 WHERE a.status = 'завершен'
    #             """
    #             params = []
    #
    #             if year is not None:
    #                 query += " AND EXTRACT(YEAR FROM date) = %s"
    #                 params.append(year)
    #
    #             query += " GROUP BY year ORDER BY year DESC"
    #
    #             logging.debug(f"Executing yearly stats query: {query} with params: {params}")
    #             cur.execute(query, params)
    #             stats = cur.fetchall()
    #
    #         # Формируем гарантированно правильную структуру ответа
    #         headers = ["Год", "Количество приемов", "Доход"]
    #
    #         if not stats:
    #             return headers, []
    #
    #         data = []
    #         for row in stats:
    #             try:
    #                 year = int(row[0]) if row[0] is not None else 0
    #                 appointments = row[1] if row[1] is not None else 0
    #                 income = float(row[2]) if row[2] is not None else 0.0
    #                 data.append([year, appointments, income])
    #             except Exception as e:
    #                 logging.error(f"Ошибка обработки строки статистики: {row}. Ошибка: {str(e)}")
    #                 continue
    #
    #         return headers, data
    #
    #     except Exception as e:
    #         logging.error(f"Ошибка генерации годового отчета: {str(e)}")
    #         return ["Ошибка"], [[f"Не удалось получить данные: {str(e)}"]]
