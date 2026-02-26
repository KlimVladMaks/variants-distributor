import random
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
    format_students_by_flows,
)
from ..database import crud
from ..database.models import Student, Variant
from ..google_sheets.gs_export import export_to_google_sheets
from ..google_sheets.gs_import import (
    get_students_data_from_google_sheets,
    get_variants_data_from_google_sheets,
)


router = Router()


# ============================
# ===== TEACHER HANDLERS =====
# ============================


# Авторизация
@router.message(StateFilter(TS.auth_st))
async def teacher_auth(message: Message, 
                       state: FSMContext, 
                       is_init=False):
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
            await crud.add_teacher_chat_id(message.chat.id)
            await state.set_state(TS.main_menu_st)
            await teacher_main_menu(message, state, is_init=True)
        
        else:
            await message.answer(
                "Неверный пароль. " \
                "Попробуйте ввести верный пароль или вернитесь назад."
            )


# Главное меню
@router.message(StateFilter(TS.main_menu_st))
async def teacher_main_menu(message: Message, 
                            state: FSMContext, 
                            is_init=False):
    if is_init:
        await message.answer(
            "Главное меню преподавателя. Выберите интересующий вас раздел:",
            reply_markup=TK.main_menu_kb()
        )
    
    elif message.text == BT.UPDATE:
        await state.set_state(TS.confirm_update_data_st)
        await teacher_confirm_update_data(message, state, is_init=True)
    
    elif message.text == BT.VIEW:
        await message.answer("Текущие данные в БД:")

        students = await crud.get_all_students_with_flows()
        await message.answer("👨‍🎓 Список студентов по потокам:")
        if not students:
            await message.answer("Нет студентов.")
        else:
            await message.answer(f"Всего студентов: {len(students)}")
            students_by_flows = format_students_by_flows(students)
            for flow, students_str in students_by_flows:
                await message.answer(flow + ":")
                await message.answer(students_str)
        
        variants = await crud.get_all_variants()
        await message.answer("📄 Список вариантов:")
        if not variants:
            await message.answer("Нет вариантов.")
        else:
            await message.answer(f"Всего вариантов: {len(variants)}")
            for number, title, description in variants:
                await message.answer(f"№{number}. {title}\n\n{description}")
        
        await teacher_main_menu(message, state, is_init=True)
    
    elif message.text == BT.EXPORT:
        msg = await message.answer("Экспорт в Google Таблицу...")
        try:
            await export_to_google_sheets()
        except Exception as e:
            await msg.edit_text(
                "Не удалось совершить экспорт в Google Таблицу. " \
                "Попробуйте позже. Возврат в главное меню."
            )
        else:
            await msg.edit_text(
                "Данные успешно экспортированы в Google Таблицу."
            )
        await teacher_main_menu(message, state, is_init=True)

    else:
        await message.answer(
            "Команда не распознана. Выберите интересующий вас раздел:",
            reply_markup=TK.main_menu_kb()
        )


