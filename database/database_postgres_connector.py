#  database_postgres_connector.py

import os
import time
from datetime import datetime

from psycopg2 import pool

import psycopg2
from dotenv import load_dotenv
import logging

class PostgresConnector:
    _instance = None
    _connection_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresConnector, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        load_dotenv()
        self.db_url = os.getenv("POSTGRES_URL")
        self._retry_count = 0
        self._max_retries = 3
        try:
            self._init_pool()
        except Exception as e:
            logging.error(f"Initial pool initialization failed: {e}")
            self._retry_initialization()

    def _init_pool(self):
        self._connection_pool = pool.ThreadedConnectionPool(
            minconn=5,
            maxconn=20,
            dsn=self.db_url
        )
        # Проверка соединения
        conn = self._connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
        finally:
            self._connection_pool.putconn(conn)
        logging.info("PostgreSQL connection pool initialized successfully")

    def _retry_initialization(self):
        while self._retry_count < self._max_retries:
            self._retry_count += 1
            try:
                logging.info(f"Retrying pool initialization (attempt {self._retry_count})")
                self._init_pool()
                return
            except Exception as e:
                logging.error(f"Retry {self._retry_count} failed: {e}")
        raise Exception("Failed to initialize connection pool after retries")

    def get_connection(self):
        try:
            conn = self._connection_pool.getconn()
            logging.debug("Successfully obtained connection from pool")
            return conn
        except Exception as e:
            logging.error(f"Connection receipt error: {e}")
            raise


    def put_connection(self, conn):
        try:
            self._connection_pool.putconn(conn)
            logging.debug("Connection returned to pool successfully")
        except Exception as e:
            logging.error(f"Error returning connection: {e}")
            if conn:
                conn.close()

    def close_all(self):
        if self._connection_pool:
            self._connection_pool.closeall()
            logging.info("All PostgreSQL connections closed")

    def test_connection(self):
        """Проверка работоспособности соединения"""
        try:
            conn = self.get_connection()

            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1;")
                return True
        except Exception as e:
            logging.error(f"Connection test failed: {e}")
            return False

    def get_cursor(self):
        """Получает курсор из пула соединений"""
        conn = self.get_connection()
        return conn.cursor()

    def check_active_connections(self):
        try:
            with self._get_cursor() as cursor:
                cursor.execute("""
                    SELECT pid, usename, application_name, client_addr,
                           query_start, query, state
                    FROM pg_stat_activity
                    WHERE state = 'active';
                """)
                active_connections = cursor.fetchall()
                if active_connections:
                    logging.warning(f"Active connections: {len(active_connections)}")
                    for conn in active_connections:
                        logging.warning(f"Active connection: {conn}")
                return active_connections
        except Exception as e:
            logging.error(f"Error checking active connections: {e}")
            return []

    def get_pool_stats(self):
        return {
            'min': self._connection_pool.minconn,
            'max': self._connection_pool.maxconn,
            'used': len(self._connection_pool._used),
            'idle': len(self._connection_pool._idle)
        }
