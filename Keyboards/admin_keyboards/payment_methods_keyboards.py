from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from Database.Admin_db import Database

db = Database()



# Кнопки для ручной платежной системы


class PaymentMethods(CallbackData, prefix='call'):
    action: str
    method_id: str


class EditPaymentMethod(CallbackData, prefix='call'):
    action: str
    method_id: str
    what_to_edit: str




def user_payment_methods_kb(project_id):
    builder = InlineKeyboardBuilder()

    list_payment_method = db.get_list_manual_payment_methods(project_id=project_id)

    for method in list_payment_method:
        if method[3]:
            builder.row(InlineKeyboardButton(text=f'{method[4]}', callback_data=PaymentMethods(action='open_payment_method', method_id=f'{method[0]}').pack()))
        else: 
            builder.row(InlineKeyboardButton(text=f'💤 {method[4]}', callback_data=PaymentMethods(action='open_payment_method', method_id=f'{method[0]}').pack()))


    if len(list_payment_method) < 20:
        builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ', callback_data=PaymentMethods(action='add_new_manual_payment_method', method_id=f'{project_id}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='payment_methods'))

    return builder


def cancel_add_manual_payment_method():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='manual_payment_method'))

    return builder


def manual_payment_method_kb(method_id):
    builder = InlineKeyboardBuilder()

    payment_method_data = db.get_manual_paymetn_method_data(method_id=method_id)

    builder.row(InlineKeyboardButton(text='🔖 НАЗВАНИЕ', callback_data=EditPaymentMethod(action='edit_manual_payment_method', method_id=f'{method_id}', what_to_edit='payment_name').pack()), InlineKeyboardButton(text='📝 ОПИСАНИЕ', callback_data=EditPaymentMethod(action='edit_manual_payment_method', method_id=f'{method_id}', what_to_edit='payment_description').pack()), width=2)

    if payment_method_data[0][3]:
        builder.row(InlineKeyboardButton(text='✅ ВКЛЮЧЕН', callback_data=EditPaymentMethod(action='edit_manual_payment_method', method_id=f'{method_id}', what_to_edit='payment_method_off').pack()))
    else:
        builder.row(InlineKeyboardButton(text='💤 ВЫКЛЮЧЕН', callback_data=EditPaymentMethod(action='edit_manual_payment_method', method_id=f'{method_id}', what_to_edit='payment_method_on').pack()))

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=EditPaymentMethod(action='edit_manual_payment_method', method_id=f'{method_id}', what_to_edit='want_to_delete').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='manual_payment_method'))

    return builder


def cancel_edit_manual_payment_method(method_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=PaymentMethods(action='open_payment_method', method_id=f'{method_id}').pack()))

    return builder

def return_manual_payment_method_kb(method_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=PaymentMethods(action='open_payment_method', method_id=f'{method_id}').pack()))

    return builder


def delete_manual_payment_method(method_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Да, уверен', callback_data=EditPaymentMethod(action='delete_manual_payment_method', method_id=f'{method_id}', what_to_edit='yes_i_am_sure').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=PaymentMethods(action='open_payment_method', method_id=f'{method_id}').pack()))

    return builder



# Кнопки для раздела с автоматической оплаты


class AutoPaymentMethods(CallbackData, prefix='call'):
    action: str
    method_id: str
    data: str


def user_auto_payment_methods_kb(project_id):
    builder = InlineKeyboardBuilder()

    list_payment_method = db.get_list_auto_payment_methods(project_id=project_id)

    for method in list_payment_method:
        if method[3]:
            builder.row(InlineKeyboardButton(text=f'{method[4]}', callback_data=AutoPaymentMethods(action='open_auto_payment_method', method_id=f'{method[0]}', data='none').pack()))
        else:
            builder.row(InlineKeyboardButton(text=f'💤 {method[4]}', callback_data=AutoPaymentMethods(action='open_auto_payment_method', method_id=f'{method[0]}', data='none').pack()))

    builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ', callback_data='add_new_auto_payment_method'))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='payment_methods'))

    return builder


def add_new_auto_payment_method():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='CryptoBot', callback_data=AutoPaymentMethods(action='add_new_auto_payment_method', method_id='none', data='CryptoBot').pack()))
    builder.row(InlineKeyboardButton(text='WalletPay', callback_data=AutoPaymentMethods(action='add_new_auto_payment_method', method_id='none', data='WalletPay').pack()))
    builder.row(InlineKeyboardButton(text='Юмани', callback_data=AutoPaymentMethods(action='add_new_auto_payment_method', method_id='none', data='Yoomoney').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='automatic_payment_method'))

    return builder



def cancel_add_new_auto_payment_method():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='add_new_auto_payment_method'))

    return builder


def cancel_add_new_yoomoney_payment_method():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='НАСТРОИТЬ АВТОПЛАТЕЖИ', url='https://yoomoney.ru/transfer/myservices/http-notification'))
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='add_new_auto_payment_method'))

    return builder


def finis_add_new_auto_payment_method(method_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='⚙️ НАСТРОИТЬ Юmoney', callback_data=AutoPaymentMethods(action='open_auto_payment_method', method_id=f'{method_id}', data='none').pack()))

    return builder



def auto_payment_method_kb(method_id):
    builder = InlineKeyboardBuilder()

    method_data = db.get_data_auto_payment_method(method_id=method_id)

    builder.row(InlineKeyboardButton(text='🔖 НАЗВАНИЕ', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_name').pack()), InlineKeyboardButton(text='📝 ОПИСАНИЕ', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_description').pack()), width=2)

    if method_data[0][2] != 'auto_Yoomoney':
        if method_data[0][3]:
            builder.row(InlineKeyboardButton(text='✅ ВКЛЮЧЕН', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_off').pack()), InlineKeyboardButton(text='♻️ ОБНОВИТЬ ТОКЕН', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_token').pack()), width=2)
        else:
            builder.row(InlineKeyboardButton(text='💤 ВЫКЛЮЧЕН', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_on').pack()), InlineKeyboardButton(text='♻️ ОБНОВИТЬ ТОКЕН', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_token').pack()), width=2)
    else:
        if method_data[0][3]:
            builder.row(InlineKeyboardButton(text='✅ ВКЛЮЧЕН', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_off').pack()), InlineKeyboardButton(text='♻️ ОБНОВИТЬ SECRET', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_token').pack()), width=2)
        else:
            builder.row(InlineKeyboardButton(text='💤 ВЫКЛЮЧЕН', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_on').pack()), InlineKeyboardButton(text='♻️ ОБНОВИТЬ SECRET', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='method_token').pack()), width=2)




    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=AutoPaymentMethods(action='edit_auto_payment_method', method_id=f'{method_id}', data='delete_auto_method').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='automatic_payment_method'))

    return builder


def cancel_edit_auto_payment_method(method_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=AutoPaymentMethods(action='open_auto_payment_method', method_id=f'{method_id}', data='none').pack()))

    return builder


def return_auto_payment_method_kb(method_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=AutoPaymentMethods(action='open_auto_payment_method', method_id=f'{method_id}', data='none').pack()))

    return builder


def delete_auto_payment_method(method_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Да, уверен', callback_data=AutoPaymentMethods(action='delete_auto_payment_method', method_id=f'{method_id}', data='yes_i_am_sure').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=AutoPaymentMethods(action='open_auto_payment_method', method_id=f'{method_id}', data='none').pack()))

    return builder












