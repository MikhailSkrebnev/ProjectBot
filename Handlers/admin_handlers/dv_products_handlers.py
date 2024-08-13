from aiogram import types, F, Router
from aiogram.filters import or_f
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link


from Database.Admin_db import Database


from Keyboards.admin_keyboards.dv_products_keyboards import(
    user_products_dv_kb,
    cancel_add_product_dv,
    product_delivery_kb,
    choose_list_delivery,
    user_methods_dv_kb,
    cancel_add_method_dv,
    method_delivery_kb,
    cancel_edit_product,
    delete_product_dv,
    return_product_dv_kb,
    cancel_edit_method_dv,
    delete_method_dv,
    return_edit_method_dv,
    edit_pictures_dv,
    cancel_add_picture,
    return_list_picture,
    picture_dv_kb,
    choose_orders,
    list_delivery_orders,
    order_kb,
    edit_order_status,
    cancel_edit_order_data,
    return_order_data,
    edit_choose_list_delivery,
    return_list_products_dv,
    Paginator,
    ListMethodsDv,
    ListProductsDv,
    ChooseMethodDV,
    EditProducrDV,
    EditMethodDV,
    ListPicturesDv,
    DeliveryOrders,
    EditDeliveryOrder,
    PaginatorOrders
)


db = Database()
router = Router()


class Add_Product_dv(StatesGroup):
    project_id_dv = State()
    product_name_dv = State()
    product_description_dv = State()
    product_price_dv = State()
    product_methods = State()
    product_id_dv = State()


class Add_Delivery_method(StatesGroup):
    method_name = State()
    method_description = State()
    method_price = State()



class Edit_Product_DV(StatesGroup):
    edit_product_dv = State()
    product_id = State()
    what_to_edit = State()    

class Edit_Method_DV(StatesGroup):
    edit_method_dv = State()
    method_id = State()


class Edit_Order_DV(StatesGroup):
    action = State()
    order_id = State()



@router.callback_query(F.data == 'delivery_products')
async def call_products_delivery(call: types.CallbackQuery):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)


    caption = '''
<b>Список добавленных товаров:</b>
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=user_products_dv_kb(project_id=project_id, page=0).as_markup()
    )




# PAGINATOR of Products_dv

@router.callback_query(Paginator.filter(F.array_name == 'products_dv'))
async def paginator_products_delivery(call: types.CallbackQuery, state: FSMContext, callback_data: Paginator):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    caption = '''
<b>Список добавленных товаров:</b>
'''

    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text=caption,
                reply_markup=user_products_dv_kb(project_id=project_id, page=page).as_markup()
            )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text=caption,
                reply_markup=user_products_dv_kb(project_id=project_id, page=page).as_markup()
            )
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()




# OPEN PRODUCT (DELIVERY)

@router.callback_query(ListProductsDv.filter(F.action == 'open_product_dv'))
async def open_product_channel(call: types.CallbackQuery, callback_data: ListProductsDv, state: FSMContext):
    product_data = db.get_product_data(product_id=callback_data.product_id)

    link = await create_start_link(call.bot, f'{product_data[0][0]}', encode=True)
    total_price = product_data[0][6]

    if product_data[0][7] > 0:
        total_price = total_price - total_price / 100 * product_data[0][7]

    caption = f'''
<b>Название товара:</b> {product_data[0][8]}
<b>Описание товара:</b> {product_data[0][9]}

<b>Стоимость товара:</b> {product_data[0][6]} 🇷🇺RUB
<b>Скидка на товар:</b> {product_data[0][7]}%
<b>Итоговая стоимость:</b> {round(total_price)} 🇷🇺RUB

<b>Количество товара:</b> {product_data[0][11]}
<b>Количество продаж:</b> {product_data[0][13]}

