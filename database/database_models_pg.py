# database_models_pg.py
import datetime
import time

from PyQt6.QtCore import QDate
import logging
from database.database_postgres_connector import PostgresConnector
from contextlib import contextmanager


class PostgresModels:
    def __init__(self):
        self.db = PostgresConnector()
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("SELECT 1;")
        except Exception as e:
            logging.critical(f"Failed to initialize PostgreSQL connection: {e}")
            raise Exception("Failed to initialize PostgreSQL connection")

    @contextmanager
    def _get_cursor(self):
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.db.put_connection(conn)

    def _check_connection(self):
        """Проверяет активность соединения с БД"""
        try:
            conn = self.db.get_connection()
            if conn and not conn.closed:
                return True
            return self.db.connect()
        except Exception as e:
            logging.error(f"Ошибка проверки соединения: {e}")
            return False

    def _execute_query(self, query, params=None, fetch=False):
        """
        Универсальный метод выполнения запросов
        :param query: SQL запрос
        :param params: Параметры запроса
        :param fetch: Нужно ли получать результат
        :return: Результат выполнения
        """
        logging.debug(f"Executing query: {query} with params: {params}")

        conn = None
        cur = None
        try:
            conn = self.db.get_connection()
            conn.autocommit = False
            cur = conn.cursor()

            # таймаут выполнения запроса (в секундах)
            cur.execute("SET statement_timeout = 5000;")  # 5 секунд

            cur.execute(query, params or ())

            if fetch:
                result = cur.fetchall()
                return result
            else:
                conn.commit()
                return True

        except Exception as e:
            logging.error(f"Ошибка выполнения запроса: {e}\nQuery: {query}\nParams: {params}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                self.db.put_connection(conn)  # Гарантированное возвращение соединения

    def create_tables(self):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS Филиалы (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Сотрудники (
                id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                branch_id INTEGER NOT NULL REFERENCES Филиалы(id) ON DELETE RESTRICT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Услуги (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL CHECK (price >= 0)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Приёмы (
                id SERIAL PRIMARY KEY,
                animal_id TEXT NOT NULL,
                vet_id INTEGER NOT NULL REFERENCES Сотрудники(id) ON DELETE RESTRICT,
                date DATE NOT NULL,
                time TIME NOT NULL,
                service_id INTEGER NOT NULL REFERENCES Услуги(id) ON DELETE RESTRICT,
                status TEXT NOT NULL CHECK (status IN ('запланирован', 'завершен', 'отменен')),
                CONSTRAINT unique_appointment UNIQUE (vet_id, date, time)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Журнал_входа (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES Сотрудники(id) ON DELETE CASCADE,
                datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL CHECK (event_type IN ('вход', 'выход'))
            );
            """
        )
        try:
            for command in commands:
                if not self._execute_query(command):
                    return False
            logging.info("Таблицы успешно созданы")
            return True
        except Exception as e:
            logging.error(f"Ошибка создания таблиц: {e}")
            return False

    # Базовые CRUD операции для филиалов
    def insert_branch(self, branch_data):
        """ Добавляет новый филиал в базу данных.
        """
        name = branch_data.get("name")
        address = branch_data.get("address")
        phone = branch_data.get("phone")

        # Дополнительная валидация данных
        if not name:
            raise ValueError("Название филиала не может быть пустым")
        if len(phone) < 5:  # Минимальная длина номера телефона
            raise ValueError("Номер телефона слишком короткий")

        sql = "INSERT INTO Филиалы (name, address, phone) VALUES (%s, %s, %s) RETURNING id;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (name, address, phone))
                result = cursor.fetchone()

                if result:
                    branch_id = result[0]
                    logging.info(f"Филиал '{name}' успешно добавлен с ID: {branch_id}")
                    return branch_id
                logging.error("Не удалось получить ID созданного филиала")
                return None
        except Exception as e:
            logging.error(f"Ошибка при добавлении филиала: {e}")
            return None

    def get_branch_by_id(self, branch_id):
        """
        Получает филиал по ID.
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE id = %s;"

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (branch_id,))
                result = cursor.fetchone()

                if result:
                    # Преобразуем результат в словарь с названиями полей
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, result))

                logging.info(f"Филиал с ID {branch_id} не найден")
                return None
        except Exception as e:
            logging.error(f"Ошибка при получении филиала по ID: {e}")
            return None

    def get_all_branches(self):
        """
        Получает все филиалы из базы данных.

        """
        sql = "SELECT id, name, address, phone FROM Филиалы ORDER BY id;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при получении всех филиалов: {e}")
            return None

    def update_branch(self, branch_id, update_data):
        """
        Обновляет данные филиала по ID.
        """
        sql = "UPDATE Филиалы SET "
        params = []
        for key, value in update_data.items():
            sql += f"{key} = %s, "
            params.append(value)
        sql = sql.rstrip(", ") + " WHERE id = %s;"
        params.append(branch_id)

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                if cursor.rowcount == 0:
                    logging.warning(f"Филиал с ID {branch_id} не найден")
                    return False
                logging.info(f"Филиал с ID {branch_id} успешно обновлен.")
                return True
        except Exception as e:
            logging.error(f"Ошибка при обновлении филиала: {e}")
            return False


    def delete_branch(self, branch_id):
        sql = "DELETE FROM Филиалы WHERE id = %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (branch_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"Филиал с ID {branch_id} не найден")
                    return False

                logging.info(f"Филиал с ID {branch_id} успешно удален")
                return True
        except Exception as e:
            logging.error(f"Ошибка при удалении филиала: {e}")
            return True

    def search_branches_by_name(self, search_text):
        """
        Поиск филиалов по названию.
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE name ILIKE %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (f'%{search_text}%',))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при поиске филиалов по названию: {e}")
            return []

    def search_branches_by_address(self, search_text):
        """
        Поиск филиалов по адресу.
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE address ILIKE %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (f'%{search_text}%',))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при поиске филиалов по адресу: {e}")
            return []

    def search_branches_by_phone(self, search_text):
        """
        Поиск филиалов по телефону.
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE phone ILIKE %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (f'%{search_text}%',))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при поиске филиалов по адресу: {e}")
            return []

    # Операции с сотрудниками
    def insert_employee(self, employee_data):
        """Добавляет нового сотрудника"""
        sql = "INSERT INTO Сотрудники (full_name, login, password_hash, role, branch_id) VALUES (%s, %s, %s, %s, %s) RETURNING id;"
        params = (
            employee_data.get("full_name"),
            employee_data.get("login"),
            employee_data.get("password_hash"),
            employee_data.get("role"),
            employee_data.get("branch_id")
        )

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"Error inserting employee: {e}")
            return None

    def get_employee_by_id(self, employee_id):
        """Получает сотрудника по ID"""
        sql = """
                SELECT id, full_name, login, password_hash, role, branch_id 
                FROM Сотрудники WHERE id = %s;
                """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (employee_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Ошибка при получении сотрудника по ID: {e}")
            return None

    def get_employee_by_login(self, login):
        """Получает сотрудника по логину"""
        sql = """
        SELECT id, full_name, login, password_hash, role, branch_id 
        FROM Сотрудники WHERE login = %s;
        """
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(sql, (login,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error getting employee by login: {e}")
            return None

    def get_all_employees(self):
        """Получает список всех сотрудников"""
        sql = """
        SELECT id, full_name, login, password_hash, role, branch_id 
        FROM Сотрудники;
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при получении всех сотрудников: {e}")
            return None


    def update_employee(self, employee_id, full_name, login, password_hash, role, branch_id):
        """Обновляет данные сотрудника"""
        sql = ("UPDATE Сотрудники SET full_name = %s, login = %s, password_hash = %s, "
               "role = %s, branch_id = %s WHERE id = %s;")
        params = (full_name, login, password_hash, role, branch_id, employee_id)

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                # Проверяем, была ли обновлена хотя бы одна строка
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Ошибка при обновлении сотрудника {employee_id}: {str(e)}")
        return False

    def update_employee_password(self, employee_id, new_password_hash):

        sql = "UPDATE Сотрудники SET password_hash = %s WHERE id = %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (new_password_hash, employee_id))
                print(f"Пароль сотрудника с ID {employee_id} успешно обновлен.")
                return True
        except Exception as e:
            logging.error(f"Ошибка при обновлении пароля сотрудника: {e}.")
        return False

    def delete_employee(self, employee_id):
        """Удаляет сотрудника"""
        sql = "DELETE FROM Сотрудники WHERE id = %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (employee_id,))
                return True
        except Exception as e:
            logging.error(f"Ошибка при удалении сотрудника: {e}")
        return False

    # Операции с услугами
    def insert_service(self, title, description, price):
        """Добавляет новую услугу"""
        sql = """
        INSERT INTO Услуги (title, description, price) 
        VALUES (%s, %s, %s) RETURNING id;
        """
        params = (title, description, price)

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()
                if result:
                    service_id = result[0]
                    logging.info(f"Услуга '{title}' добавлена с ID: {service_id}")
                    return service_id
                logging.error("Не удалось получить ID созданной услуги")
                return None

        except Exception as e:
            logging.error(f"Ошибка при добавлении услуги: {e}")
            return None

    def get_service_by_id(self, service_id):
        """Получает услугу по ID"""
        sql = "SELECT id, title, description, price FROM Услуги WHERE id = %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (service_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Ошибка при получении услуги по ID: {e}")
            return None

    def get_all_services(self):
        """Получает список всех услуг"""
        sql = "SELECT id, title, description, price FROM Услуги;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при получении всех услуг: {e}")
            return []

    def update_service(self, service_id, title, description, price):
        """Обновляет данные услуги"""
        sql = "UPDATE Услуги SET title = %s, description = %s, price = %s WHERE id = %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (title, description, price, service_id))
                logging.info(f"Услуга с ID {service_id} успешно обновлена.")
                return True
        except Exception as e:
            logging.error(f"Ошибка при обновлении услуги: {e}")
            return False

    def delete_service(self, service_id) :
        """Удаляет услугу"""
        sql = "DELETE FROM Услуги WHERE id = %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (service_id,))
                logging.info(f"Услуга с ID {service_id} успешно удалена.")
                return True
        except Exception as e:
            logging.error(f"Ошибка при удалении услуги: {e}")
            return  False

    # Операции с приёмами
    def insert_appointment(self, animal_id, vet_id, date, time, service_id, status):
        """
        Добавляет новый приём в базу данных
        """
        sql = """
        INSERT INTO Приёмы (animal_id, vet_id, date, time, service_id, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            animal_id, vet_id, date, time, service_id, status
        )

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()
                if result:
                    return result[0]
                return None
        except Exception as e:
            logging.info(f"Ошибка при добавлении приёма: {e}")
            return None

    def get_appointment_by_id(self, id):
        """Получает приём по ID"""
        sql = """
        SELECT id, animal_id, vet_id, date, time, service_id, status 
        FROM Приёмы WHERE id = %s;
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (id,))
                return cursor.fetchone()
        except Exception as e:
            logging.info(f"Ошибка при получении приёма по ID: {e}")

    def get_appointments_by_date(self, date, status=None):
        """Получает приёмы на указанную дату"""
        sql = """
        SELECT id, animal_id, vet_id, date, time, service_id, status
        FROM Приёмы WHERE date = %s
        """
        params = [date]

        if status:
            sql += " AND status = %s"
            params.append(status)

        sql += " ORDER BY time;"

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении приёмов по дате: {e}")
            return []

    def get_appointment_by_date_range(self, date_from, date_to):
        """Получает приёмы за период"""
        if not date_from or not date_to:
            logging.error("Не указаны даты для поиска")
            return []

        sql = """
        SELECT id, animal_id, vet_id, date, time, service_id, status 
        FROM Приёмы
        WHERE date BETWEEN %s AND %s
        ORDER BY date, time;
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (date_from, date_to))
                result = cursor.fetchall()
                logging.debug(f"Найдено {len(result)} записей за период {date_from} - {date_to}")
                return result
        except Exception as e:
            logging.error(f"Ошибка в get_appointment_by_date_range: {str(e)}")
            return []

    def get_appointments_by_doctor(self, vet_id, date_from, date_to):
        """Получает приёмы конкретного врача за период"""
        sql = """
        SELECT id, animal_id, date, time, service_id, status
        FROM Приёмы
        WHERE vet_id = %s AND date BETWEEN %s AND %s
        ORDER BY date, time;
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (vet_id, date_from, date_to))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при получении приемов врача: {e}")
        return []

    def get_all_appointments(self, status_filter=None):
        """Получает все приёмы из базы данных с опциональной фильтрацией по статусу
        """
        sql = "SELECT * FROM Приёмы"
        params = []

        if status_filter:
            sql += " WHERE status = %s"
            params.append(status_filter)

        sql += " ORDER BY date, time"

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, tuple(params))
            result = cursor.fetchall()
            logging.debug(f"Найдено {len(result)} приемов" +
                          (f" со статусом {status_filter}" if status_filter else ""))
            return result

        except Exception as e:
            logging.error(f"Ошибка в get_all_appointments: {str(e)}")
            return []

    def update_appointment(self, id, animal_id, vet_id, date, time, service_id, status):
        """Обновляет данные приёма"""
        sql = """
                UPDATE Приёмы
                SET animal_id = %s,
                    vet_id = %s,
                    date = %s,
                    time = %s,
                    service_id = %s,
                    status = %s
                WHERE id = %s
                """
        params = (animal_id, vet_id, date, time, service_id, status, id)

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                # Проверяем, была ли обновлена хотя бы одна строка
                updated = cursor.rowcount > 0
                if not updated:
                    logging.warning(f"Приём с ID {id} не найден")
                return updated
        except Exception as e:
            logging.error(f"Ошибка при обновлении приёма: {e}")
            return False

    def delete_appointment(self, id):
        """Удаляет приём"""
        sql = "DELETE FROM Приёмы WHERE id = %s;"
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, (id,))
                deleted = cursor.rowcount > 0
                if not deleted:
                    logging.warning(f"Приём с ID {id} не найден")
                return deleted
        except Exception as e:
            logging.error(f"Ошибка при удалении приёма: {e}")
            return False

    def check_vet_availability(self, vet_id, date, time, exclude_id=None):
        """Проверяет доступность врача в указанное время"""
        sql = """
        SELECT id FROM Приёмы
        WHERE vet_id = %s AND date = %s AND time = %s AND status != 'отменен'
        """
        params = [vet_id, date, time]

        if exclude_id:
            sql += " AND id != %s"
            params.append(exclude_id)

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Ошибка при проверке доступности ветеринара: {e}")
            return True

    # Отчеты и статистика
    def get_financial_stats(self, date_from, date_to):
        """Получает финансовую статистику за период"""
        try:
            # Основные показатели
            sql_main = """
                SELECT 
                    COUNT(*) as total_count,
                    COALESCE(SUM(s.price), 0) as total_income,
                    COUNT(DISTINCT a.vet_id) as doctors_count
                FROM Приёмы a
                JOIN Услуги s ON a.service_id = s.id
                WHERE a.status = 'завершен' 
                    AND a.date BETWEEN %s AND %s
                """

            # Статистика по услугам
            sql_services = """
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

            # Статистика по врачам
            sql_doctors = """
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

            params = (date_from, date_to)

            # Выполняем запросы
            with self._get_cursor() as cursor:
                cursor.execute(sql_main, params)
                main_stats = cursor.fetchone()

                cursor.execute(sql_services, params)
                services = cursor.fetchall()

                cursor.execute(sql_doctors, params)
                doctors = cursor.fetchall()

                if not main_stats:
                    logging.info(f"Нет данных за период с {date_from} по {date_to}")
                    return None

                if not main_stats:
                    return None

                return {
                    'total_count': main_stats[0] if main_stats else 0,
                    'total_income': float(main_stats[1]) if main_stats else 0.0,
                    'doctors_count': main_stats[2] if main_stats else 0,
                    'services': [{
                        'service_name': row[0],
                        'service_count': row[1],
                        'service_income': float(row[2])
                    } for row in services] if services else [],
                    'doctors': [{
                        'doctor_name': row[0],
                        'appointment_count': row[1],
                        'doctor_income': float(row[2])
                    } for row in doctors] if doctors else []
                }

        except Exception as e:
            logging.error(f"Ошибка получения финансовой статистики: {e}")
            return None

    def get_monthly_financial_stats(self, year=None, month=None):
        """Получает месячную статистику"""
        sql = """
        SELECT 
            EXTRACT(MONTH FROM date) AS month,
            COUNT(*) FILTER (WHERE status = 'завершен') AS completed_count,
            COALESCE(SUM(s.price, 0) AS income
        FROM Приёмы a
        JOIN Услуги s ON a.service_id = s.id
        WHERE status = 'завершен'
        """
        params = []

        if year:
            sql += " AND EXTRACT(YEAR FROM date) = %s"
            params.append(year)
        if month:
            sql += " AND EXTRACT(MONTH FROM date) = %s"
            params.append(month)

        sql += " GROUP BY month ORDER BY month;"

        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, tuple(params))
                result =  cursor.fetchall()

                return [
                    (int(row[0]), int(row[1]), float(row[2]))
                    for row in result
                ] if result else []
        except Exception as e:
            logging.error(f"Ошибка получения месячной статистики: {str(e)}")
            return []

    def get_all_doctors(self):
        """Получает список всех врачей"""
        sql = """
        SELECT id, full_name 
        FROM Сотрудники 
        WHERE role = 'doctor'
        ORDER BY full_name;
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при получении списка врачей: {str(e)}")
            return []

    def generate_monthly_stats_report(self,  year=None, month=None):
        """Генерирует отчет по месячной статистике"""
        try:
            stats = self.get_monthly_financial_stats(year, month)
            headers = ["Месяц", "Количество приемов", "Доход"]

            if not stats:
                return headers, [["Нет данных за выбранный период"]]

            month_names = [
                "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
            ]

            data = []
            for row in stats:
                month_num, count, income = row
                month_name = month_names[int(month_num) - 1]
                data.append([month_name, str(count), f"{float(income):.2f} ₽"])

            return headers, data

        except Exception as e:
            logging.error(f"Ошибка генерации отчета: {e}")
            return ["Ошибка"], [[f"Не удалось сформировать отчет: {str(e)}"]]

        # Журнал входа

    def insert_login_log(self, user_id, event_type):
        """Добавляет запись в журнал входа"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Журнал_входа (user_id, event_type) VALUES (%s, %s) RETURNING id;",
                    (user_id, event_type)
                )
                result = cursor.fetchone()
                conn.commit()
                return result[0] if result else None
        except Exception as e:
            logging.error(f"Ошибка записи в журнал входа: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if 'conn' in locals():
                self.db.put_connection(conn)
