# database_mongodb_connector.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

class MongoDBConnector:
    def __init__(self):
        load_dotenv()
        self.connection_string = os.getenv("MONGO_URL")
        self.database_name = os.getenv("MONGO_DB_NAME")
        self.collection_name = os.getenv("MONGO_COLLECTION_NAME")
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print("Успешное подключение к MongoDB")
            return True
        except Exception as e:
            print(f"Ошибка подключения к MongoDB: {e}")
            return False

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Отключение от MongoDB")
        self.client = None
        self.db = None
        self.collection = None

    def get_collection(self):
        return self.collection

    def get_database(self):
        return self.db

    def get_client(self):
        return self.client