<b>Ссылка на товар:</b> {link}
'''
    await call.message.edit_text(
        text=caption,
        reply_markup=product_delivery_kb(product_id=product_data[0][0]).as_markup()
    )

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()
   



# Добавление нового товара

@router.callback_query(ListProductsDv.filter(F.action == 'add_new_product_dv'))
async def add_new_product_dv(call: types.CallbackQuery, callback_data: ListProductsDv, state: FSMContext):

    if db.get_list_delivery_methods(project_id=callback_data.project_id) != []:
        await call.message.edit_text('Как будет называться твой товар?', reply_markup=cancel_add_product_dv().as_markup())

        await state.set_state(Add_Product_dv.product_name_dv)
        await state.update_data(project_id_dv=callback_data.project_id)
    else:
        await call.answer(
            text='Добавь хотя бы 1 способ доставки 😉',
            show_alert=True
        )




@router.message(Add_Product_dv.product_name_dv, F.text)
async def get_product_name_dv(msg: types.Message, state: FSMContext):

    if len(msg.text) > 24:
        await msg.answer('Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов', reply_markup=cancel_add_product_dv().as_markup())
    else:
        await msg.answer('Какое будет описание товара?', reply_markup=cancel_add_product_dv().as_markup())

        await state.set_state(Add_Product_dv.product_description_dv)
        await state.update_data(product_name_dv=msg.text)


@router.message(Add_Product_dv.product_description_dv, F.text)
async def get_product_description_dv(msg: types.Message, state: FSMContext):

    if len(msg.text) > 1024:
        await msg.answer(text='Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 1024 символов', reply_markup=cancel_add_product_dv().as_markup())
    else:
        await msg.answer('Какая будет стоимость товара?', reply_markup=cancel_add_product_dv().as_markup())
        await state.set_state(Add_Product_dv.product_price_dv)
        await state.update_data(product_description_dv=msg.html_text)


@router.message(Add_Product_dv.product_price_dv, F.text)
async def get_product_price_dv(msg: types.Message, state: FSMContext):

    if msg.text.isdigit() and int(msg.text) > 0:   
        getFSM = await state.get_data()

        await state.update_data(product_price=msg.text)
        await state.set_state(Add_Product_dv.product_methods)

        selected = [] # Задаем пустой список выбранных способов доставки
        await state.update_data(product_methods=selected)

        await msg.answer('Выбери способ доставки:', reply_markup=choose_list_delivery(project_id=getFSM.get('project_id_dv'), page=0, selected=selected).as_markup())

    else:
        await msg.answer('Пришли целое число больше 0 RUB 😉', reply_markup=cancel_add_product_dv().as_markup())


@router.callback_query(Add_Product_dv.product_methods, ChooseMethodDV.filter(F.action == 'choose_method'))
async def get_product_dv_methods(call: types.CallbackQuery, state: FSMContext, callback_data: ChooseMethodDV):
    getFSM = await state.get_data()
    
    # --------------- Здесь обновляем список ресурсов, которые были выбраны пользователем
    selected = getFSM.get('product_methods')
    if callback_data.method_id in selected:
        selected.remove(f'{callback_data.method_id}')
    else:
        selected.append(callback_data.method_id)
    await state.update_data(product_methods=selected)
    # ---------------

    await call.message.edit_text(
        text='<b>Выбери способ доставки:</b>', 
        reply_markup=choose_list_delivery(project_id=getFSM.get('project_id_dv'), selected=selected, page=callback_data.page).as_markup()
    )


# Пагинатор

@router.callback_query(Paginator.filter(F.array_name == 'method_of_choice'))
async def paginator_methods_of_choice(call: types.CallbackQuery, callback_data: Paginator, state: FSMContext):
    getFSM = await state.get_data()
    selected = getFSM.get('product_methods')

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)


    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text('Выбери способ доставки:', reply_markup=choose_list_delivery(project_id=getFSM.get('project_id_dv'), page=page, selected=selected).as_markup())
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text('Выбери способ доставки:', reply_markup=choose_list_delivery(project_id=getFSM.get('project_id_dv'), page=page, selected=selected).as_markup())
        else:
            await call.answer(text='Это начало страницы')


@router.callback_query(Add_Product_dv.product_methods, F.data == 'choice_delivery_methods')
async def produc_created(call: types.CallbackQuery, state: FSMContext):
    getFSM = await state.get_data()

    if getFSM.get('product_methods') == []:
        await call.answer('Нужно выбрать хотя бы 1 способ доставки🙏', show_alert=True)
    else:
        db.add_product(
            project_id=getFSM.get('project_id_dv'),
            product_type='delivery',
            reusable='False',
            product_name=getFSM.get('product_name_dv'),
            product_description=getFSM.get('product_description_dv'),
            product_price=getFSM.get('product_price'),
            contents=getFSM.get('product_methods'),
            product_photo=[]
        )
        product_data = db.get_last_product(project_id=getFSM.get('project_id_dv'), product_type='delivery')

        link = await create_start_link(call.bot, f'{product_data[0][0]}', encode=True)
        total_price = product_data[0][6]

        if product_data[0][7] > 0:
            total_price = total_price - total_price / 100 * product_data[0][7]

        caption = f'''
<b>Название товара:</b> {product_data[0][8]}
<b>Описание товара:</b> {product_data[0][9]}

<b>Стоимость товара:</b> {product_data[0][6]} 🇷🇺RUB
<b>Скидка на товар:</b> {product_data[0][7]}%
<b>Итоговая стоимость:</b> {round(total_price)} 🇷🇺RUB

<b>Количество товара:</b> {product_data[0][11]}
<b>Количество продаж:</b> {product_data[0][13]}

<b>Ссылка на товар:</b> {link}
'''
        await call.message.edit_text(
            text=caption,
            reply_markup=product_delivery_kb(product_id=product_data[0][0]).as_markup()
        )

        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
            
        await state.clear()




# -------------------------- Редактирование товара

class Edit_DV_mehotds(StatesGroup):
    new_dv_methods_list = State()



@router.callback_query(EditProducrDV.filter(F.action == 'edit_product_dv'))
async def call_edit_product_dv(call: types.CallbackQuery, callback_data: EditProducrDV, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    await state.update_data(product_id=callback_data.product_id)


    if callback_data.what_to_edit == 'product_name':
        await state.set_state(Edit_Product_DV.edit_product_dv)
        await state.update_data(what_to_edit='product_name_dv')
        await call.message.edit_text('Какое будет новое название товара?', reply_markup=cancel_edit_product(product_id=callback_data.product_id).as_markup())


    elif callback_data.what_to_edit == 'product_photo':
        caption = '''
