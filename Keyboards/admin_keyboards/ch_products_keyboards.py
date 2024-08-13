from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from Database.Admin_db import Database

db = Database()







# Кнопки для раздела РЕСУРСЫ 


class Paginator(CallbackData, prefix='call'):
    array_name: str
    button: str
    page: str
    max_pages: str






# Кнопки для раздела с товарами

class AddProductsChannel(CallbackData, prefix='call'):
    project_id: str
    add_product_channel: str

class ListResourcesChoose(CallbackData, prefix='call'):
    choose: str
    resource_id: str
    page: str

class ListProductsChannel(CallbackData, prefix='call'):
    open_product_channel: str
    product_id: str

class EditProductChannel(CallbackData, prefix='call'):
    edit_product: str
    what_to_edit: str
    product_id: str

class ListPicturesCh(CallbackData, prefix='call'):
    action: str
    picture_id: str
    product_id: str




def user_products_channel_kb(project_id, page):
    builder = InlineKeyboardBuilder()

    products = db.get_list_products(project_id=project_id, product_type='channel')
    items_per_page = 20
    pages = [products[i:i + items_per_page] for i in range(0, len(products), items_per_page)]

    if len(products) > items_per_page:
        for product in pages[page]:
            if product[3] == 'включен':
                builder.row(InlineKeyboardButton(text=f'{product[8]}', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'💤 {product[8]}', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product[0]}').pack()))
 
        builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='products_channel', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='products_channel', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for product in products:
            if product[3] == 'включен':
                builder.row(InlineKeyboardButton(text=f'{product[8]}', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'💤 {product[8]}', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product[0]}').pack()))
    
    
    builder.row(InlineKeyboardButton(text='🔗 Ресурсы', callback_data="resources"), InlineKeyboardButton(text='➕ ДОБАВИТЬ', callback_data=AddProductsChannel(add_product_channel='add_product_channel', project_id=f'{project_id}').pack()), width=2)
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='products'))


    return builder


