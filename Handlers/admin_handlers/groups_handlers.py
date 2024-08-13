from aiogram import types, F, Router
from aiogram.filters import or_f
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext



from Database.Admin_db import Database


from Keyboards.admin_keyboards.menu_keyboards import(
    start_admin_kb,
    cancel_kb,
)
from Keyboards.admin_keyboards.groups_keyboards import(
    user_groups_kb,
    user_groups_next_lvl,
    list_category_products,
    list_products_in_category,
    delete_group,
    cancel_add_new_group,
    cancel_edit_group,
    edit_group_picture,
    cancel_add_new_group_picture,
    group_picture_kb,
    ListGroups,
    AddProductToGroup,
    PaginatorCP,
    PicturesGroup,
    Paginator
)



db = Database()
router = Router()



class Add_Group(StatesGroup):
    add_group = State()
    group_name = State()
    group_description = State()
    group_lvl = State()
    parent_id = State()
    group_id = State()

class Choose_product(StatesGroup):
    product_selected = State()
    
    


@router.callback_query(F.data == 'groups')
async def call_groups(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()

    caption = '''
🛍️ Нажми кнопку "<b>Товары</b>", чтобы добавить товары на главную витрину твоего магазина

➕ Создавай категории товаров, нажав на кнопку "<b>ДОБАВИТЬ ГРУППУ</b>"
'''
    await call.message.edit_text(
        text=caption,
        reply_markup=user_groups_kb(bot_username=bot_username.username, page=0).as_markup()
        )
    
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()



# Пагинация для main group

@router.callback_query(Paginator.filter(F.array_name == 'pag_main_group'))
async def paginator_main_group(call: types.CallbackQuery, state: FSMContext, callback_data: Paginator):
    bot_username = await call.bot.get_me()

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    caption = f'''
🛍️ Нажми кнопку "<b>Товары</b>", чтобы добавить товары на главную витрину твоего магазина

➕ Создавай категории товаров, нажав на кнопку "<b>ДОБАВИТЬ ГРУППУ</b>"
'''

    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text=caption,
                reply_markup=user_groups_kb(bot_username=bot_username.username, page=page).as_markup()
            )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text=caption,
                reply_markup=user_groups_kb(bot_username=bot_username.username, page=page).as_markup()
            )
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()


    

# Добавляем товары в группу

@router.callback_query(ListGroups.filter(F.action == 'add_product_to_group'))
async def add_product_to_group(call: types.CallbackQuery, callback_data: ListGroups):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    await call.message.edit_text(
        text='Товар из какой категории хочешь добавить?',
        reply_markup=list_category_products(project_id=project_id, group_id=callback_data.group_id, group_lvl=callback_data.group_lvl, parent_id=callback_data.parent_id).as_markup()
    )


@router.callback_query(AddProductToGroup.filter(F.action == 'open_category'))
async def call_open_list_products_to_group(call: types.CallbackQuery, callback_data: AddProductToGroup, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if callback_data.parent_id == '-1':
        group_id = db.get_showcase_id(project_id)
    else: 
        group_id = callback_data.group_id


    try:

        selected = db.get_active_list_products_to_groups(group_id=group_id)
        await state.update_data(product_selected=selected)


        await call.message.edit_text(
            text='Выберите товары, которые будут отображаться в этой группе:',
            reply_markup=list_products_in_category(
                    project_id=project_id, 
                    product_type=callback_data.category_name, 
                    group_id=group_id,
                    selected=selected,
                    page=0, 
                    parent_id=callback_data.parent_id).as_markup()
        )
    except:
        await call.answer(
            text='Нет товаров из данной категории',
            show_alert=True
        )



# PAGINATOR

@router.callback_query(PaginatorCP.filter(F.array_name == 'products_of_choice'))
async def paginator_products_to_group(call: types.CallbackQuery, state: FSMContext, callback_data: PaginatorCP):
    getFSM = await state.get_data()

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)
    group_id = int(callback_data.group_id)
    project_id = int(callback_data.project_id)
    selected = getFSM.get('product_selected')
    product_type = callback_data.product_type

    caption = '''
Выберите товары, которые будут отображаться в этой группе:
'''


    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text=caption,
                reply_markup=list_products_in_category(
                    project_id=project_id, 
                    product_type=product_type, 
                    group_id=group_id,
                    selected=selected,
                    page=page, 
                    parent_id=callback_data.parent_id).as_markup()
            )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text=caption,
                reply_markup=list_products_in_category(
                    project_id=project_id, 
                    product_type=product_type, 
                    group_id=group_id,
                    selected=selected,
                    page=page, 
                    parent_id=callback_data.parent_id).as_markup()
            )
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()




