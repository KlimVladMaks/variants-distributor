from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, Document
from aiogram.fsm.context import FSMContext

from .keyboards import (
    CommonKeyboards as CK,
    TeacherKeyboards as TK,
    StudentKeyboards as SK,
)
from .constants import (
    ButtonText as BT,
    FSMKeys
)
from .states import (
    Common as CS, 
    Teacher as TS, 
    Student as SS,
)
from ..config import TG_TEACHER_PASSWORD
from .utils import (
    parse_students_csv,
    parse_variants_csv,
    format_students_by_flows,
)
from ..database.crud import (
    get_all_students_with_flows,
    get_update_students_info,
    get_update_variants_info,
    update_students,
    update_variants,
    get_all_variants,
    get_student_by_isu,
    get_student_variant_number,
    get_variants_info_for_student,
    update_student_variant,
    get_variant_by_number,
)
from ..database.models import Student, Variant


router = Router()


# ============================
# ===== TEACHER HANDLERS =====
# ============================


# Авторизация
@router.message(StateFilter(TS.auth_st))
async def teacher_auth(message: Message, state: FSMContext, is_init=False):
    """Авторизация преподавателя"""
    if is_init:
        await message.answer(
            "Введите пароль:",
            reply_markup=CK.back_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(CS.choosing_role_st)
        await choosing_role(message, state, is_init=True)
    
    else:
        password = message.text

        if password == TG_TEACHER_PASSWORD:
            await state.set_state(TS.main_menu_st)
            await teacher_main_menu(message, state, is_init=True)
        
        else:
            await message.answer(
                "Неверный пароль. " \
                "Попробуйте ввести верный пароль или вернитесь назад."
            )


# Главное меню
@router.message(StateFilter(TS.main_menu_st))
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
        await state.set_state(CS.choosing_role_st)
        await choosing_role(message, state, is_init=True)
    
    elif message.text == BT.STUDENTS_AND_FLOWS:
        await state.set_state(TS.students_menu_st)
        await teacher_students_menu(message, state, is_init=True)
    
    elif message.text == BT.VARIANTS:
        await state.set_state(TS.variants_menu_st)
        await teacher_variants_menu(message, state, is_init=True)

    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.main_menu_kb()
        )


# ===== Студенты и потоки =====


# Студенты и потоки
@router.message(StateFilter(TS.students_menu_st))
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
        await state.set_state(TS.main_menu_st)
        await teacher_main_menu(message, state, is_init=True)

    elif message.text == BT.UPDATE_STUDENTS:
        await state.set_state(TS.update_students_menu_st)
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
        await teacher_students_menu(message, state, is_init=True)
    
    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.students_menu_kb()
        )

