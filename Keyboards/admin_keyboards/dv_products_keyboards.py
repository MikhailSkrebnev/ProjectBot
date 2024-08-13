from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from Database.Admin_db import Database

db = Database()






class Paginator(CallbackData, prefix='call'):
    array_name: str
    button: str
    page: str
    max_pages: str


class PaginatorOrders(CallbackData, prefix='call'):
    array_name: str
    button: str
    page: str
    max_pages: str
    order_status: str



# Раздел для товаров с ДОСТАВКОЙ

class ListProductsDv(CallbackData, prefix='call'):
    action: str
    product_id: str
    project_id: str

class ListMethodsDv(CallbackData, prefix='call'):
    action: str
    method_id: str
    project_id: str

class EditProducrDV(CallbackData, prefix='call'):
    action: str
    product_id: str
    what_to_edit: str

class EditMethodDV(CallbackData, prefix='call'):
    action: str
    method_id: str
    what_to_edit: str

class ChooseMethodDV(CallbackData, prefix='call'):
    action: str
    method_id: str
    page: str

class ListPicturesDv(CallbackData, prefix='call'):
    action: str
    picture_id: str
    product_id: str


class DeliveryOrders(CallbackData, prefix='call'):
    action: str
    order_path: str


class EditDeliveryOrder(CallbackData, prefix='call'):
    action: str
    what_to_edit: str
    order_id: str    



def user_products_dv_kb(project_id, page):
    builder = InlineKeyboardBuilder()

    products = db.get_list_products(project_id=project_id, product_type='delivery')
    items_per_page = 20
    pages = [products[i:i + items_per_page] for i in range(0, len(products), items_per_page)]

    if len(products) > items_per_page:
        for product in pages[int(page)]:
            if product[3] == 'включен':
                builder.row(InlineKeyboardButton(text=f'{product[8]}', callback_data=ListProductsDv(action='open_product_dv', project_id=f'{project_id}', product_id=f'{product[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'💤 {product[8]}', callback_data=ListProductsDv(action='open_product_dv', project_id=f'{project_id}', product_id=f'{product[0]}').pack()))
        builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='products_dv', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='products_dv', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for product in products:
            if product[3] == 'включен':
                builder.row(InlineKeyboardButton(text=f'{product[8]}', callback_data=ListProductsDv(action='open_product_dv', project_id=f'{project_id}', product_id=f'{product[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'💤 {product[8]}', callback_data=ListProductsDv(action='open_product_dv', project_id=f'{project_id}', product_id=f'{product[0]}').pack()))


    builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ТОВАР', callback_data=ListProductsDv(action='add_new_product_dv', project_id=f'{project_id}', product_id='null').pack()))
    builder.row(InlineKeyboardButton(text='📦 ЗАКАЗЫ', callback_data=ListProductsDv(action='open_delivery_orders', project_id=f'{project_id}', product_id=f'null').pack()), InlineKeyboardButton(text='🚚 DELIVERY', callback_data=ListProductsDv(action='open_delivery_methods', project_id=f'{project_id}', product_id=f'null').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='products'))

    return builder

def cancel_add_product_dv():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='delivery_products'))

    return builder

def cancel_edit_product(product_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListProductsDv(action='open_product_dv', project_id='null', product_id=f'{product_id}').pack()))

    return builder

def product_delivery_kb(product_id):
    builder = InlineKeyboardBuilder()
    
    product_data = db.get_product_data(product_id=product_id)

    builder.row(InlineKeyboardButton(text='🌄 ФОТО', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='product_photo', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='🔖 НАЗВАНИЕ', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='product_name', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='📝 ОПИСАНИЕ', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='product_description', product_id=f'{product_id}').pack()), width=2)
    builder.row(InlineKeyboardButton(text='💰 СТОИМОСТЬ', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='product_price', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='🏷 СКИДКА', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='product_discount', product_id=f'{product_id}').pack()), width=2)
    builder.row(InlineKeyboardButton(text='🧮 КОЛИЧЕСТВО', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='product_quantity', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='🚚 ДОСТАВКА', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='delivery_methods', product_id=f'{product_id}').pack()), width=2)
    if product_data[0][3] == 'включен':
        builder.row(InlineKeyboardButton(text='✅ ВКЛЮЧЕН', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='display_status_off', product_id=f'{product_id}').pack()))
    else:
        builder.row(InlineKeyboardButton(text='💤 ВЫКЛЮЧЕН', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='display_status_on', product_id=f'{product_id}').pack()))

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='delete_product', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='delivery_products'))

    return builder


