from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from random import randint






def start_kb():
    buttons = [
        [KeyboardButton(text='🖥 Главная'), KeyboardButton(text='🛍️ Покупки')]
    ]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return kb


def start_admin_kb():
    buttons = [
        [KeyboardButton(text='/start'), KeyboardButton(text='/admin')],
        [KeyboardButton(text='🖥 Главная'), KeyboardButton(text='🛍️ Покупки')]
    ]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return kb