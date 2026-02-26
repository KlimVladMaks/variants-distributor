from dataclasses import dataclass


@dataclass(frozen=True)
class ButtonText:
    """Тексты кнопок"""
    STUDENT = "Студент"
    TEACHER = "Преподаватель"
    BACK = "Назад"
    EXIT = "Выход"
    CANCEL = "Отмена"
    YES = "Да"
    NO = "Нет"
    CHOOSE_VARIANT = "Выбрать вариант"
    CONFIRM = "Подтвердить"
    OWN_VARIANT = "Свой вариант"
    VIEW_VARIANTS = "Посмотреть варианты"
    CHANGE_VARIANT = "Выбрать другой вариант"
    RESET_VARIANT = "Сбросить вариант"
    EXPORT = "Экспорт"
    RANDOM_VARIANT = "Случайный вариант"
    GOOGLE_SHEETS = "Google Таблицы"
    UPDATE = "Обновить"
    VIEW = "Посмотреть"


@dataclass(frozen=True)
class FSMKeys:
    """Ключи для хранения данных в FSM"""
    STUDENTS = "students"
    VARIANTS = "variants"
    STUDENT = "student"
    PVN = "potential_variant_number"
    AVD = "available_variants_dict"
    UVD = "unavailable_variants_dict"
    STUDENTS_DATA = "students_data"
    VARIANTS_DATA = "variants_data"