📸 <b>Добавь фото для товара, которое будет отображаться у покупателя!</b>

🖼️ Яркое и привлекательное фото - это ключ к успешной продаже!
'''

        await call.message.edit_text(text=caption, reply_markup=edit_pictures_dv(product_id=callback_data.product_id).as_markup())
        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
            
        await state.clear()
    elif callback_data.what_to_edit == 'product_description':
        await state.set_state(Edit_Product_DV.edit_product_dv)
        await state.update_data(what_to_edit='product_description_dv')
        await call.message.edit_text('Какое будет новое описание товара?', reply_markup=cancel_edit_product(product_id=callback_data.product_id).as_markup())
    elif callback_data.what_to_edit == 'product_price':
        await state.set_state(Edit_Product_DV.edit_product_dv)
        await state.update_data(what_to_edit='product_price_dv')
        await call.message.edit_text('Какая будет новая стоимость товара?', reply_markup=cancel_edit_product(product_id=callback_data.product_id).as_markup())
    elif callback_data.what_to_edit == 'product_discount':
        await state.set_state(Edit_Product_DV.edit_product_dv)
        await state.update_data(what_to_edit='product_discount_dv')
        await call.message.edit_text('Пришли новую скидку на товар от 0 до 99', reply_markup=cancel_edit_product(product_id=callback_data.product_id).as_markup())
    elif callback_data.what_to_edit == 'product_quantity':
        await state.set_state(Edit_Product_DV.edit_product_dv)
        await state.update_data(what_to_edit='product_quantity_dv')
        await call.message.edit_text('Пришли мне количество товара, которое сейчас доступно к продаже', reply_markup=cancel_edit_product(product_id=callback_data.product_id).as_markup())
    elif callback_data.what_to_edit == 'delivery_methods':   
        await call.message.edit_text(
            text='Выбери способ доставки:',
            reply_markup=edit_choose_list_delivery(
                project_id=project_id,
                selected=db.get_list_active_dv_methods(callback_data.product_id)[0][0], 
                product_id=callback_data.product_id,
                page=0
                ).as_markup()
        )
        await state.update_data(new_dv_methods_list=db.get_list_active_dv_methods(callback_data.product_id)[0][0])
    elif callback_data.what_to_edit == 'display_status_off':
        db.update_display_status(product_id=callback_data.product_id, status='выключен')
        await call.message.edit_reply_markup(reply_markup=product_delivery_kb(product_id=callback_data.product_id).as_markup())
        await call.answer(text='Больше не показываем товар покупателям!', show_alert=True)
    elif callback_data.what_to_edit == 'display_status_on':
        db.update_display_status(product_id=callback_data.product_id, status='включен')
        await call.message.edit_reply_markup(reply_markup=product_delivery_kb(product_id=callback_data.product_id).as_markup()) 
        await call.answer(text='Снова показываем товар покупателям!', show_alert=True)
    elif callback_data.what_to_edit == 'delete_product':
        await call.message.edit_text(
            text='Ты уверен, что хочешь удалить товар? Все данные о товаре будут удалены!',
            reply_markup=delete_product_dv(project_id=str(project_id), product_id=callback_data.product_id).as_markup()
        )


@router.callback_query(ListPicturesDv.filter(F.action == 'open_picture_dv'))
async def open_picture_product_dv(call: types.CallbackQuery, callback_data: ListPicturesDv, state: FSMContext):

    photo = db.get_picture_product(picture_id=callback_data.picture_id)

    await call.message.delete()
    await call.message.answer_photo(photo=photo[0][3], reply_markup=picture_dv_kb(picture_id=callback_data.picture_id, product_id=callback_data.product_id).as_markup())


@router.callback_query(ListPicturesDv.filter(F.action == 'back_from_photo_dv'))
async def back_picture_product_dv(call: types.CallbackQuery, callback_data: ListPicturesDv, state: FSMContext):

    caption = '''
📸 <b>Добавь фото для товара, которое будет отображаться у покупателя!</b>