@router.callback_query(AddProductToGroup.filter(F.action == 'choose_product'))
async def choose_list_products(call: types.CallbackQuery, callback_data: AddProductToGroup, state: FSMContext):
    getFSM = await state.get_data()

    selected = getFSM.get('product_selected')
    if callback_data.product_id in selected:
        selected.remove(f'{callback_data.product_id}')
    else:
        selected.append(callback_data.product_id)
    await state.update_data(product_selected=selected)


    await call.message.edit_text(
        text='Выберите товары, которые будут отображаться в этой группе:',
        reply_markup=list_products_in_category(
                project_id=callback_data.project_id, 
                product_type=callback_data.category_name, 
                group_id=callback_data.group_id,
                selected=selected,
                page=callback_data.page, 
                parent_id=callback_data.parent_id).as_markup()
    )


# Open group

@router.callback_query(ListGroups.filter(F.action == 'open_group'))
async def open_group(call: types.CallbackQuery, callback_data: ListGroups, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    group_data = db.get_group_data(group_id=callback_data.group_id)

    caption = f'''
<b>Название группы: </b>{group_data[0][3]}
<b>Описание группы: </b>{group_data[0][4]}
----------------------------
<i>Добавляйте товары в группу или создайте новую группу внутри существующей</i>
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=user_groups_next_lvl(group_id=group_data[0][0], parent_id=group_data[0][1], group_lvl=group_data[0][7], project_id=project_id, page=0).as_markup()
    )

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()


# Пагинация для групп

@router.callback_query(PaginatorCP.filter(F.array_name == 'pag_groups'))
async def paginator_groups(call: types.CallbackQuery, state: FSMContext, callback_data: PaginatorCP):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    button = callback_data.button
    page = int(callback_data.page)
    max_pages = int(callback_data.max_pages)

    group_data = db.get_group_data(group_id=callback_data.group_id)

    caption = f'''
<b>Название группы: </b>{group_data[0][3]}
<b>Описание группы: </b>{group_data[0][4]}
----------------------------
<i>Добавляйте товары в группу или создайте новую группу внутри существующей</i>
'''

    if button == 'next':
        if page < max_pages-1:
            page += 1
            await call.message.edit_text(
                text=caption,
                reply_markup=user_groups_next_lvl(group_id=group_data[0][0], parent_id=group_data[0][1], group_lvl=group_data[0][7], project_id=project_id, page=page).as_markup()
            )
        else:
            await call.answer(text='Это последняя страница')
    else:
        if page > 0:
            page -= 1
            await call.message.edit_text(
                text=caption,
                reply_markup=user_groups_next_lvl(group_id=group_data[0][0], parent_id=group_data[0][1], group_lvl=group_data[0][7], project_id=project_id, page=page).as_markup()
            )
        else:
            await call.answer(text='Это начало страницы')
    
    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()






# Add New Group

@router.callback_query(ListGroups.filter(F.action == 'add_new_group'))
async def call_add_group(call: types.CallbackQuery, callback_data: ListGroups, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    

    await call.message.edit_text(
        text='Какое будет название группы?', 
        reply_markup=cancel_add_new_group(
            group_id=callback_data.group_id, 
            parent_id=callback_data.parent_id, 
            project_id=project_id
        ).as_markup()
    )

    await state.set_state(Add_Group.add_group)
    await state.update_data(group_id=callback_data.group_id)
    await state.update_data(group_lvl=callback_data.group_lvl)
    await state.update_data(parent_id=callback_data.group_id)
    await call.answer(show_alert=True)

        



@router.message(Add_Group.add_group, F.text)
async def get_group_name(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    getFSM = await state.get_data()

    if len(msg.text) > 24:
        await msg.answer(
            text='Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов', 
            reply_markup=cancel_add_new_group(
                group_id=getFSM.get('group_id'),
                parent_id=getFSM.get('parent_id'),
                project_id=project_id
            ).as_markup()
        )
    else:
        await state.update_data(group_name=msg.text)
        await state.set_state(Add_Group.group_description)

        await msg.answer(
            text='Отлично! Теперь пришли описание группы', 
            reply_markup=cancel_add_new_group(
                group_id=getFSM.get('group_id'),
                parent_id=getFSM.get('parent_id'),
                project_id=project_id
            ).as_markup()
        )


@router.message(Add_Group.group_description, F.text)
async def get_description_group(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    #----------------------------- Get states
    getFSM = await state.get_data()
    group_lvl = int(getFSM.get('group_lvl')) + 1
    group_name = getFSM.get('group_name')
    parent_id = getFSM.get('parent_id')
    #----------------------------- Get states
    

    if len(msg.html_text) > 2048:
        await msg.answer(
            text='Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 2048 символов', 
            reply_markup=cancel_add_new_group(
                group_id=getFSM.get('group_id'),
                parent_id=parent_id,
                project_id=project_id
            ).as_markup()
        )
    else:
        db.add_new_group(
            parent_id=parent_id,
            group_lvl=group_lvl,
            group_name=group_name,
            group_description=msg.html_text,
            project_id=project_id
        )

        if getFSM.get('group_lvl') == '0':
            caption = '''
🛍️ Нажми кнопку "<b>Товары</b>", чтобы добавить товары на главную витрину твоего магазина

➕ Создавай категории товаров, нажав на кнопку "<b>ДОБАВИТЬ ГРУППУ</b>"            
'''

            await msg.answer(
                text=caption,
                reply_markup=user_groups_kb(bot_username=bot_username.username, page=0).as_markup()
            )
        else:
            group_data = db.get_last_group(project_id=project_id)

            caption = f'''
<b>Название группы: </b>{group_data[0][3]}
<b>Описание группы: </b>{group_data[0][4]}
----------------------------
<i>Добавляйте товары в группу или создайте новую группу внутри существующей</i>
'''

            await msg.answer(
                text=caption,
                reply_markup=user_groups_next_lvl(group_id=group_data[0][0], parent_id=group_data[0][1], group_lvl=group_data[0][7], project_id=project_id, page=0).as_markup()
            )



        # Сбрасываем текущее состояние
        current_state = await state.get_state()

        if current_state is None:
            return
        
        await state.clear()



# Редактирование группы


class Edit_Group(StatesGroup):
    new_data = State()
    group_id = State()
    parent_id = State()
    what_to_edit = State()
    group_picture = State()





@router.callback_query(ListGroups.filter(F.action == 'edit_group'))
async def call_edit_group(call: types.CallbackQuery, callback_data: ListGroups, state: FSMContext):
    await state.set_state(Edit_Group.new_data)
    await state.update_data(group_id=callback_data.group_id)
    await state.update_data(parent_id=callback_data.parent_id)
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if callback_data.group_lvl == 'group_name':
        await call.message.edit_text(
            text='Пришли мне новое название группы', 
            reply_markup=cancel_edit_group(group_id=callback_data.group_id, parent_id=callback_data.parent_id).as_markup()
        )
        await state.update_data(what_to_edit='group_name')
    elif callback_data.group_lvl == 'group_description':
        await call.message.edit_text(
            text='Пришли мне новое описание группы', 
            reply_markup=cancel_edit_group(group_id=callback_data.group_id, parent_id=callback_data.parent_id).as_markup()
        )
        await state.update_data(what_to_edit='group_description')
    elif callback_data.group_lvl == 'group_photo':
        try:
            await call.message.edit_text(
                text='Добавь фото группы, которое будет описывать содержимое данной группы😉', 
                reply_markup=edit_group_picture(           
                    group_id=callback_data.group_id, 
                    parent_id=callback_data.parent_id,
                    group_lvl='none'
                ).as_markup()
            )
        except:
            await call.message.delete()
            await call.message.answer(
                text='Добавь фото группы, которое будет описывать содержимое данной группы😉', 
                reply_markup=edit_group_picture(           
                    group_id=callback_data.group_id, 
                    parent_id=callback_data.parent_id,
                    group_lvl='none'
                ).as_markup()
            )
    elif callback_data.group_lvl == 'delete_group': # Спрашивает, точно ли юзер хочет удалить группу
        await call.message.edit_text(
            text='При удалении группы будут удалены все группы уровня ниже. Ты уверен, что хочешь удалить группу?', 
            reply_markup=delete_group(group_id=callback_data.group_id, parent_id=callback_data.parent_id).as_markup()
        )
    elif callback_data.group_lvl == 'yes_delete_group': # Если согласен, то код ниже удалит группу и все принадлежащие ей дочерние группы
        db.delete_group(group_id=int(callback_data.group_id))

        

        if str(db.get_all_groups(project_id=project_id)[0][0]) == callback_data.parent_id:
            caption = '''
🛍️ Нажми кнопку "<b>Товары</b>", чтобы добавить товары на главную витрину твоего магазина

➕ Создавай категории товаров, нажав на кнопку "<b>ДОБАВИТЬ ГРУППУ</b>"
'''

            await call.message.edit_text(
                text=caption,
                reply_markup=user_groups_kb(bot_username=bot_username.username, page=0).as_markup()
            )

        else:
            group_data = db.get_group_data(group_id=callback_data.parent_id)

            caption = f'''
<b>Название группы: </b>{group_data[0][3]}
<b>Описание группы: </b>{group_data[0][4]}
----------------------------
<i>Добавляйте товары в группу или создайте новую группу внутри существующей</i>
'''
            await call.message.edit_text(
                text=caption,
                reply_markup=user_groups_next_lvl(group_id=group_data[0][0], parent_id=group_data[0][1], group_lvl=group_data[0][7], project_id=project_id, page=0).as_markup()
            )

            current_state = await state.get_state()
            if current_state is None:
                return

            await state.clear()



@router.callback_query(PicturesGroup.filter(F.action == 'open_group_picture'))
async def call_open_group_picture(call: types.CallbackQuery, callback_data: PicturesGroup):
    picture = db.get_group_picture(group_id=callback_data.group_id)

    await call.message.delete()
    await call.message.answer_photo(
        photo=picture[0][3],
        reply_markup=group_picture_kb(
            group_id=callback_data.group_id,
            parent_id=callback_data.parent_id,
            picture_id=picture[0][0]
        ).as_markup()
    )



@router.callback_query(PicturesGroup.filter(F.action == 'add_new_group_picture'))
async def call_add_new_group_picture(call: types.CallbackQuery, callback_data: PicturesGroup, state: FSMContext):
    await state.update_data(group_id=callback_data.group_id)
    await state.update_data(parent_id=callback_data.parent_id)

    await call.message.edit_text(
        text='Пришли фото для группы',
        reply_markup=cancel_add_new_group_picture(
            group_id=callback_data.group_id,
            parent_id=callback_data.parent_id
        ).as_markup()
    )

    await state.set_state(Edit_Group.group_picture)



@router.message(Edit_Group.group_picture)
async def get_new_group_photo(msg: types.Message, state: FSMContext):
    get_FSM = await state.get_data()


    if msg.content_type == types.ContentType.PHOTO:
        db.add_new_group_picture(
            group_id=get_FSM.get('group_id'),
            photo=msg.photo[-1].file_id
        )

        await msg.answer(
            text='Добавь фото группы, которое будет описывать содержимое данной группы😉', 
            reply_markup=edit_group_picture(           
                group_id=get_FSM.get('group_id'),
                parent_id=get_FSM.get('parent_id'),
                group_lvl='none'
            ).as_markup()
        )

        # Сбрасываем текущее состояние
        current_state = await state.get_state()

        if current_state is None:
            return
        
        await state.clear()
    else:
        await msg.answer(
                text='Пришли фото для группы',
                reply_markup=cancel_add_new_group_picture(
                group_id=get_FSM.get('group_id'),
                parent_id=get_FSM.get('parent_id')
            ).as_markup()
        )


@router.callback_query(PicturesGroup.filter(F.action == 'delete_group_picture'))
async def call_delete_group_picture(call: types.CallbackQuery, callback_data: PicturesGroup):
    db.delete_group_picture(picture_id=callback_data.picture_id)

    await call.message.delete()
    await call.message.answer(
        text='Добавь фото группы, которое будет описывать содержимое данной группы😉', 
        reply_markup=edit_group_picture(           
            group_id=callback_data.group_id, 
            parent_id=callback_data.parent_id,
            group_lvl='none'
        ).as_markup()
    )

    await call.answer(
        text='🗑 Фото удалено!'
    )




@router.message(Edit_Group.new_data, F.text)
async def get_new_data_group(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    getFSM = await state.get_data()

    if getFSM.get('what_to_edit') == 'group_name':
        if len(msg.text) > 24:
            await msg.answer(
                text='Ты прислал слишком длинное название🙃\n\nПришли название не длиннее 24 символов', 
                reply_markup=cancel_edit_group(group_id=getFSM.get('group_id'), parent_id=getFSM.get('parent_id')).as_markup()
        )
        else:
            db.edit_group(group_id=getFSM.get('group_id'), new_data=msg.text, set='group_name')

            group_data = db.get_group_data(group_id=getFSM.get('group_id'))

            caption = f'''
<b>Название группы: </b>{group_data[0][3]}
<b>Описание группы: </b>{group_data[0][4]}
----------------------------
<i>Добавляйте товары в группу или создайте новую группу внутри существующей</i>
'''

            await msg.answer(
                text=caption,
                reply_markup=user_groups_next_lvl(group_id=group_data[0][0], parent_id=group_data[0][1], group_lvl=group_data[0][7], project_id=project_id, page=0).as_markup()
            )             

            # Сбрасываем текущее состояние
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()

    else:
        if len(msg.html_text) > 2048:
            await msg.answer(
                text='Ты прислал слишком длинное описание🙃\n\nПришли описание не длиннее 2048 символов', 
                reply_markup=cancel_edit_group(group_id=getFSM.get('group_id'), parent_id=getFSM.get('parent_id')).as_markup()
            )
        else:
            db.edit_group(group_id=getFSM.get('group_id'), new_data=msg.html_text, set='group_description')

            group_data = db.get_group_data(group_id=getFSM.get('group_id'))

            caption = f'''
<b>Название группы: </b>{group_data[0][3]}
<b>Описание группы: </b>{group_data[0][4]}
----------------------------
<i>Добавляйте товары в группу или создайте новую группу внутри существующей</i>
'''

            await msg.answer(
                text=caption,
                reply_markup=user_groups_next_lvl(group_id=group_data[0][0], parent_id=group_data[0][1], group_lvl=group_data[0][7], project_id=project_id, page=0).as_markup()
            )


            # Сбрасываем текущее состояние
            current_state = await state.get_state()

            if current_state is None:
                return
        
            await state.clear()