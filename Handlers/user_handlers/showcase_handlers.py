from aiogram import types, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from Database.User_db import Database


from Keyboards.user_keyboards.products_keyboards import(
    list_buttons_not_group,
    product_kb,
    open_group_kb,
    Showcase,
    PaginatorPictures,
    Paginator
)


db = Database()
router = Router()




def discount_calculation(price, discount):
    total_price = price - price / 100 * discount
    text = '<s>' + str(price)+'</s> ' + str(round(total_price))
    return text



# Возврат в группу или на главную страницу экрана

@router.callback_query(Showcase.filter(F.action == 'back_to_catalog'))
async def button_back_to_catalog(call: types.CallbackQuery, callback_data: Showcase):
    bot_data = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_data.username)


    if callback_data.identifier == '-1' or str(db.get_all_groups(project_id=project_id)[0][0]) == callback_data.identifier: # Если это главная витрина, то выполняется if

        if db.get_caption(caption='menu_caption', bot_username=bot_data.username) == '':
            menu_caption = 'Выберите товар для покупки:'
        else:
            menu_caption = str(db.get_caption(caption='menu_caption', bot_username=bot_data.username))    

        photo = db.get_group_photo(identifier=project_id, path='menu')


        if photo != []: # Если на продукте есть фото
            try:
                photo_id = types.InputMediaPhoto(media=f'{photo[0][3]}', caption=menu_caption)
                await call.message.edit_media(
                    media=photo_id,
                    reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
                )
            except:
                await call.message.delete()
                await call.message.answer_photo(
                    photo=photo[0][3],
                    caption=menu_caption,
                    reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
                )
        else:
            try:
                await call.message.edit_text(
                    text=menu_caption,
                    reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
                )
            except:
                await call.message.delete()
                await call.message.answer(
                    text=menu_caption,
                    reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
                )
    else: # Если это группа, то выполняется else

        group_data = db. get_group_data(group_id=callback_data.group_id)
        photo = db.get_group_photo(identifier=group_data[0][0], path='group')


        if photo != []: # Если на продукте есть фото
            try:
                photo_id = types.InputMediaPhoto(media=f'{photo[0][3]}', caption=group_data[0][4])
                await call.message.edit_media(
                    media=photo_id,
                    reply_markup=open_group_kb(
                        project_id=project_id,
                        group_id=group_data[0][0],
                        parent_id=group_data[0][1],
                        page=0
                    ).as_markup()
                )
            except:
                await call.message.delete()
                await call.message.answer_photo(
                    photo=photo[0][3],
                    caption=group_data[0][4],
                    reply_markup=open_group_kb(
                        project_id=project_id,
                        group_id=group_data[0][0],
                        parent_id=group_data[0][1],
                        page=0
                    ).as_markup()
                )
        else:
            try:
                await call.message.edit_text(
                    text=group_data[0][4],
                    reply_markup=open_group_kb(
                        project_id=project_id,
                        group_id=group_data[0][0],
                        parent_id=group_data[0][1],
                        page=0
                    ).as_markup()
                )
            except:
                await call.message.delete()
                await call.message.answer(
                    text=group_data[0][4],
                    reply_markup=open_group_kb(
                        project_id=project_id,
                        group_id=group_data[0][0],
                        parent_id=group_data[0][1],
                        page=0
                    ).as_markup()
                )



@router.message(F.text == '🖥 Главная')
async def button_menu(msg: types.Message):
    bot_data = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_data.username)

    menu_caption = ''
    photo = db.get_group_photo(identifier=project_id, path='menu')

    if db.get_caption(caption='menu_caption', bot_username=bot_data.username) == '':
        menu_caption = 'Выберите товар для покупки:'
    else:
        menu_caption = str(db.get_caption(caption='menu_caption', bot_username=bot_data.username))

    try:
        if photo != []:
            await msg.answer_photo(
                photo=photo[0][3],
                caption=menu_caption,
                reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
            )
        else:
            await msg.answer(
                text=menu_caption,
                reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
            )
    except:
        await msg.answer(
                text=menu_caption,
                reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
            )