# Обновление списка студентов
@router.message(StateFilter(TS.update_students_menu_st))
async def teacher_update_students_menu(message: Message, 
                                       state: FSMContext, 
                                       is_init=False):
    if is_init:
        await message.answer(
            "Обновление списка студентов. Выберите способ обновления:",
            reply_markup=TK.update_students_menu_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(TS.students_menu_st)
        await teacher_students_menu(message, state, is_init=True)
    
    elif message.text == BT.CSV:
        await state.set_state(TS.update_students_via_csv_st)
        await teacher_update_students_via_csv(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await teacher_update_students_menu(message, state, is_init=True)


# Обновить список студентов через CSV
@router.message(StateFilter(TS.update_students_via_csv_st))
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
        await state.set_state(TS.update_students_menu_st)
        await teacher_update_students_menu(message, state, is_init=True)
    
    elif message.document:
        status_message = await message.answer("Обработка файла...")
        document: Document = message.document
        file = await message.bot.get_file(document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        students = parse_students_csv(file_content.read())
        await status_message.edit_text("Файл обработан.")
        await state.update_data({FSMKeys.STUDENTS: students})
        await state.set_state(TS.confirm_update_students_via_csv_st)
        await teacher_confirm_update_students_via_csv(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await teacher_update_students_via_csv(message, state, is_init=True)


# Подтверждение обновления списка студентов через CSV
@router.message(StateFilter(TS.confirm_update_students_via_csv_st))
async def teacher_confirm_update_students_via_csv(message: Message, 
                                                  state: FSMContext, 
                                                  is_init=False):
    students = (await state.get_data())[FSMKeys.STUDENTS]

    if is_init:
        update_students_info = await get_update_students_info(students)
        if not update_students_info:
            await message.answer("Обновлений не найдено.")
            await state.set_state(TS.update_students_menu_st)
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
        await state.set_state(TS.update_students_menu_st)
        await teacher_update_students_menu(message, state, is_init=True)
    
    elif message.text == BT.YES:
        await update_students(students)
        await state.update_data({FSMKeys.STUDENTS: None})
        await message.answer("Обновления сохранены.")
        await state.set_state(TS.update_students_menu_st)
        await teacher_update_students_menu(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await message.answer(
            "Сохранить обновления?",
            reply_markup=CK.yes_or_no_kb()
        )


# ===== Варианты =====


# Варианты
@router.message(StateFilter(TS.variants_menu_st))
async def teacher_variants_menu(message: Message, 
                                state: FSMContext, 
                                is_init=False):
    if is_init:
        await message.answer(
            "Варианты. Выберите интересующий вас раздел:",
            reply_markup=TK.variants_menu_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(TS.main_menu_st)
        await teacher_main_menu(message, state, is_init=True)
    
    elif message.text == BT.UPDATE_VARIANTS:
        await state.set_state(TS.update_variants_menu_st)
        await teacher_update_variants_menu(message, state, is_init=True)
    
    elif message.text == BT.VIEW_VARIANTS:
        await message.answer("Список вариантов:")
        variants = await get_all_variants()
        if not variants:
            await message.answer("Нет вариантов")
        else:
            for number, title, description in variants:
                await message.answer(f"№{number}. {title}\n\n{description}")
        await teacher_variants_menu(message, state, is_init=True)

    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.variants_menu_kb()
        )


# Обновить список вариантов
@router.message(StateFilter(TS.update_variants_menu_st))
async def teacher_update_variants_menu(message: Message, 
                                       state: FSMContext, 
                                       is_init=False):
    if is_init:
        await message.answer(
            "Обновление вариантов. Выберите способ обновления:",
            reply_markup=TK.update_variants_menu_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(TS.variants_menu_st)
        await teacher_variants_menu(message, state, is_init=True)
    
    elif message.text == BT.CSV:
        await state.set_state(TS.update_variants_via_csv_st)
        await teacher_update_variants_via_csv(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await teacher_update_variants_menu(message, state, is_init=True)


# Обновить список вариантов через CSV
@router.message(StateFilter(TS.update_variants_via_csv_st))
async def teacher_update_variants_via_csv(message: Message, 
                                          state: FSMContext, 
                                          is_init=False):
    if is_init:
        await message.answer(
            "Обновление списка вариантов через CSV. " \
            "Загрузите обновлённый список вариантов в формате CSV-файла:",
            reply_markup=CK.cancel_kb()
        )
    
    elif message.document:
        status_message = await message.answer("Обработка файла...")
        document: Document = message.document
        file = await message.bot.get_file(document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        variants = parse_variants_csv(file_content.read())
        await status_message.edit_text("Файл обработан.")
        await state.update_data({FSMKeys.VARIANTS: variants})
        await state.set_state(TS.confirm_update_variants_via_csv_st)
        await teacher_confirm_update_variants_via_csv(message, 
                                                      state,  
                                                      is_init=True)

    else:
        await message.answer("Команда не распознана.")
        await teacher_update_variants_via_csv(message, state, is_init=True)


# Подтвердить обновление списка вариантов через CSV
@router.message(StateFilter(TS.confirm_update_variants_via_csv_st))
async def teacher_confirm_update_variants_via_csv(message: Message, 
                                                  state: FSMContext, 
                                                  is_init=False):
    variants = (await state.get_data())[FSMKeys.VARIANTS]

    if is_init:
        update_variants_info = await get_update_variants_info(variants)
        if not update_variants_info:
            await message.answer("Обновлений не найдено.")
            await state.set_state(TS.update_variants_menu_st)
            await teacher_update_variants_menu(message, state, is_init=True)
        else:
            await message.answer("Будут внесены следующие обновления:")
            for info in update_variants_info:
                await message.answer(info)
            await message.answer(
                "Сохранить обновления?",
                reply_markup=CK.yes_or_no_kb()
            )
    
    elif message.text == BT.NO:
        await state.update_data({FSMKeys.VARIANTS: None})
        await message.answer("Отмена обновления данных.")
        await state.set_state(TS.update_variants_menu_st)
        await teacher_update_variants_menu(message, state, is_init=True)
    
    elif message.text == BT.YES:
        await update_variants(variants)
        await state.update_data({FSMKeys.VARIANTS: None})
        await message.answer("Обновления сохранены.")
        await state.set_state(TS.update_variants_menu_st)
        await teacher_update_variants_menu(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await message.answer(
            "Сохранить обновления?",
            reply_markup=CK.yes_or_no_kb()
        )


# =============================
# ===== STUDENTS HANDLERS =====
# =============================


# Авторизация студента
@router.message(StateFilter(SS.auth_st))
async def student_auth(message: Message, state: FSMContext, is_init=False):
    if is_init:
        await message.answer(
            "Введите ваш табельный номер (6 цифр):",
            reply_markup=CK.back_kb()
        )
    
    elif message.text == BT.BACK:
        await state.set_state(CS.choosing_role_st)
        await choosing_role(message, state, is_init=True)
    
    else:
        isu = message.text
        student: Student = await get_student_by_isu(isu)
        if not student:
            await message.answer(
                "Не удалось найти студента с данным табельным номером. " \
                "Повторите попытку или вернитесь назад."
            )
        else:
            await state.update_data({FSMKeys.STUDENT: student})
            await state.set_state(SS.confirm_auth_st)
            await student_confirm_auth(message, state, is_init=True)


# Подтверждение авторизации студента
@router.message(StateFilter(SS.confirm_auth_st))
async def student_confirm_auth(message: Message, 
                               state: FSMContext, 
                               is_init=False):
    if is_init:
        student: Student = (await state.get_data())[FSMKeys.STUDENT]
        await message.answer(
            f"Это ваши данные?\n\n" \
            f"{student.isu}, {student.full_name}, {student.flow.title}",
            reply_markup=CK.yes_or_no_kb()
        )
    
    elif message.text == BT.NO:
        await state.update_data({FSMKeys.STUDENT: None})
        await message.answer("Возврат к вводу табельного номера.")
        await state.set_state(SS.auth_st)
        await student_auth(message, state, is_init=True)
    
    elif message.text == BT.YES:
        student: Student = (await state.get_data())[FSMKeys.STUDENT]
        variant_number = await get_student_variant_number(student.isu)
        await message.answer(f"Здравствуйте, {student.full_name}!")
        await state.update_data({FSMKeys.STUDENT: None})
        await state.update_data({FSMKeys.ISU: student.isu})
        await state.update_data({FSMKeys.VARIANT_NUMBER: variant_number})
        await student_main_menu_router(message, state)


async def student_main_menu_router(message: Message, state: FSMContext):
    variant_number = (await state.get_data()).get(FSMKeys.VARIANT_NUMBER)
    if variant_number:
        await state.set_state(SS.main_menu_with_variant_st)
        await student_main_menu_with_variant(message, state, is_init=True)
    else:
        await state.set_state(SS.main_menu_without_variant_st)
        await student_main_menu_without_variant(message, state, is_init=True)


@router.message(StateFilter(SS.main_menu_without_variant_st))
async def student_main_menu_without_variant(message: Message, 
                                            state: FSMContext, 
                                            is_init=False):
    if is_init:
        await message.answer(
            "Главное меню.\n\nВы пока ещё выбрали вариант.\n\n" \
            "Выберите интересующий вас раздел:",
            reply_markup=SK.main_menu_without_variant_kb()
        )
    
    elif message.text == BT.EXIT:
        await message.answer("Выход из аккаунта студента.")
        await state.clear()
        await state.set_state(CS.choosing_role_st)
        await choosing_role(message, state, is_init=True)
    
    elif message.text == BT.CHOOSE_VARIANT:
        await state.set_state(SS.choose_variant_st)
        await student_choose_variant(message, state, is_init=True)

    else:
        await message.answer(
            "Не удалось распознать команду. Выберите интересующий вас раздел:"
        )


@router.message(StateFilter(SS.main_menu_with_variant_st))
async def student_main_menu_with_variant(message: Message, 
                                         state: FSMContext, 
                                         is_init=False):
    if is_init:
        await message.answer("Главное меню. Ваш текущий вариант:")
        variant_number = (await state.get_data())[FSMKeys.VARIANT_NUMBER]
        if variant_number == -1:
            await message.answer("Свой вариант")
        else:
            variant = await get_variant_by_number(variant_number)
            await message.answer(
                f"№{variant.number}\n\n{variant.title}\n\n{variant.description}",
            )
        await message.answer(
            "Выберите интересующий вас раздел:",
            reply_markup=SK.main_menu_with_variant_kb()
        )
    
    elif message.text == BT.EXIT:
        await message.answer("Выход из аккаунта студента.")
        await state.clear()
        await state.set_state(CS.choosing_role_st)
        await choosing_role(message, state, is_init=True)
    
    else:
        await message.answer(
            "Не удалось распознать команду. Выберите интересующий вас раздел:"
        )


@router.message(StateFilter(SS.choose_variant_st))
async def student_choose_variant(message: Message, 
                                 state: FSMContext, 
                                 is_init=False):
    if is_init:
        isu = (await state.get_data())[FSMKeys.ISU]
        unavailable, available = await get_variants_info_for_student(isu)
        available_variants_dict: dict[int, Variant] = {}
        unavailable_variants_dict: dict[int, Variant] = {}

        await message.answer("Выбор вариантов.")

        if unavailable:
            await message.answer("Полностью занятые варианты:")
            for number, variant, msg in unavailable:
                unavailable_variants_dict[number] = variant
                await message.answer(msg)
            await state.update_data({FSMKeys.UVD: unavailable_variants_dict})
        
        if available:
            await message.answer("Свободные варианты:")
            for number, variant, msg in available:
                available_variants_dict[number] = variant
                await message.answer(msg)
            await state.update_data({FSMKeys.AVD: available_variants_dict})
        
        await message.answer(
            'Введите номер свободного варианта или опцию "Свой вариант":',
            reply_markup=SK.choose_variant_kb()
        )
    
    elif message.text == BT.CANCEL:
        await message.answer("Отмена выбора варианта.")
        await state.update_data({FSMKeys.AVD: None})
        await state.update_data({FSMKeys.UVD: None})
        await state.set_state(SS.main_menu_without_variant_st)
        await student_main_menu_without_variant(message, state, is_init=True)
    
    elif message.text == BT.OWN_VARIANT:
        await state.update_data({FSMKeys.UVD: None})
        await state.update_data({FSMKeys.PVN: -1})
        await state.set_state(SS.confirm_choose_variant_st)
        await student_confirm_choose_variant(message, state, is_init=True)

    elif message.text.isdigit():
        available_variants_dict = (await state.get_data()).get(FSMKeys.AVD)
        unavailable_variants_dict = (await state.get_data()).get(FSMKeys.UVD)
        variant_number = int(message.text)

        if available_variants_dict and available_variants_dict.get(variant_number):
            await state.update_data({FSMKeys.UVD: None})
            await state.update_data({FSMKeys.PVN: variant_number})
            await state.set_state(SS.confirm_choose_variant_st)
            await student_confirm_choose_variant(message, state, is_init=True)
        
        elif unavailable_variants_dict and unavailable_variants_dict.get(variant_number):
            await message.answer(
                "Данный вариант уже полностью занят. " \
                "Введите номер свободного варианта:",
                reply_markup=CK.cancel_kb()
            )
        
        else:
            await message.answer(
                "Не удалось найти вариант с данным номером. " \
                "Введите номер свободного варианта:",
                reply_markup=CK.cancel_kb()
            )

    else:
        await message.answer("Не удалось распознать ввод.")
        await message.answer(
            "Введите номер свободного варианта, чтобы выбрать его:",
            reply_markup=CK.cancel_kb()
        )
    

@router.message(StateFilter(SS.confirm_choose_variant_st))
async def student_confirm_choose_variant(message: Message, 
                                         state: FSMContext, 
                                         is_init=False):
    variant_number = (await state.get_data())[FSMKeys.PVN]
    available_variants_dict = (await state.get_data())[FSMKeys.AVD]
    
    if is_init:
        await message.answer("Подтвердите выбор варианта:")
        if variant_number == -1:
            await message.answer(
                "Свой вариант.",
                reply_markup=CK.confirm_kb()
            )
        else:
            variant: Variant = available_variants_dict[variant_number]
            await message.answer(
                f"№{variant.number}\n\n{variant.title}\n\n{variant.description}",
                reply_markup=CK.confirm_kb()
            )
    
    elif message.text == BT.CANCEL:
        await message.answer(
            "Выбор данного варианта был отменён. Выберите другой вариант."
        )
        await state.update_data({FSMKeys.AVD: None})
        await state.update_data({FSMKeys.PVN: None})
        await state.set_state(SS.choose_variant_st)
        await student_choose_variant(message, state, is_init=True)
    
    elif message.text == BT.CONFIRM:
        isu = (await state.get_data())[FSMKeys.ISU]
        result = await update_student_variant(isu, variant_number)
        if result == 0:
            await state.update_data({FSMKeys.VARIANT_NUMBER: variant_number})
            await state.update_data({FSMKeys.AVD: None})
            await state.update_data({FSMKeys.PVN: None})
            await message.answer(
                "Вы успешно выбрали данный вариант. Переход в главное меню."
            )
            await state.set_state(SS.main_menu_with_variant_st)
            await student_main_menu_with_variant(message, state, is_init=True)

    else:
        await message.state(
            "Команда не распознана. Подтвердите выбор варианта."
        )


# ===========================
# ===== COMMON HANDLERS =====
# ===========================


@router.message(StateFilter(CS.choosing_role_st))
async def choosing_role(message: Message, state: FSMContext, is_init=False):
    """Раздел с выбором роли пользователя"""
    if is_init:
        await message.answer(
            "Здравствуйте! Выберите вашу роль:",
            reply_markup=CK.choosing_role_kb()
        )
    
    elif message.text == BT.TEACHER:
        await state.set_state(TS.auth_st)
        await teacher_auth(message, state, is_init=True)
    
    elif message.text == BT.STUDENT:
        await state.set_state(SS.auth_st)
        await student_auth(message, state, is_init=True)
    
    else:
        await message.answer(
            "Не удалось распознать роль. Выберите доступную вам роль:",
            reply_markup=CK.choosing_role_kb()
        )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.set_state(CS.choosing_role_st)
    await choosing_role(message, state, is_init=True)


@router.message()
async def something_wrong(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Похоже что-то пошло не так. " \
        "Нажмите на /start чтобы перезапустить бота.",
        reply_markup=CK.start_kb()
    )
