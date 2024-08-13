from aiogram import types, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from Database.Admin_db import Database


from Keyboards.admin_keyboards.resources_keyboards import(
    list_resources,
    resource_kb,
    cancel_add_new_resource,
    ListResources,
    Paginator
)



db = Database()
router = Router()





@router.callback_query(F.data == 'resources')
async def call_resources(call: types.CallbackQuery):
    bot_username = await call.bot.get_me()

    caption = '''
<b>Добавляй каналы, доступ к которым ты хочешь продавать! 🤑 </b>

P.S.: <i>Не забудь нажать кнопку "Обновить", чтобы информация о канале была актуальной! ♻️</i>
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=list_resources(bot_username=bot_username.username, page=0).as_markup()
    )


# Пагинатор

@router.callback_query(Paginator.filter(F.array_name == 'resources'))
async def paginator_resources(call: types.CallbackQuery, callback_data: Paginator, state: FSMContext):
    bot_username = await call.bot.get_me()

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    caption = '''
<b>Добавляй каналы, доступ к которым ты хочешь продавать! 🤑 </b>

P.S.: <i>Не забудь нажать кнопку "Обновить", чтобы информация о канале была актуальной! ♻️</i>
'''

    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text=caption,
                reply_markup=list_resources(bot_username=bot_username.username, page=page).as_markup()
            )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text=caption,
                reply_markup=list_resources(bot_username=bot_username.username, page=page).as_markup()
            )
        else:
            await call.answer(text='Это начало страницы')

    # Сбрасываем текущее состояние
    current_state = await state.get_state()
    if current_state is None:
        return



# Добавление нового ресурса
class AddResource(StatesGroup):
    add_resource = State()


@router.callback_query(F.data == 'add_resource')
async def call_add_resource(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()

    caption = f'''
Добавь бота @{bot_username.username} в администраторы канала с правами "Добавлять участников/Пригласительные ссылки".

Затем перешли любое сообщение из канала.
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=cancel_add_new_resource().as_markup()
    )
    await call.answer(show_alert=True)
    await state.set_state(AddResource.add_resource)



@router.message(AddResource.add_resource)
async def get_data_channel(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    try:
        channel_id = msg.forward_from_chat.id
        name_channel = msg.forward_from_chat.full_name
        
        status = await msg.bot.get_chat_member(chat_id=channel_id, user_id=msg.bot.id)
        if status.can_invite_users:
            if db.check_resource(channel_id=channel_id, bot_username=bot_username.username) == []:
                db.add_resourse(
                    project_id=db.get_project_id(bot_username=bot_username.username),
                    channel_name=name_channel,
                    channel_id=channel_id
                )

                caption = '''
Добавляй каналы, доступ к которым ты хочешь продавать! 🤑 

P.S.: Не забудь нажать кнопку "Обновить", чтобы информация о канале была актуальной! ♻️
'''

                await msg.answer(
                    text=caption,
                    reply_markup=list_resources(bot_username=bot_username.username, page=0).as_markup()
                )

                # Сбрасываем текущее состояние 
                current_state = await state.get_state()
                if current_state is None:
                    return

                await state.clear()
            else:
                await msg.answer('Данный канал уже добавлен в этот проект😄', reply_markup=cancel_add_new_resource().as_markup())
        else:
            caption = '''
Упс, бот не может работать, потому что у него нет нужных прав!  🤔  Пожалуйста, дай боту доступ к "Добавлять участников/Пригласительные ссылки"  и перешли пост из канала еще раз. 
'''

            await msg.answer(text=caption, reply_markup=cancel_add_new_resource().as_markup())
    except:
        caption = '''
Похоже, ты отправил не то сообщение! 😕  Попробуй переслать любой пост из канала, где ты добавил бота в администраторы,  или нажми "Отмена".
'''

        await msg.answer(text=caption, reply_markup=cancel_add_new_resource().as_markup())
    

# Открываем ресурс

@router.callback_query(ListResources.filter(F.action == 'open_resource'))
async def get_data_source(call: types.CallbackQuery, callback_data: ListResources):
    resource_data = db.get_data_resources(resource_id=callback_data.resource_id)
    
    await call.message.edit_text(
        text=f'<b>Название канала:</b> {resource_data[0][2]}\n<b>ID проекта:</b> {resource_data[0][1]}',
        reply_markup=resource_kb(resource_id=callback_data.resource_id).as_markup()
    )


# Удаляем ресурс

@router.callback_query(ListResources.filter(F.action == 'delete_resource'))
async def call_delete_resource(call: types.CallbackQuery, callback_data: ListResources):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    black_list = ''

    for item in db.get_list_content_ch_product(project_id=project_id): # Проверяем добавлен ли этот ресурс к одному из товаров
        if callback_data.resource_id in item[0]:
            black_list += f'\n- {item[1]}'

    if len(black_list) > 1:
        await call.answer(
            text=f'Нельзя удалить этот ресурс, так как он привязан к товарам🙃',
            show_alert=True
        )
    else:
        db.delete_resource(resource_id=callback_data.resource_id)

        caption = '''
<b>Добавляй каналы, доступ к которым ты хочешь продавать! 🤑 </b>

P.S.: <i>Не забудь нажать кнопку "Обновить", чтобы информация о канале была актуальной! ♻️</i>
'''

        await call.message.edit_text(
            text=caption,
            reply_markup=list_resources(bot_username=bot_username.username, page=0).as_markup()
        )
        await call.answer(text='🗑 Ресурс удален!', show_alert=True)
        





# Обновляем данные о товоре. На данный момоент обновится только название  канала, если оно было изменено

@router.callback_query(F.data == 'udpdate_data_resources')
async def call_udpdate_data_resources(call: types.CallbackQuery):
    bot_username = await call.bot.get_me()

    try:
        for resource in db.get_list_resources(bot_username=bot_username.username):
            status_resource = await call.bot.get_chat(chat_id=resource[3])

            if status_resource.full_name != resource[2]:
                db.update_data_resource(channel_id=resource[3], new_name=status_resource.full_name)
    except:
        pass
            
            
    await call.answer(text='✅ Данные обновлены', show_alert=True)