@router.callback_query(F.data == 'call_back_to_menu')
async def button_back_to_menu(call: types.CallbackQuery):
    bot_data = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_data.username)

    menu_caption = ''

    if db.get_caption(caption='menu_caption', bot_username=bot_data.username) == '':
        menu_caption = 'Выберите товар для покупки:'
    else:
        menu_caption = str(db.get_caption(caption='menu_caption', bot_username=bot_data.username))

    photo = db.get_group_photo(identifier=project_id, path='menu')


    if photo != []: # Если на продукте есть фото
        try:
            photo_id = types.InputMediaPhoto(media=f'{photo[0][3]}', caption=menu_caption)
            await call.message.edit_media(
                media=photo_id,
                reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
            )
        except:
            await call.message.delete()
            await call.message.answer_photo(
                photo=photo[0][3],
                caption=menu_caption,
                reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
            )
    else:
        try:
            await call.message.edit_text(
                text=menu_caption,
                reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
            )
        except:
            await call.message.delete()
            await call.message.answer(
                text=menu_caption,
                reply_markup=list_buttons_not_group(project_id=project_id, page=0).as_markup()
            )


# Paginator

@router.callback_query(Paginator.filter(F.array_name == 'showcase_no_group'))
async def paginator_no_group(call: types.CallbackQuery, state: FSMContext, callback_data: Paginator):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    if db.get_caption(caption='menu_caption', bot_username=bot_username.username) == '':
        menu_caption = 'Выберите товар для покупки:'
    else:
        menu_caption = str(db.get_caption(caption='menu_caption', bot_username=bot_username.username))

    photo = db.get_group_photo(identifier=project_id, path='menu')


    if button == 'next':
        if page < max_pages-1:
            page += 1
            if photo != []: # Если на продукте есть фото
                try:
                    photo_id = types.InputMediaPhoto(media=f'{photo[0][3]}', caption=menu_caption)
                    await call.message.edit_media(
                        media=photo_id,
                        reply_markup=list_buttons_not_group(project_id=project_id, page=page).as_markup()
                    )
                except:
                    await call.message.delete()
                    await call.message.answer_photo(
                        photo=photo[0][3],
                        caption=menu_caption,
                        reply_markup=list_buttons_not_group(project_id=project_id, page=page).as_markup()
                    )
            else:
                try:
                    await call.message.edit_text(
                        text=menu_caption,
                        reply_markup=list_buttons_not_group(project_id=project_id, page=page).as_markup()
                    )
                except:
                    await call.message.delete()
                    await call.message.answer(
                        text=menu_caption,
                        reply_markup=list_buttons_not_group(project_id=project_id, page=page).as_markup()
                    )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            if photo != []: # Если на продукте есть фото
                try:
                    photo_id = types.InputMediaPhoto(media=f'{photo[0][3]}', caption=menu_caption)
                    await call.message.edit_media(
                        media=photo_id,
                        reply_markup=list_buttons_not_group(project_id=project_id, page=page).as_markup()
                    )
                except:
                    await call.message.delete()
                    await call.message.answer_photo(
                        photo=photo[0][3],
                        caption=menu_caption,
                        reply_markup=list_buttons_not_group(project_id=project_id, page=page).as_markup()
                    )
            else:
                try:
                    await call.message.edit_text(
                        text=menu_caption,
                        reply_markup=list_buttons_not_group(project_id=project_id, page=page).as_markup()
                    )
                except:
                    await call.message.delete()
                    await call.message.answer(
                        text=menu_caption,
                        reply_markup=list_buttons_not_group(project_id=project_id, page=page).as_markup()
                    )
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()




# Открытия продукта

@router.callback_query(Showcase.filter(F.action == 'open_product'))
async def user_open_product(call: types.CallbackQuery, callback_data: Showcase):
    product_data = db.get_product_data(product_id=callback_data.identifier)


    if product_data[0][10] == []: # Проверяем, есть ли фото на товаре. Если true, то фото нет
        if product_data[0][2] == 'channel': # Проверяем, является ли товар количественным. Если true, то товар не является количественным
            try:
                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                
                await call.message.edit_text(
                    text=caption,
                    reply_markup=product_kb(product_id=f'{callback_data.identifier}', group_id=f'{callback_data.group_id}', page=0).as_markup()
                )   
            except:
                await call.message.delete()

                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                await call.message.answer(
                    text=caption,
                    reply_markup=product_kb(product_id=f'{callback_data.identifier}', group_id=f'{callback_data.group_id}', page=0).as_markup()
                )
        else:
            try:
                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Осталось:</b> {product_data[0][11]}
