from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..keyboards import role_keyboard
from ..states import Common

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.set_state(Common.choosing_role)
    await message.answer(
        "Привет! Выберите вашу роль:",
        reply_markup=role_keyboard()
    )


