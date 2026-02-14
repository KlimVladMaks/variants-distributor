from aiogram.fsm.state import State, StatesGroup


class Common(StatesGroup):
    """Общие состояния (используются до выбора пользователем роли)"""
    choosing_role_st = State()


class Teacher(StatesGroup):
    """Состояния пользователя с ролью 'Преподаватель'"""
    auth_st = State()
    main_menu_st = State()
    students_menu_st = State()
    add_students_menu_st = State()
    add_students_via_csv_st = State()
    confirm_students_csv_input_st = State()
    variants_menu_st = State()
    add_variants_menu_st = State()
    add_variants_via_csv_st = State()
    confirm_variants_csv_input_st = State()
