from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from random import randint
from datetime import datetime


from Database.User_db import Database

db = Database()



class Paginator(CallbackData, prefix='call'):
    array_name: str
    button: str
    data: str
    page: str
    max_pages: str


class Showcase(CallbackData, prefix='call'):
    action: str
    identifier: str
    group_id: str

class PaginatorPictures(CallbackData, prefix='call'):
    action: str
    product_id: str
    group_id: str
    button: str
    page: int
    max_page: str


class BuyGoods(CallbackData, prefix='call'):
    action: str
    product_id: str
    group_id: str
    quantity: str
    count: str
    process: str


class DVMehtods(CallbackData, prefix='call'):
    action: str
    product_id: str
    group_id: str
    quantity: str
    method_id: str


class PaymentForGoods(CallbackData, prefix='call'):
    action: str
    product_id: str
    group_id: str
    quantity: str
    payment_method_id: str
    delivery_method_id: str


class AddDeliveryAddress(CallbackData, prefix='call'):
    action: str
    order_id: str


class Purchases(CallbackData, prefix='call'):
    action: str
    purchase_id: str




def list_buttons_not_group(project_id, page):
    builder = InlineKeyboardBuilder()

    parent_group = db.get_all_groups(project_id=project_id)

    list_groups = db.get_user_groups(project_id=project_id, parent_id=parent_group[0][0])
    list_products = db.list_of_displayed_products_no_group(project_id=project_id)

    list_buttons = []

    for item in list_groups:
        if item != '':
            list_buttons.append(item)

    for item in list_products:
        if item != '':
            list_buttons.append(item)

    items_per_page = 20
    pages = [list_buttons[i:i + items_per_page] for i in range(0, len(list_buttons), items_per_page)]
    
    try:
        if len(list_buttons) > items_per_page:
            for item in pages[int(page)]:
                try:
                    builder.row(InlineKeyboardButton(text=f'{item[9]}', callback_data=Showcase(action='open_product', identifier=f'{item[1]}', group_id='-1').pack()))
                except:
                    builder.row(InlineKeyboardButton(text=f'{item[3]}', callback_data=Showcase(action='open_group', identifier=f'{item[0]}', group_id=f'{item[0]}').pack()))
            builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='showcase_no_group', data='none', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='showcase_no_group', data='none', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)        
        else:
            for item in pages[int(page)]:
                try:
                    builder.row(InlineKeyboardButton(text=f'{item[9]}', callback_data=Showcase(action='open_product', identifier=f'{item[1]}', group_id='-1').pack()))
                except:
                    builder.row(InlineKeyboardButton(text=f'{item[3]}', callback_data=Showcase(action='open_group', identifier=f'{item[0]}', group_id=f'{item[0]}').pack()))
    except:
        pass
    
    
    return builder


def product_kb(product_id, group_id, page):
    builder = InlineKeyboardBuilder()

    product_data = db.get_product_data(product_id=product_id)

    if len(product_data[0][10]) > 1:
        builder.row(InlineKeyboardButton(text='«', callback_data=PaginatorPictures(action='paginator_pictures', product_id=product_id, group_id=group_id, button='back', page=page, max_page=f'{len(product_data[0][10])}').pack()), InlineKeyboardButton(text='»', callback_data=PaginatorPictures(action='paginator_pictures', product_id=product_id, group_id=group_id, button='next', page=page, max_page=f'{len(product_data[0][10])}').pack()), width=2)

    builder.row(InlineKeyboardButton(text='🛒 КУПИТЬ', callback_data=BuyGoods(action='buy_goods', product_id=f'{product_id}', group_id=f'{group_id}', quantity='1', count='null', process='null').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=Showcase(action='back_to_catalog', identifier=f'{group_id}', group_id=f'{group_id}').pack()))

    return builder




