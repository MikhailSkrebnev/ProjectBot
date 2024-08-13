from aiogram import types, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from datetime import datetime

from Database.Admin_db import Database

from Keyboards.admin_keyboards.statistics_keyboards import(
    statistics_kb,
    back_to_statistics
)


router = Router()
db = Database()


@router.callback_query(F.data == 'statistics')
async def call_statistics(call: types.CallbackQuery):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    current_date = datetime.now().strftime('%Y-%m-%d')

    total_statistics = db.get_total_statistics(project_id=project_id)
    statistics_over_time = db.get_statistics_over_time(project_id=project_id, date=current_date)

    caption = f'''
<b>📊 СТАТИСТИКА</b>

<b>👥 Всего пользователей:</b> {total_statistics[0][0]}
<b>🛒 Покупателей:</b> {total_statistics[0][1]}
<b>💰 Всего заработано:</b> {total_statistics[0][2]}₽

<b>📅 За последние 24 часа</b>
<b>🔹 Новых пользователей:</b> {statistics_over_time[0][0]}
<b>🔹 Новых покупателей:</b> {statistics_over_time[0][1]}
<b>🔹 Заработано:</b> {statistics_over_time[0][2] if statistics_over_time[0][2] != None else '0'}₽
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=statistics_kb().as_markup()
    )



@router.callback_query(F.data == 'products_statistics')
async def call_products_statistics(call: types.CallbackQuery):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = f'''
<b>📈 СТАТИСТИКА ПО ТОВАРАМ</b>

<b>ТОП 10 ТОВАРОВ</b>
'''

    for item in db.get_products_statistics(project_id=project_id):
        caption += f'\n\n<b>Товар:</b> {item[1]}\n<b>Кол-во продаж:</b> {item[3]}\n<b>Сумма продаж:</b> {item[2]}₽'
    
    await call.message.edit_text(
        text=caption,
        reply_markup=back_to_statistics().as_markup()
    )




@router.callback_query(F.data == 'statistics_on_customers')
async def call_statistics_on_customers(call: types.CallbackQuery):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = f'''
<b>📈 СТАТИСТИКА ПО ПОКУПАТЕЛЯМ</b>

<b>ТОП 10 ПОКУПАТЕЛЕЙ</b>
'''
    
    for user in db.get_statistics_on_customers(project_id=project_id):
        caption += f"\n\n<b>Покупатель:</b> <code>{user[0]}</code> \n* ID: <code>{user[1]}</code> \n* USERNAME: <code>{'@' + user[2] if user[2] != 'None' else 'не указан'}</code>\n<b>Кол-во покупок:</b> {user[3]}\n<b>Сумма покупок:</b> {user[4]}₽"

    await call.message.edit_text(
        text=caption,
        reply_markup=back_to_statistics().as_markup()
    )


