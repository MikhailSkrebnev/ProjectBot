from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from Database.Admin_db import Database


from Keyboards.admin_keyboards.menu_keyboards import(
    menu_admin_kb,
    products_kb,
)



db = Database()
router = Router()


@router.message(Command('admin'))
async def cmd_admin(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()

    caption = '''
<b>🔧 Админ Панель Бота</b>


🛍 <b>Добавляй товары:</b> Управляйте ассортиментом вашего магазина.

💳 <b>Добавляй способы оплаты:</b> Настраивайте удобные варианты оплаты для ваших клиентов.

📊 <b>Смотри статистику:</b> Отслеживайте ключевые метрики и анализируйте производительность.

✉️ <b>Делай рассылку:</b> Оповещайте пользователей о новинках и акциях.

🎨 <b>Оформи дизайн бота:</b> Персонализируйте внешний вид и стиль вашего бота.
'''
    
    if msg.from_user.id == db.check_user_id_admin(bot_username=bot_username.username):
        await msg.answer(text=caption, reply_markup=menu_admin_kb())

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()

    

@router.callback_query(F.data == 'main_menu_admin')
async def call_main_menu_admin(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()

    caption = '''
<b>🔧 Админ Панель Бота</b>


🛍 <b>Добавляй товары:</b> Управляйте ассортиментом вашего магазина.

💳 <b>Добавляй способы оплаты:</b> Настраивайте удобные варианты оплаты для ваших клиентов.

📊 <b>Смотри статистику:</b> Отслеживайте ключевые метрики и анализируйте производительность.

✉️ <b>Делай рассылку:</b> Оповещайте пользователей о новинках и акциях.

🎨 <b>Оформи дизайн бота:</b> Персонализируйте внешний вид и стиль вашего бота.
'''
    
    if call.from_user.id == db.check_user_id_admin(bot_username=bot_username.username):
        await call.message.edit_text(text=caption, reply_markup=menu_admin_kb())


    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()



# РАЗДЕЛ ТОВАРЫ ----------------------------------------

class AddResource(StatesGroup):
    add_resource = State()

@router.callback_query(F.data == 'products')
async def call_products(call: types.CallbackQuery):
    caption = '''
<b>🛍 Добавление Товаров</b>

В этом разделе вы можете добавлять товары различных типов:

<b>1. Платная подписка на канал 📅</b>
<blockquote>Предлагайте пользователям эксклюзивный контент и привилегии через подписку на ваш канал.</blockquote>

<b>2. Информационные товары 📚</b>
<blockquote>Электронные книги, ключи активации и другие цифровые продукты.</blockquote>

<b>3. Физические товары 📦</b>
<blockquote>Управляйте продажей физических товаров с удобным отслеживанием статуса заказа.</blockquote>

<b>🛍 Витрина</b>
<blockquote><i>В разделе "Витрина" вы можете размещать добавленные товары на витрине продаж. Это позволит вашим пользователям просматривать и приобретать товары напрямую через бота.</i>

<b>- - Добавляйте товары на витрину:</b> <i>Сделайте ваши товары видимыми для покупателей.</i>
<b>- - Управляйте витриной:</b> <i>Легко обновляйте и организуйте товары для удобства пользователей.</i></blockquote> 
'''

    await call.message.edit_text(
        text=caption, 
        reply_markup=products_kb().as_markup()
    )
    


