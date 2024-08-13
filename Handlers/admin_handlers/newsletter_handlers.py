from aiogram import types, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command


from Database.Admin_db import Database


from Keyboards.admin_keyboards.newsletter_keyboards import(
    newsletter_kb,
    cancel_create_newsletter,
    send_newsletter_kb,
    return_newsletter
)

router = Router()
db = Database()


class Create_Newsletter(StatesGroup):
    newsletter_content = State()
    newsletter_caption = State()
    newsletter_type = State()


@router.callback_query(F.data == 'newsletter')
async def call_newsletter(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    newsletter_data = db.get_statistic_newsletter(project_id=project_id)

    caption = f'''
<b>💌 Делись новостями, акциями или запускай рекламу! 😉</b>

👥 Всего пользователей: {newsletter_data[0][0]}
🚫 Заблокировали бота: {newsletter_data[0][1]}

<i>📊 Данные учитываются с последней рассылки</i>
'''
    try:
        await call.message.edit_text(
            text=caption,
            reply_markup=newsletter_kb().as_markup()
        )
    except:
        await call.message.delete()
        await call.message.answer(
            text=caption,
            reply_markup=newsletter_kb().as_markup()
        )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()



@router.callback_query(F.data == 'create_newsletter')
async def call_create_newsletter(call: types.CallbackQuery, state: FSMContext):

    caption = '''
С каким сообщением нужно сделать рассылку?
'''
    
    try:
        await call.message.edit_text(
            text= caption,
            reply_markup=cancel_create_newsletter().as_markup()
        )
    except:
        await call.message.delete()
        await call.message.answer(
            text= caption,
            reply_markup=cancel_create_newsletter().as_markup()
        )
    await state.set_state(Create_Newsletter.newsletter_content)



@router.message(Create_Newsletter.newsletter_content)
async def get_content_newsletter(msg: types.Message, state: FSMContext):

    if msg.content_type == types.ContentType.TEXT:
        await msg.answer(
            text=str(msg.html_text),
            reply_markup=send_newsletter_kb().as_markup()
        )
        await state.update_data(newsletter_type='text')
        await state.update_data(newsletter_content=str(msg.html_text))
    elif msg.content_type == types.ContentType.PHOTO:
        photo = msg.photo[-1].file_id
        caption = msg.caption

        await msg.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=send_newsletter_kb().as_markup()
        )
        await state.update_data(newsletter_type='photo')
        await state.update_data(newsletter_content=photo)
        await state.update_data(newsletter_caption=caption)
    elif msg.content_type == types.ContentType.VIDEO:
        video = msg.video.file_id
        caption = msg.caption

        await msg.answer_video(
            video=video,
            caption=caption,
            reply_markup=send_newsletter_kb().as_markup()
        )
        await state.update_data(newsletter_type='video')
        await state.update_data(newsletter_content=video)
        await state.update_data(newsletter_caption=caption)
    else:
        await msg.answer(
            text='К сожалению, бот не может отправить это сообщение. 😔\n\nПришли другое сообщение или нажми <b>🚫 ОТМЕНА</b>',
            reply_markup=cancel_create_newsletter().as_markup()
        )



@router.callback_query(F.data == 'send_newsletter')
async def call_send_newsletter(call: types.CallbackQuery, state: FSMContext):
    getFSM = await state.get_data()

    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    newsletter_type = getFSM.get('newsletter_type')
    newsletter_content = getFSM.get('newsletter_content')
    newsletter_caption = getFSM.get('newsletter_caption')
    
    done = 0
    block = 0

    caption = '''
<b>Рассылка успешно запущена! 📤</b>

Мы уведомим вас, как только рассылка завершится и предоставим отчет с результатами.

Спасибо за ваше терпение! 😊
'''

    try:
        sent_message = await call.message.edit_text(
            text=caption
        )
    except:
        await call.message.delete()
        sent_message = await call.message.answer(
            text=caption
        )

    if newsletter_type == 'text':
        for user in db.get_list_users(project_id=project_id):
            try:
                await call.bot.send_message(chat_id=user[1], text=newsletter_content)
                db.update_status_user_client(user_id=user[0], status='true')
                done += 1
            except:
                db.update_status_user_client(user_id=user[0], status='false')
                block += 1
    elif newsletter_type == 'photo':
        for user in db.get_list_users(project_id=project_id):
            try:
                await call.bot.send_photo(chat_id=user[1], photo=newsletter_content, caption=newsletter_caption)
                db.update_status_user_client(user_id=user[0], status='true')
                done += 1
            except:
                db.update_status_user_client(user_id=user[0], status='false')
                block += 1
    elif newsletter_type == 'video':
        for user in db.get_list_users(project_id=project_id):
            try:
                await call.bot.send_video(chat_id=user[1], video=newsletter_content, caption=newsletter_caption)
                db.update_status_user_client(user_id=user[0], status='true')
                done += 1
            except:
                db.update_status_user_client(user_id=user[0], status='false')
                block += 1

    caption = f'''
<b>Рассылка завершена! 📤✅</b>


<b>📊 Отчет о рассылке</b>
----------------
<b>Общее количество пользователей:</b> {done + block} 👥
<b>Получили сообщение:</b> {done} 📩
<b>Заблокировали бота:</b> {block} 🚫
'''

    await call.bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=sent_message.message_id,
        text=caption,
        reply_markup=return_newsletter().as_markup()
    )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()
    