🖼️ Яркое и привлекательное фото - это ключ к успешной продаже!
'''

    await call.message.delete()
    await call.message.answer(text=caption, reply_markup=edit_pictures_dv(product_id=callback_data.product_id).as_markup())


@router.callback_query(ListPicturesDv.filter(F.action == 'delete_picture_dv'))
async def delete_picture_product_dv(call: types.CallbackQuery, callback_data: ListPicturesDv, state: FSMContext):
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
    await call.message.answer(text=caption, reply_markup=edit_pictures_dv(product_id=callback_data.product_id).as_markup())
    await call.answer(text='🗑 Фото удалено!')



@router.callback_query(ListPicturesDv.filter(F.action == 'add_picture_dv'))
async def add_picture_product_dv(call: types.CallbackQuery, callback_data: ListPicturesDv, state: FSMContext):

    await call.message.edit_text(
        text='Пришли фото твоего товара👌',
        reply_markup=cancel_add_picture(product_id=callback_data.product_id).as_markup()
    )

    await state.set_state(Edit_Product_DV.edit_product_dv)
    await state.update_data(what_to_edit='add_picture_dv')




@router.message(Edit_Product_DV.edit_product_dv, or_f(
        F.photo,
        F.text)
)
async def get_new_product_dv_data(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if getFSM.get('what_to_edit') == 'product_name_dv':
        if len(msg.text) > 24:
            await msg.answer('Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов')
        else:
            db.edit_product(product_id=getFSM.get('product_id'),  set='product_name', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару',
                reply_markup=return_product_dv_kb(project_id=project_id, product_id=str(getFSM.get('product_id'))).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()

    elif getFSM.get('what_to_edit') == 'product_description_dv':
        if len(msg.text) > 1024:
            await msg.answer('Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 1024 символов')
        else:
            db.edit_product(product_id=getFSM.get('product_id'),  set='product_description', new_data=msg.html_text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару',
                reply_markup=return_product_dv_kb(project_id=project_id, product_id=str(getFSM.get('product_id'))).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()

    elif getFSM.get('what_to_edit') == 'product_price_dv':
        if 0 < msg.text.isdigit() and int(msg.text) < 1000001:
            db.edit_product(product_id=getFSM.get('product_id'),  set='price', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару',
                reply_markup=return_product_dv_kb(project_id=project_id, product_id=str(getFSM.get('product_id'))).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()
        else:
            await msg.answer('Пришли стоимость товара не меньше 1 RUB и не больше 1,000,000 RUB 😉')

    elif getFSM.get('what_to_edit') == 'product_discount_dv':
        if -1 < msg.text.isdigit() and int(msg.text) < 100:
            product_data = db.get_product_data(product_id=getFSM.get('product_id'))

            total_price = product_data[0][6] - product_data[0][6] / 100 * int(msg.text)

            if round(total_price) == 0:
                db.edit_product(product_id=getFSM.get('product_id'), set='discount', new_data=msg.text)
                await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару', 
                reply_markup=return_product_dv_kb(project_id=project_id, product_id=str(getFSM.get('product_id'))).as_markup()
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
                reply_markup=return_product_dv_kb(project_id=project_id, product_id=str(getFSM.get('product_id'))).as_markup()
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
    elif getFSM.get('what_to_edit') == 'product_quantity_dv':
        if -1 < msg.text.isdigit() and int(msg.text) < 1000000:
            db.edit_product(product_id=getFSM.get('product_id'),  set='quantity', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару',
                reply_markup=return_product_dv_kb(project_id=project_id, product_id=str(getFSM.get('product_id'))).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()
        else:
            await msg.answer('Пришли кол-во товара в диапазоне от 0 до 999999')
    elif getFSM.get('what_to_edit') == 'add_picture_dv':
        try:
            picture_id = msg.photo[-1].file_id
            db.add_new_picture_product(product_id=getFSM.get('product_id'), picture_id=picture_id) # Добавляем новое фото

            list_pic = []
            for photo in db.get_list_pictures(product_id=getFSM.get('product_id')):
                list_pic.append(photo[0])

            db.edit_product(product_id=getFSM.get('product_id'), set='product_photo', new_data=list_pic)
        
            await msg.answer(text='✅ Новое фото для товара добавлено!', reply_markup=return_list_picture(product_id=getFSM.get('product_id')).as_markup())

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()
        except:
            await msg.answer('Пришлите фото')
        



@router.callback_query(ChooseMethodDV.filter(F.action == 'edit_choose_method'))
async def edit_choose_dv_methods(call: types.CallbackQuery, callback_data: ChooseMethodDV, state: FSMContext):
    getFSM = await state.get_data()
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    
    # --------------- Здесь обновляем список ресурсов, которые были выбраны пользователем
    selected = getFSM.get('new_dv_methods_list')

    if callback_data.method_id in selected:
        if len(selected) == 1:
            await call.answer(
                text='Нужно оставить хотя бы 1 способ доставки😉',
                show_alert=True
            )
        else:
            selected.remove(f'{callback_data.method_id}')
    else:
        selected.append(callback_data.method_id)
    await state.update_data(new_dv_methods_list=selected)
    # ---------------


    try:
        await call.message.edit_text(
            text='Выбери способ доставки:', 
            reply_markup=edit_choose_list_delivery(
                project_id=project_id, 
                product_id=getFSM.get('product_id'), 
                page=callback_data.page, 
                selected=selected).as_markup()
        )
    except:
        pass



@router.callback_query(Paginator.filter(F.array_name == 'edit_method_of_choice'))
async def paginator_edit_methods_of_choice(call: types.CallbackQuery, callback_data: Paginator, state: FSMContext):
    getFSM = await state.get_data()
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    selected = getFSM.get('new_dv_methods_list')


    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)


    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text('Выбери способ доставки:', reply_markup=edit_choose_list_delivery(project_id=project_id, product_id=getFSM.get('product_id'), page=page, selected=selected).as_markup())
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text('Выбери способ доставки:', reply_markup=edit_choose_list_delivery(project_id=project_id, product_id=getFSM.get('product_id'), page=page, selected=selected).as_markup())
        else:
            await call.answer(text='Это начало страницы')






@router.callback_query(EditProducrDV.filter(F.action == 'delete_dv'))
async def del_product_dv(call: types.CallbackQuery, callback_data: EditProducrDV, state: FSMContext):
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
            reply_markup=return_list_products_dv().as_markup()
        )
        
    else:
        await call.answer(
                text='Товар находится на стадии оплаты, попробуйте позже ⏳',
                show_alert=True
            )




    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()




























# DELIVERY METHODS

@router.callback_query(ListProductsDv.filter(F.action == 'open_delivery_methods'))
async def call_delivery_methods(call: types.CallbackQuery, callback_data: ListProductsDv):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)


    caption = '''
