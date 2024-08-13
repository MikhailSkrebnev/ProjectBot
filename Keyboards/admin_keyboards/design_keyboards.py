from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from Database.Admin_db import Database

db = Database()



# Раздел с настройками

class EditMessage(CallbackData, prefix='call'):
    message: str
    edit: str


class Edit(CallbackData, prefix='call'):
    edit_message: str
    edit: str
    project_id: str


class DesignDecor(CallbackData, prefix='call'):
    action: str
    data: str



def design_kb():
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text='✉️ Сообщения', callback_data='design_message'))
    builder.row(InlineKeyboardButton(text='👨‍🎨 Оформление', callback_data='design_decor'))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='main_menu_admin'))
    
    return builder



def design_decor_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🌄 Фото в меню', callback_data=DesignDecor(action='menu_picture', data='none').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='design'))

    return builder




def menu_picture_kb(project_id):
    builder = InlineKeyboardBuilder()

    menu_pic = db.get_menu_picture(project_id=project_id)

    for picture in menu_pic:
        builder.row(InlineKeyboardButton(text='ФОТО', callback_data=DesignDecor(action='open_menu_picture', data=f'{picture[0]}').pack()))

    if menu_pic == []:
        builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ФОТО', callback_data=DesignDecor(action='add_menu_picture', data=f'{project_id}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='design_decor'))

    return builder


def picture_kb(picture_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=DesignDecor(action='delete_menu_pic', data=f'{picture_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=DesignDecor(action='menu_picture', data='none').pack()))

    return builder


def cancel_add_menu_pic():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=DesignDecor(action='menu_picture', data='none').pack()))

    return builder




def design_message_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Стартовое сообщение', callback_data=EditMessage(message='message', edit='start_caption').pack()))
    builder.row(InlineKeyboardButton(text='Сообщение в меню', callback_data=EditMessage(message='message', edit='menu_caption').pack()))
    builder.row(InlineKeyboardButton(text='Сообщение после оплаты', callback_data=EditMessage(message='message', edit='after_payment_caption').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='design'))

    return builder

def cancel_edit_message(edit):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=EditMessage(message='message', edit=f'{edit}').pack()))

    return builder


def edit_message_kb(edit, project_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='РЕДАКТИРОВАТЬ', callback_data=Edit(edit_message='edit_message', edit=f'{edit}', project_id=f'{project_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='design_message'))

    return builder