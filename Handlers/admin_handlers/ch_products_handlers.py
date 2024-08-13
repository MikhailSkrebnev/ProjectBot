from aiogram import types, F, Router
from aiogram.filters import or_f
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link


from Database.Admin_db import Database


from Keyboards.admin_keyboards.ch_products_keyboards import(
    user_products_channel_kb,
    list_resources_choose,
    product_channel_kb,
    cancel_add_picture_ch,
    cancel_inline_kb,
    edit_list_resources_choose,
    return_product_channel_kb,
    delete_product_ch,
    edit_pictures_ch,
    picture_ch_kb,
    return_list_picture_ch,
    cancel_add_new_ch_product,
    return_list_products_ch,
    AddProductsChannel,
    ListPicturesCh,
    ListProductsChannel,
    ListResourcesChoose,
    EditProductChannel,
    Paginator
)



db = Database()
router = Router()


class Add_Product_Channel(StatesGroup):
    add_product = State()
    project_id = State()
    product_name = State()
    product_discription = State()
    product_price = State()
    product_resources = State()

class Edit_Product_Channel(StatesGroup):
    edit_product = State()
    product_id = State()
    what_to_edit = State()






@router.callback_query(F.data == 'products_channel')
async def call_products_channel(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = f'''
<b>Список добавленных товаров:</b>
'''

    await call.message.edit_text(
        text=caption, 
        reply_markup=user_products_channel_kb(project_id=project_id, page=0).as_markup()
    )

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()


# Пагинатор

@router.callback_query(Paginator.filter(F.array_name == 'products_channel'))
async def paginator_products_channel(call: types.CallbackQuery, state: FSMContext, callback_data: Paginator):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    caption = f'''
<b>Список добавленных товаров:</b>
'''

    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(text=caption, reply_markup=user_products_channel_kb(project_id=project_id, page=page).as_markup())
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(text=caption, reply_markup=user_products_channel_kb(project_id=project_id, page=page).as_markup())
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()
    



# OPEN PRODUCT (CHANNEL)

@router.callback_query(ListProductsChannel.filter(F.open_product_channel == 'open'))
async def open_product_channel(call: types.CallbackQuery, callback_data: ListProductsChannel, state: FSMContext):
    product_data = db.get_product_data(product_id=callback_data.product_id)

    link = await create_start_link(call.bot, f'{product_data[0][0]}', encode=True)
    list_resources = '\n'

    for resource in product_data[0][5]:
        list_resources += '- Канал ' + f'{db.get_data_resources(resource_id=resource)[0][2]}' + '\n'

    total_price = product_data[0][6]

    if product_data[0][7] > 0:
        total_price = total_price - total_price / 100 * product_data[0][7]

    caption = f'''
<b>Название товара:</b> {product_data[0][8]} 
<b>Описание товара:</b> {product_data[0][9]} 

<b>Стоимость товара:</b> {product_data[0][6]} 🇷🇺RUB
<b>Скидка на товар:</b> {product_data[0][7]} %
<b>Итоговая цена:</b> {round(total_price)} 🇷🇺RUB

<b>Количество продаж:</b> {product_data[0][13]}
<b>Ресурсы, которые привязанаы к товару:</b> {list_resources}

<b>Ссылка на товар:</b> {link}
'''
    
    await call.message.edit_text(
        text=caption,
        reply_markup=product_channel_kb(product_data[0][0]).as_markup()
    )

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()



# Добавление нового товара

@router.callback_query(AddProductsChannel.filter(F.add_product_channel == 'add_product_channel'))
async def call_add_product_channel(call: types.CallbackQuery, callback_data: AddProductsChannel, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if db.check_list_resources(project_id=project_id) != []:
        await call.message.edit_text('Как будет называться твой товар?', reply_markup=cancel_add_new_ch_product().as_markup())

        await state.set_state(Add_Product_Channel.add_product)
        await state.update_data(project_id=callback_data.project_id)
    else:
        await call.answer(
            text='Добавь хотя бы один ресур 😉',
            show_alert=True
        )




@router.message(Add_Product_Channel.add_product, F.text)
async def get_name_product(msg: types.Message, state: FSMContext):

    if len(msg.text) > 24:
        await msg.answer('Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов', reply_markup=cancel_add_new_ch_product().as_markup())
    else:
        await state.update_data(product_name=msg.text)
        await state.set_state(Add_Product_Channel.product_discription)
        await msg.answer('Какое будет описание товара?', reply_markup=cancel_add_new_ch_product().as_markup())


@router.message(Add_Product_Channel.product_discription, F.text)
async def get_description_product(msg: types.Message, state: FSMContext):

    if len(msg.html_text) > 1024:
        await msg.answer('Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 1024 символов', reply_markup=cancel_add_new_ch_product().as_markup())
    else:
        await state.update_data(product_discription=msg.html_text)
        await state.set_state(Add_Product_Channel.product_price)
        await msg.answer('Какая будет стоимость товара?', reply_markup=cancel_add_new_ch_product().as_markup())


@router.message(Add_Product_Channel.product_price, F.text)
async def get_description_product(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()

    if msg.text.isdigit() and int(msg.text) > 0:
        await state.update_data(product_price=msg.text)
        await state.set_state(Add_Product_Channel.product_resources)

        selected = [] # Задаем пустой список выбранных ресурсов
        await state.update_data(product_resources=selected)

        await msg.answer('Теперь из списка выбери канал(ы), которые кочешь привязать к товару😉', reply_markup=list_resources_choose(bot_username=bot_username.username, selected=selected, page=0).as_markup())
    else:
        await msg.answer('Пришли целое число больше 0 RUB 😉', reply_markup=cancel_add_new_ch_product().as_markup())


@router.callback_query(Add_Product_Channel.product_resources, ListResourcesChoose.filter(F.choose == 'choose'))
async def choose_resource(call: types.CallbackQuery, callback_data: ListResourcesChoose, state: FSMContext):
    bot_username = await call.bot.get_me()
    getFSM = await state.get_data()
    
    # --------------- Здесь обновляем список ресурсов, которые были выбраны пользователем
    selected = getFSM.get('product_resources')
    if callback_data.resource_id in selected:
        selected.remove(f'{callback_data.resource_id}')
    else:
        selected.append(callback_data.resource_id)
    await state.update_data(product_resources=selected)
    # ---------------

    await call.message.edit_text(
        text='Теперь из списка выбери канал(ы), которые кочешь привязать к товару😉', 
        reply_markup=list_resources_choose(bot_username=bot_username.username, selected=selected, page=callback_data.page).as_markup()
    )


# Пагинатор для привязывания ресурсов к товару

@router.callback_query(Paginator.filter(F.array_name == 'resource_of_choice'))
async def paginator_resource_of_choice(call: types.CallbackQuery, callback_data: Paginator, state: FSMContext):
    bot_username = await call.bot.get_me()
    getFSM = await state.get_data()
    selected = getFSM.get('product_resources')

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    
    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text='Теперь из списка выбери канал(ы), которые кочешь привязать к товару😉', 
                reply_markup=list_resources_choose(bot_username=bot_username.username, selected=selected, page=page).as_markup()
            )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text='Теперь из списка выбери канал(ы), которые кочешь привязать к товару😉', 
                reply_markup=list_resources_choose(bot_username=bot_username.username, selected=selected, page=page).as_markup()
            )  
        else:
            await call.answer(text='Это начало страницы')



@router.callback_query(Add_Product_Channel.product_resources, F.data == 'made_a_choice')
async def produc_created(call: types.CallbackQuery, state: FSMContext):
    getFSM = await state.get_data()

    if getFSM.get('product_resources') == []:
        await call.answer('Нужно выбрать хотя бы 1 ресурс🙏', show_alert=True)
    else:
        db.add_product(
            project_id=getFSM.get('project_id'),
            product_type='channel',
            reusable='False',
            contents=getFSM.get('product_resources'),
            product_price=getFSM.get('product_price'),
            product_name=getFSM.get('product_name'),
            product_description=getFSM.get('product_discription'),
            product_photo=[]
        )

        product_data = db.get_last_product(project_id=getFSM.get('project_id'), product_type='channel')

        link = await create_start_link(call.bot, f'{product_data[0][0]}', encode=True)
        list_resources = '\n'

        for resource in product_data[0][5]:
            list_resources += '- Канал ' + f'{db.get_data_resources(resource_id=resource)[0][2]}' + '\n'

        total_price = product_data[0][6]

        if product_data[0][7] > 0:
            total_price = total_price - total_price / 100 * product_data[0][7]

        caption = f'''
<b>Название товара:</b> {product_data[0][8]} 
<b>Описание товара:</b> {product_data[0][9]} 

<b>Стоимость товара:</b> {product_data[0][6]} 🇷🇺RUB
<b>Скидка на товар:</b> {product_data[0][7]} %
<b>Итоговая цена:</b> {round(total_price)} 🇷🇺RUB

<b>Количество продаж:</b> {product_data[0][13]}
<b>Ресурсы, которые привязанаы к товару:</b> {list_resources}

<b>Ссылка на товар:</b> {link}
'''
    
        await call.message.edit_text(
            text=caption,
            reply_markup=product_channel_kb(product_data[0][0]).as_markup()
        )


        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
        
        await state.clear()




#------------ Редактирование товара

class Edit_Resources(StatesGroup):
    new_resources_list = State()


@router.callback_query(EditProductChannel.filter(F.edit_product == 'edit'))
async def edit_product_channel(call: types.CallbackQuery, callback_data: EditProductChannel, state: FSMContext):
    bot_username = await call.bot.get_me()
    list_active_resources = db.get_list_active_resources(callback_data.product_id)[0][0]

    await state.update_data(product_id=callback_data.product_id)


    if callback_data.what_to_edit == 'price':
        await state.set_state(Edit_Product_Channel.edit_product)
        await state.update_data(what_to_edit='price')
        await call.message.edit_text(
            text='Какая будет новая стоимость товара?',
            reply_markup=cancel_inline_kb(callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'picture':
        caption = '''
📸 <b>Добавь фото для товара, которое будет отображаться у покупателя!</b>

🖼️ Яркое и привлекательное фото - это ключ к успешной продаже!
'''
        await call.message.edit_text(text=caption, reply_markup=edit_pictures_ch(product_id=callback_data.product_id).as_markup())
        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
            
        await state.clear()
    elif callback_data.what_to_edit == 'discount':
        await state.set_state(Edit_Product_Channel.edit_product)
        await state.update_data(what_to_edit='discount')
        await call.message.edit_text(
            text='Пришли новую скидку на товар от 0 до 99',
            reply_markup=cancel_inline_kb(callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'product_name':
        await state.set_state(Edit_Product_Channel.edit_product)
        await state.update_data(what_to_edit='product_name')
        await call.message.edit_text(
            text='Какое будет новое название товара?',
            reply_markup=cancel_inline_kb(callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'product_discription':
        await state.set_state(Edit_Product_Channel.edit_product)
        await state.update_data(what_to_edit='product_discription')
        await call.message.edit_text(
            text='Какое будет новое описание товара?',
            reply_markup=cancel_inline_kb(callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'resources':
        await call.message.edit_text(
            text='Выбери ресурсы, которые будут привязаны к товару:',
            reply_markup=edit_list_resources_choose(
                bot_username=bot_username.username,
                selected=list_active_resources, 
                product_id=callback_data.product_id,
                page=0
                ).as_markup()
        )
        await state.update_data(new_resources_list=list_active_resources)
    elif callback_data.what_to_edit == 'display_status_of':
        db.update_display_status(product_id=callback_data.product_id, status='выключен')
        await call.message.edit_reply_markup(reply_markup=product_channel_kb(product_id=callback_data.product_id).as_markup())
        await call.answer(text='Больше не показываем товар покупателям!', show_alert=True)
    elif callback_data.what_to_edit == 'display_status_on':
        db.update_display_status(product_id=callback_data.product_id, status='включен')
        await call.message.edit_reply_markup(reply_markup=product_channel_kb(product_id=callback_data.product_id).as_markup()) 
        await call.answer(text='Снова показываем товар покупателям!', show_alert=True)
    elif callback_data.what_to_edit == 'delete_product':
        await call.message.edit_text(
            text='Ты уверен, что хочешь удалить товар? Все данные о товаре будут удалены!',
            reply_markup=delete_product_ch(product_id=callback_data.product_id).as_markup()
        )




@router.callback_query(ListPicturesCh.filter(F.action == 'open_picture_ch'))
async def open_picture_product_ch(call: types.CallbackQuery, callback_data: ListPicturesCh, state: FSMContext):

    photo = db.get_picture_product(picture_id=callback_data.picture_id)

    await call.message.delete()
    await call.message.answer_photo(photo=photo[0][3], reply_markup=picture_ch_kb(picture_id=callback_data.picture_id, product_id=callback_data.product_id).as_markup())


@router.callback_query(ListPicturesCh.filter(F.action == 'back_from_photo_ch'))
async def back_picture_product_ch(call: types.CallbackQuery, callback_data: ListPicturesCh, state: FSMContext):
    caption = '''
📸 <b>Добавь фото для товара, которое будет отображаться у покупателя!</b>

🖼️ Яркое и привлекательное фото - это ключ к успешной продаже!
'''

    await call.message.delete()
    await call.message.answer(text=caption, reply_markup=edit_pictures_ch(product_id=callback_data.product_id).as_markup())


@router.callback_query(ListPicturesCh.filter(F.action == 'delete_picture_ch'))
async def delete_picture_product_ch(call: types.CallbackQuery, callback_data: ListPicturesCh, state: FSMContext):
    db.delete_picture_product(picture_id=callback_data.picture_id)

    list_pic = []
    for photo in db.get_list_pictures(product_id=callback_data.product_id):
        list_pic.append(photo[0])

    db.edit_product(product_id=callback_data.product_id, set='product_photo', new_data=list_pic)

    caption = '''
📸 <b>Добавь фото для товара, которое будет отображаться у покупателя!</b>

🖼️ Яркое и привлекательное фото - это ключ к успешной продаже!
'''

    await call.message.delete()
    await call.message.answer(text=caption, reply_markup=edit_pictures_ch(product_id=callback_data.product_id).as_markup())
    await call.answer(text='🗑 Фото удалено')



@router.callback_query(ListPicturesCh.filter(F.action == 'add_picture_ch'))
async def add_picture_product_ch(call: types.CallbackQuery, callback_data: ListPicturesCh, state: FSMContext):

    await call.message.edit_text(
        text='Пришли фото твоего товара👌',
        reply_markup=cancel_add_picture_ch(product_id=callback_data.product_id).as_markup()
    )

    await state.set_state(Edit_Product_Channel.edit_product)
    await state.update_data(what_to_edit='add_picture_ch')








@router.message(Edit_Product_Channel.edit_product, or_f(
        F.photo,
        F.text)
)
async def get_new_product_channel_data(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()

    if getFSM.get('what_to_edit') == 'price':
        if 0 < msg.text.isdigit() and int(msg.text) < 1000001:
            db.edit_product(product_id=getFSM.get('product_id'), set='price', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару', 
                reply_markup=return_product_channel_kb(product_id=getFSM.get('product_id')).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()
        else:
            await msg.answer(text='Пришли стоимость товара не меньше 1 RUB и не больше 1,000,000 RUB 😉')

    elif getFSM.get('what_to_edit') == 'discount':
        if (msg.text.isdigit() and int(msg.text) > -1) and  (msg.text.isdigit() and int(msg.text) < 100):
            product_data = db.get_product_data(product_id=getFSM.get('product_id'))

            total_price = product_data[0][6] - product_data[0][6] / 100 * int(msg.text)

            if round(total_price) == 0:
                db.edit_product(product_id=getFSM.get('product_id'), set='discount', new_data=msg.text)
                await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару', 
                reply_markup=return_product_channel_kb(product_id=getFSM.get('product_id')).as_markup()
            )
                # Сбрасываем текущее состояния
                current_state = await state.get_state()

                if current_state is None:
                    return
        
                await state.clear()
            elif round(total_price) > 0:
                db.edit_product(product_id=getFSM.get('product_id'), set='discount', new_data=msg.text)
                await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару', 
                reply_markup=return_product_channel_kb(product_id=getFSM.get('product_id')).as_markup()
            )
                # Сбрасываем текущее состояния
                current_state = await state.get_state()

                if current_state is None:
                    return
        
                await state.clear()
            else:
                await msg.answer(text='Итоговая стоимость товара со скидкой не должна быть меньше 1 🇷🇺RUB.')
        else:
            await msg.answer(text='Пришли размер скидки от 0 до 99')
    
    elif getFSM.get('what_to_edit') == 'product_name':

        if len(msg.text) > 24:
            await msg.answer('Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов')
        else:
            db.edit_product(product_id=getFSM.get('product_id'), set='product_name', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару', 
                reply_markup=return_product_channel_kb(product_id=getFSM.get('product_id')).as_markup()
            )
            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()

    elif getFSM.get('what_to_edit') == 'product_discription':

        if len(msg.text) > 1024:
            await msg.answer('Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 1024 символов')
        else:
            db.edit_product(product_id=getFSM.get('product_id'), set='product_description', new_data=msg.html_text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару', 
                reply_markup=return_product_channel_kb(product_id=getFSM.get('product_id')).as_markup()
            )
            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()
    elif getFSM.get('what_to_edit') == 'add_picture_ch':
        try:
            picture_id = msg.photo[-1].file_id
            db.add_new_picture_product(product_id=getFSM.get('product_id'), picture_id=picture_id) # Добавляем новое фото

            list_pic = []
            for photo in db.get_list_pictures(product_id=getFSM.get('product_id')):
                list_pic.append(photo[0])

            db.edit_product(product_id=getFSM.get('product_id'), set='product_photo', new_data=list_pic)
        
            await msg.answer(text='✅ Новое фото для товара добавлено!', reply_markup=return_list_picture_ch(product_id=getFSM.get('product_id')).as_markup())

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()
        except:
            await msg.answer('Пришлите фото')


    
@router.callback_query(ListResourcesChoose.filter(F.choose == 'edit_choose_resources'))
async def choose_resource(call: types.CallbackQuery, callback_data: ListResourcesChoose, state: FSMContext):
    bot_username = await call.bot.get_me()
    getFSM = await state.get_data()
    
    # --------------- Здесь обновляем список ресурсов, которые были выбраны пользователем
    selected = getFSM.get('new_resources_list')
    
    if callback_data.resource_id in selected:
        if len(selected) == 1:
            await call.answer(
                text='Нужно оставить хотя бы 1 ресурс😉',
                show_alert=True
            )
        else:
            selected.remove(f'{callback_data.resource_id}')
    else:
        selected.append(callback_data.resource_id)
    await state.update_data(new_resources_list=selected)
    # ---------------

    try:
        await call.message.edit_text(
                    text='Выбери ресурсы, которые будут привязаны к товару:', 
                    reply_markup=edit_list_resources_choose(
                        bot_username=bot_username.username,
                        selected=selected, 
                        product_id=getFSM.get('product_id'),
                        page=callback_data.page
                        ).as_markup()
                    )
    except:
        pass

@router.callback_query(Paginator.filter(F.array_name == 'edit_resource_of_choice'))
async def paginator_edit_resource_of_choice(call: types.CallbackQuery, callback_data: Paginator, state: FSMContext):
    bot_username = await call.bot.get_me()
    getFSM = await state.get_data()
    selected = getFSM.get('new_resources_list')

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)


    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text='Выбери ресурсы, которые будут привязаны к товару:', 
                reply_markup=edit_list_resources_choose(
                    bot_username=bot_username.username,
                    selected=selected, 
                    product_id=getFSM.get('product_id'),
                    page=page
                    ).as_markup()
                )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text='Выбери ресурсы, которые будут привязаны к товару:', 
                reply_markup=edit_list_resources_choose(
                    bot_username=bot_username.username,
                    selected=selected, 
                    product_id=getFSM.get('product_id'),
                    page=page
                    ).as_markup()
                )
        else:
            await call.answer(text='Это начало страницы')



@router.callback_query(EditProductChannel.filter(F.edit_product == 'delete'))
async def delete_product(call: types.CallbackQuery, callback_data: EditProductChannel):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    delete_status = True

    for item in db.get_all_processing(project_id=project_id): # Проверяем, находится ли удаляем товар на стадии оплаты. Если товар находится на стадии оплаты, то удалить не получится
        if callback_data.product_id == str(item[7]):
            delete_status = False
            break


    if delete_status:
        for group in db.get_all_groups(project_id=project_id): # Перебираем все группы принадлежащие этому проекту
            if callback_data.product_id in group[6]: # Проверяем, есть ли удаляемы товар в списке продуктов группы
                new_list = group[6]
                new_list.remove(f'{callback_data.product_id}') # Удаляем товар из списка продуктов группы
                db.update_list_product_to_group(group_id=group[0], selected=new_list) # Обновляем список товаров в группе

        db.delete_product(product_id=callback_data.product_id)

        await call.message.edit_text(
            text='🗑 Товар удален!',
            reply_markup=return_list_products_ch().as_markup()
        )
        
    else:
        await call.answer(
                text='Товар находится на стадии оплаты, попробуйте позже ⏳',
                show_alert=True
            )





