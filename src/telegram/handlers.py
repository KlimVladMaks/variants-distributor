from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, Document
from aiogram.fsm.context import FSMContext

from .keyboards import (
    CommonKeyboards as CK,
    TeacherKeyboards as TK,
)
from .constants import (
    ButtonText as BT,
    FSMKeys
)
from .states import Common, Teacher
from ..config import TG_TEACHER_PASSWORD
from .utils import (
    parse_students_csv,
    parse_variants_csv,
    format_students_by_flows,
)
from ..database.crud import (
    get_all_students_with_flows,
    get_update_students_info,
    update_students,
    save_variants,
    get_all_variants,

)


router = Router()


# ============================
# ===== TEACHER HANDLERS =====
# ============================


# Авторизация
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
                "Попробуйте ввести верный пароль или вернитесь назад."
            )


# Главное меню
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
            "Вы вышли из роли преподавателя."
        )
        await state.set_state(Common.choosing_role_st)
        await choosing_role(message, state, is_init=True)
    
    elif message.text == BT.STUDENTS_AND_FLOWS:
        await state.set_state(Teacher.students_menu_st)
        await teacher_students_menu(message, state, is_init=True)
    
    elif message.text == BT.VARIANTS:
        await state.set_state(Teacher.variants_menu_st)
        await teacher_variants_menu(message, state, is_init=True)

    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.main_menu_kb()
        )


# Студенты и потоки
@router.message(StateFilter(Teacher.students_menu_st))
async def teacher_students_menu(message: Message, 
                                state: FSMContext, 
                                is_init=False):
    """Меню преподавателя 'Студенты и потоки'"""
    if is_init:
        await message.answer(
            "Студенты и потоки. Выберите интересующий вас раздел:",
            reply_markup=TK.students_menu_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(Teacher.main_menu_st)
        await teacher_main_menu(message, state, is_init=True)

    elif message.text == BT.UPDATE_STUDENTS:
        await state.set_state(Teacher.update_students_menu_st)
        await teacher_update_students_menu(message, state, is_init=True)
    
    elif message.text == BT.VIEW_STUDENTS:
        students = await get_all_students_with_flows()
        if not students:
            await message.answer("Нет студентов.")
        else:
            await message.answer(
                "Список студентов по потокам:"
            )
            students_by_flows = format_students_by_flows(students)
            for flow, students_str in students_by_flows:
                await message.answer(flow + ":")
                await message.answer(students_str)
        await state.set_state(Teacher.students_menu_st)
        await teacher_students_menu(message, state, is_init=True)
    
    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.students_menu_kb()
        )

