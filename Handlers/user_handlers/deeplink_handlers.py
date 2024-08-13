from aiogram import types, F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import decode_payload
from aiogram.fsm.context import FSMContext


from datetime import date, datetime
from Database.User_db import Database


from Keyboards.user_keyboards.munu_keyboards import(
    start_admin_kb,
    start_kb,
)

from Keyboards.user_keyboards.products_keyboards import(
    product_kb
)

from Handlers.user_handlers.showcase_handlers import(
    discount_calculation
)


db = Database()
router = Router()



@router.message(CommandStart(deep_link=True))
async def deep_link(msg: types.Message, command: CommandObject, state: FSMContext):
    bot_data = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_data.username)

    args = command.args
    product_id = decode_payload(args)

    product_data = db.get_product_data(product_id=product_id)
    start_caption = str(db.get_caption(caption='start_caption', bot_username=bot_data.username))


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



    if product_data == []:
        await msg.answer(
            text='Этот товар недоступен для продажи😔'
        )
    else:
        if product_data[0][10] == []: # Проверяем, есть ли фото на товаре. Если true, то фото нет
            if product_data[0][2] == 'channel': # Проверяем, является ли товар количественным. Если true, то товар не является количественным
                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                await msg.answer(
                    text=caption,
                    reply_markup=product_kb(product_id=f'{product_data[0][0]}', group_id='-1', page=0).as_markup()
                )
            else:

                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Осталось:</b> {product_data[0][11]}
<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                
                await msg.answer(
                    text=caption,
                    reply_markup=product_kb(product_id=f'{product_data[0][0]}', group_id='-1', page=0).as_markup()
                )
        else: # Если на товаре есть фото
            if (product_data[0][2] == 'channel'): # Проверяем, является ли товар количественным. Если true, то товар не является количественным
                
                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''     
                await msg.answer_photo(
                    photo=f'{db.get_product_photos(product_id=product_data[0][0])[0]}',
                    caption=caption,
                    reply_markup=product_kb(product_id=f'{product_data[0][0]}', group_id='-1', page=0).as_markup()
                )
            else:

                caption = f'''
{product_data[0][8]}

{product_data[0][9]}

<b>Осталось:</b> {product_data[0][11]}
<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else discount_calculation(price=product_data[0][6], discount=product_data[0][7])} 🇷🇺RUB
'''
                await msg.answer_photo(
                    photo=f'{db.get_product_photos(product_id=product_data[0][0])[0]}',
                    caption=caption,
                    reply_markup=product_kb(product_id=f'{product_data[0][0]}', group_id='-1', page=0).as_markup()
                )   


    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()