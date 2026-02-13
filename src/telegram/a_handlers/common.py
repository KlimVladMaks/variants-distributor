from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..keyboards import CommonKeyboards as CK
from ..button_text import ButtonText as BT
from ..states import Common


router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.set_state(Common.choosing_role_st)
    await choosing_role(message, state)


@router.message(StateFilter(Common.choosing_role_st))
async def choosing_role(message: Message, state: FSMContext):
    """Раздел с выбором роли пользователя"""
    if message.text == "/start":
        await message.answer(
            "Здравствуйте! Выберите вашу роль:",
            reply_markup=CK.choosing_role_kb()
        )
    
    elif message.text == BT.TEACHER:
        await state.set_state()


'''
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.set_state(Common.choosing_role)
    await message.answer(
        "Здравствуйте! Выберите вашу роль:",
        reply_markup=CK.choosing_role()
    )


@router.message(StateFilter(Common.choosing_role))
async def unknown_role(message: Message, state: FSMContext):
    await message.answer(
        "Не удалось распознать роль. Выберите доступную вам роль:",
        reply_markup=CK.choosing_role()
    )


@router.message()
async def something_wrong(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Похоже что-то пошло не так. " \
        "Нажмите на /start чтобы перезапустить бота.",
        reply_markup=CK.start()
    )
'''
