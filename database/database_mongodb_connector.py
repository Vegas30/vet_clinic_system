# Подключение к MongoDB
from pymongo import MongoClient

def get_mongo_connection():
    # TODO: Реализовать подключение к базе MongoDB
    """Подключение к MongoDB"""
    try:
        # Подключение к MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["vet_clinic_mDB"]
        return db
    except Exception as e:
        print(f"Ошибка подключения к MongoDB: {e}")
        return None