from aiogram import types, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext



from Database.Admin_db import Database


from Keyboards.admin_keyboards.menu_keyboards import(
    start_admin_kb,
    cancel_kb,
)
from Keyboards.admin_keyboards.design_keyboards import(
    design_kb,
    design_message_kb,
    edit_message_kb,
    design_decor_kb,
    menu_picture_kb,
    cancel_add_menu_pic,
    picture_kb,
    cancel_edit_message,
    EditMessage,
    Edit,
    DesignDecor
)




db = Database()
router = Router()




class EditCaption(StatesGroup):
    edit_caption = State()
    project_id = State()


class Add_Menu_Pic(StatesGroup):
    get_photo = State()
    project_id = State()



@router.callback_query(F.data == 'design')
async def call_design(call: types.CallbackQuery):
    caption = '''
<b>🎨 ДИЗАЙН</b>

В этом разделе вы можете персонализировать внешний вид и сообщения вашего магазина:

<blockquote><b>Добавить фото в главное меню 🖼</b>

Загружайте привлекательные изображения, чтобы сделать ваше главное меню более визуально привлекательным и уникальным.</blockquote>
<blockquote><b>Изменить дефолтные сообщения ✉️</b>

Настраивайте сообщения, которые получают пользователи после оплаты, при запуске бота и в главном меню. Создайте индивидуальный стиль общения с клиентами!</blockquote>
'''

    await call.message.edit_text(f'{caption}', reply_markup=design_kb().as_markup())




# Раздел design_decor

@router.callback_query(F.data == 'design_decor')
async def call_design_decor(call: types.CallbackQuery):

    caption = '''
Добавь фото в главное меню бота
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=design_decor_kb().as_markup()
    )


@router.callback_query(DesignDecor.filter(F.action == 'menu_picture'))
async def call_menu_picture(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = '''
Можешь добавить или удалить фото
'''

    try:
        await call.message.edit_text(
            text=caption,
            reply_markup=menu_picture_kb(project_id=project_id).as_markup()
        )
    except:
        await call.message.delete()
        await call.message.answer(
            text=caption,
            reply_markup=menu_picture_kb(project_id=project_id).as_markup()
        )

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()



@router.callback_query(DesignDecor.filter(F.action == 'open_menu_picture'))
async def call_open_menu_picture(call: types.CallbackQuery, callback_data: DesignDecor):

    photo = db.get_pic(pic_id=callback_data.data)

    await call.message.delete()
    await call.message.answer_photo(
        photo=photo[0][3],
        reply_markup=picture_kb(picture_id=photo[0][0]).as_markup()
    )



@router.callback_query(DesignDecor.filter(F.action == 'add_menu_picture'))
async def call_add_menu_picture(call: types.CallbackQuery, callback_data: DesignDecor, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    await call.message.edit_text(
        text='Ожидаю фото...',
        reply_markup=cancel_add_menu_pic().as_markup()
    )

    await state.set_state(Add_Menu_Pic.get_photo)
    await state.update_data(project_id=project_id)


@router.message(Add_Menu_Pic.get_photo)
async def get_menu_picture(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()

    if msg.content_type == types.ContentType.PHOTO:
        db.add_menu_picture(project_id=getFSM.get('project_id'), photo=msg.photo[-1].file_id)

        caption = '''
Можешь добавить или удалить фото
'''

        await msg.answer(
            text=caption,
            reply_markup=menu_picture_kb(project_id=getFSM.get('project_id')).as_markup()
        )

        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
            
        await state.clear()
    else:
        await msg.answer(
            text='Ты прислал что-то другое 🙃\nОжидаю фото...',
            reply_markup=cancel_add_menu_pic().as_markup()
        )



@router.callback_query(DesignDecor.filter(F.action == 'delete_menu_pic'))
async def call_delete_menu_picture(call: types.CallbackQuery, callback_data: DesignDecor):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    db.delete_menu_picture(picture_id=callback_data.data)

    caption = '''
Можешь добавить или удалить фото
'''

    await call.message.delete()
    await call.message.answer(
        text=caption,
        reply_markup=menu_picture_kb(project_id=project_id).as_markup()
    )







# Раздел design_message


@router.callback_query(F.data == 'design_message')
async def call_design_message(call: types.CallbackQuery):
    caption = '''
<b>🎨 Дизайн</b>

В этом разделе вы можете настроить сообщения по умолчанию для вашего бота, делая его более персонализированным и привлекательным для пользователей.

