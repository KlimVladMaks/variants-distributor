from aiogram.types import (
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
)

def role_keyboard():
    """Клавиатура выбора роли: 'Студент' или 'Преподаватель'"""
    buttons = [
        [KeyboardButton(text="Студент")],
        [KeyboardButton(text="Преподаватель")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

def back_keyboard():
    """Клавиатура с кнопкой 'Назад'"""
    buttons = [[KeyboardButton(text="Назад")]]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

def teacher_main_keyboard():
    """Главное меню преподавателя"""
    buttons = [
        [KeyboardButton(text="Студенты и потоки")],
        [KeyboardButton(text="Варианты")],
        [KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Выход")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

remove_keyboard = ReplyKeyboardRemove()