def delete_product_dv(product_id, project_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='ДА, Я УВЕРЕН!', callback_data=EditProducrDV(action='delete_dv', what_to_edit='delete_dv', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListProductsDv(action='open_product_dv', project_id=f'{project_id}', product_id=f'{product_id}').pack()))

    return builder


def return_list_products_dv():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 К СПИСКУ ТОВАРОВ', callback_data='delivery_products'))

    return builder



def return_product_dv_kb(product_id, project_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='✅ ВЕРНУТЬСЯ К ТОВАРУ', callback_data=ListProductsDv(action='open_product_dv', project_id=f'{project_id}', product_id=f'{product_id}').pack()))

    return builder



def edit_choose_list_delivery(project_id, product_id, page, selected):
    builder = InlineKeyboardBuilder()

    delivey_methods = db.get_list_delivery_methods(project_id=project_id)

    items_per_page = 20
    pages = [delivey_methods[i:i + items_per_page] for i in range(0, len(delivey_methods), items_per_page)]

    if len(delivey_methods) == 0:
        pass
    else:
        if len(delivey_methods) > 2:
            for method in pages[int(page)]:
                if str(method[0]) in selected:
                    builder.row(InlineKeyboardButton(text=f'🔸 {method[2]}', callback_data=ChooseMethodDV(action='edit_choose_method', page=f'{page}', method_id=f'{method[0]}').pack()))
                else:
                    builder.row(InlineKeyboardButton(text=f'{method[2]}', callback_data=ChooseMethodDV(action='edit_choose_method', page=f'{page}', method_id=f'{method[0]}').pack()))

            builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='edit_method_of_choice', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='edit_method_of_choice', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
        else:
            for method in pages[int(page)]:
                if str(method[0]) in selected:
                    builder.row(InlineKeyboardButton(text=f'🔸 {method[2]}', callback_data=ChooseMethodDV(action='edit_choose_method', page=f'{page}', method_id=f'{method[0]}').pack()))
                else:
                    builder.row(InlineKeyboardButton(text=f'{method[2]}', callback_data=ChooseMethodDV(action='edit_choose_method', page=f'{page}', method_id=f'{method[0]}').pack()))
    
    db.update_list_dv_method(product_id=product_id, methods_id=selected)

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsDv(action='open_product_dv', project_id=f'{project_id}', product_id=f'{product_id}').pack()))

    return builder







def choose_list_delivery(project_id, page, selected):
    builder = InlineKeyboardBuilder()

    delivey_methods = db.get_list_delivery_methods(project_id=project_id)

    items_per_page = 20
    pages = [delivey_methods[i:i + items_per_page] for i in range(0, len(delivey_methods), items_per_page)]

    if len(delivey_methods) == 0:
        pass
    else:
        if len(delivey_methods) > 2:
            for method in pages[int(page)]:
                if str(method[0]) in selected:
                    builder.row(InlineKeyboardButton(text=f'🔸 {method[2]}', callback_data=ChooseMethodDV(action='choose_method', page=f'{page}', method_id=f'{method[0]}').pack()))
                else:
                    builder.row(InlineKeyboardButton(text=f'{method[2]}', callback_data=ChooseMethodDV(action='choose_method', page=f'{page}', method_id=f'{method[0]}').pack()))

            builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='method_of_choice', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='method_of_choice', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
        else:
            for method in pages[int(page)]:
                if str(method[0]) in selected:
                    builder.row(InlineKeyboardButton(text=f'🔸 {method[2]}', callback_data=ChooseMethodDV(action='choose_method', page=f'{page}', method_id=f'{method[0]}').pack()))
                else:
                    builder.row(InlineKeyboardButton(text=f'{method[2]}', callback_data=ChooseMethodDV(action='choose_method', page=f'{page}', method_id=f'{method[0]}').pack()))
    
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='delivery_products'))
    builder.row(InlineKeyboardButton(text='✅ Продолжить', callback_data='choice_delivery_methods'))

    return builder    








def edit_pictures_dv(product_id):
    builder = InlineKeyboardBuilder()

    list_pic = db.get_list_pictures(product_id=product_id)
    i = 0

    for picture in list_pic:
        i += 1
        builder.row(InlineKeyboardButton(text=f'ФОТО {i}', callback_data=ListPicturesDv(action='open_picture_dv', picture_id=f'{picture[0]}', product_id=f'{product_id}').pack()))

    if len(list_pic) < 15:
        builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ФОТО', callback_data=ListPicturesDv(action='add_picture_dv', picture_id='no', product_id=f'{product_id}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsDv(action='open_product_dv', project_id='no', product_id=f'{product_id}').pack()))

    return builder

