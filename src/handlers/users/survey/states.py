from aiogram.dispatcher.filters.state import State, StatesGroup


class StudentForm(StatesGroup):
    github = State()
    teacher = State()
    queue = State()
