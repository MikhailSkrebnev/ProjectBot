from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from Database.Admin_db import Database

db = Database()




def statistics_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='СТАТИСТИКА ПО ТОВАРАМ', callback_data='products_statistics'))
    builder.row(InlineKeyboardButton(text='СТАТИСТИКА ПО ПОКУПАТЕЛЯМ', callback_data='statistics_on_customers'))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='main_menu_admin'))

    return builder


def back_to_statistics():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='statistics'))

    return builder