def open_group_kb(project_id, group_id, parent_id, page):
    builder = InlineKeyboardBuilder()

    list_groups = db.get_group_from_group(parent_id=group_id, project_id=project_id)
    list_products = db.list_products_in_a_group(group_id=group_id)

    list_buttons = []

    for item in list_groups:
        if item != '':
            list_buttons.append(item)

    for item in list_products:
        if item != '':
            list_buttons.append(item)

    items_per_page = 20
    pages = [list_buttons[i:i + items_per_page] for i in range(0, len(list_buttons), items_per_page)]

    try:
        if len(list_buttons) > items_per_page:
            for item in pages[int(page)]:
                try:
                    builder.row(InlineKeyboardButton(text=f'{item[9]}', callback_data=Showcase(action='open_product', identifier=f'{item[1]}', group_id=f'{group_id}').pack()))
                except:
                    builder.row(InlineKeyboardButton(text=f'{item[3]}', callback_data=Showcase(action='open_group', identifier=f'{item[0]}', group_id=f'{item[0]}').pack()))
            builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='showcase_in_group', data=f'{group_id}', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='showcase_in_group', data=f'{group_id}', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)        
        else:
            for item in pages[int(page)]:
                try:
                    builder.row(InlineKeyboardButton(text=f'{item[9]}', callback_data=Showcase(action='open_product', identifier=f'{item[1]}', group_id=f'{group_id}').pack()))
                except:
                    builder.row(InlineKeyboardButton(text=f'{item[3]}', callback_data=Showcase(action='open_group', identifier=f'{item[0]}', group_id=f'{item[0]}').pack()))
    except:
        pass

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=Showcase(action='back_to_catalog', identifier=f'{parent_id}', group_id=f'{parent_id}').pack()))

    return builder


def counter_kb(product_id, group_id, quantity):
    builder = InlineKeyboardBuilder()

    product_data = db.get_product_data(product_id=product_id)


    builder.row(InlineKeyboardButton(text='-', callback_data=BuyGoods(action='counter', product_id=product_id, group_id=group_id, quantity=quantity, count='minus', process='null').pack()), InlineKeyboardButton(text=f'{quantity}', callback_data=BuyGoods(action='counter', product_id=product_id, group_id=group_id, quantity=quantity, count='none', process='null').pack()), InlineKeyboardButton(text='+', callback_data=BuyGoods(action='counter', product_id=product_id, group_id=group_id, quantity=quantity, count='plus', process='null').pack()), width=3)


    if product_data[0][2] == 'delivery':
        builder.row(InlineKeyboardButton(text='🚚 СПОСОБ ДОСТАВКИ', callback_data=BuyGoods(action='choose_delivery_method', product_id=f'{product_id}', group_id=f'{group_id}', quantity=f'{quantity}', count='null', process='null').pack()))
    else:
        builder.row(InlineKeyboardButton(text='💳 ОПЛАТИТЬ', callback_data=BuyGoods(action='buy_goods_not_delivery', product_id=f'{product_id}', group_id=f'{group_id}', quantity=f'{quantity}', count='null', process='null').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=Showcase(action='open_product', identifier=f'{product_id}', group_id=f'{group_id}').pack()))

    return builder


def choose_delivery_methods_kb(product_id, group_id, quantity):
    builder = InlineKeyboardBuilder()

    for method in db.get_delivery_methods(product_id=product_id):
        builder.row(InlineKeyboardButton(text=f'{method[2]}', callback_data=DVMehtods(action='open_DVmethod', product_id=product_id, group_id=group_id, quantity=quantity, method_id=f'{method[0]}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=BuyGoods(action='counter', product_id=product_id, group_id=group_id, quantity=quantity, count='none', process='null').pack()))

    return builder



def delivery_method_kb(product_id, group_id, quantity, method_id):
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text='💳 ОПЛАТИТЬ', callback_data=BuyGoods(action='buy_goods_delivery', product_id=f'{product_id}', group_id=f'{group_id}', quantity=f'{quantity}', count=f'{method_id}', process='null').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=BuyGoods(action='choose_delivery_method', product_id=f'{product_id}', group_id=f'{group_id}', quantity=f'{quantity}', count='null', process='null').pack()))

    return builder


def payment_methods(project_id, product_id, group_id):
    builder = InlineKeyboardBuilder()

    for method in db.get_payment_methods(project_id=project_id):
        builder.row(InlineKeyboardButton(text=f'{method[4]}', callback_data=PaymentForGoods(action='payment_for_goods', product_id=product_id, group_id=group_id, quantity='none', payment_method_id=f'{method[0]}', delivery_method_id='none').pack()))
    
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=Showcase(action='open_product', identifier=f'{product_id}', group_id=f'{group_id}').pack()))

    return builder



def payment_methods_not_delivery(project_id, product_id, group_id, quantity):
    builder = InlineKeyboardBuilder()

    for method in db.get_payment_methods(project_id=project_id):
        builder.row(InlineKeyboardButton(text=f'{method[4]}', callback_data=PaymentForGoods(action='payment_for_goods', product_id=product_id, group_id=group_id, quantity=quantity, payment_method_id=f'{method[0]}', delivery_method_id='none').pack()))
    
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=BuyGoods(action='counter', product_id=product_id, group_id=group_id, quantity=quantity, count='none', process='null').pack()))

    return builder



