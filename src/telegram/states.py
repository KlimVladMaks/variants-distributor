from aiogram.fsm.state import State, StatesGroup


class Common(StatesGroup):
    """Общие состояния (используются до выбора пользователем роли)"""
    # Выбор пользователем роли
    choosing_role = State()


class Teacher(StatesGroup):
    """Состояния пользователя с ролью 'Преподаватель'"""
    # Ожидание ввода пароля
    password_input = State()

    # Главное меню
    main_menu = State()

    # Раздел со студентами и потоками
    students_menu = State()

    # Раздел с добавлением студентов
    add_students_menu = State()
