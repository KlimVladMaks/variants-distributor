from aiogram.fsm.state import State, StatesGroup


class Common(StatesGroup):
    """Общие состояния (используются до выбора пользователем роли)"""
    choosing_role_st = State()


class Teacher(StatesGroup):
    """Состояния пользователя с ролью 'Преподаватель'"""
    auth_st = State()
    main_menu_st = State()

    # ===== Студенты и потоки =====

    students_menu_st = State()
    update_students_menu_st = State()
    update_students_via_csv_st = State()
    confirm_update_students_via_csv_st = State()

    # ===== Варианты =====

    variants_menu_st = State()
    update_variants_menu_st = State()
    update_variants_via_csv_st = State()
    confirm_update_variants_via_csv_st = State()


class Student(StatesGroup):
    auth_st = State()
    confirm_auth_st = State()
    main_menu_without_variant_st = State()
    update_variant_st = State()
    confirm_choose_variant_st = State()
    main_menu_with_variant_st = State()
    reset_variant_st = State()
