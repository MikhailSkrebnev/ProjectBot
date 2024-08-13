from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from Database.Admin_db import Database

db = Database()



class ListResources(CallbackData, prefix='call'):
    action: str
    resource_id: str

class Paginator(CallbackData, prefix='call'):
    array_name: str
    button: str
    page: str
    max_pages: str




def list_resources(bot_username, page):
    builder = InlineKeyboardBuilder()

    resources = db.get_list_resources(bot_username=bot_username)
    items_per_page = 20
    pages = [resources[i:i + items_per_page] for i in range(0, len(resources), items_per_page)]

    if len(resources) > items_per_page:
        for resource in pages[page]:
            builder.row(InlineKeyboardButton(text=f'{resource[2]}', callback_data=ListResources(action='open_resource', resource_id=f'{resource[0]}').pack()))

        builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='resources', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='resources', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for resource in resources:
            builder.row(InlineKeyboardButton(text=f'{resource[2]}', callback_data=ListResources(action='open_resource', resource_id=f'{resource[0]}').pack()))

    
    builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ', callback_data='add_resource'), InlineKeyboardButton(text='♻️ ОБНОВИТЬ', callback_data='udpdate_data_resources'), width=2)
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='products_channel'))

    return builder


def cancel_add_new_resource():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='resources'))

    return builder


def resource_kb(resource_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=ListResources(action='delete_resource', resource_id=f'{resource_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='resources'))

    return builder
