from aiogram import types, F, Router
from aiogram.filters import or_f, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link


from Database.Admin_db import Database


from Keyboards.admin_keyboards.inf_products_keyboards import(
    user_products_inf_kb,
    product_inf_kb,
    cancel_edit_product_inf,
    contetn_no_reusable_product_inf,
    return_product_inf_kb,
    delete_product_inf_product,
    return_list_products_inf,
    cancel_add_product_inf,
    choose_inf_content,
    skip_add_contnet,
    list_product_content,
    product_content_kb,
    product_content_no_reusable_kb,
    cancel_add_new_content,
    edit_pictures_inf, 
    picture_inf_kb,
    cancel_add_picture_inf,
    return_list_picture_inf,
    cancel_add_new_content_no_reusable,
    ListProductsInf,
    EditProductINF,
    Paginator,
    PaginatorContent,
    CallProductContent,
    ListPicturesInf
)



db = Database()
router = Router()





@router.callback_query(F.data == 'information_products')
async def call_products_inf(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = '''
<b>Список добавленных товаров:</b>
'''

    await call.message.edit_text(
        text=caption, 
        reply_markup=user_products_inf_kb(project_id, page=0).as_markup()
    )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()


# --------- Paginator

@router.callback_query(Paginator.filter(F.array_name == 'products_inf'))
async def paginator_products_inf(call: types.CallbackQuery, callback_data: Paginator, state: FSMContext):
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
            await call.message.edit_text(caption, reply_markup=user_products_inf_kb(project_id=project_id, page=page).as_markup())
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(caption, reply_markup=user_products_inf_kb(project_id=project_id, page=page).as_markup())
        else:
            await call.answer(text='Это начало страницы')
    
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()
    
    


@router.callback_query(ListProductsInf.filter(F.open_product_inf == 'open_inf'))
async def open_product_inf(call: types.CallbackQuery, callback_data: ListProductsInf, state: FSMContext):
    product_data = db.get_product_data(product_id=callback_data.product_id)

    link = await create_start_link(call.bot, f'{product_data[0][0]}-{product_data[0][1]}', encode=True)
    total_price = product_data[0][6]

    if product_data[0][7] > 0:
        total_price = total_price - total_price / 100 * product_data[0][7]

    caption = f'''
<b>Название товара:</b> {product_data[0][8]}
<b>Описание товара:</b> {product_data[0][9]}

<b>Стоимость товара:</b> {product_data[0][6]} 🇷🇺RUB
<b>Скидка на товар:</b> {product_data[0][7]}%
<b>Итоговая цена:</b> {round(total_price)} 🇷🇺RUB

<b>Количество товара:</b> {product_data[0][11]}
<b>Количество продаж:</b> {product_data[0][13]}

<b>Ссылка на товар:</b> {link}
'''


    await call.message.edit_text(
            text=caption,
            reply_markup=product_inf_kb(product_id=product_data[0][0]).as_markup()
        )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()





# ----------------- Добавление нового товара

class Add_New_Product_Inf(StatesGroup):
    name_product_inf = State()
    description_product_inf = State()
    price_product_inf = State()
    choose_content = State()
    content_product_inf = State()
    more_inf_content = State()
    product_id = State()




@router.callback_query(F.data == 'add_product_inf')
async def call_add_product_inf(call: types.CallbackQuery, state: FSMContext):
    
    await call.message.edit_text(
        text='Как будет называться твой товар?',
        reply_markup=cancel_add_product_inf().as_markup()
    )

    await state.set_state(Add_New_Product_Inf.name_product_inf)



@router.message(Add_New_Product_Inf.name_product_inf, F.text)
async def get_name_product_inf(msg: types.Message, state: FSMContext):

    if len(msg.text) > 24:
        await msg.answer(
            text='Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов',
            reply_markup=cancel_add_product_inf().as_markup()
        )
    else:
        await state.update_data(name_product_inf=msg.text)
        await state.set_state(Add_New_Product_Inf.description_product_inf)

        await msg.answer(
            text='Какое будет описание товара?',
            reply_markup=cancel_add_product_inf().as_markup()
        )


@router.message(Add_New_Product_Inf.description_product_inf, F.text)
async def get_description_product_inf(msg: types.Message, state: FSMContext):

    if len(msg.text) > 1024:
        await msg.answer(
            text='Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 1024 символов',
            reply_markup=cancel_add_product_inf().as_markup()
        )
    else:
        await state.update_data(description_product_inf=msg.html_text)
        await state.set_state(Add_New_Product_Inf.price_product_inf)

        await msg.answer(
            text='Какая будет стоимость товара?',
            reply_markup=cancel_add_product_inf().as_markup()
        )


@router.message(Add_New_Product_Inf.price_product_inf, F.text)
async def get_price_product_inf(msg: types.Message, state: FSMContext):

    if msg.text.isdigit() and int(msg.text) > 0:
        await state.update_data(price_product_inf=msg.text)
        await state.set_state(Add_New_Product_Inf.choose_content)

        await msg.answer(
            text='Подскажите, товар будет одинаковым для всех покупателей или уникальным для каждой продажи?\n\nНапример, ключ активации программы или данные от аккаунта в Steam.',
            reply_markup=choose_inf_content().as_markup()
        )
    else:
        await msg.answer(
            text='Пришли целое число больше 0 RUB 😉',
            reply_markup=cancel_add_product_inf().as_markup()
        )


@router.callback_query(Add_New_Product_Inf.choose_content, F.data == 'more_inf_content')
async def choose_more_inf_content(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await call.answer(show_alert=True)
    bot_username = await call.bot.get_me()
    getFSM = await state.get_data()
    project_id = db.get_project_id(bot_username.username)

    db.add_product(
            project_id=project_id,
            product_type='inf',
            reusable='True',
            product_name=getFSM.get('name_product_inf'),
            product_description=getFSM.get('description_product_inf'),
            product_price=getFSM.get('price_product_inf'),
            contents=[],
            product_photo=[]
        )
    product_data = db.get_last_product(project_id, product_type='inf')

    await call.message.edit_text(
        text='<b>Добавим первый товар👌</b>\n\nПришли любой файл, видео, фото, голосовое или просто текст',
        reply_markup=skip_add_contnet(product_id=product_data[0][0]).as_markup()
    )

    await state.update_data(product_id=product_data[0][0])
    await state.set_state(Add_New_Product_Inf.more_inf_content)



@router.message(Add_New_Product_Inf.more_inf_content, or_f(
        F.photo,
        F.text,
        F.document,
        F.video,
        F.voice
))
async def add_contnent_product_inf(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()

    if msg.content_type == types.ContentType.TEXT:
        content = msg.html_text
        content_type = 'text'
    elif msg.content_type == types.ContentType.PHOTO:
        content = msg.photo[-1].file_id
        content_type = 'photo'
    elif msg.content_type == types.ContentType.DOCUMENT:
        content = msg.document.file_id
        content_type = 'document'
    elif msg.content_type == types.ContentType.VOICE:
        content = msg.voice.file_id
        content_type = 'voice'
    elif msg.content_type == types.ContentType.VIDEO:
        content = msg.video.file_id
        content_type = 'video'

    db.add_product_content(product_id=getFSM.get('product_id'), content=content, product_type=content_type)


    list_content = [] # Здесь будет храниться список айдишников контента, который будет на товаре

    for content in db.get_list_product_content(product_id=getFSM.get('product_id'))[0][5]:
        list_content.append(str(content))

    list_content.append(db.get_last_product_content(product_id=getFSM.get('product_id'))[0][0]) # Добавляем последний добавленный добавленный контент в товары

    db.update_list_contents(product_id=getFSM.get('product_id'), contents_id=list_content, quantity='yes')
    
    await msg.answer(
        text='<b>Список добавленных товаров:</b>',
        reply_markup=list_product_content(product_id=getFSM.get('product_id'), page=0).as_markup()
    )


    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()



# Паганиция для товаров (инфопродуктов)


@router.callback_query(PaginatorContent.filter(F.array_name == 'content_inf'))
async def paginator_content_inf(call: types.CallbackQuery, callback_data: PaginatorContent, state: FSMContext):

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    caption = '''
<b>Список добавленных товаров:</b>
'''

    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(caption, reply_markup=list_product_content(product_id=callback_data.product_id, page=page).as_markup())
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(caption, reply_markup=list_product_content(product_id=callback_data.product_id, page=page).as_markup())
        else:
            await call.answer(text='Это начало страницы')
    
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()
    
















# -----------------------------------

@router.callback_query(CallProductContent.filter(F.action == 'open_content_no_reusable'))
async def open_product_content(call: types.CallbackQuery, callback_data: CallProductContent):
    content_data = db.get_product_content(content_id=callback_data.id)

    if content_data[0][3] == 'text':
        await call.message.edit_text(text=content_data[0][2])
    elif content_data[0][3] == 'video':
        await call.message.delete()
        await call.message.answer_video(video=str(content_data[0][2]))
    elif content_data[0][3] == 'voice':
        await call.message.delete()
        await call.message.answer_voice(voice=str(content_data[0][2]))
    elif content_data[0][3] == 'photo':
        await call.message.delete()
        await call.message.answer_photo(photo=str(content_data[0][2]))
    elif content_data[0][3] == 'document':
        await call.message.delete()
        await call.message.answer_document(document=str(content_data[0][2]))

    caption = '👆 это то, что будет отправлено после успешной оплаты'

    await call.message.answer(
        text=caption,
        reply_markup=product_content_no_reusable_kb(content_id=content_data[0][0], product_id=content_data[0][1]).as_markup()
    )


@router.callback_query(CallProductContent.filter(F.action == 'replace_product_content'))
async def add_new_product_content_inf(call: types.CallbackQuery, callback_data: CallProductContent, state: FSMContext):
    
    await call.message.edit_text(
        text='Пришли любой файл, видео, фото, голосовое или просто текст',
        reply_markup=cancel_add_new_content_no_reusable(product_id=callback_data.id).as_markup()
    )

    await state.update_data(product_id=callback_data.id)
    await state.set_state(Edit_Product_Inf.edit_product_inf)
    await state.update_data(what_to_edit='product_content')


# -----------------------------------


@router.callback_query(CallProductContent.filter(F.action == 'open_content'))
async def open_product_content(call: types.CallbackQuery, callback_data: CallProductContent):
    content_data = db.get_product_content(content_id=callback_data.id)

    if content_data[0][3] == 'text':
        await call.message.edit_text(text=content_data[0][2])
    elif content_data[0][3] == 'video':
        await call.message.delete()
        await call.message.answer_video(video=str(content_data[0][2]))
    elif content_data[0][3] == 'voice':
        await call.message.delete()
        await call.message.answer_voice(voice=str(content_data[0][2]))
    elif content_data[0][3] == 'photo':
        await call.message.delete()
        await call.message.answer_photo(photo=str(content_data[0][2]))
    elif content_data[0][3] == 'document':
        await call.message.delete()
        await call.message.answer_document(document=str(content_data[0][2]))

    caption = '👆 это то, что будет отправлено после успешной оплаты'

    await call.message.answer(
        text=caption,
        reply_markup=product_content_kb(content_id=content_data[0][0], product_id=content_data[0][1]).as_markup()
    )
    

@router.callback_query(CallProductContent.filter(F.action == 'delete_product_content')) 
async def delepe_product_content(call: types.CallbackQuery, callback_data: CallProductContent):
    product_id = db.get_product_content(content_id=callback_data.id)[0][1] # Получить айдишник продукта, чтобы вернуть клавиатуру с товарами
    content_id = str(db.get_product_content(content_id=callback_data.id)[0][0])

    list_content = [] # Здесь будет храниться список айдишников контента, который будет на товаре

    for content in db.get_list_product_content(product_id=product_id)[0][5]:
        if content != (content_id):
            list_content.append(str(content))

    db.update_list_contents(product_id=product_id, contents_id=list_content, quantity='yes')

    await call.answer(text='🗑 Товар удален!')

    await call.message.edit_text(
        text='Список добавленных товаров:',
        reply_markup=list_product_content(product_id=product_id, page=0).as_markup()
    )


@router.callback_query(CallProductContent.filter(F.action == 'add_content'))
async def add_new_product_content_inf(call: types.CallbackQuery, callback_data: CallProductContent, state: FSMContext):
    
    await call.message.edit_text(
        text='Пришли любой файл, видео, фото, голосовое или просто текст',
        reply_markup=cancel_add_new_content(product_id=callback_data.id).as_markup()
    )

    await state.set_state(Add_New_Product_Inf.more_inf_content)
    await state.update_data(product_id=callback_data.id)




# -----------------------------------

@router.callback_query(Add_New_Product_Inf.choose_content, F.data == 'one_inf_content')
async def choose_one_inf_content(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await call.answer(show_alert=True)

    await call.message.answer(
        text='Пришли любой файл, видео, фото, голосовое или просто текст'
    )
    await state.set_state(Add_New_Product_Inf.content_product_inf)



@router.message(Add_New_Product_Inf.content_product_inf, or_f(
        F.photo,
        F.text,
        F.document,
        F.video,
        F.voice
))
async def get_content_product_inf(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    getFSM = await state.get_data()
    project_id = db.get_project_id(bot_username.username)

    if msg.content_type == types.ContentType.TEXT:
        content = msg.html_text
        content_type = 'text'
    elif msg.content_type == types.ContentType.PHOTO:
        content = msg.photo[-1].file_id
        content_type = 'photo'
    elif msg.content_type == types.ContentType.DOCUMENT:
        content = msg.document.file_id
        content_type = 'document'
    elif msg.content_type == types.ContentType.VOICE:
        content = msg.voice.file_id
        content_type = 'voice'
    elif msg.content_type == types.ContentType.VIDEO:
        content = msg.video.file_id
        content_type = 'video'

    db.add_product(
            project_id=project_id,
            product_type='inf',
            reusable='False',
            product_name=getFSM.get('name_product_inf'),
            product_description=getFSM.get('description_product_inf'),
            product_price=getFSM.get('price_product_inf'),
            contents=[],
            product_photo=[]
        )
    product_data = db.get_last_product(project_id, product_type='inf')

    db.add_product_content(product_id=product_data[0][0], content=content, product_type=content_type) # Добавляем контент в таблицу
    content_id = db.get_last_product_content(product_id=product_data[0][0])[0][0] # Получаем айдишник последнего добавленного контента

    db.update_list_contents(product_id=product_data[0][0], contents_id=[content_id], quantity='no') # Обновляем товар на товаре с одним товаром

    link = await create_start_link(msg.bot, f'{product_data[0][0]}', encode=True)
    total_price = product_data[0][6]

    if product_data[0][7] > 0:
        total_price = total_price - total_price / 100 * product_data[0][7]

    caption = f'''
<b>Название товара:</b> {product_data[0][8]}
<b>Описание товара:</b> {product_data[0][9]}

<b>Стоимость товара:</b> {product_data[0][6]} 🇷🇺RUB
<b>Скидка на товар:</b> {product_data[0][7]}%
<b>Итоговая цена:</b> {round(total_price)} 🇷🇺RUB

<b>Количество товара:</b> {product_data[0][11]}
<b>Количество продаж:</b> {product_data[0][12]}

<b>Ссылка на товар:</b> {link}
'''
    
    await msg.answer(
        text=caption,
        reply_markup=product_inf_kb(product_id=product_data[0][0]).as_markup()
    )

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()






# ----------------- Редактирование товара (инфопродукт)

class Edit_Product_Inf(StatesGroup):
    edit_product_inf = State()
    product_id = State()
    what_to_edit = State()


@router.callback_query(EditProductINF.filter(F.edit_product == 'edit_inf'))
async def edit_product_inf(call: types.CallbackQuery, callback_data: EditProductINF, state: FSMContext):
    await state.update_data(product_id=callback_data.product_id)
    
    if callback_data.what_to_edit == 'product_photo':

        caption = '''
📸 <b>Добавь фото для товара, которое будет отображаться у покупателя!</b>

🖼️ Яркое и привлекательное фото - это ключ к успешной продаже!
'''

        await call.message.edit_text(text=caption, reply_markup=edit_pictures_inf(product_id=callback_data.product_id).as_markup())
        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
            
        await state.clear()
    elif callback_data.what_to_edit == 'product_name':
        await state.set_state(Edit_Product_Inf.edit_product_inf)
        await state.update_data(what_to_edit='product_name')
        await call.message.edit_text(
            text='Какое будет новое название товара?',
            reply_markup=cancel_edit_product_inf(product_id=callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'product_description':
        await state.set_state(Edit_Product_Inf.edit_product_inf)
        await state.update_data(what_to_edit='product_description')
        await call.message.edit_text(
            text='Какое будет новое описание товара?',
            reply_markup=cancel_edit_product_inf(product_id=callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'product_price':
        await state.set_state(Edit_Product_Inf.edit_product_inf)
        await state.update_data(what_to_edit='product_price')
        await call.message.edit_text(
            text='Какая будет новая стоимость товара?',
            reply_markup=cancel_edit_product_inf(product_id=callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'product_discount':
        await state.set_state(Edit_Product_Inf.edit_product_inf)
        await state.update_data(what_to_edit='product_discount')
        await call.message.edit_text(
            text='Пришли новую скидку на товар от 0 до 99',
            reply_markup=cancel_edit_product_inf(product_id=callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'product_quantity':
        await state.set_state(Edit_Product_Inf.edit_product_inf)
        await state.update_data(what_to_edit='product_quantity')
        await call.message.edit_text(
            text='Пришли мне количество товара, которое сейчас доступно к продаже',
            reply_markup=cancel_edit_product_inf(product_id=callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'product_content':
        await call.message.edit_text(
            text='Товар, который будет выдан после покупки:',
            reply_markup=contetn_no_reusable_product_inf(product_id=callback_data.product_id).as_markup()
        )
    elif callback_data.what_to_edit == 'product_contents':
        await call.message.edit_text(
            text='Список добавленных товаров:',
            reply_markup=list_product_content(product_id=callback_data.product_id, page=0).as_markup()
        )
    elif callback_data.what_to_edit == 'display_status_of':
        db.update_display_status(product_id=callback_data.product_id, status='выключен')
        await call.message.edit_reply_markup(reply_markup=product_inf_kb(product_id=callback_data.product_id).as_markup())
        await call.answer(text='Больше не показываем товар покупателям!', show_alert=True)
    elif callback_data.what_to_edit == 'display_status_on':
        db.update_display_status(product_id=callback_data.product_id, status='включен')
        await call.message.edit_reply_markup(reply_markup=product_inf_kb(product_id=callback_data.product_id).as_markup()) 
        await call.answer(text='Снова показываем товар покупателям!', show_alert=True)  
    elif callback_data.what_to_edit == 'delete_product':
        await call.message.edit_text(
            text='Ты уверен, что хочешь удалить товар? Все данные о товаре будут удалены!',
            reply_markup=delete_product_inf_product(product_id=callback_data.product_id).as_markup()
        )


@router.callback_query(ListPicturesInf.filter(F.action == 'open_picture_inf'))
async def open_picture_product_dv(call: types.CallbackQuery, callback_data: ListPicturesInf, state: FSMContext):

    photo = db.get_picture_product(picture_id=callback_data.picture_id)

    await call.message.delete()
    await call.message.answer_photo(photo=photo[0][3], reply_markup=picture_inf_kb(picture_id=callback_data.picture_id, product_id=callback_data.product_id).as_markup())


@router.callback_query(ListPicturesInf.filter(F.action == 'back_from_photo_inf'))
async def back_picture_product_dv(call: types.CallbackQuery, callback_data: ListPicturesInf, state: FSMContext):

    caption = '''
📸 <b>Добавь фото для товара, которое будет отображаться у покупателя!</b>

🖼️ Яркое и привлекательное фото - это ключ к успешной продаже!
'''

    await call.message.delete()
    await call.message.answer(text=caption, reply_markup=edit_pictures_inf(product_id=callback_data.product_id).as_markup())


@router.callback_query(ListPicturesInf.filter(F.action == 'delete_picture_inf'))
async def delete_picture_product_dv(call: types.CallbackQuery, callback_data: ListPicturesInf, state: FSMContext):
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
    await call.message.answer(text=caption, reply_markup=edit_pictures_inf(product_id=callback_data.product_id).as_markup())
    await call.answer(text='🗑 Фото удалено!')



@router.callback_query(ListPicturesInf.filter(F.action == 'add_picture_inf'))
async def add_picture_product_dv(call: types.CallbackQuery, callback_data: ListPicturesInf, state: FSMContext):

    await call.message.edit_text(
        text='Пришли фото твоего товара😉',
        reply_markup=cancel_add_picture_inf(product_id=callback_data.product_id).as_markup()
    )

    await state.set_state(Edit_Product_Inf.edit_product_inf)
    await state.update_data(what_to_edit='add_picture_inf')




@router.message(Edit_Product_Inf.edit_product_inf, or_f(
        F.photo,
        F.audio,
        F.text,
        F.document,
        F.video,
        F.voice
))
async def get_new_product_inf_data(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()

    if getFSM.get('what_to_edit') == 'add_picture_inf':
        try:
            picture_id = msg.photo[-1].file_id
            db.add_new_picture_product(product_id=getFSM.get('product_id'), picture_id=picture_id) # Добавляем новое фото

            list_pic = []
            for photo in db.get_list_pictures(product_id=getFSM.get('product_id')):
                list_pic.append(photo[0])

            db.edit_product(product_id=getFSM.get('product_id'), set='product_photo', new_data=list_pic)
        
            await msg.answer(text='✅ Новое фото товара добавлено!', reply_markup=return_list_picture_inf(product_id=getFSM.get('product_id')).as_markup())

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()
        except:
            await msg.answer('Кажется ты прислал что-то не то🧐')
        
    elif getFSM.get('what_to_edit') == 'product_name':
        if len(msg.text) > 24:
            await msg.answer('Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов', reply_markup=cancel_edit_product_inf(product_id=getFSM.get('product_id')).as_markup())
        else:
            db.edit_product(product_id=getFSM.get('product_id'),  set='product_name', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару',
                reply_markup=return_product_inf_kb(product_id=str(getFSM.get('product_id'))).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()
    elif getFSM.get('what_to_edit') == 'product_description':
        if len(msg.text) > 1024:
            await msg.answer(text='Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 1024 символов', reply_markup=cancel_edit_product_inf(product_id=getFSM.get('product_id')).as_markup())
        else:
            db.edit_product(product_id=getFSM.get('product_id'),  set='product_description', new_data=msg.html_text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару',
                reply_markup=return_product_inf_kb(product_id=str(getFSM.get('product_id'))).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()
    elif getFSM.get('what_to_edit') == 'product_quantity':
        if (msg.text.isdigit() and int(msg.text) > -1) and  (msg.text.isdigit() and int(msg.text) < 1000000):
            db.edit_product(product_id=getFSM.get('product_id'),  set='quantity', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару',
                reply_markup=return_product_inf_kb(product_id=str(getFSM.get('product_id'))).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
            
            await state.clear()
        else:
            await msg.answer('Пришли кол-во товара в диапазоне от 0 до 999999', reply_markup=cancel_edit_product_inf(product_id=getFSM.get('product_id')).as_markup())
    elif getFSM.get('what_to_edit') == 'product_price':
        if msg.text.isdigit() and int(msg.text) > 0 and msg.text.isdigit() and int(msg.text) < 1000001: 
            db.edit_product(product_id=getFSM.get('product_id'),  set='price', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару',
                reply_markup=return_product_inf_kb(product_id=str(getFSM.get('product_id'))).as_markup()
            )

            # Сбрасываем текущее состояния
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()
        else:
            await msg.answer('Пришли стоимость товара не меньше 1 RUB и не больше 1,000,000 RUB 😉', reply_markup=cancel_edit_product_inf(product_id=getFSM.get('product_id')).as_markup())
    elif getFSM.get('what_to_edit') == 'product_discount':
        if (msg.text.isdigit() and int(msg.text) > -1) and  (msg.text.isdigit() and int(msg.text) < 100):
            product_data = db.get_product_data(product_id=getFSM.get('product_id'))

            total_price = product_data[0][6] - product_data[0][6] / 100 * int(msg.text)

            if round(total_price) == 0:
                db.edit_product(product_id=getFSM.get('product_id'), set='discount', new_data=msg.text)
                await msg.answer(
                text='✅ Готово! Изменения применены, возвращайся к товару', 
                reply_markup=return_product_inf_kb(product_id=getFSM.get('product_id')).as_markup()
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
                reply_markup=return_product_inf_kb(product_id=getFSM.get('product_id')).as_markup()
            )
                # Сбрасываем текущее состояния
                current_state = await state.get_state()

                if current_state is None:
                    return
        
                await state.clear()
            else:
                await msg.answer(text='Итоговая стоимость товара со скидкой не должна быть меньше 1 🇷🇺RUB.', reply_markup=cancel_edit_product_inf(product_id=getFSM.get('product_id')).as_markup())
        else:
            await msg.answer(text='Пришли размер скидки от 0 до 99', reply_markup=cancel_edit_product_inf(product_id=getFSM.get('product_id')).as_markup())
    elif getFSM.get('what_to_edit') == 'product_content':

        if msg.content_type == types.ContentType.TEXT:
            content = msg.html_text
            content_type = 'text'
        elif msg.content_type == types.ContentType.PHOTO:
            content = msg.photo[-1].file_id
            content_type = 'photo'
        elif msg.content_type == types.ContentType.DOCUMENT:
            content = msg.document.file_id
            content_type = 'document'
        elif msg.content_type == types.ContentType.VOICE:
            content = msg.voice.file_id
            content_type = 'voice'
        elif msg.content_type == types.ContentType.VIDEO:
            content = msg.video.file_id
            content_type = 'video'

        # нужно добавить новый контент в таблицу и заменить его на товаре

        db.add_product_content(product_id=getFSM.get('product_id'), content=content, product_type=content_type) # Добавляем контент в таблицу
        content_id = db.get_last_product_content(product_id=getFSM.get('product_id'))[0][0] # Получаем айдишник последнего добавленного контента
        db.update_list_contents(product_id=getFSM.get('product_id'), contents_id=[content_id], quantity='no') # Обновляем товар на товаре с одним товаром

        await msg.answer(
            text='Товар, который будет выдан после покупки:',
            reply_markup=contetn_no_reusable_product_inf(product_id=getFSM.get('product_id')).as_markup()
        )




@router.callback_query(EditProductINF.filter(F.edit_product == 'delete_inf'))
async def delete_product_inf(call: types.CallbackQuery, callback_data: EditProductINF, state: FSMContext):
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
                reply_markup=return_list_products_inf().as_markup()
            )
    else:
        await call.answer(
                text='Товар находится на стадии оплаты, попробуйте позже ⏳',
                show_alert=True
            )


    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()