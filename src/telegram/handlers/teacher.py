from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..states import Common, Teacher
from ..keyboards import (
    back_keyboard, 
    role_keyboard, 
    teacher_main_keyboard, 
    remove_keyboard,
)
from ...config import TG_TEACHER_PASSWORD


router = Router()


@router.message(StateFilter(Common.choosing_role), F.text == "Преподаватель")
async def teacher_start(message: Message, state: FSMContext):
    """Начало авторизации преподавателя"""
    await state.set_state(Teacher.waiting_for_password)
    await message.answer(
        "Введите пароль:",
        reply_markup=back_keyboard()
    )


@router.message(StateFilter(Teacher.waiting_for_password), F.text == "Назад")
async def back_from_password(message: Message, state: FSMContext):
    """Возврат к выбору роли из ввода пароля"""
    await state.set_state(Common.choosing_role)
    await message.answer(
        "Выберите вашу роль:",
        reply_markup=role_keyboard()
    )


@router.message(StateFilter(Teacher.waiting_for_password))
async def check_password(message: Message, state: FSMContext):
    """Проверка пароля"""
    password = message.text

    if password == TG_TEACHER_PASSWORD:
        await state.set_state(Teacher.main_menu)
        await message.answer(
            "Добро пожаловать в главное меню! " \
            "Выберите интересующий вас раздел:",
            reply_markup=teacher_main_keyboard()
        )
    
    else:
        await message.answer(
            "Неверный пароль. " \
            "Попробуйте ввести верный пароль или вернитесь назад.",
            reply_markup=back_keyboard()
        )


@router.message(StateFilter(Teacher.main_menu), F.text == "Выход")
async def teacher_logout(message: Message, state: FSMContext):
    """Выход из режима преподавателя"""
    await state.set_state(Common.choosing_role)
    await message.answer(
        "Вы вышли из режима преподавателя. Выберите вашу роль:",
        reply_markup=remove_keyboard
    )