def picture_dv_kb(picture_id, product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=ListPicturesDv(action='delete_picture_dv', picture_id=f'{picture_id}', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListPicturesDv(action='back_from_photo_dv', picture_id='no', product_id=f'{product_id}').pack()))

    return builder


def cancel_add_picture(product_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='product_photo', product_id=f'{product_id}').pack()))

    return builder


def return_list_picture(product_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=EditProducrDV(action='edit_product_dv', what_to_edit='product_photo', product_id=f'{product_id}').pack()))

    return builder


















def user_methods_dv_kb(project_id, page):
    builder = InlineKeyboardBuilder()

    methods = db.get_list_delivery_methods(project_id=project_id)
    items_per_page = 20
    pages = [methods[i:i + items_per_page] for i in range(0, len(methods), items_per_page)]

    if len(methods) > items_per_page:
        for method in pages[int(page)]:
            if method[5] == True:
                builder.row(InlineKeyboardButton(text=f'{method[2]}', callback_data=ListMethodsDv(action='open_methods_dv', project_id=f'{project_id}', method_id=f'{method[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'💤 {method[2]}', callback_data=ListMethodsDv(action='open_methods_dv', project_id=f'{project_id}', method_id=f'{method[0]}').pack()))
        builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='methods_dv', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='methods_dv', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for method in methods:
            if method[5] == True:
                builder.row(InlineKeyboardButton(text=f'{method[2]}', callback_data=ListMethodsDv(action='open_methods_dv', project_id=f'{project_id}', method_id=f'{method[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'💤 {method[2]}', callback_data=ListMethodsDv(action='open_methods_dv', project_id=f'{project_id}', method_id=f'{method[0]}').pack()))


    builder.row(InlineKeyboardButton(text='➕ СПОСОБ ДОСТАВКИ', callback_data=ListMethodsDv(action='add_new_methods_dv', project_id=f'{project_id}', method_id='null').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='delivery_products'))

    return builder

def cancel_add_method_dv(project_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListProductsDv(action='open_delivery_methods', project_id=f'{project_id}', product_id=f'null').pack()))

    return builder

def method_delivery_kb(method_id, project_id):
    builder = InlineKeyboardBuilder()

    method_data = db.get_method_data(method_id=method_id)

    builder.row(InlineKeyboardButton(text='🔖 НАЗВАНИЕ', callback_data=EditMethodDV(action='edit_method_dv', what_to_edit='method_name', method_id=f'{method_id}').pack()), InlineKeyboardButton(text='📝 ОПИСАНИЕ', callback_data=EditMethodDV(action='edit_method_dv', what_to_edit='method_description', method_id=f'{method_id}').pack()))
    builder.row(InlineKeyboardButton(text='💰 СТОИМОСТЬ', callback_data=EditMethodDV(action='edit_method_dv', what_to_edit='method_price', method_id=f'{method_id}').pack()))

    if method_data[0][5] == True:
        builder.row(InlineKeyboardButton(text='✅ ВКЛЮЧЕН', callback_data=EditMethodDV(action='edit_method_dv', what_to_edit='display_status_off', method_id=f'{method_id}').pack()))
    else:
        builder.row(InlineKeyboardButton(text='💤 ВЫКЛЮЧЕН', callback_data=EditMethodDV(action='edit_method_dv', what_to_edit='display_status_onn', method_id=f'{method_id}').pack()))

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=EditMethodDV(action='edit_method_dv', what_to_edit='delete_method', method_id=f'{method_id}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsDv(action='open_delivery_methods', project_id=f'{project_id}', product_id=f'null').pack()))

    return builder


def cancel_edit_method_dv(method_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListMethodsDv(action='open_methods_dv', project_id='null', method_id=f'{method_id}').pack()))

    return builder

def return_edit_method_dv(method_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 К ТОВАРУ', callback_data=ListMethodsDv(action='open_methods_dv', project_id='null', method_id=f'{method_id}').pack()))

    return builder

def delete_method_dv(project_id, method_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='ДА, Я УВЕРЕН!', callback_data=EditMethodDV(action='delete_method_dv', what_to_edit='delete_method_dv', method_id=f'{method_id}').pack()))
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListMethodsDv(action='open_delivery_methods', project_id=f'{project_id}', method_id=f'{method_id}').pack()))

    return builder














def choose_orders():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='⏳ Заказы в обработке', callback_data=DeliveryOrders(action='list_orders', order_path='orders_are_being_processed').pack()))
    builder.row(InlineKeyboardButton(text='✈️ Заказы в пути', callback_data=DeliveryOrders(action='list_orders', order_path='orders_on_the_way').pack()))
    builder.row(InlineKeyboardButton(text='✅ Завершенный заказы', callback_data=DeliveryOrders(action='list_orders', order_path='completed_order').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='delivery_products'))

    return builder


def list_delivery_orders(project_id, order_status, page):
    builder = InlineKeyboardBuilder()

    list_orders = db.get_list_delivery_orders(project_id=project_id, order_status=order_status)

    items_per_page = 20
    pages = [list_orders[i:i + items_per_page] for i in range(0, len(list_orders), items_per_page)]


    if len(list_orders) > items_per_page:
        for order in pages[int(page)]:
            builder.row(InlineKeyboardButton(text=f'ЗАКАЗ {order[0]}', callback_data=DeliveryOrders(action='open_order', order_path=f'{order[0]}').pack()))
        builder.row(InlineKeyboardButton(text='«', callback_data=PaginatorOrders(array_name='pag_orders_dv', page=f'{page}', max_pages=f'{len(pages)}', button='back', order_status=f'{order_status}').pack()), InlineKeyboardButton(text='»', callback_data=PaginatorOrders(array_name='pag_orders_dv', page=f'{page}', max_pages=f'{len(pages)}', button='next', order_status=f'{order_status}').pack()), width=2)
    else:
        for order in list_orders:
            builder.row(InlineKeyboardButton(text=f'ЗАКАЗ {order[0]}', callback_data=DeliveryOrders(action='open_order', order_path=f'{order[0]}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsDv(action='open_delivery_orders', project_id=f'{project_id}', product_id=f'null').pack()))

    return builder



def order_kb(order_path, order_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Изменить комментарий', callback_data=EditDeliveryOrder(action='edit_order', what_to_edit='edit_order_comment', order_id=f'{order_id}').pack()))
    builder.row(InlineKeyboardButton(text='Изменить статус', callback_data=EditDeliveryOrder(action='edit_order', what_to_edit='edit_order_status', order_id=f'{order_id}').pack()))
    builder.row(InlineKeyboardButton(text='Изменить трек-номер', callback_data=EditDeliveryOrder(action='edit_order', what_to_edit='edit_order_track_number', order_id=f'{order_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=DeliveryOrders(action='list_orders', order_path=f'{order_path}').pack()))

    return builder



def edit_order_status(order_id, order_status):
    builder = InlineKeyboardBuilder()

    if order_status == 'в обработке':
        builder.row(InlineKeyboardButton(text='✈️ В ПУТИ', callback_data=EditDeliveryOrder(action='edit_order_status', what_to_edit='в пути', order_id=f'{order_id}').pack()))
        builder.row(InlineKeyboardButton(text='✅ ЗАВЕРШЕН', callback_data=EditDeliveryOrder(action='edit_order_status', what_to_edit='завершен', order_id=f'{order_id}').pack()))
    elif order_status == 'в пути':
        builder.row(InlineKeyboardButton(text='⏳ В ОБРАБОТКЕ', callback_data=EditDeliveryOrder(action='edit_order_status', what_to_edit='в обработке', order_id=f'{order_id}').pack()))
        builder.row(InlineKeyboardButton(text='✅ ЗАВЕРШЕН', callback_data=EditDeliveryOrder(action='edit_order_status', what_to_edit='завершен', order_id=f'{order_id}').pack()))
    else:
        builder.row(InlineKeyboardButton(text='⏳ В ОБРАБОТКЕ', callback_data=EditDeliveryOrder(action='edit_order_status', what_to_edit='в обработке', order_id=f'{order_id}').pack()))
        builder.row(InlineKeyboardButton(text='✈️ В ПУТИ', callback_data=EditDeliveryOrder(action='edit_order_status', what_to_edit='в пути', order_id=f'{order_id}').pack()))


    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=DeliveryOrders(action='open_order', order_path=f'{order_id}').pack()))

    return builder



def cancel_edit_order_data(order_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=DeliveryOrders(action='open_order', order_path=f'{order_id}').pack()))

    return builder

def return_order_data(order_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=DeliveryOrders(action='open_order', order_path=f'{order_id}').pack()))

    return builder


def open_edit_order(order_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='ОТКРЫТЬ ЗАКАЗ', callback_data=DeliveryOrders(action='open_order', order_path=f'{order_id}').pack()))

    return builder