# Подтверждение обновления данных
@router.message(StateFilter(TS.confirm_update_data_st))
async def teacher_confirm_update_data(message: Message, 
                                      state: FSMContext, 
                                      is_init=False):
    if is_init:
        msg = await message.answer("Импорт данных из Google Таблицы...")

        try:
            students_data = get_students_data_from_google_sheets()
            variants_data = get_variants_data_from_google_sheets()
        except:
            msg.edit_text("Не удалось совершить импорт из Google Таблицы. Попробуйте позже.")
            await state.set_state(TS.main_menu_st)
            await teacher_main_menu(message, state, is_init=True)
            return

        await msg.edit_text("Данные из Google Таблицы загружены.")
        await message.answer("В БД будут внесены следующие обновления:")
        students_update_info = await crud.get_update_students_info(students_data)
        variants_update_info = await crud.get_update_variants_info(variants_data)

        if students_update_info:
            for info in students_update_info:
                await message.answer(info)
            await state.update_data({FSMKeys.STUDENTS_DATA: students_data})
        else:
            await message.answer("Нет обновлений для студентов.")
        
        if variants_update_info:
            for info in variants_update_info:
                await message.answer(info)
            await state.update_data({FSMKeys.VARIANTS_DATA: variants_data})
        else:
            await message.answer("Нет обновлений для вариантов.")
        
        if students_update_info or variants_update_info:
            await message.answer(
                "Сохранить данные обновления?",
                reply_markup=CK.yes_or_no_kb()
            )
        else:
            await message.answer("Обновлений не найдено.")
            await state.set_state(TS.main_menu_st)
            await teacher_main_menu(message, state, is_init=True)
    
    elif message.text == BT.NO:
        await state.update_data({FSMKeys.STUDENTS_DATA: None})
        await state.update_data({FSMKeys.VARIANTS_DATA: None})
        await message.answer("Отмена обновлений. Возврат в главное меню.")
        await state.set_state(TS.main_menu_st)
        await teacher_main_menu(message, state, is_init=True)
    
    elif message.text == BT.YES:
        students = (await state.get_data()).get(FSMKeys.STUDENTS_DATA)
        variants = (await state.get_data()).get(FSMKeys.VARIANTS_DATA)
        if students:
            await crud.update_students(students)
        if variants:
            await crud.update_variants(variants)
        await message.answer("Обновления сохранены. Возврат в главное меню.")
        await state.set_state(TS.main_menu_st)
        await teacher_main_menu(message, state, is_init=True)
    
    else:
        await message.answer(
            "Не удалось распознать команду. Сохранить данные обновления?",
            reply_markup=CK.yes_or_no_kb()
        )


# =============================
# ===== STUDENTS HANDLERS =====
# =============================


# Авторизация студента
@router.message(StateFilter(SS.auth_st))
async def student_auth(message: Message, 
                       state: FSMContext, 
                       is_init=False):
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
        student: Student = await crud.get_student_by_isu(isu)
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
        await state.update_data({FSMKeys.STUDENT: None})
        await crud.update_student_chat_id(student.isu, message.chat.id)
        await message.answer(f"Здравствуйте, {student.full_name}!")
        await student_main_menu_router(message, state)


# Роутер для распределения между главными меню
async def student_main_menu_router(message: Message, state: FSMContext):
    student = await crud.get_student_by_chat_id(message.chat.id)
    if student.distribution:
        await state.set_state(SS.main_menu_with_variant_st)
        await student_main_menu_with_variant(message, state, is_init=True)
    else:
        await state.set_state(SS.main_menu_without_variant_st)
        await student_main_menu_without_variant(message, state, is_init=True)


# Главное меню (для студента без варианта)
@router.message(StateFilter(SS.main_menu_without_variant_st))
async def student_main_menu_without_variant(message: Message, 
                                            state: FSMContext, 
                                            is_init=False):
    if is_init:
        student = await crud.get_student_by_chat_id(message.chat.id)
        await message.answer(
            f"Главное меню.\n\n" \
            f"{student.isu}, {student.full_name}, {student.flow.title}\n\n" \
            f"Вы пока ещё не выбрали вариант.\n\n" \
            f"Выберите интересующий вас раздел:",
            reply_markup=SK.main_menu_without_variant_kb()
        )
    
    elif message.text == BT.CHOOSE_VARIANT:
        await state.set_state(SS.update_variant_st)
        await student_update_variant(message, state, is_init=True)
    
    elif message.text == BT.VIEW_VARIANTS:
        await message.answer("Список всех вариантов:")
        unavailable, available = await crud.get_variants_info_for_student(message.chat.id)
        if unavailable:
            await message.answer("Полностью занятые варианты:")
            for _, _, msg in unavailable:
                await message.answer(msg)
        if available:
            await message.answer("Свободные варианты:")
            for _, _, msg in available:
                await message.answer(msg)
        await student_main_menu_without_variant(message, state, is_init=True)

    else:
        await message.answer(
            "Не удалось распознать команду. Выберите интересующий вас раздел:"
        )


