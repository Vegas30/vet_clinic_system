# database_mongodb_connector.py
import logging
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from threading import Lock

class MongoDBConnector:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MongoDBConnector, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv()
        self.connection_string = os.getenv("MONGO_URL")
        self.database_name = os.getenv("MONGO_DB_NAME")
        self.collection_name = os.getenv("MONGO_COLLECTION_NAME")
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        if self.client is None:
            try:
                self.client = MongoClient(self.connection_string)
                self.db = self.client[self.database_name]
                self.collection = self.db[self.collection_name]
                print("Успешное подключение к MongoDB")
                return True
            except Exception as e:
                print(f"Ошибка подключения к MongoDB: {e}")
                return False
        return True

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Отключение от MongoDB")
        self.client = None
        self.db = None
        self.collection = None

    def get_collection(self):
        if self.client is None:
            self.connect()
        return self.collection

    def get_database(self):
        if self.client is None:
            self.connect()
        return self.db

    def get_client(self):
        if self.client is None:
            self.connect()
        return self.client

    def get_connection(self):
        try:
            conn = self._connection_pool.getconn()
            logging.debug(
                f"Got connection from pool (current: {len(self._connection_pool._used)} used, {len(self._connection_pool._idle)} idle)")
            return conn
        except Exception as e:
            logging.error(f"Error getting connection: {e}")
            raise

    def put_connection(self, conn):
        try:
            self._connection_pool.putconn(conn)
            logging.debug(
                f"Returned connection to pool (current: {len(self._connection_pool._used)} used, {len(self._connection_pool._idle)} idle)")
        except Exception as e:
            logging.error(f"Error returning connection: {e}")
            if conn:
                conn.close()
