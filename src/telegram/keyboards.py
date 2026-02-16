from aiogram.types import (
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
)

from .constants import ButtonText as BT


class CommonKeyboards:
    """Общие клавиатуры"""
    def choosing_role_kb():
        """Выбор роли: 'Студент' или 'Преподаватель'"""
        buttons = [
            [KeyboardButton(text=BT.STUDENT)],
            [KeyboardButton(text=BT.TEACHER)]
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    def back_kb():
        """Кнопка 'Назад'"""
        buttons = [[KeyboardButton(text=BT.BACK)]]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    def cancel_kb():
        """Кнопка 'Отмена'"""
        buttons = [[KeyboardButton(text=BT.CANCEL)]]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )
    
    def start_kb():
        """Кнопка 'start'"""
        buttons = [[KeyboardButton(text=BT.START)]]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )
    
    def yes_or_no_kb():
        """Клавиатура Да или Нет"""
        buttons = [
            [KeyboardButton(text=BT.YES)],
            [KeyboardButton(text=BT.NO)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )


class TeacherKeyboards:
    """Клавиатуры для раздела 'Преподаватель'"""
    def main_menu_kb():
        """Главное меню"""
        buttons = [
            [KeyboardButton(text=BT.STUDENTS_AND_FLOWS)],
            [KeyboardButton(text=BT.VARIANTS)],
            [KeyboardButton(text=BT.STATS)],
            [KeyboardButton(text=BT.EXIT)]
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    def students_menu_kb():
        """Раздел со студентами и потоками"""
        buttons = [
            [KeyboardButton(text=BT.UPDATE_STUDENTS)],
            [KeyboardButton(text=BT.VIEW_STUDENTS)],
            [KeyboardButton(text=BT.BACK)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    def update_students_menu_kb():
        buttons = [
            [KeyboardButton(text=BT.CSV)],
            [KeyboardButton(text=BT.BACK)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    def variants_menu_kb():
        buttons = [
            [KeyboardButton(text=BT.UPDATE_VARIANTS)],
            [KeyboardButton(text=BT.VIEW_VARIANTS)],
            [KeyboardButton(text=BT.BACK)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    def update_variants_menu_kb():
        buttons = [
            [KeyboardButton(text=BT.CSV)],
            [KeyboardButton(text=BT.BACK)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )


class StudentKeyboards:
    """Клавиатуры для раздела 'Студент'"""
    def main_menu_without_variant_kb():
        buttons = [
            [KeyboardButton(text=BT.CHOOSE_VARIANT)],
            [KeyboardButton(text=BT.EXIT)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )


# Для удаления клавиатуры
remove_keyboard = ReplyKeyboardRemove()
