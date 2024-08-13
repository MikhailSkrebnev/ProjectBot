from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from Database.Admin_db import Database

db = Database()





# Основная клавиатура

def start_admin_kb():
    buttons = [
        [KeyboardButton(text='/start'), KeyboardButton(text='/admin')],
        [KeyboardButton(text='🖥 Главная'), KeyboardButton(text='🛍️ Покупки')]
    ]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return kb


def menu_admin_kb():
    buttons = [
        [InlineKeyboardButton(text='📦 ТОВАРЫ', callback_data='products'), InlineKeyboardButton(text='📈 СТАТИСТИКА', callback_data='statistics')],
        [InlineKeyboardButton(text='📤 РАССЫЛКА', callback_data='newsletter'), InlineKeyboardButton(text='💳 ОПЛАТА', callback_data='payment_methods')],
        [InlineKeyboardButton(text='🎨 ДИЗАЙН', callback_data='design')]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb


def method_payments():
    buttons = [
        [InlineKeyboardButton(text='Ручная проверка оплаты', callback_data='manual_payment_method')],
        [InlineKeyboardButton(text='Автоматическая оплата', callback_data='automatic_payment_method')],
        [InlineKeyboardButton(text='👈 НАЗАД', callback_data='main_menu_admin')],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


def cancel_kb():
    button = [
        [KeyboardButton(text='🚫 ОТМЕНА')]
    ]
    kb = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

    return kb

def products_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Подписка на канал', callback_data='products_channel'), InlineKeyboardButton(text='Инфо-товары', callback_data='information_products'), width=2)
    builder.row(InlineKeyboardButton(text='Товары с доставкой', callback_data='delivery_products'))
    builder.row(InlineKeyboardButton(text='🛍️ Витрина', callback_data='groups'))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='main_menu_admin'))

    return builder

