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
    students_list_to_str,
    unique_flows_to_str,
)
from ..database.crud import (
    get_all_students_with_flows,
    save_students,
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

    elif message.text == BT.ADD_STUDENTS:
        await state.set_state(Teacher.add_students_menu_st)
        await teacher_add_students_menu(message, state, is_init=True)
    
    elif message.text == BT.STUDENTS_LIST:
        students = await get_all_students_with_flows()
        await message.answer(
            "Список студентов:"
        )
        await message.answer(
            students_list_to_str(students)
        )
        await state.set_state(Teacher.students_menu_st)
        await teacher_students_menu(message, state, is_init=True)
    
    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.students_menu_kb()
        )


# Добавить студентов
@router.message(StateFilter(Teacher.add_students_menu_st))
async def teacher_add_students_menu(message: Message, 
                                    state: FSMContext, 
                                    is_init=False):
    """Меню преподавателя 'Добавить студентов'"""
    if is_init:
        await message.answer(
            "Добавление студентов. Выберите способ добавления:",
            reply_markup=TK.add_students_menu_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(Teacher.students_menu_st)
        await teacher_students_menu(message, state, is_init=True)
    
    elif message.text == BT.CSV:
        await state.set_state(Teacher.add_students_via_csv_st)
        await teacher_add_students_via_csv(message, state, is_init=True)

    else:
        await message.answer(
            "Команда не распознана. Как вы хотите добавить студентов?",
            reply_markup=TK.add_students_menu_kb()
        )


# Добавить студентов через CSV
@router.message(StateFilter(Teacher.add_students_via_csv_st))
async def teacher_add_students_via_csv(message: Message, 
                                       state: FSMContext, 
                                       is_init=False):
    """Добавление студентов через CSV"""
    if is_init:
        await message.answer(
            "Добавление студентов через CSV-файл. " \
            "Загрузите CSV-файл со студентами:",
            reply_markup=CK.cancel_kb()
        )
    
    elif message.text == BT.CANCEL:
        await state.set_state(Teacher.add_students_menu_st)
        await teacher_add_students_menu(message, state, is_init=True)
    
    elif message.document:
        status_message = await message.answer("Обработка файла...")
        document: Document = message.document
        file = await message.bot.get_file(document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        students = parse_students_csv(file_content.read())
        await status_message.edit_text("Файл обработан.")
        await state.update_data({
            FSMKeys.STUDENTS: students
        })
        await state.set_state(Teacher.confirm_students_csv_input_st)
        await teacher_confirm_students_csv_input(message, 
                                                 state,  
                                                 is_init=True)
        
    else:
        await message.answer(
            "Ввод не распознан. " \
            "Загрузите CSV-файл со студентами или отмените операцию.",
            reply_markup=CK.cancel_kb()
        )


# Подтвердить добавление студентов через CSV
@router.message(StateFilter(Teacher.confirm_students_csv_input_st))
async def teacher_confirm_students_csv_input(message: Message, 
                                             state: FSMContext,
                                             is_init=False):
    """Подтверждение ввода студентов из CSV-файла"""
    students = (await state.get_data())[FSMKeys.STUDENTS]

    if is_init:
        await message.answer(
            "Удалось распознать следующих студентов:"
        )
        await message.answer(
            students_list_to_str(students)
        )
        await message.answer(
            "Удалось распознать следующие потоки:"
        )
        await message.answer(
            unique_flows_to_str(students)
        )
        await message.answer(
            "Сохранить?",
            reply_markup=CK.yes_or_no_kb()
        )
    
    elif message.text == BT.NO:
        await state.update_data({
            FSMKeys.STUDENTS: None
        })
        await message.answer(
            "Отмена сохранения данных из CSV-файла."
        )
        await state.set_state(Teacher.add_students_menu_st)
        await teacher_add_students_menu(message, state, is_init=True)
    
    elif message.text == BT.YES:
        await save_students(students)
        await state.update_data({
            FSMKeys.STUDENTS: None
        })
        await message.answer(
            "Данные сохранены."
        )
        await state.set_state(Teacher.add_students_menu_st)
        await teacher_add_students_menu(message, state, is_init=True)

    else:
        await message.answer(
            "Команда не распознана. Сохранить?",
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
    
    elif message.text == BT.ADD_VARIANTS:
        await state.set_state(Teacher.add_variants_menu_st)
        await teacher_add_variants_menu(message, state, is_init=True)
    
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
    
    else:
        await message.answer(
            "Команда не распознана. Загрузите CSV-файл:",
            reply_markup=CK.cancel_kb()
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
