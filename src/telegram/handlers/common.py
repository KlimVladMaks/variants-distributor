from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..keyboards import role_keyboard
from ..states import Common
from .teacher import router as teacher_router


router = Router()
router.include_router(teacher_router)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.set_state(Common.choosing_role)
    await message.answer(
        "Здравствуйте! Выберите вашу роль:",
        reply_markup=role_keyboard()
    )


@router.message(StateFilter(Common.choosing_role))
async def unknown_role(message: Message, state: FSMContext):
    await message.answer(
        "Не удалось распознать роль. Выберите доступную вам роль:",
        reply_markup=role_keyboard()
    )


@router.message()
async def something_wrong(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Похоже что-то пошло не так. Введите /start чтобы перезапустить бота.",
        reply_markup=role_keyboard()
    )