Добавь способ доставки ваших товаров: 

* Название (например, Курьерская💨, Самовывоз🚶)
* Описание (сроки, условия)
* Стоимость (в зависимости от способа доставки)
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=user_methods_dv_kb(project_id=project_id, page=0).as_markup()
    )



# OPEN DELIVERY METHOD 

@router.callback_query(ListMethodsDv.filter(F.action == 'open_methods_dv'))
async def call_delivery_methods(call: types.CallbackQuery, callback_data: ListMethodsDv, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    method_data = db.get_method_data(method_id=callback_data.method_id)

    caption = f'''
<b>Название:</b> {method_data[0][2]}
<b>Описание:</b> {method_data[0][3]}

<b>Стоимость доставки:</b> {method_data[0][4]} 🇷🇺RUB
'''
        
    await call.message.edit_text(
        text=caption,
        reply_markup=method_delivery_kb(method_id=callback_data.method_id, project_id=project_id).as_markup()
    )

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()



# Пагинация для раздела DELIVERY

@router.callback_query(Paginator.filter(F.array_name == 'methods_dv'))
async def paginator_delivery_methods(call: types.CallbackQuery, state: FSMContext, callback_data: Paginator):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    caption = '''
Добавь способ доставки ваших товаров: 

* Название (например, Курьерская💨, Самовывоз🚶)
* Описание (сроки, условия)
* Стоимость (в зависимости от способа доставки)
'''

    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text=caption,
                reply_markup=user_methods_dv_kb(project_id=project_id, page=page).as_markup()
            )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text=caption,
                reply_markup=user_methods_dv_kb(project_id=project_id, page=page).as_markup()
            )
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()




# Добавление нового способа доставки

@router.callback_query(ListMethodsDv.filter(F.action == 'add_new_methods_dv'))
async def add_new_product_dv(call: types.CallbackQuery, callback_data: ListMethodsDv, state: FSMContext):

    await call.message.edit_text('Пришли название способа доставки😉', reply_markup=cancel_add_method_dv(project_id=callback_data.project_id).as_markup())

    await state.set_state(Add_Delivery_method.method_name)


