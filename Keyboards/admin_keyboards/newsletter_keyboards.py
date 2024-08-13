from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from Database.Admin_db import Database

db = Database()



def newsletter_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Сделать рассылку', callback_data='create_newsletter'))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='main_menu_admin'))

    return builder


def cancel_create_newsletter():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='newsletter'))

    return builder


def send_newsletter_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚀 ОТПРАВИТЬ', callback_data='send_newsletter'))
    builder.row(InlineKeyboardButton(text='♻️ ДРУГОЕ СООБЩЕНИЕ', callback_data='create_newsletter'))
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='newsletter'))

    return builder


def return_newsletter():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='newsletter'))

    return builder