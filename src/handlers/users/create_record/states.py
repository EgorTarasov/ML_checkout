from aiogram.dispatcher.filters.state import State, StatesGroup


class StudentForm(StatesGroup):
    auth = State()
    teacher = State()
    queue = State()
