# database_models_pg.py
import datetime

from PyQt6.QtCore import QDate
import logging

from database.database_postgres_connector import PostgresConnector


class PostgresModels:
    def __init__(self):
        self.db = PostgresConnector()

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
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                for command in commands:
                    cur.execute(command)
                conn.commit()
                print("Таблицы PostgreSQL успешно созданы или уже существуют.")
        except Exception as e:
            print(f"Ошибка при создании таблиц PostgreSQL: {e}")
        finally:
            self.db.disconnect()

    def insert_branch(self, branch_data):
        """ Добавляет новый филиал в базу данных.
        Args:
            branch_data (dict): Словарь с данными филиала, например:
                {
                    "name": "Название Филиала",
                    "address": "Адрес Филиала",
                    "phone": "Телефон Филиала"
                }
        Returns:
            int: ID созданного филиала или None при ошибке
        """
        name = branch_data.get("name")
        address = branch_data.get("address")
        phone = branch_data.get("phone")

        sql = "INSERT INTO Филиалы (name, address, phone) VALUES (%s, %s, %s) RETURNING id;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (name, address, phone))
                branch_id = cur.fetchone()[0]
                conn.commit()
                print(f"Филиал {name} успешно добавлен с ID: {branch_id}")
                return branch_id
        except Exception as e:
            print(f"Ошибка при добавлении филиала: {e}")
        finally:
            self.db.disconnect()

    def get_all_branches(self):
        """
        Получает все филиалы из базы данных.

        Returns:
            list: Список кортежей с данными филиалов (id, name, address, phone)
        """
        sql = "SELECT id, name, address, phone FROM Филиалы ORDER BY id;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql)
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при получении всех филиалов: {e}")
        finally:
            self.db.disconnect()
        return []

    def delete_branch(self, branch_id):
        sql = "DELETE FROM Филиалы WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (branch_id,))
                conn.commit()
                print(f"Филиал с ID {branch_id} успешно удален.")
                return True
        except Exception as e:
            print(f"Ошибка при удалении филиала: {e}")
        finally:
            self.db.disconnect()

    def update_branch(self, branch_id, update_data):
        """
        Обновляет данные филиала по ID.

        Args:
            branch_id (int): ID филиала
            update_data (dict): Словарь с данными для обновления, например:
                {
                    "name": "Новый Название",
                    "address": "Новый Адрес",
                    "phone": "Новый Телефон"
                }

        Returns:
            bool: True при успешном обновлении, False в противном случае
        """
        sql = "UPDATE Филиалы SET "
        params = []
        for key, value in update_data.items():
            sql += f"{key} = %s, "
            params.append(value)
        sql = sql.rstrip(", ") + " WHERE id = %s;"
        params.append(branch_id)

        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, tuple(params))
                conn.commit()
                print(f"Филиал с ID {branch_id} успешно обновлен.")
                return True
        except Exception as e:
            print(f"Ошибка при обновлении филиала: {e}")
        finally:
            self.db.disconnect()

    def get_branch_by_id(self, branch_id):
        """
        Получает филиал по ID.

        Args:
            branch_id (int): ID филиала

        Returns:
            tuple: Данные филиала (id, name, address, phone) или None, если не найден
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (branch_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Ошибка при получении филиала по ID: {e}")
        finally:
            self.db.disconnect()

    def search_branches_by_id(self, search_text):
        """
        Поиск филиалов по ID.

        Args:
            search_text (str): ID для поиска

        Returns:
            list: Список кортежей с данными филиалов
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (search_text,))
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при поиске филиалов по ID: {e}")
        finally:
            self.db.disconnect()
        return []

    def search_branches_by_name(self, search_text):
        """
        Поиск филиалов по названию.

        Args:
            search_text (str): Название для поиска

        Returns:
            list: Список кортежей с данными филиалов
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE name ILIKE %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (f'%{search_text}%',))
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при поиске филиалов по названию: {e}")
        finally:
            self.db.disconnect()
        return []

    def search_branches_by_address(self, search_text):
        """
        Поиск филиалов по адресу.

        Args:
            search_text (str): Адрес для поиска

        Returns:
            list: Список кортежей с данными филиалов
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE address ILIKE %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (f'%{search_text}%',))
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при поиске филиалов по адресу: {e}")
        finally:
            self.db.disconnect()
        return []

    def search_branches_by_phone(self, search_text):
        """
        Поиск филиалов по телефону.

        Args:
            search_text (str): Телефон для поиска

        Returns:
            list: Список кортежей с данными филиалов
        """
        sql = "SELECT id, name, address, phone FROM Филиалы WHERE phone ILIKE %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (f'%{search_text}%',))
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при поиске филиалов по телефону: {e}")
        finally:
            self.db.disconnect()
        return []

    def insert_employee(self, full_name, login, password_hash, role, branch_id):
        sql = "INSERT INTO Сотрудники (full_name, login, password_hash, role, branch_id) VALUES (%s, %s, %s, %s, %s) RETURNING id;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (full_name, login, password_hash, role, branch_id))
                employee_id = cur.fetchone()[0]
                conn.commit()
                print(f"Сотрудник {full_name} успешно добавлен с ID: {employee_id}")
                return employee_id
        except Exception as e:
            print(f"Ошибка при добавлении сотрудника: {e}")
        finally:
            self.db.disconnect()

    def get_employee_by_login(self, login):
        sql = "SELECT id, full_name, login, password_hash, role, branch_id FROM Сотрудники WHERE login = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (login,))
                return cur.fetchone()
        except Exception as e:
            print(f"Ошибка при получении сотрудника по логину: {e}")
        finally:
            self.db.disconnect()

    def get_employee_by_id(self, employee_id):
        sql = "SELECT id, full_name, login, password_hash, role, branch_id FROM Сотрудники WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (employee_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Ошибка при получении сотрудника по ID: {e}")
        finally:
            self.db.disconnect()

    def update_employee(self, employee_id, full_name, login, password_hash, role, branch_id):
        sql = "UPDATE Сотрудники SET full_name = %s, login = %s, password_hash = %s, role = %s, branch_id = %s WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (full_name, login, password_hash, role, branch_id, employee_id))
                conn.commit()
                print(f"Сотрудник с ID {employee_id} успешно обновлен.")
                return True
        except Exception as e:
            print(f"Ошибка при обновлении сотрудника: {e}")
        finally:
            self.db.disconnect()

    def delete_employee(self, employee_id):
        sql = "DELETE FROM Сотрудники WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (employee_id,))
                conn.commit()
                print(f"Сотрудник с ID {employee_id} успешно удален.")
                return True
        except Exception as e:
            print(f"Ошибка при удалении сотрудника: {e}")
        finally:
            self.db.disconnect()

    def insert_service(self, title, description, price):
        """Добавление новой услуги"""
        sql = "INSERT INTO Услуги (title, description, price) VALUES (%s, %s, %s) RETURNING id;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (title, description, price))
                service_id = cur.fetchone()[0]
                conn.commit()
                print(f"Услуга {title} успешно добавлена с ID: {service_id}")
                return service_id
        except Exception as e:
            print(f"Ошибка при добавлении услуги: {e}")
        finally:
            self.db.disconnect()

    def get_service_by_id(self, service_id):

        sql = "SELECT id, title, description, price FROM Услуги WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (service_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Ошибка при получении услуги по ID: {e}")
        finally:
            self.db.disconnect()

    def update_service(self, service_id, title, description, price):
        """Обновление услуги"""
        sql = "UPDATE Услуги SET title = %s, description = %s, price = %s WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (title, description, price, service_id))
                conn.commit()
                print(f"Услуга с ID {service_id} успешно обновлена.")
                return True
        except Exception as e:
            print(f"Ошибка при обновлении услуги: {e}")
        finally:
            self.db.disconnect()

    def delete_service(self, service_id):
        sql = "DELETE FROM Услуги WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (service_id,))
                conn.commit()
                print(f"Услуга с ID {service_id} успешно удалена.")
                return True
        except Exception as e:
            print(f"Ошибка при удалении услуги: {e}")
        finally:
            self.db.disconnect()

    def get_all_services(self):
        """Получение всех услуг"""
        sql = "SELECT id, title, description, price FROM Услуги;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql)
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при получении всех услуг: {e}")
        finally:
            self.db.disconnect()

    def insert_login_log(self, user_id, event_type):
        sql = "INSERT INTO Журнал_входа (user_id, event_type) VALUES (%s, %s) RETURNING id;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (user_id, event_type))
                log_id = cur.fetchone()[0]
                conn.commit()
                print(f"Запись в журнале входа успешно добавлена с ID: {log_id}")
                return log_id
        except Exception as e:
            print(f"Ошибка при добавлении записи в журнал входа: {e}")
        finally:
            self.db.disconnect()

    def get_all_employees(self):
        sql = "SELECT id, full_name, login, password_hash, role, branch_id FROM Сотрудники;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql)
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при получении всех сотрудников: {e}")
        finally:
            self.db.disconnect()

    def update_employee_password(self, employee_id, new_password_hash):
        sql = "UPDATE Сотрудники SET password_hash = %s WHERE id = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (new_password_hash, employee_id))
                conn.commit()
                print(f"Пароль сотрудника с ID {employee_id} успешно обновлен.")
                return True
        except Exception as e:
            print(f"Ошибка при обновлении пароля сотрудника: {e}")
        finally:
            self.db.disconnect()

    def get_appointment_by_id(self, id):
        """
        Получает приём по ID.
        Args: id (int): ID приёма
        Returns: tuple: Данные приёма
        """
        sql = """
        SELECT id, animal_id, vet_id, date, time, service_id, status 
        FROM Приёмы
        WHERE id = %s
        """
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Ошибка при получении приёма по ID: {e}")
        finally:
            self.db.disconnect()

    def get_appointments_by_date(self, date, status=None):
        """
        Получает приёмы на указанную дату с опциональной фильтрацией по статусу.
        Args:
            date (str): Дата в формате 'YYYY-MM-DD'
            status (str, optional): Статус приёма для фильтрации
        Returns:
            list: Список приёмов
        """
        sql = """
        SELECT id, animal_id, vet_id, date, time, service_id, status
        FROM Приёмы
        WHERE date = %s
        """
        params = [date]

        if status:
            sql += " AND status = %s"
            params.append(status)

        try:
            conn = self.db.connect()
            if not conn:
                raise Exception("Не удалось подключиться к базе данных")

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при получении приёмов по дате: {e}")
            return []
        finally:
            self.db.disconnect()

    def update_appointment(self, id, animal_id, vet_id, date, time, service_id, status):
        """
        Обновляет данные приёма.

        Args:
            id (int): ID приёма
            animal_id (str): ID животного
            vet_id (int): ID ветеринара
            date (str): Дата в формате 'YYYY-MM-DD'
            time (str): Время в формате 'HH:MM'
            service_id (int): ID услуги
            status (str): Статус приёма

        Returns:
            bool: True при успешном обновлении
        """
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
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (animal_id, vet_id, date, time, service_id, status, id))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении приёма: {e}")
        finally:
            self.db.disconnect()
        return False

    def delete_appointment(self, id):
        """
        Удаляет приём.
        Args:
            id (int): ID приёма
        Returns:
            bool: True при успешном удалении
        """
        sql = "DELETE FROM Приёмы WHERE id = %s"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (id,))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            print(f"Ошибка при удалении приёма: {e}")
        finally:
            self.db.disconnect()
        return False

    def insert_appointment(self, animal_id, vet_id, date, time, service_id, status):
        """
        Добавляет новый приём в базу данных

        Args:
            animal_id (str): ID животного
            vet_id (int): ID ветеринара
            date (str): Дата в формате 'YYYY-MM-DD'
            time (str): Время в формате 'HH:MM'
            service_id (int): ID услуги
            status (str): Статус приёма

        Returns:
            int: ID созданного приёма или None при ошибке
        """
        sql = """
        INSERT INTO Приёмы (animal_id, vet_id, date, time, service_id, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        try:
            conn = self.db.connect()
            with conn.cursor() as cur:
                cur.execute(sql, (animal_id, vet_id, date, time, service_id, status))
                appointment_id = cur.fetchone()[0]
                conn.commit()
                return appointment_id
        except Exception as e:
            print(f"Ошибка при добавлении приёма: {e}")
            return None
        finally:
            if conn:
                self.db.disconnect()

    def get_appointment_by_date_range(self, date_from, date_to):
        """
        Получает приёмы за указанный период дат
        Args:
            date_from (str): Начальная дата в формате 'YYYY-MM-DD'
            date_to (str): Конечная дата в формате 'YYYY-MM-DD'
        Returns:
            list: Список приёмов или пустой список при ошибке
        """
        if not date_from or not date_to:
            logging.error("Пустые даты в get_appointment_by_date_range")
            return []

        if date_from > date_to:
            logging.warning(f"Некорректный диапазон дат: {date_from} > {date_to}")
            return []

        sql = """
        SELECT id, animal_id, vet_id, date, time, service_id, status 
        FROM Приёмы
        WHERE date BETWEEN %s AND %s
        ORDER BY date, time
        """
        try:
            conn = self.db.connect()
            if not conn:
                logging.error("Не удалось подключиться к базе данных")
                return []

            with conn.cursor() as cur:
                cur.execute(sql, (date_from, date_to))
                result = cur.fetchall()
                logging.debug(f"Найдено {len(result)} записей за период {date_from} - {date_to}")
                return result
        except Exception as e:
            logging.error(f"Ошибка в get_appointment_by_date_range: {str(e)}")
            return []
        finally:
            self.db.disconnect()

    def get_appointments_by_doctor(self, vet_id, date_from, date_to):
        """Получаем приемы конкретного доктора"""
        sql = """
        SELECT id, animal_id, date, time, service_id, status
        FROM Приёмы
        WHERE vet_id = %s AND date BETWEEN %s AND %s
        ORDER BY date, time
        """
        try:
            conn = self.db.connect()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (vet_id, date_from, date_to))
                    return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при получении приемов врача: {e}")
            return []
        finally:
            self.db.disconnect()

    def get_all_appointments(self, status_filter=None):
        """Получает все приёмы из базы данных с опциональной фильтрацией по статусу
        Args:
            status_filter (str, optional): Фильтр по статусу ('запланирован', 'завершен', 'отменен')
        Returns:
            list: Список приёмов или пустой список при ошибке
        """
        sql = "SELECT * FROM Приёмы"
        params = []

        if status_filter:
            sql += " WHERE status = %s"
            params.append(status_filter)

        sql += " ORDER BY date, time"

        try:
            conn = self.db.connect()
            if not conn:
                logging.error("Не удалось подключиться к базе данных")
                return []

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                result = cur.fetchall()
                logging.debug(f"Найдено {len(result)} приемов" +
                              (f" со статусом {status_filter}" if status_filter else ""))
                return result
        except Exception as e:
            logging.error(f"Ошибка в get_all_appointments: {str(e)}")
            return []
        finally:
            self.db.disconnect()

    def get_financial_stats(self, date_from, date_to):
        """Получает финансовую статистику за период"""
        try:
            conn = self.db.connect()
            if not conn:
                raise Exception("Не удалось подключиться к базе данных")

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

            with conn.cursor() as cur:
                # Основные показатели
                cur.execute(sql_main, params)
                main_stats = cur.fetchone()

                # Статистика по услугам
                cur.execute(sql_services, params)
                services = []
                for row in cur.fetchall():
                    services.append({
                        'service_name': row[0],
                        'service_count': row[1],
                        'service_income': float(row[2])
                    })

                # Статистика по врачам
                cur.execute(sql_doctors, params)
                doctors = []
                for row in cur.fetchall():
                    doctors.append({
                        'doctor_name': row[0],
                        'appointment_count': row[1],
                        'doctor_income': float(row[2])
                    })

                return {
                    'total_count': main_stats[0] if main_stats else 0,
                    'total_income': float(main_stats[1]) if main_stats else 0.0,
                    'doctors_count': main_stats[2] if main_stats else 0,
                    'services': services,
                    'doctors': doctors
                }

        except Exception as e:
            logging.error(f"Ошибка при получении финансовой статистики: {str(e)}")
            return None
        finally:
            self.db.disconnect()

    def get_all_doctors(self):
        """Получаем всех сотрудников с ролью 'doctor"""
        sql = """
        SELECT id, full_name 
        FROM Сотрудники 
        WHERE role = 'doctor'
        ORDER BY full_name
        """
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql)
                return cur.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при получении списка врачей: {str(e)}")
            return []
        finally:
            self.db.disconnect()

    def get_monthly_stats(self, year=None):
        """Статистика приемов и услуг по месяцам"""
        sql = """
        SELECT 
            EXTRACT(MONTH FROM date) AS month,
            COUNT(*) AS total_appointments,
            COUNT(DISTINCT animal_id) AS unique_animals,
            COUNT(DISTINCT vet_id) AS unique_vets,
            SUM(CASE WHEN status = 'завершен' THEN 1 ELSE 0 END) AS completed,
            SUM(s.price) AS total_income
        FROM Приёмы a
        JOIN Услуги s ON a.service_id = s.id
        """

        params = []
        if year:
            sql += " WHERE EXTRACT(YEAR FROM date) = %s"
            params.append(year)

        sql += " GROUP BY month ORDER BY month"

        try:
            conn = self.db.connect()
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception as e:
            logging.error(f"Ошибка получения статистики: {str(e)}")
            return []

    def check_vet_availability(self, vet_id, date, time, exclude_id=None):
        """
        Проверяет доступность ветеринара в указанное время

        Args:
            vet_id (int): ID ветеринара
            date (str): Дата в формате 'YYYY-MM-DD'
            time (str): Время в формате 'HH:MM'
            exclude_id (int, optional): ID приёма для исключения (при редактировании)

        Returns:
            bool: True если время занято, False если свободно
        """
        sql = """
        SELECT id FROM Приёмы
        WHERE vet_id = %s AND date = %s AND time = %s AND status != 'отменен'
        """
        params = [vet_id, date, time]

        if exclude_id:
            sql += " AND id != %s"
            params.append(exclude_id)

        try:
            conn = self.db.connect()
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchone() is not None
        except Exception as e:
            print(f"Ошибка при проверке доступности ветеринара: {e}")
            return True
        finally:
            if conn:
                self.db.disconnect()

