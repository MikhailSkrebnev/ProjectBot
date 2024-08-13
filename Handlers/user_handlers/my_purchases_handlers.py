from aiogram import types, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


from Database.User_db import Database



from Keyboards.user_keyboards.products_keyboards import(
    purchases_kb,
    purchase_dv_kb,
    Purchases
)


db = Database()
router = Router()





# Раздел ПОКУПКИ

@router.message(F.text == '🛍️ Покупки')
async def button_purchases(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = f'''
<b>Список оплаченных товаров:</b>
'''
    
    await msg.answer(
        text=caption,
        reply_markup=purchases_kb(project_id=project_id, user_id=msg.from_user.id).as_markup()
    )

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
            
    await state.clear()



@router.callback_query(F.data == 'call_purchases')
async def call_purchases(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = f'''
<b>Список оплаченных товаров:</b>
'''
    
    await call.message.edit_text(
        text=caption,
        reply_markup=purchases_kb(project_id=project_id, user_id=call.from_user.id).as_markup()
    )   

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
            
    await state.clear()




# Открыть покупку

@router.callback_query(Purchases.filter(F.action == 'open_purchase'))
async def call_open_purchase(call: types.CallbackQuery, callback_data: Purchases):

    purchase_data = db.get_purchase_data(purchase_id=callback_data.purchase_id)


    if purchase_data[0][8] == 'delivery':
        delivery_data = db.get_delivery_order(sale_id=purchase_data[0][0])

        caption = f'''
<b>Информация о твоем заказе:</b>

<b>Номер заказа:</b> {delivery_data[0][0]}

<b>Товар:</b> {delivery_data[0][4]}
<b>Кол-во:</b> {delivery_data[0][6]}
<b>Стоимость 1 ед. товара:</b> {delivery_data[0][5]} 🇷🇺RUB

<b>Способ доставки:</b> {delivery_data[0][7]}
<b>Стоимость доставки:</b> {delivery_data[0][8]} 🇷🇺RUB

<b>Адрес доставки:</b> {delivery_data[0][9]}
<b>Трек номер:</b> {delivery_data[0][10]}
<b>Статус заказа:</b> {delivery_data[0][11]}

<b>Комментарий от продавца:</b> {delivery_data[0][12]}
'''

        await call.message.edit_text(
            text=caption,
            reply_markup=purchase_dv_kb(order_id=delivery_data[0][0]).as_markup()
        )

    elif purchase_data[0][8] == 'inf':

        for content in db.get_sale_data(sale_id=purchase_data[0][0])[0][3]: # Получаем список товара, который должны прислать покупателю
            content_data = db.get_inf_product_content(content_id=content) # Получаем данные о инфопродукте

            try:
                if content_data[0][3] == 'text':
                    await call.message.answer(text=content_data[0][2])
                elif content_data[0][3] == 'video':
                    await call.message.answer_video(video=str(content_data[0][2]))
                elif content_data[0][3] == 'voice':
                    await call.message.answer_voice(voice=str(content_data[0][2]))
                elif content_data[0][3] == 'photo':
                    await call.message.answer_photo(photo=str(content_data[0][2]))
                elif content_data[0][3] == 'document':
                    await call.message.answer_document(document=str(content_data[0][2]))
            except:
                await call.message.answer('Не удалось отправить товар, обратитесь к продавцу')

        await call.answer(show_alert=False)

    elif purchase_data[0][8] == 'channel':

        builder = InlineKeyboardBuilder()

        black_list = '<i>Еще ты должен был получить доступ к следующим каналам:</i>\n '

        for channel in purchase_data[0][9]:
            try:
                channel_data = db.get_ch_product_content(content_id=channel) # Получаем данные о канале

                create_link = await call.bot.create_chat_invite_link(chat_id=channel_data[0][3], name='Оплаченная ссылка', creates_join_request=True) # Создаем ссылку с заявкой на вступление
                link = create_link.invite_link # Вытаскиваем ссылку

                builder.row(types.InlineKeyboardButton(text=f'Канал: {channel_data[0][2]}', url=link)) # Создаем кнопку с ссылкой на канал
            except:
                try:
                    black_list += f'\n<b>- {channel_data[0][2]}</b>'
                except:
                    black_list += f'\n<b>- неизвестный канал</b>'

        black_list += '\n\n<i>но произошла ошибка. Для получения доступа обратитесь к администартору!</i>'

        if len(black_list) == 143: # Если во время создания ссылок произошла ошибка, то black_list покажет к каким каналм не удалось получит доступ
            black_list = ''
        else:
            black_list = black_list

        builder.row(types.InlineKeyboardButton(text='✅ Принять заявку', callback_data=f'approve_{purchase_data[0][0]}'))
        builder.row(types.InlineKeyboardButton(text='👈 НАЗАД', callback_data='call_purchases'))

        await call.message.edit_text(
            text=f'Подай заяву на канал и нажми кнопку "✅ Принять заявку" \n\n{black_list}',
            reply_markup=builder.as_markup()
        )


    



  

