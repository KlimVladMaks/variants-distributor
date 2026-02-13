from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..states import Common, Teacher
from ..keyboards import (
    CommonKeyboards as CK,
    TeacherKeyboards as TK,
)
from ..button_text import ButtonText as BT
from ...config import TG_TEACHER_PASSWORD


router = Router()


@router.message(StateFilter(Common.choosing_role_st), F.text == BT.TEACHER)
async def teacher_start(message: Message, state: FSMContext):
    """Начало авторизации преподавателя"""
    await state.set_state(Teacher.password_input_st)
    await message.answer(
        "Введите пароль:",
        reply_markup=CK.back_kb()
    )


@router.message(StateFilter(Teacher.password_input_st), F.text == BT.BACK)
async def back_from_check_password(message: Message, state: FSMContext):
    """Возврат к выбору роли из ввода пароля"""
    await state.set_state(Common.choosing_role_st)
    await message.answer(
        "Выберите вашу роль:",
        reply_markup=CK.choosing_role_kb()
    )


@router.message(StateFilter(Teacher.password_input_st))
async def check_password(message: Message, state: FSMContext):
    """Проверка пароля"""
    password = message.text

    if password == TG_TEACHER_PASSWORD:
        await state.set_state(Teacher.main_menu_st)
        await message.answer(
            "Главное меню. Выберите интересующий вас раздел:",
            reply_markup=TK.main_menu_kb()
        )
    
    else:
        await message.answer(
            "Неверный пароль. " \
            "Попробуйте ввести верный пароль или вернитесь назад.",
            reply_markup=CK.back_kb()
        )


@router.message(StateFilter(Teacher.main_menu_st), F.text == BT.EXIT)
async def teacher_logout(message: Message, state: FSMContext):
    """Выход из режима преподавателя"""
    await state.set_state(Common.choosing_role_st)
    await message.answer(
        "Вы вышли из режима преподавателя. Выберите вашу роль:",
        reply_markup=CK.choosing_role_kb()
    )


@router.message(StateFilter(Teacher.main_menu_st), F.text == BT.STUDENTS_AND_FLOWS)
async def students_menu(message: Message, state: FSMContext):
    """Открытие меню для работы со студентами и потоками"""
    await state.set_state(Teacher.students_menu_st)
    await message.answer(
        "Раздел для работы со студентами и потоками. " \
        "Выберите интересующую вас опцию:",
        reply_markup=TK.students_menu_kb()
    )


@router.message(StateFilter(Teacher.students_menu_st), F.text == BT.BACK)
async def back_from_students_menu(message: Message, state: FSMContext):
    """Возврат в главное меню из раздела 'Студенты и потоки'"""
    await state.set_state(Teacher.main_menu_st)
    await message.answer(
        "Главное меню. Выберите интересующий вас раздел:",
        reply_markup=TK.main_menu_kb()
    )


@router.message(StateFilter(Teacher.students_menu_st), F.text == BT.ADD_STUDENTS)
async def add_students_menu(message: Message, state: FSMContext):
    """Открытие меню у опции добавления студентов"""
    await state.set_state(Teacher.add_students_menu_st)
    await message.answer(
        "Как вы хотите добавить студентов?",
        reply_markup=TK.add_students_menu_kb()
    )
