#  logic_calendar_utils.py
from PyQt6.QtCore import QDate, QTime
import logging
from datetime import datetime


class CalendarUtils:
    WORKING_HOURS = {
        'start': QTime(9, 0),
        'end': QTime(18, 0),
        'slot_duration': 30  # минуты
    }

    @staticmethod
    def get_available_slots(vet_id, date, db_connection):
        """Возвращает список доступных временных слотов для врача на указанную дату"""
        try:
            # Преобразуем date в строку, если это QDate
            date_str = date.toString('yyyy-MM-dd') if isinstance(date, QDate) else date

            booked_slots = db_connection.get_appointments_by_date(
                date_str,
                vet_id=vet_id
            )
            booked_times = {QTime.fromString(appt[4].strftime('%H:%M'), '%H:%M') for appt in booked_slots}

            available_slots = []
            current_time = CalendarUtils.WORKING_HOURS['start']

            while current_time <= CalendarUtils.WORKING_HOURS['end']:
                if current_time not in booked_times:
                    available_slots.append(current_time.toString('HH:mm'))
                current_time = current_time.addSecs(CalendarUtils.WORKING_HOURS['slot_duration'] * 60)

            return available_slots
        except Exception as e:
            logging.error(f"Ошибка при получении слотов: {str(e)}")
            return []

    @staticmethod
    def validate_appointment_time(vet_id, date, time, db_connection, exclude_id=None):
        """Проверяет, доступно ли время для записи"""
        try:
            # Преобразуем дату и время в строки
            date_str = date.toString('yyyy-MM-dd') if isinstance(date, QDate) else date
            time_str = time.toString('HH:mm') if isinstance(time, QTime) else time

            return not db_connection.check_vet_availability(
                vet_id,
                date_str,
                time_str,
                exclude_id
            )
        except Exception as e:
            logging.error(f"Ошибка валидации времени: {str(e)}")
            return False

    @staticmethod
    def get_next_available_time():
        """Возвращает ближайшее доступное время (округлённое до 30 минут)"""
        now = datetime.now()
        current_time = QTime(now.hour, now.minute)

        if not CalendarUtils.is_within_working_hours(current_time):
            return CalendarUtils.WORKING_HOURS['start']

        if now.minute < 30:
            return QTime(now.hour, 30)
        return QTime(now.hour + 1 if now.hour < 23 else 23, 0)

    @staticmethod
    def is_working_day(date):
        """Проверяет, является ли день рабочим"""
        if isinstance(date, str):
            date = QDate.fromString(date, 'yyyy-MM-dd')
        return date.dayOfWeek() not in (6, 7)

    @staticmethod
    def is_within_working_hours(time):
        """Проверяет, попадает ли время в рабочие часы (9:00-18:00)"""
        if isinstance(time, str):
            time = QTime.fromString(time, 'HH:mm')
        return (CalendarUtils.WORKING_HOURS['start'] <= time <=
                CalendarUtils.WORKING_HOURS['end'])

    @staticmethod
    def is_past_time(date, time):
        """Проверяет, является ли время в прошлом относительно текущего момента"""
        current_datetime = datetime.now()
        try:
            if isinstance(date, QDate):
                selected_datetime = datetime(
                    date.year(), date.month(), date.day(),
                    time.hour(), time.minute()
                )
            else:
                # Если date уже datetime или строка
                selected_datetime = date if isinstance(date, datetime) else datetime.strptime(date, '%Y-%m-%d')
                selected_datetime = selected_datetime.replace(hour=time.hour(), minute=time.minute())

            return selected_datetime < current_datetime
        except Exception as e:
            logging.error(f"Ошибка в is_past_time: {str(e)}")
            return True  # В случае ошибки считаем время прошедшим

    @staticmethod
    def validate_appointment_datetime(date, time, is_admin=False):
        """Проверяет корректность даты и времени приёма"""
        # Проверка рабочего времени (9:00-18:00)
        if not CalendarUtils.is_within_working_hours(time):
            return False, "Запись возможна только с 9:00 до 18:00"

        # Проверка на прошедшее время (если не админ)
        if not is_admin and CalendarUtils.is_past_time(date, time):
            return False, "Нельзя записать на прошедшее время"

        return True, ""