@router.message(Add_Delivery_method.method_name, F.text)
async def get_method_name_dv(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if len(msg.text) > 24:
        await msg.answer('Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов', reply_markup=cancel_add_method_dv(project_id=project_id).as_markup())
    else:
        await msg.answer('Пришли описание способа доставки😉', reply_markup=cancel_add_method_dv(project_id=project_id).as_markup())

        await state.set_state(Add_Delivery_method.method_description)
        await state.update_data(method_name=msg.text)


@router.message(Add_Delivery_method.method_description, F.text)
async def get_method_description_dv(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if len(msg.html_text) > 1024:
        await msg.answer('Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 1024 символов', reply_markup=cancel_add_method_dv(project_id=project_id).as_markup())
    else:
        await msg.answer('Пришли стоимость способа доставки😉', reply_markup=cancel_add_method_dv(project_id=project_id).as_markup())

        await state.set_state(Add_Delivery_method.method_price)
        await state.update_data(method_description=msg.html_text)


@router.message(Add_Delivery_method.method_price, F.text)
async def get_product_price_dv(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if msg.text.isdigit() and int(msg.text) > -1:
        getFSM = await state.get_data()

        db.add_delivery_method(
            project_id=project_id,
            name=getFSM.get('method_name'),
            description=getFSM.get('method_description'),
            price=msg.text
        )

        method_data = db.get_last_delivery_method(project_id=project_id)

        caption = f'''
<b>Название:</b> {method_data[0][2]}
<b>Описание:</b> {method_data[0][3]}

<b>Стоимость доставки:</b> {method_data[0][4]} 🇷🇺RUB
'''
        
        await msg.answer(
            text=caption,
            reply_markup=method_delivery_kb(method_id=method_data[0][0], project_id=project_id).as_markup()
        )

        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
        
        await state.clear()
    else:
        await msg.answer('Стоимость доставки не может быть меньше 0 RUB 🙃', reply_markup=cancel_add_method_dv(project_id=project_id).as_markup())


# Редактирование способа доставки

@router.callback_query(EditMethodDV.filter(F.action == 'edit_method_dv'))
async def edit_dv_method(call: types.CallbackQuery, callback_data: EditMethodDV, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    await state.update_data(method_id=callback_data.method_id)


    if callback_data.what_to_edit == 'method_name':
        await state.set_state(Edit_Method_DV.edit_method_dv)
        await state.update_data(what_to_edit='method_name')
        await call.message.edit_text('Какое будет новое название способа доставки?', reply_markup=cancel_edit_method_dv(method_id=callback_data.method_id).as_markup())
    elif callback_data.what_to_edit == 'method_description':
        await state.set_state(Edit_Method_DV.edit_method_dv)
        await state.update_data(what_to_edit='method_description')
        await call.message.edit_text('Какое будет новое описание способа доставки?', reply_markup=cancel_edit_method_dv(method_id=callback_data.method_id).as_markup())
    elif callback_data.what_to_edit == 'method_price':
        await state.set_state(Edit_Method_DV.edit_method_dv)
        await state.update_data(what_to_edit='method_price')
        await call.message.edit_text('Какая будет новая стоимость способа доставки?', reply_markup=cancel_edit_method_dv(method_id=callback_data.method_id).as_markup())
    elif callback_data.what_to_edit == 'display_status_off':
        db.method_display_status(method_id=callback_data.method_id, status=False)
        await call.message.edit_reply_markup(reply_markup=method_delivery_kb(method_id=callback_data.method_id, project_id=project_id).as_markup())
        await call.answer(text='Способ доставки больше не доступен покупателям!', show_alert=True)
    elif callback_data.what_to_edit == 'display_status_onn':
        db.method_display_status(method_id=callback_data.method_id, status=True)
        await call.message.edit_reply_markup(reply_markup=method_delivery_kb(method_id=callback_data.method_id,project_id=project_id).as_markup()) 
        await call.answer(text='Способ доставки снова доступен покупателям!', show_alert=True)
    elif callback_data.what_to_edit == 'delete_method':
        await call.message.edit_text(
            text='Ты уверен, что хочешь удалить этот способ доставки?\nТовары, к которым он был привязан, больше не смогут быть доставлены таким образом!',
            reply_markup=delete_method_dv(project_id=str(project_id), method_id=callback_data.method_id).as_markup()
        )


@router.message(Edit_Method_DV.edit_method_dv, F.text)
async def get_new_dv_method_data(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if getFSM.get('what_to_edit') == 'method_name':
        if len(msg.text) > 24:
            await msg.answer('Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов')
        else:
            db.edit_dv_method(method_id=getFSM.get('method_id'),  set='method_name', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены!',
                reply_markup=return_edit_method_dv(method_id=getFSM.get('method_id')).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()

    elif getFSM.get('what_to_edit') == 'method_description':
        if len(msg.text) > 1024:
            await msg.answer('Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 1024 символов')
        else:
            db.edit_dv_method(method_id=getFSM.get('method_id'),  set='method_description', new_data=msg.html_text)
            await msg.answer(
                text='✅ Готово! Изменения применены!',
                reply_markup=return_edit_method_dv(method_id=getFSM.get('method_id')).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()

    elif getFSM.get('what_to_edit') == 'method_price':
        if -1 < msg.text.isdigit() and int(msg.text) < 1000001:
            db.edit_dv_method(method_id=getFSM.get('method_id'),  set='cost_of_delivery', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены!',
                reply_markup=return_edit_method_dv(method_id=getFSM.get('method_id')).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()
        else:
            await msg.answer('Стоимость доставки должна быть меньше 0 RUB и не больше 1,000,00 RUB')




@router.callback_query(EditMethodDV.filter(F.action == 'delete_method_dv'))
async def delete_method(call: types.CallbackQuery, callback_data: EditMethodDV, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username.username)

    list_product_name = ''

    for product in db.get_product_dv_methods(project_id=project_id): # Получаем все айди и способы доставки продуктов пользователя и пропускаем через цикл
        if str(callback_data.method_id) in product[1]: # Проверяем, есть ли в списке способов доставки - способ, который мы удалили
            list_product_name += f'\n* {product[2]}'


    if len(list_product_name) > 0:
        await call.message.answer(
            text=f'<b>Перед удалением способа доставки, отвяжите его от следующих товаров:</b>\n{list_product_name}',
        )
        await call.answer(show_alert=True)
    else:
        db.delete_method_dv(method_id=callback_data.method_id) # Удаляем способ доставки


        caption = '''
Добавь способ доставки ваших товаров: 

* Название (например, Курьерская💨, Самовывоз🚶)
* Описание (сроки, условия)
* Стоимость (в зависимости от способа доставки)
'''

        await call.message.edit_text(
            text=caption,
            reply_markup=user_methods_dv_kb(project_id=project_id, page=0).as_markup()
        )
        await call.answer(text='🗑 Способ доставки удален!')


    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()













# DELIVERY ORDERS


@router.callback_query(ListProductsDv.filter(F.action == 'open_delivery_orders'))
async def call_delivery_orders(call: types.CallbackQuery, callback_data: ListProductsDv):


    caption = '''
<b>В этом разделе вы можете: </b> 

<b>* Изменить статус заказа 😉</b> -  <i>сортируйте заказы по категориям (в обработке, в доставке или завершенный заказ).</i>
<b>* Добавить трек-номер 🚚</b> -  <i>добавляйте трек-номер, чтобы покупатель мог отслеживать свой заказ.</i>
<b>* Оставить комментарий  💬</b> -  <i>задайте вопрос или оставьте информацию по заказу.</i>

Все ваши заказы - в одном месте, всё удобно и прозрачно! 👌
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=choose_orders().as_markup()
    )



@router.callback_query(DeliveryOrders.filter(F.action == 'list_orders'))
async def call_open_orders(call: types.CallbackQuery, callback_data: DeliveryOrders):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username.username)

    if callback_data.order_path == 'orders_are_being_processed':  
        await call.message.edit_text(
            text='⏳ Здесь отображаются заказы, находящиеся в обработке',
            reply_markup=list_delivery_orders(project_id=project_id, order_status='в обработке', page=0).as_markup()
        )
    elif callback_data.order_path == 'orders_on_the_way':
        await call.message.edit_text(
            text='✈️ Здесь отображаются заказы, находящиеся в пути',
            reply_markup=list_delivery_orders(project_id=project_id, order_status='в пути', page=0).as_markup()
        )
    elif callback_data.order_path == 'completed_order':
        await call.message.edit_text(
            text='✅ Здесь отображаются завершенные заказы',
            reply_markup=list_delivery_orders(project_id=project_id, order_status='завершен', page=0).as_markup()
        )



# Пагинация для раздела ORDERS

@router.callback_query(PaginatorOrders.filter(F.array_name == 'pag_orders_dv'))
async def paginator_delivery_orders(call: types.CallbackQuery, state: FSMContext, callback_data: PaginatorOrders):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    if callback_data.order_status == 'в обработке':
        caption = '''
⏳ Здесь отображаются заказы, находящиеся в обработке
'''
    elif callback_data.order_status == 'в пути':
        caption = '''
✈️ Здесь отображаются заказы, находящиеся в пути
'''
    elif callback_data.order_status == 'в пути':
        caption = '''
✅ Здесь отображаются завершенные заказы
'''


    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text=caption,
                reply_markup=list_delivery_orders(project_id=project_id, page=page, order_status=callback_data.order_status).as_markup()
            )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text=caption,
                reply_markup=list_delivery_orders(project_id=project_id, page=page, order_status=callback_data.order_status).as_markup()
            )
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()



# Открывает заказ

@router.callback_query(DeliveryOrders.filter(F.action == 'open_order'))
async def call_open_order(call: types.CallbackQuery, callback_data: DeliveryOrders, state: FSMContext):

    order_data = db.get_order_data(order_id=callback_data.order_path)
    user = db.get_user_data(project_id=order_data[0][3], user_id=order_data[0][2])

    caption = f'''
<b>ИНФОРМАЦИЯ О ЗАКАЗЕ</b>

<b>Номер заказа:</b> <code>{order_data[0][0]}</code>

<b>Покупатель:</b> ID <code>{order_data[0][2]}</code> USERNAME {'не указан' if user[0][4] == 'None' else f'<code>{user[0][4]}</code>'}

<b>Товар:</b> {order_data[0][4]}
<b>Кол-во:</b> {order_data[0][6]}
<b>Стоимость 1 ед. товара:</b> {order_data[0][5]} 🇷🇺RUB

<b>Способ доставки:</b> {order_data[0][7]}
<b>Стоимость доставки:</b> {order_data[0][8]} 🇷🇺RUB

<b>Адрес доставки:</b> {order_data[0][9]}
<b>Трек номер:</b> {order_data[0][10]}
<b>Статус заказа:</b> {order_data[0][11]}

<b>Комментарий от продавца:</b> {order_data[0][12]}
'''

    
    if order_data[0][11] == 'в обработке':
        order_path = 'orders_are_being_processed'
    elif order_data[0][11] == 'в пути':
        order_path = 'orders_on_the_way'
    else:
        order_path = 'completed_order'
    
    await call.message.edit_text(
        text=caption,
        reply_markup=order_kb(order_path=f'{order_path}', order_id=order_data[0][0]).as_markup()
    )

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()


# Редактирование заказа

@router.callback_query(EditDeliveryOrder.filter(F.action == 'edit_order'))
async def call_edit_order(call: types.CallbackQuery, callback_data: EditDeliveryOrder, state: FSMContext):
    order_data = db.get_order_data(order_id=callback_data.order_id)


    if callback_data.what_to_edit == 'edit_order_comment':
        await call.message.edit_text(
            text='💬 Оставьте комментарий к заказу\n\n<i>🔔 После изменения комментария заказа, покупатель получит уведомление</i>',
            reply_markup=cancel_edit_order_data(order_id=callback_data.order_id).as_markup()
        )

        await state.set_state(Edit_Order_DV.action)
        await state.update_data(action='order_comment')
        await state.update_data(order_id=f'{callback_data.order_id}')
    elif callback_data.what_to_edit == 'edit_order_status':
        await call.message.edit_text(
            text='✅ Измени статус заказа\n\n<i>🔔 После изменения статуса заказа, покупатель получит уведомление</i>',
            reply_markup=edit_order_status(order_id=callback_data.order_id, order_status=order_data[0][11]).as_markup()
        )
    elif callback_data.what_to_edit == 'edit_order_track_number':
        await call.message.edit_text(
            text='🔗 Добавь трект-номер или ссылку для отслеживания заказа\n\n<i>🔔 После изменения трек-номера заказа, покупатель получит уведомление</i>',
            reply_markup=cancel_edit_order_data(order_id=callback_data.order_id).as_markup()
        )

        await state.set_state(Edit_Order_DV.action)
        await state.update_data(action='order_track_number')
        await state.update_data(order_id=f'{callback_data.order_id}')





# Меняем статус заказа

@router.callback_query(EditDeliveryOrder.filter(F.action == 'edit_order_status'))
async def call_edit_order_status(call: types.CallbackQuery, callback_data: EditDeliveryOrder):
    order_data = db.get_order_data(order_id=callback_data.order_id)

    if callback_data.what_to_edit == 'в обработке':
        db.update_order_status(order_id=callback_data.order_id, status=f'{callback_data.what_to_edit}')
        order_path = 'orders_are_being_processed'
    elif callback_data.what_to_edit == 'в пути':
        db.update_order_status(order_id=callback_data.order_id, status=f'{callback_data.what_to_edit}')
        order_path = 'orders_on_the_way'
    elif callback_data.what_to_edit == 'завершен':
        db.update_order_status(order_id=callback_data.order_id, status=f'{callback_data.what_to_edit}')
        order_path = 'completed_order'

    order_data = db.get_order_data(order_id=callback_data.order_id)
    user = db.get_user_data(project_id=order_data[0][3], user_id=order_data[0][2])

    caption = f'''
<b>ИНФОРМАЦИЯ О ЗАКАЗЕ</b>

<b>Номер заказа:</b> <code>{order_data[0][0]}</code>

<b>Покупатель:</b> ID <code>{order_data[0][2]}</code> USERNAME {'не указан' if user[0][4] == 'None' else f'<code>{user[0][4]}</code>'}

<b>Товар:</b> {order_data[0][4]}
<b>Кол-во:</b> {order_data[0][6]}
<b>Стоимость 1 ед. товара:</b> {order_data[0][5]} 🇷🇺RUB

<b>Способ доставки:</b> {order_data[0][7]}
<b>Стоимость доставки:</b> {order_data[0][8]} 🇷🇺RUB

<b>Адрес доставки:</b> {order_data[0][9]}
<b>Трек номер:</b> {order_data[0][10]}
<b>Статус заказа:</b> {order_data[0][11]}

<b>Комментарий от продавца:</b> {order_data[0][12]}
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=order_kb(order_path=f'{order_path}', order_id=order_data[0][0]).as_markup()
    )

    try:
        await call.bot.send_message(chat_id=order_data[0][2], text=f'Продавец изменил статус заказа с номером: {order_data[0][0]}') 
    except:
        await call.answer(text='Покупатель не получил уведомление, так как заблокировал бота 🚫', show_alert=True)





@router.message(Edit_Order_DV.action, F.text)
async def edit_comment_tracknumber(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()
    order_data = db.get_order_data(order_id=getFSM.get('order_id'))


    if getFSM.get('action') == 'order_comment':
        if len(msg.text) > 512:
            await msg.answer(
                text='Комментарий слишком длинный🙃\n\nПришли новый не длиннее 512 символов',
                reply_markup=cancel_edit_order_data(order_id=getFSM.get('order_id')).as_markup()
            )
        else:
            db.update_order_data(order_id=getFSM.get('order_id'), what_to_edit='order_comment', data=msg.text)

            await msg.answer(
                text='✅ Комментарий добавлен к заказу!',
                reply_markup=return_order_data(order_id=order_data[0][0]).as_markup()
            )

            try:
                await msg.bot.send_message(chat_id=order_data[0][2], text=f'Продавец изменил комментарий заказа с номером: {order_data[0][0]}') 
            except:
                await msg.answer(text='Покупатель не получил уведомление, так как заблокировал бота 🚫', show_alert=True)
    elif getFSM.get('action') == 'order_track_number':
        if len(msg.text) > 1028:
            await msg.answer(
                text='Трек-номер или ссылка на отслеживание заказ не должна превышать 128 символов',
                reply_markup=cancel_edit_order_data(order_id=getFSM.get('order_id')).as_markup()
            )
        else:
            db.update_order_data(order_id=getFSM.get('order_id'), what_to_edit='track_number', data=msg.text)

            await msg.answer(
                text='✅ Трек-номер добавлен к заказу!',
                reply_markup=return_order_data(order_id=order_data[0][0]).as_markup()
            )

            try:
                await msg.bot.send_message(chat_id=order_data[0][2], text=f'Продавец изменил трек-номер заказа с номером: {order_data[0][0]}') 
            except:
                await msg.answer(text='Покупатель не получил уведомление, так как заблокировал бота 🚫', show_alert=True)


    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()