def list_resources_choose(bot_username, selected, page):
    builder = InlineKeyboardBuilder()

    resources = db.get_list_resources(bot_username=bot_username)
    items_per_page = 20
    pages = [resources[i:i + items_per_page] for i in range(0, len(resources), items_per_page)]

    if len(resources) > items_per_page:
        for resource in pages[int(page)]:
            if str(resource[0]) in selected:
                builder.row(InlineKeyboardButton(text=f'🔸 {resource[2]}', callback_data=ListResourcesChoose(choose='choose', page=f'{page}', resource_id=f'{resource[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'{resource[2]}', callback_data=ListResourcesChoose(choose='choose', page=f'{page}', resource_id=f'{resource[0]}').pack()))

        builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='resource_of_choice', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='resource_of_choice', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for resource in pages[int(page)]:
            if str(resource[0]) in selected:
                builder.row(InlineKeyboardButton(text=f'🔸 {resource[2]}', callback_data=ListResourcesChoose(choose='choose', page=f'{page}', resource_id=f'{resource[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'{resource[2]}', callback_data=ListResourcesChoose(choose='choose', page=f'{page}', resource_id=f'{resource[0]}').pack()))


    builder.row(InlineKeyboardButton(text='✅ Продолжить', callback_data='made_a_choice'))

    return builder


def cancel_add_new_ch_product():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='information_products'))

    return builder



def product_channel_kb(product_id):
    builder = InlineKeyboardBuilder()

    product_data = db.get_product_data(product_id=product_id)

    builder.row(InlineKeyboardButton(text='🌄 ФОТО', callback_data=EditProductChannel(edit_product='edit', what_to_edit='picture', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='🔖 НАЗВАНИЕ', callback_data=EditProductChannel(edit_product='edit', what_to_edit='product_name', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='📝 ОПИСАНИЕ', callback_data=EditProductChannel(edit_product='edit', what_to_edit='product_discription', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='💰 СТОИМОСТЬ', callback_data=EditProductChannel(edit_product='edit', what_to_edit='price', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='🏷 СКИДКА', callback_data=EditProductChannel(edit_product='edit', what_to_edit='discount', product_id=f'{product_id}').pack()), width=2)

    if product_data[0][3] == 'включен':
        builder.row(InlineKeyboardButton(text='🔗 РЕСУРСЫ', callback_data=EditProductChannel(edit_product='edit', what_to_edit='resources', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='✅ ВКЛЮЧЕН', callback_data=EditProductChannel(edit_product='edit', what_to_edit='display_status_of', product_id=f'{product_id}').pack()))
    else:
        builder.row(InlineKeyboardButton(text='🔗 РЕСУРСЫ', callback_data=EditProductChannel(edit_product='edit', what_to_edit='resources', product_id=f'{product_id}').pack()), InlineKeyboardButton(text='💤 ВЫКЛЮЧЕН', callback_data=EditProductChannel(edit_product='edit', what_to_edit='display_status_on', product_id=f'{product_id}').pack()))

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=EditProductChannel(edit_product='edit', what_to_edit='delete_product', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='products_channel'))

    return builder





def edit_pictures_ch(product_id):
    builder = InlineKeyboardBuilder()

    list_pic = db.get_list_pictures(product_id=product_id)
    i = 0

    for picture in list_pic:
        i += 1
        builder.row(InlineKeyboardButton(text=f'ФОТО {i}', callback_data=ListPicturesCh(action='open_picture_ch', picture_id=f'{picture[0]}', product_id=f'{product_id}').pack()))

    if len(list_pic) < 15:
        builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ФОТО', callback_data=ListPicturesCh(action='add_picture_ch', picture_id='no', product_id=f'{product_id}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product_id}').pack()))

    return builder


def picture_ch_kb(picture_id, product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=ListPicturesCh(action='delete_picture_ch', picture_id=f'{picture_id}', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListPicturesCh(action='back_from_photo_ch', picture_id='no', product_id=f'{product_id}').pack()))

    return builder



def cancel_add_picture_ch(product_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=EditProductChannel(edit_product='edit', what_to_edit='picture', product_id=f'{product_id}').pack()))

    return builder


def return_list_picture_ch(product_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=EditProductChannel(edit_product='edit', what_to_edit='picture', product_id=f'{product_id}').pack()))

    return builder



def cancel_inline_kb(product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product_id}').pack()))

    return builder

def return_product_channel_kb(product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='✅ ВЕРНУТЬСЯ К ТОВАРУ', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product_id}').pack()))

    return builder



def edit_list_resources_choose(bot_username, selected, product_id, page):
    builder = InlineKeyboardBuilder()


    resources = db.get_list_resources(bot_username=bot_username)
    items_per_page = 20
    pages = [resources[i:i + items_per_page] for i in range(0, len(resources), items_per_page)]

    if len(resources) > items_per_page:
        for resource in pages[int(page)]:
            if str(resource[0]) in selected:
                builder.row(InlineKeyboardButton(text=f'🔸 {resource[2]}', callback_data=ListResourcesChoose(choose='edit_choose_resources', page=f'{page}', resource_id=f'{resource[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'{resource[2]}', callback_data=ListResourcesChoose(choose='edit_choose_resources', page=f'{page}', resource_id=f'{resource[0]}').pack()))

        builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='edit_resource_of_choice', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='edit_resource_of_choice', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for resource in pages[int(page)]:
            if str(resource[0]) in selected:
                builder.row(InlineKeyboardButton(text=f'🔸 {resource[2]}', callback_data=ListResourcesChoose(choose='edit_choose_resources', page=f'{page}', resource_id=f'{resource[0]}').pack()))
            else:
                builder.row(InlineKeyboardButton(text=f'{resource[2]}', callback_data=ListResourcesChoose(choose='edit_choose_resources', page=f'{page}', resource_id=f'{resource[0]}').pack()))

    db.update_resources_product_channel(product_id=product_id, resources=selected)

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product_id}').pack()))


    return builder


def delete_product_ch(product_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='ДА, Я УВЕРЕН!', callback_data=EditProductChannel(edit_product='delete', what_to_edit='delete', product_id=f'{product_id}').pack()))
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListProductsChannel(open_product_channel='open', product_id=f'{product_id}').pack()))

    return builder


def return_list_products_ch():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='👈 К СПИСКУ ТОВАРОВ', callback_data='products_channel'))

    return builder