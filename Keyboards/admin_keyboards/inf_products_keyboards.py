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

class PaginatorContent(CallbackData, prefix='call'):
    array_name: str
    button: str
    page: str
    max_pages: str
    product_id: str

class ListProductsInf(CallbackData, prefix='call'):
    open_product_inf: str
    product_id: str

class EditProductINF(CallbackData, prefix='call'):
    edit_product: str
    what_to_edit: str
    product_id: str

class CallProductContent(CallbackData, prefix='call'):
    action: str
    id: str

class ListPicturesInf(CallbackData, prefix='call'):
    action: str
    picture_id: str
    product_id: str


def user_products_inf_kb(project_id, page):
    builder = InlineKeyboardBuilder()

    products = db.get_list_products(project_id=project_id, product_type='inf')
    items_per_page = 20
    pages = [products[i:i + items_per_page] for i in range(0, len(products), items_per_page)]

    if len(products) > items_per_page:
        for product in pages[int(page)]:
            if product[3] == 'включен':
                builder.row(InlineKeyboardButton(text=f'{product[8]}', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'💤 {product[8]}', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product[0]}').pack()))
        builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='products_inf', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='products_inf', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for product in products:
            if product[3] == 'включен':
                builder.row(InlineKeyboardButton(text=f'{product[8]}', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'💤 {product[8]}', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product[0]}').pack()))

    builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ТОВАР', callback_data='add_product_inf'))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='products'))


    return builder


def cancel_add_product_inf():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='information_products'))

    return builder

def choose_inf_content():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='ОДИН ПРОДУКТ', callback_data='one_inf_content'))
    builder.row(InlineKeyboardButton(text='МНОГО ПРОДУКТОВ', callback_data='more_inf_content'))
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='information_products'))

    return builder

def skip_add_contnet(product_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Добавлю позже', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product_id}').pack()))

    return builder


def cancel_edit_product_inf(product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product_id}').pack()))

    return builder


def contetn_no_reusable_product_inf(product_id):
    builder = InlineKeyboardBuilder()

    content_id = db.get_list_product_content(product_id=product_id)[0][5][0]

    builder.row(InlineKeyboardButton(text=f'ТОВАР', callback_data=CallProductContent(action='open_content_no_reusable', id=f'{content_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product_id}').pack()))

    return builder


def product_content_no_reusable_kb(content_id, product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Заменить товар', callback_data=CallProductContent(action='replace_product_content', id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_content', product_id=f'{product_id}').pack()))
    
    return builder


def cancel_add_new_content_no_reusable(product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_content', product_id=f'{product_id}').pack()))

    return builder


def cancel_add_new_content(product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_contents', product_id=f'{product_id}').pack()))

    return builder




def return_product_inf_kb(product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='✅ ВЕРНУТЬСЯ К ТОВАРУ', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product_id}').pack()))

    return builder



def return_list_products_inf():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 К СПИСКУ ТОВАРОВ', callback_data='information_products'))

    return builder


def product_inf_kb(product_id):
    builder = InlineKeyboardBuilder()
    
    product_data = db.get_product_data(product_id=product_id)

    if product_data[0][4] == False:
        builder.row(InlineKeyboardButton(text='🌄 ФОТО', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_photo', product_id=f'{product_id}').pack()))
        builder.row(InlineKeyboardButton(text='🔖 НАЗВАНИЕ', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_name', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='📝 ОПИСАНИЕ', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_description', product_id=f'{product_id}').pack()), width=2)
        builder.row(InlineKeyboardButton(text='💰 СТОИМОСТЬ', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_price', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='🏷 СКИДКА', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_discount', product_id=f'{product_id}').pack()), width=2)
        builder.row(InlineKeyboardButton(text='📦 ТОВАР', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_content', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='🧮 КОЛИЧЕСТВО', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_quantity', product_id=f'{product_id}').pack()), width=2)
        if product_data[0][3] == 'включен':
            builder.row(InlineKeyboardButton(text='✅ ВКЛЮЧЕН', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='display_status_of', product_id=f'{product_id}').pack()))
        else:
            builder.row(InlineKeyboardButton(text='💤 ВЫКЛЮЧЕН', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='display_status_on', product_id=f'{product_id}').pack()))
    else:
        builder.row(InlineKeyboardButton(text='🌄 ФОТО', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_photo', product_id=f'{product_id}').pack()))
        builder.row(InlineKeyboardButton(text='🔖 НАЗВАНИЕ', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_name', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='📝 ОПИСАНИЕ', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_description', product_id=f'{product_id}').pack()), width=2)
        builder.row(InlineKeyboardButton(text='💰 СТОИМОСТЬ', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_price', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='🏷 СКИДКА', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_discount', product_id=f'{product_id}').pack()), width=2)
        builder.row(InlineKeyboardButton(text=f'📦 ТОВАРЫ ({len(product_data[0][5])})', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_contents', product_id=f'{product_id}').pack()))
        if product_data[0][3] == 'включен':
            builder.row(InlineKeyboardButton(text='✅ ВКЛЮЧЕН', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='display_status_of', product_id=f'{product_id}').pack()))
        else:
            builder.row(InlineKeyboardButton(text='💤 ВЫКЛЮЧЕН', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='display_status_on', product_id=f'{product_id}').pack()))


    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='delete_product', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='information_products'))

    return builder


