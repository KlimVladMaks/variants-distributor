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
    ADD_STUDENTS = "Добавить студентов"
    DEL_STUDENTS = "Удалить студентов"
