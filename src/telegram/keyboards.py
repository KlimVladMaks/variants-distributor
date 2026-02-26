from aiogram.types import (
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
)

from .constants import ButtonText as BT


class CommonKeyboards:
    """Общие клавиатуры"""
    @staticmethod
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

    @staticmethod
    def back_kb():
        """Кнопка 'Назад'"""
        buttons = [[KeyboardButton(text=BT.BACK)]]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    @staticmethod
    def cancel_kb():
        """Кнопка 'Отмена'"""
        buttons = [[KeyboardButton(text=BT.CANCEL)]]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )
    
    @staticmethod
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

    @staticmethod
    def confirm_kb():
        buttons = [
            [KeyboardButton(text=BT.CONFIRM)],
            [KeyboardButton(text=BT.CANCEL)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )


class TeacherKeyboards:
    """Клавиатуры для раздела 'Преподаватель'"""
    @staticmethod
    def main_menu_kb():
        """Главное меню"""
        buttons = [
            [KeyboardButton(text=BT.UPDATE)],
            [KeyboardButton(text=BT.VIEW)],
            [KeyboardButton(text=BT.EXPORT)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )


class StudentKeyboards:
    """Клавиатуры для раздела 'Студент'"""
    @staticmethod
    def main_menu_without_variant_kb():
        buttons = [
            [KeyboardButton(text=BT.CHOOSE_VARIANT)],
            [KeyboardButton(text=BT.VIEW_VARIANTS)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    @staticmethod
    def main_menu_with_variant_kb():
        buttons = [
            [KeyboardButton(text=BT.CHANGE_VARIANT)],
            [KeyboardButton(text=BT.RESET_VARIANT)],
            [KeyboardButton(text=BT.VIEW_VARIANTS)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

    @staticmethod
    def update_variant_kb():
        buttons = [
            [KeyboardButton(text=BT.OWN_VARIANT)],
            [KeyboardButton(text=BT.RANDOM_VARIANT)],
            [KeyboardButton(text=BT.CANCEL)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )


# Для удаления клавиатуры
remove_keyboard = ReplyKeyboardRemove()
