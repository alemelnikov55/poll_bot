from aiogram.fsm.state import State, StatesGroup


class RandomStates(StatesGroup):
    GET_USERS = State()