# Главное меню (для студента с вариантом)
@router.message(StateFilter(SS.main_menu_with_variant_st))
async def student_main_menu_with_variant(message: Message, 
                                         state: FSMContext, 
                                         is_init=False):
    if is_init:
        student = await crud.get_student_by_chat_id(message.chat.id)
        await message.answer(
            f"Главное меню.\n\n" \
            f"{student.isu}, {student.full_name}, {student.flow.title}\n\n" \
            f"Ваш текущий вариант:"
        )
        student = await crud.get_student_by_chat_id(message.chat.id)
        if student.distribution.variant is None:
            await message.answer("Свой вариант")
        else:
            variant = student.distribution.variant
            await message.answer(
                f"№{variant.number}\n\n{variant.title}\n\n{variant.description}",
            )
        await message.answer(
            "Выберите интересующий вас раздел:",
            reply_markup=SK.main_menu_with_variant_kb()
        )
    
    elif message.text == BT.CHANGE_VARIANT:
        await state.set_state(SS.update_variant_st)
        await student_update_variant(message, state, is_init=True)
    
    elif message.text == BT.VIEW_VARIANTS:
        await message.answer("Список всех вариантов:")
        unavailable, available = await crud.get_variants_info_for_student(message.chat.id)
        if unavailable:
            await message.answer("Полностью занятые варианты:")
            for _, _, msg in unavailable:
                await message.answer(msg)
        if available:
            await message.answer("Свободные варианты:")
            for _, _, msg in available:
                await message.answer(msg)
        await student_main_menu_with_variant(message, state, is_init=True)
    
    elif message.text == BT.RESET_VARIANT:
        await state.set_state(SS.reset_variant_st)
        await student_reset_variant(message, state, is_init=True)
    
    else:
        await message.answer(
            "Не удалось распознать команду. Выберите интересующий вас раздел:"
        )


# Сброс варианта
@router.message(StateFilter(SS.reset_variant_st))
async def student_reset_variant(message: Message, 
                                state: FSMContext, 
                                is_init=False):
    if is_init:
        await message.answer(
            "Вы уверены, что хотите сбросить свой текущий вариант?",
            reply_markup=CK.yes_or_no_kb()
        )
    
    elif message.text == BT.NO:
        await message.answer("Отмена сброса варианта.")
        await state.set_state(SS.main_menu_with_variant_st)
        await student_main_menu_with_variant(message, state, is_init=True)
    
    elif message.text == BT.YES:
        await crud.update_student_variant(message.chat.id, variant_number=None)
        await message.answer("Ваш вариант был успешно сброшен.")
        await state.set_state(SS.main_menu_without_variant_st)
        await student_main_menu_without_variant(message, state, is_init=True)
    
    else:
        await message.answer("Не удалось распознать команду.")
        await student_reset_variant(message, state, is_init=True)


