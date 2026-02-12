from aiogram.fsm.state import State, StatesGroup


class Common(StatesGroup):
    """Общие состояния (используются до выбора пользователем роли)"""
    # Выбор пользователем роли
    choosing_role = State()


class Teacher(StatesGroup):
    """Состояния пользователя с ролью 'Преподаватель'"""
    # Ожидание ввода пароля
    waiting_for_password = State()

    # Главное меню
    main_menu = State()

    # Секции (временно)
    sections = State()
