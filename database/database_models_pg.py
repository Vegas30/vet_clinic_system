# Классы и SQL-запросы к PostgreSQL
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

    def insert_branch(self, name, address, phone):
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
        sql = "SELECT id, name, address, phone FROM Филиалы;"
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

    def insert_appointment(self, animal_id, vet_id, date, time, service_id, status):
        sql = "INSERT INTO Приёмы (animal_id, vet_id, date, time, service_id, status) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (animal_id, vet_id, date, time, service_id, status))
                appointment_id = cur.fetchone()[0]
                conn.commit()
                print(f"Приём успешно добавлен с ID: {appointment_id}")
                return appointment_id
        except Exception as e:
            print(f"Ошибка при добавлении приёма: {e}")
        finally:
            self.db.disconnect()

    def get_appointments_by_vet_and_date(self, vet_id, date):
        sql = "SELECT id, animal_id, vet_id, date, time, service_id, status FROM Приёмы WHERE vet_id = %s AND date = %s;"
        try:
            conn = self.db.connect()
            cur = self.db.get_cursor()
            if conn and cur:
                cur.execute(sql, (vet_id, date))
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при получении приёмов по врачу и дате: {e}")
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