def payment_methods_delivery(project_id, product_id, group_id, quantity, method_id):
    builder = InlineKeyboardBuilder()

    for method in db.get_payment_methods(project_id=project_id):
        builder.row(InlineKeyboardButton(text=f'{method[4]}', callback_data=PaymentForGoods(action='payment_for_goods', product_id=product_id, group_id=group_id, quantity=quantity, payment_method_id=f'{method[0]}', delivery_method_id=method_id).pack()))
    
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=DVMehtods(action='open_DVmethod', product_id=product_id, group_id=group_id, quantity=quantity, method_id=f'{method_id}').pack()))

    return builder



def payment_for_goods_kb(product_id, group_id, quantity, delivery_method_id, payment_method_id, url, process_id):
    builder = InlineKeyboardBuilder()

    payment_method_data = db.get_payment_method_data(method_id=payment_method_id)

    if payment_method_data[0][2] == 'manual':
        builder.row(InlineKeyboardButton(text='✅ Я ОПЛАТИЛ', callback_data='proof_of_payment'))
    else:
        builder.row(InlineKeyboardButton(text='Перейти к оплате', url=f'{url}'))

    if quantity == 'none':
        builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=BuyGoods(action='buy_goods', product_id=f'{product_id}', group_id=f'{group_id}', quantity='1', count='null', process=f'{process_id}').pack()))
    elif delivery_method_id == 'none':
        builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=BuyGoods(action='buy_goods_not_delivery', product_id=f'{product_id}', group_id=f'{group_id}', quantity=f'{quantity}', count='null', process=f'{process_id}').pack()))
    else:
        builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=BuyGoods(action='buy_goods_delivery', product_id=f'{product_id}', group_id=f'{group_id}', quantity=f'{quantity}', count=f'{delivery_method_id}', process=f'{process_id}').pack()))
    

    return builder



def cancel_send_proof():
    buttons = [
        [InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='call_back_to_menu')],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb


def receive_paid_goods_kb(sale_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Получить товар', callback_data=f'usersaleid_{sale_id}'))

    return builder


def proof_payment_kb(process_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='✅ ОДОБРИТЬ', callback_data=f'confirmpayment_{process_id}'))
    builder.row(InlineKeyboardButton(text='⛔️ ОТКЛОНИТЬ', callback_data=f'rejectpayment_{process_id}'))

    return builder





def back_to_menu_kb():
    buttons = [
        [InlineKeyboardButton(text='👈 НАЗАД', callback_data='call_back_to_menu')],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb



def edit_delivery_address(delivery_order):
    builder = InlineKeyboardBuilder()

    delivery_data = db.get_delivery_data(order_id=delivery_order)

    if delivery_data[0][11] == 'в обработке':
        builder.row(InlineKeyboardButton(text='Указать адрес', callback_data=AddDeliveryAddress(action='add_delivery_address', order_id=f'{delivery_order}').pack()))
    else:
        builder.row(InlineKeyboardButton(text='К ПОКУПКАМ', callback_data='call_purchases'))

    return builder


def cancel_edit_delivery_address():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='call_purchases'))

    return builder
    





# Кнопки для раздела покупки

def purchases_kb(project_id, user_id):
    builder = InlineKeyboardBuilder()

    list_paid_items = db.get_paid_items(user_id=user_id, project_id=project_id)


    for purchase in list_paid_items:
        date_str = f"{purchase[2]}"
        date_object = datetime.strptime(date_str, "%Y-%m-%d")
        date = date_object.strftime("%d.%m.%y")
        builder.row(InlineKeyboardButton(text=f'{purchase[7]} {date}', callback_data=Purchases(action='open_purchase', purchase_id=f'{purchase[0]}').pack()))


    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='call_back_to_menu'))

    return builder


def purchase_dv_kb(order_id):
    builder = InlineKeyboardBuilder()


    delivery_data = db.get_delivery_data(order_id=order_id)

    if delivery_data[0][11] == 'в обработке':
        builder.row(InlineKeyboardButton(text='Изменить адрес', callback_data=AddDeliveryAddress(action='add_delivery_address', order_id=f'{order_id}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='call_purchases'))

    return builder
    