# Выбор варианта
@router.message(StateFilter(SS.update_variant_st))
async def student_update_variant(message: Message, 
                                 state: FSMContext, 
                                 is_init=False):
    if is_init:
        unavailable, available = await crud.get_variants_info_for_student(message.chat.id)
        available_variants_dict: dict[int, Variant] = {}
        unavailable_variants_dict: dict[int, Variant] = {}

        student = await crud.get_student_by_chat_id(message.chat.id)
        if student.distribution:
            await message.answer("Ваш текущий вариант:")
            if student.distribution.variant is None:
                await message.answer("Свой вариант.")
            else:
                variant: Variant = student.distribution.variant
                await message.answer(
                    f"№{variant.number}\n\n{variant.title}\n\n{variant.description}",
                )

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
            'Введите номер свободного варианта или выберите опцию "Свой вариант":',
            reply_markup=SK.update_variant_kb()
        )
    
    elif message.text == BT.CANCEL:
        await message.answer("Отмена выбора варианта.")
        await state.update_data({FSMKeys.AVD: None})
        await state.update_data({FSMKeys.UVD: None})
        await state.set_state(SS.main_menu_without_variant_st)
        await student_main_menu_router(message, state)
    
    elif message.text == BT.OWN_VARIANT:
        await state.update_data({FSMKeys.UVD: None})
        await state.update_data({FSMKeys.PVN: -1})
        await state.set_state(SS.confirm_choose_variant_st)
        await student_confirm_update_variant(message, state, is_init=True)

    elif message.text == BT.RANDOM_VARIANT:
        await message.answer("Вам будет предложен случайный вариант из доступных.")
        available_variants_dict = (await state.get_data()).get(FSMKeys.AVD)
        if available_variants_dict:
            variant_number = random.choice(list(available_variants_dict.keys()))
            await state.update_data({FSMKeys.UVD: None})
            await state.update_data({FSMKeys.PVN: variant_number})
            await state.set_state(SS.confirm_choose_variant_st)
            await student_confirm_update_variant(message, state, is_init=True)
        else:
            await message.answer("Нет доступных вариантов.")

    elif message.text.isdigit():
        available_variants_dict = (await state.get_data()).get(FSMKeys.AVD)
        unavailable_variants_dict = (await state.get_data()).get(FSMKeys.UVD)
        variant_number = int(message.text)

        if available_variants_dict and available_variants_dict.get(variant_number):
            await state.update_data({FSMKeys.UVD: None})
            await state.update_data({FSMKeys.PVN: variant_number})
            await state.set_state(SS.confirm_choose_variant_st)
            await student_confirm_update_variant(message, state, is_init=True)
        
        elif unavailable_variants_dict and unavailable_variants_dict.get(variant_number):
            await message.answer(
                'Данный вариант уже полностью занят. ' \
                'Введите номер свободного варианта или выберите опцию "Свой вариант":',
                reply_markup=SK.update_variant_kb()
            )
        
        else:
            await message.answer(
                'Не удалось найти вариант с данным номером. ' \
                'Введите номер свободного варианта или выберите опцию "Свой вариант":',
                reply_markup=SK.update_variant_kb()
            )

    else:
        await message.answer(
            'Не удалось распознать ввод. ' \
            'Введите номер свободного варианта или выберите опцию "Свой вариант":',
            reply_markup=CK.cancel_kb()
        )
    

# Подтверждение выбора варианта
@router.message(StateFilter(SS.confirm_choose_variant_st))
async def student_confirm_update_variant(message: Message, 
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
        await state.set_state(SS.update_variant_st)
        await student_update_variant(message, state, is_init=True)
    
    elif message.text == BT.CONFIRM:
        result = await crud.update_student_variant(message.chat.id, variant_number)
        await state.update_data({FSMKeys.AVD: None})
        await state.update_data({FSMKeys.PVN: None})
        if result == 0:
            await message.answer(
                "Вы успешно выбрали данный вариант. Переход в главное меню."
            )
            await state.set_state(SS.main_menu_with_variant_st)
            await student_main_menu_with_variant(message, state, is_init=True)
        else:
            await message.answer(
                "Извините, но похоже, что лимит для данного варианта уже достигнут. " \
                "Попробуйте выбрать другой вариант."
            )
            await state.set_state(SS.update_variant_st)
            await student_update_variant(message, state, is_init=True)

        
    else:
        await message.answer(
            "Команда не распознана. Подтвердите выбор варианта."
        )


# ===========================
# ===== COMMON HANDLERS =====
# ===========================


# Выбор роли
@router.message(StateFilter(CS.choosing_role_st))
async def choosing_role(message: Message, 
                        state: FSMContext, 
                        is_init=False):
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


# Роутер по-умолчанию
@router.message()
async def default_router(message: Message, state: FSMContext):
    chat_id = message.chat.id
    is_teacher = await crud.is_teacher_chat_id(chat_id)
    if is_teacher:
        await message.answer(
            f"Здравствуйте! Похоже, бот был перезапущен. " \
            f"Вы будете перенаправлены в главное меню."
        )
        await state.set_state(TS.main_menu_st)
        await teacher_main_menu(message, state, is_init=True)
        return
    student = await crud.get_student_by_chat_id(chat_id)
    if student:
        await message.answer(
            f"Здравствуйте, {student.full_name}! Похоже, бот был перезапущен. " \
            f"Вы будете перенаправлены в главное меню."
        )
        await student_main_menu_router(message, state)
    else:
        await state.set_state(CS.choosing_role_st)
        await choosing_role(message, state, is_init=True)
