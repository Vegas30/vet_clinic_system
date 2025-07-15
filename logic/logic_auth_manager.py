# # Авторизация и роли
"""
Менеджер аутентификации и авторизации.
Обрабатывает логику входа пользователей и проверку прав доступа
"""
import hashlib
from database.database_models_pg import PostgresModels


class AuthManager:
    def __init__(self):
        self.db = PostgresModels()
        self.current_user = None

    def authenticate(self, login: str, password: str) -> dict or None:
        """
        Аутентификация пользователя

        Параметры:
            login (str): Логин пользователя
            password (str): Пароль пользователя

        Возвращает:
            dict: Данные пользователя при успешной аутентификации
            None: При неудачной аутентификации
        """
        # Получаем пользователя из базы данных
        employee = self.db.get_employee_by_login(login)

        if not employee:
            return None

        # Простая проверка пароля БЕЗ хеширования
        if password != employee[3]:  # 3 - индекс password_hash в кортеже
            return None

        # Формируем данные пользователя
        user_data = {
            'id': employee[0],
            'full_name': employee[1],
            'login': employee[2],
            'role': employee[4],
            'branch_id': employee[5]
        }

        # Логируем вход
        self.db.insert_login_log(user_data['id'], 'вход')

        self.current_user = user_data
        return user_data

    # def _hash_password(self, password: str) -> str:
    #     """
    #     Хеширование пароля с солью
    #
    #     Параметры:
    #         password (str): Пароль в открытом виде
    #
    #     Возвращает:
    #         str: Хеш пароля
    #     """
    #     salt = "vet_clinic_salt"  # Соль для хеширования
    #     return hashlib.sha256((password + salt).encode()).hexdigest()

    # def _check_password(self, input_password: str, stored_hash: str) -> bool:
    #     """
    #     Проверка соответствия пароля хешу
    #
    #     Параметры:
    #         input_password (str): Введенный пароль
    #         stored_hash (str): Хранимый хеш из базы данных
    #
    #     Возвращает:
    #         bool: True если пароль верный, иначе False
    #     """
    #     return self._hash_password(input_password) == stored_hash

    def get_current_user(self) -> dict or None:
        """
        Получение данных текущего пользователя

        Возвращает:
            dict: Данные пользователя если авторизован
            None: Если пользователь не авторизован
        """
        return self.current_user

    def logout(self):
        """Выход пользователя из системы"""
        if self.current_user:
            self.db.insert_login_log(self.current_user['id'], 'выход')
            self.current_user = None

# # TODO: Реализовать менеджер авторизации и ролей пользователей