# Обновление списка студентов
@router.message(StateFilter(Teacher.update_students_menu_st))
async def teacher_update_students_menu(message: Message, 
                                       state: FSMContext, 
                                       is_init=False):
    if is_init:
        await message.answer(
            "Обновление списка студентов. Выберите способ обновления:",
            reply_markup=TK.update_students_menu_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(Teacher.students_menu_st)
        await teacher_students_menu(message, state, is_init=True)
    
    elif message.text == BT.CSV:
        await state.set_state(Teacher.update_students_via_csv_st)
        await teacher_update_students_via_csv(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await teacher_update_students_menu(message, state, is_init=True)


# Обновить список студентов через CSV
@router.message(StateFilter(Teacher.update_students_via_csv_st))
async def teacher_update_students_via_csv(message: Message, 
                                          state: FSMContext, 
                                          is_init=False):
    if is_init:
        await message.answer(
            "Обновление списка студентов через CSV. " \
            "Загрузите обновлённый список студентов в формате CSV-файла:",
            reply_markup=CK.cancel_kb()
        )
    
    elif message.text == BT.CANCEL:
        await state.set_state(Teacher.update_students_menu_st)
        await teacher_update_students_menu(message, state, is_init=True)
    
    elif message.document:
        status_message = await message.answer("Обработка файла...")
        document: Document = message.document
        file = await message.bot.get_file(document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        students = parse_students_csv(file_content.read())
        await status_message.edit_text("Файл обработан.")
        await state.update_data({FSMKeys.STUDENTS: students})
        await state.set_state(Teacher.confirm_update_students_via_csv_st)
        await confirm_update_students_via_csv(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await teacher_update_students_via_csv(message, state, is_init=True)


# Подтверждение обновления списка студентов через CSV
@router.message(StateFilter(Teacher.confirm_update_students_via_csv_st))
async def confirm_update_students_via_csv(message: Message, 
                                          state: FSMContext, 
                                          is_init=False):
    students = (await state.get_data())[FSMKeys.STUDENTS]

    if is_init:
        update_students_info = await get_update_students_info(students)
        if not update_students_info:
            await message.answer("Обновлений не найдено.")
            await state.set_state(Teacher.update_students_menu_st)
            await teacher_update_students_menu(message, state, is_init=True)
        else:
            await message.answer("Будут внесены следующие обновления:")
            for info in update_students_info:
                await message.answer(info)
            await message.answer(
                "Сохранить обновления?",
                reply_markup=CK.yes_or_no_kb()
            )
    
    elif message.text == BT.NO:
        await state.update_data({FSMKeys.STUDENTS: None})
        await message.answer("Отмена обновления данных.")
        await state.set_state(Teacher.update_students_menu_st)
        await teacher_update_students_menu(message, state, is_init=True)
    
    elif message.text == BT.YES:
        await update_students(students)
        await state.update_data({FSMKeys.STUDENTS: None})
        await message.answer(
            "Обновления сохранены."
        )
        await state.set_state(Teacher.update_students_menu_st)
        await teacher_update_students_menu(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await message.answer(
            "Сохранить обновления?",
            reply_markup=CK.yes_or_no_kb()
        )


# Варианты
@router.message(StateFilter(Teacher.variants_menu_st))
async def teacher_variants_menu(message: Message, 
                                state: FSMContext, 
                                is_init=False):
    if is_init:
        await message.answer(
            "Варианты. Выберите интересующий вас раздел:",
            reply_markup=TK.variants_menu_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(Teacher.main_menu_st)
        await teacher_main_menu(message, state, is_init=True)
    
    elif message.text == BT.UPDATE_VARIANTS:
        await state.set_state(Teacher.add_variants_menu_st)
        await teacher_add_variants_menu(message, state, is_init=True)
    
    elif message.text == BT.VIEW_VARIANTS:
        await message.answer("Список вариантов:")
        variants = await get_all_variants()
        for number, title, description in variants:
            await message.answer(
                str(number) + "\n\n" + title + "\n\n" + description
            )
        await teacher_variants_menu(message, state, is_init=True)

    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.variants_menu_kb()
        )


# Добавить варианты
@router.message(StateFilter(Teacher.add_variants_menu_st))
async def teacher_add_variants_menu(message: Message, 
                                    state: FSMContext, 
                                    is_init=False):
    if is_init:
        await message.answer(
            "Добавление вариантов. Выберите способ добавления:",
            reply_markup=TK.add_variants_menu_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(Teacher.variants_menu_st)
        await teacher_variants_menu(message, state, is_init=True)
    
    elif message.text == BT.CSV:
        await state.set_state(Teacher.add_variants_via_csv_st)
        await teacher_add_variants_via_csv(message, state, is_init=True)
    
    else:
        await message.answer(
            "Команда не распознана. Выберите способ добавления вариантов:",
            reply_markup=TK.add_variants_menu_kb()
        )


# Добавить варианты через CSV
@router.message(StateFilter(Teacher.add_variants_via_csv_st))
async def teacher_add_variants_via_csv(message: Message, 
                                       state: FSMContext, 
                                       is_init=False):
    if is_init:
        await message.answer(
            "Загрузите CSV-файл с вариантами:",
            reply_markup=CK.cancel_kb()
        )
    
    elif message.text == BT.CANCEL:
        await state.set_state(Teacher.add_variants_menu_st)
        await teacher_add_variants_menu(message, state, is_init=True)
    
    elif message.document:
        status_message = await message.answer("Обработка файла...")
        document: Document = message.document
        file = await message.bot.get_file(document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        variants = parse_variants_csv(file_content.read())
        await status_message.edit_text("Файл обработан.")
        await state.update_data({
            FSMKeys.VARIANTS: variants
        })
        await state.set_state(Teacher.confirm_variants_csv_input_st)
        await teacher_confirm_variants_csv_input(message, 
                                                 state,  
                                                 is_init=True)
    
    else:
        await message.answer(
            "Команда не распознана. Загрузите CSV-файл:",
            reply_markup=CK.cancel_kb()
        )


# Подтвердить добавление вариантов через CSV
@router.message(StateFilter(Teacher.confirm_variants_csv_input_st))
async def teacher_confirm_variants_csv_input(message: Message, 
                                             state: FSMContext, 
                                             is_init=False):
    variants = (await state.get_data())[FSMKeys.VARIANTS]

    if is_init:
        await message.answer(
            "Удалось распознать следующие варианты:"
        )
        for number, title, description in variants:
            await message.answer(
                str(number) + "\n\n" + title + "\n\n" + description
            )
        await message.answer(
            "Сохранить?",
            reply_markup=CK.yes_or_no_kb()
        )
    
    elif message.text == BT.NO:
        await message.answer(
            "Отмена сохранения."
        )
        await state.update_data({FSMKeys.VARIANTS: None})
        await state.set_state(Teacher.add_variants_menu_st)
        await teacher_add_variants_menu(message, state, is_init=True)
    
    elif message.text == BT.YES:
        await save_variants(variants)
        await state.update_data({FSMKeys.VARIANTS: None})
        await message.answer("Данные сохранены.")
        await state.set_state(Teacher.add_variants_menu_st)
        await teacher_add_variants_menu(message, state, is_init=True)

    else:
        await message.answer(
            "Команда не распознана. Сохранить?",
            reply_markup=CK.yes_or_no_kb()
        )


# ===========================
# ===== COMMON HANDLERS =====
# ===========================


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
            "Данный раздел находится в разработке. Выберите другую роль:"
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
