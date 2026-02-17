from dataclasses import dataclass


@dataclass(frozen=True)
class ButtonText:
    """Неизменяемый класс с текстами кнопок"""
    STUDENT = "Студент"
    TEACHER = "Преподаватель"
    BACK = "Назад"
    STUDENTS_AND_FLOWS = "Студенты и потоки"
    VARIANTS = "Варианты"
    STATS = "Статистика"
    EXIT = "Выход"
    UPDATE_STUDENTS = "Обновить список студентов"
    CSV = "CSV"
    MANUALLY = "Вручную"
    START = "/start"
    CANCEL = "Отмена"
    YES = "Да"
    NO = "Нет"
    VIEW_STUDENTS = "Посмотреть список студентов"
    UPDATE_VARIANTS = "Обновить список вариантов"
    VIEW_VARIANTS = "Посмотреть список вариантов"
    CHOOSE_VARIANT = "Выбрать вариант"
    CONFIRM = "Подтвердить"
    OWN_VARIANT = "Свой вариант"


@dataclass(frozen=True)
class FSMKeys:
    """Ключи для хранения данных в state"""
    STUDENTS = "students"
    VARIANTS = "variants"
    STUDENT = "student"
    ISU = "isu"
    VARIANT_NUMBER = "variant_number"
    PVN = "potential_variant_number"
    AVD = "available_variants_dict"
    UVD = "unavailable_variants_dict"
