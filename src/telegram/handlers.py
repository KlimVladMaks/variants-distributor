from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .keyboards import (
    CommonKeyboards as CK,
    TeacherKeyboards as TK,
    remove_keyboard,
)
from .button_text import ButtonText as BT
from .states import Common, Teacher
from ..config import TG_TEACHER_PASSWORD


router = Router()


# ===== TEACHER HANDLERS =====


@router.message(StateFilter(Teacher.auth_st))
async def teacher_auth(message: Message, state: FSMContext, is_init=False):
    """Авторизация преподавателя"""
    if is_init:
        await message.answer(
            "Введите пароль:",
            reply_markup=CK.back_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(Common.choosing_role_st)
        await choosing_role(message, state, is_init=True)
    
    else:
        password = message.text

        if password == TG_TEACHER_PASSWORD:
            await state.set_state(Teacher.main_menu_st)
            await teacher_main_menu(message, state, is_init=True)
        
        else:
            await message.answer(
                "Неверный пароль. " \
                "Попробуйте ввести верный пароль или вернитесь назад.",
                reply_markup=CK.back_kb()
            )


@router.message(StateFilter(Teacher.main_menu_st))
async def teacher_main_menu(message: Message, state: FSMContext, is_init=False):
    """Главное меню преподавателя"""
    if is_init:
        await message.answer(
            "Главное меню преподавателя. Выберите интересующий вас раздел:",
            reply_markup=TK.main_menu_kb()
        )
    
    elif message.text == BT.EXIT:
        await message.answer(
            "Вы вышли из роли преподавателя.",
            reply_markup=remove_keyboard
        )
        await state.set_state(Common.choosing_role_st)
        await choosing_role(message, state, is_init=True)
    
    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.main_menu_kb()
        )


# ===== COMMON HANDLERS =====


@router.message(StateFilter(Common.choosing_role_st))
async def choosing_role(message: Message, state: FSMContext, is_init=False):
    """Раздел с выбором роли пользователя"""
    if is_init:
        await message.answer(
            "Здравствуйте! Выберите вашу роль:",
            reply_markup=CK.choosing_role_kb()
        )
    
    elif message.text == BT.TEACHER:
        await state.set_state(Teacher.auth_st)
        await teacher_auth(message, state, is_init=True)
    
    elif message.text == BT.STUDENT:
        await message.answer(
            "Данный раздел находится в разработке. Выберите другую роль:",
            reply_markup=CK.choosing_role_kb()
        )
    
    else:
        await message.answer(
            "Не удалось распознать роль. Выберите доступную вам роль:",
            reply_markup=CK.choosing_role_kb()
        )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.set_state(Common.choosing_role_st)
    await choosing_role(message, state, is_init=True)


@router.message()
async def something_wrong(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Похоже что-то пошло не так. " \
        "Нажмите на /start чтобы перезапустить бота.",
        reply_markup=CK.start_kb()
    )