<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                
                await call.message.edit_text(
                    text=caption,
                    reply_markup=product_kb(product_id=f'{callback_data.identifier}', group_id=f'{callback_data.group_id}', page=0).as_markup()
                )

            except:
                await call.message.delete()

                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Осталось:</b> {product_data[0][11]}
<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                
                await call.message.answer(
                    text=caption,
                    reply_markup=product_kb(product_id=f'{callback_data.identifier}', group_id=f'{callback_data.group_id}', page=0).as_markup()
                )
    else:
        if (product_data[0][2] == 'channel'): # Проверяем, является ли товар количественным. Если true, то товар не является количественным
            try: # Если все без ошибок, то редактируем действующее сообщение с фото
                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                
                photo = types.InputMediaPhoto(media=f'{db.get_product_photos(product_id=product_data[0][0])[0]}', caption=caption)

                await call.message.edit_media(
                    media=photo,
                    reply_markup=product_kb(product_id=f'{callback_data.identifier}', group_id=f'{callback_data.group_id}', page=0).as_markup()
                )
            except: # При возникновении ошибки, удаляем сообщение и отправляем новое с фото
                await call.message.delete()

                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''     
                await call.message.answer_photo(
                    photo=f'{db.get_product_photos(product_id=product_data[0][0])[0]}',
                    caption=caption,
                    reply_markup=product_kb(product_id=f'{callback_data.identifier}', group_id=f'{callback_data.group_id}', page=0).as_markup()
                )
        else:
            try:
                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Осталось:</b> {product_data[0][11]}
<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                photo = types.InputMediaPhoto(media=f'{db.get_product_photos(product_id=product_data[0][0])[0]}', caption=caption)

                await call.message.edit_media(
                    media=photo,
                    reply_markup=product_kb(product_id=f'{callback_data.identifier}', group_id=f'{callback_data.group_id}', page=0).as_markup()
                )

            except:
                await call.message.delete()

                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Осталось:</b> {product_data[0][11]}
<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                await call.message.answer_photo(
                    photo=f'{db.get_product_photos(product_id=product_data[0][0])[0]}',
                    caption=caption,
                    reply_markup=product_kb(product_id=f'{callback_data.identifier}', group_id=f'{callback_data.group_id}', page=0).as_markup()
                )        



# Пагинатор для фото товара

@router.callback_query(PaginatorPictures.filter(F.action == 'paginator_pictures'))
async def paginator_pictures(call: types.CallbackQuery, callback_data: PaginatorPictures):
    product_data = db.get_product_data(product_id=callback_data.product_id)

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_page)

    if product_data[0][2] == 'channel': # Проверяем, является ли товар количественным. Если true, то товар не является количественным  
        caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
    else:
        caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Осталось:</b> {product_data[0][11]}
<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''


    try:
        if button == 'next':
            if page < max_pages-1:
                page += 1

                photo = types.InputMediaPhoto(media=f'{db.get_product_photos(product_id=product_data[0][0])[page]}', caption=caption)

                await call.message.edit_media(
                    media=photo,
                    reply_markup=product_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, page=page).as_markup()
                )
            else:
                await call.answer(text='Это последнее фото')
        else:
            if page > 0:
                page -= 1

                photo = types.InputMediaPhoto(media=f'{db.get_product_photos(product_id=product_data[0][0])[page]}', caption=caption)

                await call.message.edit_media(
                    media=photo,
                    reply_markup=product_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, page=page).as_markup()
                )
            else:
                await call.answer(text='Это первое фото')
    except:
        await call.answer(text='Что-то пошло не так😵')






# Открываем группу

