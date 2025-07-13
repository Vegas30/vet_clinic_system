import os
from pymongo import MongoClient
from dotenv import load_dotenv

class MongoDBConnector:
    def __init__(self):
        load_dotenv()
        self.mongo_url = os.getenv("MONGO_URL")
        self.client = None
        self.db = None

    def connect(self):
        if self.client is None or not self.client.admin.command('ping'):
            try:
                self.client = MongoClient(self.mongo_url)
                self.db = self.client.get_database()
                print("Успешное подключение к MongoDB")
            except Exception as e:
                print(f"Ошибка подключения к MongoDB: {e}")
                self.client = None
                self.db = None
        return self.db

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Отключение от MongoDB")
        self.client = None
        self.db = None

    def get_database(self):
        return self.db
