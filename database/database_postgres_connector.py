# Подключение к PostgreSQL
import psycopg2

def get_pg_connection():
    # TODO: Реализовать подключение к базе PostgreSQL
    """Подключение к PostgreSQL"""
    try:
        # Подключение к PostgreSQL
        # Измените пароль подключения согласно вашим настройкам
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="vet_clinica_pSQL",
            user="postgres",
            password="7773"
        )
        return connection
    except Exception as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
        return None    