@router.callback_query(Showcase.filter(F.action == 'open_group'))
async def user_open_group(call: types.CallbackQuery, callback_data: Showcase):
    bot_data = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_data.username)

    group_data = db.get_group_data(group_id=callback_data.group_id)
    photo = db.get_group_photo(identifier=group_data[0][0], path='group')


    if photo != []: # Если на продукте есть фото
        try:
            photo_id = types.InputMediaPhoto(media=f'{photo[0][3]}', caption=group_data[0][4])
            await call.message.edit_media(
                media=photo_id,
                reply_markup=open_group_kb(
                    project_id=project_id,
                    group_id=group_data[0][0],
                    parent_id=group_data[0][1],
                    page=0
                ).as_markup()
            )
        except:
            await call.message.delete()
            await call.message.answer_photo(
                photo=photo[0][3],
                caption=group_data[0][4],
                reply_markup=open_group_kb(
                    project_id=project_id,
                    group_id=group_data[0][0],
                    parent_id=group_data[0][1],
                    page=0
                ).as_markup()
            )
    else:
        try:
            await call.message.edit_text(
                text=group_data[0][4],
                reply_markup=open_group_kb(
                    project_id=project_id,
                    group_id=group_data[0][0],
                    parent_id=group_data[0][1],
                    page=0
                ).as_markup()
            )
        except:
            await call.message.delete()
            await call.message.answer(
                text=group_data[0][4],
                reply_markup=open_group_kb(
                    project_id=project_id,
                    group_id=group_data[0][0],
                    parent_id=group_data[0][1],
                    page=0
                ).as_markup()
            )



#Paginator

@router.callback_query(Paginator.filter(F.array_name == 'showcase_in_group'))
async def paginator_in_group(call: types.CallbackQuery, state: FSMContext, callback_data: Paginator):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    group_data = db.get_group_data(group_id=callback_data.data)
    photo = db.get_group_photo(identifier=group_data[0][0], path='group')


    if button == 'next':
        if page < max_pages-1:
            page += 1
            if photo != []: # Если на продукте есть фото
                try:
                    photo_id = types.InputMediaPhoto(media=f'{photo[0][3]}', caption=group_data[0][4])
                    await call.message.edit_media(
                        media=photo_id,
                        reply_markup=open_group_kb(
                            project_id=project_id,
                            group_id=group_data[0][0],
                            parent_id=group_data[0][1],
                            page=page
                        ).as_markup()
                    )
                except:
                    await call.message.delete()
                    await call.message.answer_photo(
                        photo=photo[0][3],
                        caption=group_data[0][4],
                        reply_markup=open_group_kb(
                            project_id=project_id,
                            group_id=group_data[0][0],
                            parent_id=group_data[0][1],
                            page=page
                        ).as_markup()
                    )
            else:
                try:
                    await call.message.edit_text(
                        text=group_data[0][4],
                        reply_markup=open_group_kb(
                            project_id=project_id,
                            group_id=group_data[0][0],
                            parent_id=group_data[0][1],
                            page=page
                        ).as_markup()
                    )
                except:
                    await call.message.delete()
                    await call.message.answer(
                        text=group_data[0][4],
                        reply_markup=open_group_kb(
                            project_id=project_id,
                            group_id=group_data[0][0],
                            parent_id=group_data[0][1],
                            page=page
                        ).as_markup()
                    )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            if photo != []: # Если на продукте есть фото
                try:
                    photo_id = types.InputMediaPhoto(media=f'{photo[0][3]}', caption=group_data[0][4])
                    await call.message.edit_media(
                        media=photo_id,
                        reply_markup=open_group_kb(
                            project_id=project_id,
                            group_id=group_data[0][0],
                            parent_id=group_data[0][1],
                            page=page
                        ).as_markup()
                    )
                except:
                    await call.message.delete()
                    await call.message.answer_photo(
                        photo=photo[0][3],
                        caption=group_data[0][4],
                        reply_markup=open_group_kb(
                            project_id=project_id,
                            group_id=group_data[0][0],
                            parent_id=group_data[0][1],
                            page=page
                        ).as_markup()
                    )
            else:
                try:
                    await call.message.edit_text(
                        text=group_data[0][4],
                        reply_markup=open_group_kb(
                            project_id=project_id,
                            group_id=group_data[0][0],
                            parent_id=group_data[0][1],
                            page=page
                        ).as_markup()
                    )
                except:
                    await call.message.delete()
                    await call.message.answer(
                        text=group_data[0][4],
                        reply_markup=open_group_kb(
                            project_id=project_id,
                            group_id=group_data[0][0],
                            parent_id=group_data[0][1],
                            page=page
                        ).as_markup()
                    )
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()