def edit_pictures_inf(product_id):
    builder = InlineKeyboardBuilder()

    list_pic = db.get_list_pictures(product_id=product_id)
    i = 0

    for picture in list_pic:
        i += 1
        builder.row(InlineKeyboardButton(text=f'ФОТО {i}', callback_data=ListPicturesInf(action='open_picture_inf', picture_id=f'{picture[0]}', product_id=f'{product_id}').pack()))

    if len(list_pic) < 15:
        builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ФОТО', callback_data=ListPicturesInf(action='add_picture_inf', picture_id='no', product_id=f'{product_id}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product_id}').pack()))

    return builder



def picture_inf_kb(picture_id, product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=ListPicturesInf(action='delete_picture_inf', picture_id=f'{picture_id}', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListPicturesInf(action='back_from_photo_inf', picture_id='no', product_id=f'{product_id}').pack()))

    return builder



def cancel_add_picture_inf(product_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_photo', product_id=f'{product_id}').pack()))

    return builder


def return_list_picture_inf(product_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_photo', product_id=f'{product_id}').pack()))

    return builder




def list_product_content(product_id, page):
    builder = InlineKeyboardBuilder()

    i = 0
    list_content = []

    for content in db.get_list_product_content(product_id=product_id)[0][5]: # Вытаскиваем все айдишники контента на продукте
        list_content.append(db.get_product_content(content_id=content)[0]) # Получаем данные об этих товарах

    items_per_page = 20
    pages = [list_content[i:i + items_per_page] for i in range(0, len(list_content), items_per_page)]

    if len(list_content) > items_per_page:
        i = items_per_page * page
        for item in pages[int(page)]:
            i += 1
            builder.row(InlineKeyboardButton(text=f'Товар {i}', callback_data=CallProductContent(action='open_content', id=f'{item[0]}').pack()))
        builder.row(InlineKeyboardButton(text='«', callback_data=PaginatorContent(array_name='content_inf', page=f'{page}', max_pages=f'{len(pages)}', button='back', product_id=product_id).pack()), InlineKeyboardButton(text='»', callback_data=PaginatorContent(array_name='content_inf', page=f'{page}', max_pages=f'{len(pages)}', button='next', product_id=product_id).pack()), width=2)
    else:
        for item in list_content:
            i += 1
            builder.row(InlineKeyboardButton(text=f'Товар {i}', callback_data=CallProductContent(action='open_content', id=f'{item[0]}').pack()))
            

    builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ', callback_data=CallProductContent(action='add_content', id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product_id}').pack()))

    return builder



def product_content_kb(content_id, product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=CallProductContent(action='delete_product_content', id=f'{content_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=EditProductINF(edit_product='edit_inf', what_to_edit='product_contents', product_id=f'{product_id}').pack()))
    
    return builder


def delete_product_inf_product(product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='ДА, Я УВЕРЕН!', callback_data=EditProductINF(edit_product='delete_inf', what_to_edit='delete_inf', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListProductsInf(open_product_inf='open_inf', product_id=f'{product_id}').pack()))

    return builder