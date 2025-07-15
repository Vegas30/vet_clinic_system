# Операции с MongoDB (животные)
from database.database_mongodb_connector import MongoDBConnector
from uuid import uuid4

class MongoDBModels:
    def __init__(self):
        self.db_connector = MongoDBConnector()
        self.db = self.db_connector.connect()
        self.animals_collection = None
        if self.db is not None:
            self.animals_collection = self.db["animals"]

