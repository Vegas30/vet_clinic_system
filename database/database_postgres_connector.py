import os
import psycopg2
from dotenv import load_dotenv

class PostgresConnector:
    def __init__(self):
        load_dotenv()
        self.db_url = os.getenv("POSTGRES_URL")
        self.conn = None
        self.cur = None

    def connect(self):
        if self.conn is None or self.conn.closed:
            try:
                self.conn = psycopg2.connect(self.db_url)
                self.cur = self.conn.cursor()
                print("Успешное подключение к PostgreSQL")
            except Exception as e:
                print(f"Ошибка подключения к PostgreSQL: {e}")
                self.conn = None
                self.cur = None
        return self.conn

    def disconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            print("Отключение от PostgreSQL")
        self.conn = None
        self.cur = None

    def get_connection(self):
        return self.conn

    def get_cursor(self):
        return self.cur
