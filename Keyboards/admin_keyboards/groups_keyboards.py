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


class PaginatorCP(CallbackData, prefix='call'):
    array_name: str
    button: str
    page: str
    max_pages: str
    group_id: str
    project_id: str
    product_type: str
    parent_id: str

class ListGroups(CallbackData, prefix='call'):
    action: str
    group_id: str
    parent_id: str
    group_lvl: str


class AddProductToGroup(CallbackData, prefix='call'):
    action: str
    category_name: str
    project_id: str
    group_id: str
    parent_id: str
    page: str
    product_id: str


class PicturesGroup(CallbackData, prefix='call'):
    action: str
    picture_id: str
    group_id: str
    parent_id: str


def user_groups_kb(bot_username, page):
    builder = InlineKeyboardBuilder()
    project_id = db.get_project_id(bot_username=bot_username)

    parent_group = db.get_all_groups(project_id=project_id)

    list_groups = db.get_list_groups(bot_username=bot_username, parent_id=parent_group[0][0])

    items_per_page = 20
    pages = [list_groups[i:i + items_per_page] for i in range(0, len(list_groups), items_per_page)]

    
    if len(list_groups) > items_per_page:
        for group in pages[int(page)]:
            builder.row(InlineKeyboardButton(text=f'{group[3]}', callback_data=ListGroups(action='open_group', group_id=f'{group[0]}', parent_id=f'{group[1]}', group_lvl=f'{group[7]}').pack()))
        builder.row(InlineKeyboardButton(text='«', callback_data=Paginator(array_name='pag_main_group', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=Paginator(array_name='pag_main_group', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    elif pages == []:
        pass
    else:
        for group in pages[int(page)]:
            builder.row(InlineKeyboardButton(text=f'{group[3]}', callback_data=ListGroups(action='open_group', group_id=f'{group[0]}', parent_id=f'{group[1]}', group_lvl=f'{group[7]}').pack()))
        

    builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ГРУППУ', callback_data=ListGroups(action='add_new_group', group_id=f'{parent_group[0][0]}', parent_id=f'{parent_group[0][0]}', group_lvl=f'{parent_group[0][7]}').pack()))
    builder.row(InlineKeyboardButton(text='🛍️ Товары', callback_data=ListGroups(action='add_product_to_group',  group_id='null', parent_id='-1', group_lvl='0').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='products'))

    return builder



def cancel_add_new_group(group_id, parent_id, project_id):
    builder = InlineKeyboardBuilder()

    parent_group_id = db.get_parent_id(project_id=project_id)

    if parent_id == f'{parent_group_id[0][0]}':
        builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data='groups'))
    else:
        builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListGroups(action='open_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='null').pack()))

    return builder



def user_groups_next_lvl(parent_id, group_id, group_lvl, project_id, page):
    builder = InlineKeyboardBuilder()

    list_group = db.get_parent_groups(group_id=group_id)
    parent_group_id = db.get_parent_id(project_id=project_id)[0][0]

    items_per_page = 20
    pages = [list_group[i:i + items_per_page] for i in range(0, len(list_group), items_per_page)]

    if len(list_group) > items_per_page:
        for group in pages[int(page)]:
            builder.row(InlineKeyboardButton(text=f'{group[3]}', callback_data=ListGroups(action='open_group', group_id=f'{group[0]}', parent_id=f'{group[1]}', group_lvl=f'{group[7]}').pack()))
        builder.row(InlineKeyboardButton(text='«', callback_data=PaginatorCP(array_name='pag_groups', parent_id=f'{parent_id}', product_type=f'none',  group_id=f'{group_id}', project_id=f'{project_id}', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=PaginatorCP(array_name='pag_groups', parent_id=f'{parent_id}', product_type=f'none', group_id=f'{group_id}', project_id=f'{project_id}', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for group in list_group:
            builder.row(InlineKeyboardButton(text=f'{group[3]}', callback_data=ListGroups(action='open_group', group_id=f'{group[0]}', parent_id=f'{group[1]}', group_lvl=f'{group[7]}').pack()))


    builder.row(InlineKeyboardButton(text='НАЗВАНИЕ', callback_data=ListGroups(action='edit_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='group_name').pack()), InlineKeyboardButton(text='🌄 ФОТО', callback_data=ListGroups(action='edit_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='group_photo').pack()), InlineKeyboardButton(text='ОПИСАНИЕ', callback_data=ListGroups(action='edit_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='group_description').pack()), width=3)
    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=ListGroups(action='edit_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='delete_group').pack()), InlineKeyboardButton(text='🛍️ Товары', callback_data=ListGroups(action='add_product_to_group',  group_id=f'{group_id}', parent_id=f'{group_id}', group_lvl=f'{group_lvl}').pack()))
    if group_lvl != 5:
        builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ГРУППУ', callback_data=ListGroups(action='add_new_group', group_id=f'{group_id}', parent_id=f'{group_id}', group_lvl=f'{group_lvl}').pack()))
    
    if parent_id == parent_group_id:
        builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='groups'))
    else:
        builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListGroups(action='open_group', group_id=f'{parent_id}', parent_id=f'{group_id}', group_lvl=f'{group_lvl}').pack()))

    return builder












def edit_group_picture(parent_id, group_id, group_lvl):
    builder = InlineKeyboardBuilder()

    list_pic = db.get_group_pictures(group_id=group_id)
    i = 0

    for picture in list_pic:
        i += 1
        builder.row(InlineKeyboardButton(text=f'ФОТО {i}', callback_data=PicturesGroup(action='open_group_picture', picture_id=f'{picture[0]}', group_id=f'{group_id}', parent_id=f'{parent_id}').pack()))

    if len(list_pic) == 0:
        builder.row(InlineKeyboardButton(text='➕ ДОБАВИТЬ ФОТО', callback_data=PicturesGroup(action='add_new_group_picture', picture_id='no', group_id=f'{group_id}', parent_id=f'{parent_id}').pack()))

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListGroups(action='open_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl=f'{group_lvl}').pack()))

    return builder

def group_picture_kb(group_id, parent_id, picture_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🗑 УДАЛИТЬ', callback_data=PicturesGroup(action='delete_group_picture', picture_id=f'{picture_id}', group_id=f'{group_id}', parent_id=f'{parent_id}').pack()))
    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListGroups(action='edit_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='group_photo').pack()))

    return builder


def cancel_add_new_group_picture(group_id, parent_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListGroups(action='edit_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='group_photo').pack()))

    return builder




def cancel_edit_group(group_id, parent_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListGroups(action='open_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='null').pack()))

    return builder



def delete_group(group_id, parent_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='ДА, Я УВЕРЕН!', callback_data=ListGroups(action='edit_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='yes_delete_group').pack()))
    builder.row(InlineKeyboardButton(text='🚫 ОТМЕНА', callback_data=ListGroups(action='open_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='null').pack()))

    return builder


# Выбираем товары, которые будут привязаны к группе 

def list_category_products(project_id, group_id, group_lvl, parent_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Подписка на канал', callback_data=AddProductToGroup(action='open_category',  product_id='null', group_id=f'{group_id}', parent_id=f'{parent_id}', category_name='channel', project_id=f'{project_id}', page='0').pack()))
    builder.row(InlineKeyboardButton(text='Инфопродокт', callback_data=AddProductToGroup(action='open_category', product_id='null', group_id=f'{group_id}', parent_id=f'{parent_id}', category_name='inf', project_id=f'{project_id}', page='0').pack()))
    builder.row(InlineKeyboardButton(text='Товар с доставкой', callback_data=AddProductToGroup(action='open_category',  product_id='null', group_id=f'{group_id}', parent_id=f'{parent_id}', category_name='delivery', project_id=f'{project_id}', page='0').pack()))

    if parent_id == '-1':
        builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data='groups'))
    else:
        builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListGroups(action='open_group', group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl=f'{group_lvl}').pack()))

    return builder


def list_products_in_category(project_id, product_type, group_id, parent_id, selected, page):
    builder = InlineKeyboardBuilder()

    list_product = db.get_list_products_to_groups(project_id=project_id, product_type=f'{product_type}')

    items_per_page = 20
    pages = [list_product[i:i + items_per_page] for i in range(0, len(list_product), items_per_page)]

    if len(list_product) > items_per_page:
        for product in pages[int(page)]:
            if str(product[0]) in selected:
                builder.row(InlineKeyboardButton(text=f'🔸 {product[8]}', callback_data=AddProductToGroup(action='choose_product', product_id=f'{product[0]}', group_id=f'{group_id}', parent_id=f'{parent_id}', category_name=f'{product_type}', project_id=f'{project_id}', page=f'{page}').pack()))
            else: 
                builder.row(InlineKeyboardButton(text=f'{product[8]}', callback_data=AddProductToGroup(action='choose_product', product_id=f'{product[0]}', group_id=f'{group_id}', parent_id=f'{parent_id}', category_name=f'{product_type}', project_id=f'{project_id}', page=f'{page}').pack()))
        builder.row(InlineKeyboardButton(text='«', callback_data=PaginatorCP(array_name='products_of_choice', parent_id=f'{parent_id}', product_type=f'{product_type}',  group_id=f'{group_id}', project_id=f'{project_id}', page=f'{page}', max_pages=f'{len(pages)}', button='back').pack()), InlineKeyboardButton(text='»', callback_data=PaginatorCP(array_name='products_of_choice', parent_id=f'{parent_id}', product_type=f'{product_type}', group_id=f'{group_id}', project_id=f'{project_id}', page=f'{page}', max_pages=f'{len(pages)}', button='next').pack()), width=2)
    else:
        for product in pages[int(page)]:
            if str(product[0]) in selected:
                builder.row(InlineKeyboardButton(text=f'🔸 {product[8]}', callback_data=AddProductToGroup(action='choose_product', product_id=f'{product[0]}', group_id=f'{group_id}', parent_id=f'{parent_id}', category_name=f'{product_type}', project_id=f'{project_id}', page=f'{page}').pack()))
            else: 
                builder.row(InlineKeyboardButton(text=f'{product[8]}', callback_data=AddProductToGroup(action='choose_product', product_id=f'{product[0]}', group_id=f'{group_id}', parent_id=f'{parent_id}', category_name=f'{product_type}', project_id=f'{project_id}', page=f'{page}').pack()))
    
    db.update_list_product_to_group(group_id=group_id, selected=selected)

    builder.row(InlineKeyboardButton(text='👈 НАЗАД', callback_data=ListGroups(action='add_product_to_group',  group_id=f'{group_id}', parent_id=f'{parent_id}', group_lvl='null').pack()))

    return builder