# database_models_mongo.py
from database.database_mongodb_connector import MongoDBConnector
from bson.objectid import ObjectId
from datetime import datetime
import uuid


class MongoDBModels:
    def __init__(self):
        self.db = MongoDBConnector()
        self.db.connect()
        self.collection = self.db.get_collection()

    def create_animal(self, animal_data):
        """
        Создание новой карточки животного

        :param animal_data: словарь с данными животного
        :return: ObjectId созданного документа или None
        """
        try:
            # Генерируем UUID если не предоставлен
            if '_id' not in animal_data:
                animal_data['_id'] = str(uuid.uuid4())

            # Добавляем timestamp создания
            animal_data['created_at'] = datetime.now()

            result = self.collection.insert_one(animal_data)
            print(f"Создано животное с ID: {result.inserted_id}")
            return animal_data['_id']
        except Exception as e:
            print(f"Ошибка при создании животного: {e}")
            return None

    def get_animal_by_id(self, animal_id):
        """
        Получение животного по ID

        :param animal_id: строковый ID животного
        :return: документ животного или None
        """
        try:
            animal = self.collection.find_one({'_id': animal_id})
            return animal
        except Exception as e:
            print(f"Ошибка при получении животного по ID: {e}")
            return None

    def update_animal(self, animal_id, update_data):
        """
        Обновление данных животного

        :param animal_id: строковый ID животного
        :param update_data: словарь с обновляемыми полями
        :return: количество измененных документов
        """
        try:
            # Добавляем timestamp обновления
            update_data['updated_at'] = datetime.now()

            result = self.collection.update_one(
                {'_id': animal_id},
                {'$set': update_data}
            )
            print(f"Обновлено {result.modified_count} документов")
            return result.modified_count
        except Exception as e:
            print(f"Ошибка при обновлении животного: {e}")
            return 0

    def delete_animal(self, animal_id):
        """
        Удаление животного по ID

        :param animal_id: строковый ID животного
        :return: количество удаленных документов
        """
        try:
            result = self.collection.delete_one({'_id': animal_id})
            print(f"Удалено {result.deleted_count} документов")
            return result.deleted_count
        except Exception as e:
            print(f"Ошибка при удалении животного: {e}")
            return 0

    def search_animals(self, search_criteria):
        """
        Поиск животных по критериям

        :param search_criteria: словарь с критериями поиска
        :return: список найденных животных
        """
        try:
            animals = list(self.collection.find(search_criteria))
            return animals
        except Exception as e:
            print(f"Ошибка при поиске животных: {e}")
            return []

    def add_medical_record(self, animal_id, record_data):
        """
        Добавление медицинской записи в историю животного

        :param animal_id: строковый ID животного
        :param record_data: словарь с данными записи
        :return: обновленный документ животного или None
        """
        try:
            # Убедимся, что есть дата
            if 'date' not in record_data:
                record_data['date'] = datetime.now().strftime("%Y-%m-%d")

            result = self.collection.update_one(
                {'_id': animal_id},
                {'$push': {'medical_history': record_data}}
            )
            if result.modified_count > 0:
                return self.get_animal_by_id(animal_id)
            return None
        except Exception as e:
            print(f"Ошибка при добавлении медицинской записи: {e}")
            return None

    def update_medical_record(self, animal_id, record_index, update_data):
        """
        Обновление медицинской записи

        :param animal_id: строковый ID животного
        :param record_index: индекс записи в массиве medical_history
        :param update_data: словарь с обновляемыми полями
        :return: обновленный документ животного или None
        """
        try:
            update_query = {}
            for key, value in update_data.items():
                update_query[f'medical_history.{record_index}.{key}'] = value

            result = self.collection.update_one(
                {'_id': animal_id},
                {'$set': update_query}
            )
            if result.modified_count > 0:
                return self.get_animal_by_id(animal_id)
            return None
        except Exception as e:
            print(f"Ошибка при обновлении медицинской записи: {e}")
            return None

    def get_animals_by_diagnosis(self, diagnosis):
        """
        Поиск животных по диагнозу в медицинской истории

        :param diagnosis: строка с диагнозом для поиска
        :return: список животных с указанным диагнозом
        """
        try:
            animals = list(self.collection.find({
                'medical_history.diagnosis': diagnosis
            }))
            return animals
        except Exception as e:
            print(f"Ошибка при поиске животных по диагнозу: {e}")
            return []

    def get_all_animals(self):
        """
        Получение всех животных

        :return: список всех животных
        """
        try:
            animals = list(self.collection.find())
            return animals
        except Exception as e:
            print(f"Ошибка при получении всех животных: {e}")
            return []

    def get_all_diagnoses(self):
        """Получает список уникальных диагнозов"""
        try:
            pipeline = [
                {"$unwind": "$medical_history"},
                {"$group": {"_id": "$medical_history.diagnosis"}},
                {"$sort": {"_id": 1}}
            ]
            diagnoses = self.collection.aggregate(pipeline)
            return [d['_id'] for d in diagnoses if d['_id']]
        except Exception as e:
            print(f"Ошибка при получении диагнозов: {e}")
            return []

    def get_animals_by_diagnosis(self, diagnosis):
        """Получает животных с указанным диагнозом"""
        try:
            animals = self.collection.find({
                "medical_history.diagnosis": diagnosis
            })
            return list(animals)
        except Exception as e:
            print(f"Ошибка при поиске животных по диагнозу: {e}")
            return []

