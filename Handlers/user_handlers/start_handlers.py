from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from datetime import date, datetime


from Database.User_db import Database


from Keyboards.user_keyboards.munu_keyboards import(
    start_admin_kb,
    start_kb,
)

from Keyboards.user_keyboards.products_keyboards import(
    list_buttons_not_group
)


db = Database()
router = Router()




@router.message(Command('test'))
async def test_mesg(msg: types.Message):
    bot = await msg.bot.get_me()

    await msg.answer(bot.id)

# Регистрация пользователя и обновление данных

@router.message(Command('start'))
async def cmd_start(msg: types.Message, state: FSMContext):  
    bot_data = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_data.username)

    start_caption = str(db.get_caption(caption='start_caption', bot_username=bot_data.username))
    menu_caption = ''

    if db.get_caption(caption='menu_caption', bot_username=bot_data.username) == '':
        menu_caption = 'Выберите товар для покупки:'
    else:
        menu_caption = str(db.get_caption(caption='menu_caption', bot_username=bot_data.username))

    if db.check_reg_user(project_id=project_id, user_id=msg.from_user.id) == []:
        if msg.from_user.id == db.check_user_id_admin(bot_username=bot_data.username):
            now = datetime.now() 
            time = now.strftime("%H:%M:%S")
            db.reg_new_user(
                project_id=project_id,
                user_id=msg.from_user.id,
                fullname=msg.from_user.full_name,
                username=msg.from_user.username,
                date_reg=date.today(),
                time_reg=time,
                job_title='Admin'
            )
            await msg.answer(f'{start_caption}\n\nБот создан при помощи @JustMakeBot', reply_markup=start_admin_kb())
        else:
            now = datetime.now() 
            time = now.strftime("%H:%M:%S")
            db.reg_new_user(
                project_id=project_id,
                user_id=msg.from_user.id,
                fullname=msg.from_user.full_name,
                username=msg.from_user.username,
                date_reg=date.today(),
                time_reg=time,
                job_title='User'
            ) 
            await msg.answer(f'{start_caption}\n\nБот создан при помощи @JustMakeBot', reply_markup=start_kb())
    else:
        if msg.from_user.id == db.check_user_id_admin(bot_username=bot_data.username):
            db.update_user_data(
                user_id=msg.from_user.id,
                fullname=msg.from_user.full_name,
                username=msg.from_user.username
            )
            await msg.answer(f'{start_caption}\n\nБот создан при помощи @JustMakeBot', reply_markup=start_admin_kb())
        else:
            db.update_user_data(
                user_id=msg.from_user.id,
                fullname=msg.from_user.full_name,
                username=msg.from_user.username
            )
            await msg.answer(f'{start_caption}\n\nБот создан при помощи @JustMakeBot', reply_markup=start_kb())


    photo = db.get_group_photo(identifier=project_id, path='menu')

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


    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()