<blockquote>💳 Сообщение после оплаты: Настройте сообщение, которое пользователи будут получать после успешной оплаты.</blockquote>
<blockquote>👋 Сообщение после нажатия кнопки /start: Задайте приветственное сообщение для новых пользователей.</blockquote>
<blockquote>🏠 Сообщение в главном меню: Измените текст главного меню, чтобы лучше отразить суть вашего бота.</blockquote>
'''

    await call.message.edit_text(f'{caption}', reply_markup=design_message_kb().as_markup())



@router.callback_query(EditMessage.filter(F.message == 'message'))
async def call_edit_message(call: types.CallbackQuery, callback_data: EditMessage):
    bot_username = await call.bot.get_me()

    if call.from_user.id == db.check_user_id_admin(bot_username=bot_username.username):
        if callback_data.edit == 'start_caption':
            caption = ''

            if db.get_caption(caption='start_caption', bot_username=bot_username.username) == '':
                caption = 'Старотовое сообщение не задано'
            else: 
                caption = f"{db.get_caption(caption='start_caption', bot_username=bot_username.username)}"
            
            await call.message.edit_text(text=f'<b>СТАРТОВОЕ СООБЩЕНИЕ</b>\n\n{caption}', reply_markup=edit_message_kb(edit='start_caption', project_id=db.get_project_id(bot_username=bot_username.username)).as_markup())
        elif callback_data.edit == 'menu_caption':
            caption = ''

            if db.get_caption(caption='menu_caption', bot_username=bot_username.username) == '':
                caption = 'Cообщение для меню не задано'
            else: 
                caption = f"{db.get_caption(caption='menu_caption', bot_username=bot_username.username)}"
            
            await call.message.edit_text(text=f'<b>СООБЩЕНИЕ ПОСЛЕ ЗАПУСКА БОТА</b>\n\n{caption}', reply_markup=edit_message_kb(edit='menu_caption', project_id=db.get_project_id(bot_username=bot_username.username)).as_markup())
        elif callback_data.edit == 'after_payment_caption':
            caption = ''

            if db.get_caption(caption='after_payment_caption', bot_username=bot_username.username) == '':
                caption = 'Cообщение после оплаты не задано'
            else: 
                caption = f"{db.get_caption(caption='after_payment_caption', bot_username=bot_username.username)}"
            
            await call.message.edit_text(text=f'<b>СООБЩЕНИЕ ПОСЛЕ УСПЕШНОЙ ОПЛАТЫ</b>\n\n{caption}', reply_markup=edit_message_kb(edit='after_payment_caption', project_id=db.get_project_id(bot_username=bot_username.username)).as_markup()) 



@router.callback_query(Edit.filter(F.edit_message == 'edit_message'))
async def call_edit(call: types.CallbackQuery, callback_data: Edit, state: FSMContext):
    await call.message.edit_text(
        text='Пришли новое сообщение не более 1024 символов и только текст', 
        reply_markup=cancel_edit_message(edit=callback_data.edit).as_markup()
    )

    await state.set_state(EditCaption.edit_caption)
    await state.update_data(edit_caption = callback_data.edit)
    await state.update_data(project_id = callback_data.project_id)



@router.message(EditCaption.edit_caption, F.text)
async def get_new_caption(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()
    bot_username = await msg.bot.get_me()

    if len(msg.text) < 1025:
        db.edit_caption(project_id=getFSM.get('project_id'), caption=getFSM.get('edit_caption'), new_caption=msg.html_text)   

        caption = str(db.get_caption(caption=getFSM.get('edit_caption'), bot_username=bot_username.username))

        if getFSM.get('edit_caption') == 'start_caption':
            chapter = '<b>СТАРТОВОЕ СООБЩЕНИЕ</b>'
        elif getFSM.get('edit_caption') == 'menu_caption':
            chapter = '<b>СООБЩЕНИЕ ПОСЛЕ ЗАПУСКА БОТА</b>'
        elif getFSM.get('edit_caption') == 'after_payment_caption':
            chapter = '<b>СООБЩЕНИЕ ПОСЛЕ УСПЕШНОЙ ОПЛАТЫ</b>'

        await msg.answer(text=f"{chapter}\n\n{caption}", reply_markup=edit_message_kb(edit=getFSM.get('edit_caption'), project_id=getFSM.get('project_id')).as_markup())

        # Сбрасываем текущее состояние
        if getFSM is None:
            return

        await state.clear()

    else:
        await msg.answer(
            text='Твое сообщение превышает 1024 символов!',
            reply_markup=cancel_edit_message(edit=getFSM.get('edit_caption')).as_markup()
        )