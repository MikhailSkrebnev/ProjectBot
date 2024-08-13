from aiogram import types, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from Database.User_db import Database


from Keyboards.admin_keyboards.dv_products_keyboards import(
    open_edit_order
)



from Keyboards.user_keyboards.products_keyboards import(
    edit_delivery_address,
    cancel_edit_delivery_address,
    purchase_dv_kb,
    AddDeliveryAddress,
)


db = Database()
router = Router()



class Edit_Delivery_Address(StatesGroup):
    order_id = State()



# Выдача товара после успешной покупки

@router.callback_query(F.data.startswith('usersaleid_'))
async def process_successful_payment(call: types.CallbackQuery):
    call_data = call.data # Получаем данные из коллбэка
    sale_id = call_data.split('_')[1]# Получаем id продажи, чтобы вытащить нужные данные о товаре

    product_data = db.get_sale_data(sale_id=sale_id)

    if product_data[0][1] == 'inf':
        await call.message.edit_text(text='Твои товары 👇')
        for content in product_data[0][3]:
            content_data = db.get_inf_product_content(content_id=content)

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
    elif product_data[0][1] == 'channel':
        builder = InlineKeyboardBuilder()

        black_list = '<i>Еще ты должен был получить доступ к следующим каналам:</i>\n '

        for channel in product_data[0][3]:
            try:
                channel_data = db.get_ch_product_content(content_id=channel) # Получаем данные о канале

                create_link = await call.bot.create_chat_invite_link(chat_id=channel_data[0][3], name='Оплаченная ссылка', creates_join_request=True) # Создаем ссылку с заявкой на вступление
                link = create_link.invite_link # Вытаскиваем ссылку

                builder.row(types.InlineKeyboardButton(text=f'Канал: {channel_data[0][2]}', url=link)) # Создаем кнопку с ссылкой на канал
            except:
                black_list += f'\n<b>- {channel_data[0][2]}</b>'

        black_list += '\n\n<i>но произошла ошибка. Для получения доступа обратитесь к администартору!</i>'

        if len(black_list) == 143: # Если во время создания ссылок произошла ошибка, то black_list покажет к каким каналм не удалось получит доступ
            black_list = ''
        else:
            black_list = black_list

        builder.row(types.InlineKeyboardButton(text='✅ Принять заявку', callback_data=f'approve_{sale_id}'))
        builder.row(types.InlineKeyboardButton(text='👈 НАЗАД', callback_data='call_purchases'))

        await call.message.edit_text(
            text=f'Подай заяву на канал и нажми кнопку "✅ Принять заявку" \n\n{black_list}',
            reply_markup=builder.as_markup()
        )
    elif product_data[0][1] == 'delivery':
        content_data = db.get_dv_product_content(sale_id=sale_id)

        caption = f'''
<b>Информация о твоем заказе:</b>

<b>Номер заказа:</b> {content_data[0][0]}

<b>Товар:</b> {content_data[0][4]}
<b>Кол-во:</b> {content_data[0][6]}
<b>Стоимость 1 ед. товара:</b> {content_data[0][5]} 🇷🇺RUB

<b>Способ доставки:</b> {content_data[0][7]}
<b>Стоимость доставки:</b> {content_data[0][8]} 🇷🇺RUB

<b>Адрес доставки:</b> {content_data[0][9]}
<b>Трек номер:</b> <code>{content_data[0][10]}</code>
<b>Статус заказа:</b> {content_data[0][11]}

<b>Комментарий от продавца:</b> {content_data[0][12]}
'''

        await call.message.edit_text(
            text=caption,
            reply_markup=edit_delivery_address(delivery_order=content_data[0][0]).as_markup()
        )



@router.callback_query(AddDeliveryAddress.filter(F.action == 'add_delivery_address'))
async def call_add_delivery_address(call: types.CallbackQuery, callback_data: AddDeliveryAddress, state: FSMContext):
    order_data = db.get_delivery_data(order_id=callback_data.order_id)

    if order_data[0][11] == 'в обработке':
        await call.message.edit_text(
            text='Укажите адрес доставки или адрес ПВЗ/ПАСТОМАТА',
            reply_markup=cancel_edit_delivery_address().as_markup()
        )
        await state.set_state(Edit_Delivery_Address.order_id)
        await state.update_data(order_id=callback_data.order_id)
    else:
        await call.answer(text='🚫 Статус заказа изменен, изменить адрес не получится', show_alert=True)



@router.message(Edit_Delivery_Address.order_id, F.text)
async def get_new_delivery_address(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username.username)
    getFSM = await state.get_data()

    if len(msg.text) > 128:
        await msg.answer('Адрес доставки не должен превышать 128 символов', reply_markup=cancel_edit_delivery_address().as_markup())
    else:
        db.update_delivery_address(order_id=getFSM.get('order_id'), new_address=msg.text) # Обновляем адресс доставки

        delivery_data = db.get_delivery_data(order_id=getFSM.get('order_id'))

        caption = f'''
<b>Информация о твоем заказе:</b>

<b>Номер заказа:</b> {delivery_data[0][0]}

<b>Товар:</b> {delivery_data[0][4]}
<b>Кол-во:</b> {delivery_data[0][6]}
<b>Стоимость 1 ед. товара:</b> {delivery_data[0][5]} 🇷🇺RUB

<b>Способ доставки:</b> {delivery_data[0][7]}
<b>Стоимость доставки:</b> {delivery_data[0][8]} 🇷🇺RUB

<b>Адрес доставки:</b> {delivery_data[0][9]}
<b>Трек номер:</b> <code>{delivery_data[0][10]}</code>
<b>Статус заказа:</b> {delivery_data[0][11]}

<b>Комментарий от продавца:</b> {delivery_data[0][12]}
'''
        
        await msg.answer(
            text=caption,
            reply_markup=purchase_dv_kb(order_id=delivery_data[0][0]).as_markup()
        )


        # Отправляем сообщение админу бота
        try:
            await msg.bot.send_message(chat_id=db.who_is_admin(project_id), text=f'Покупатель с ID: <code>{delivery_data[0][2]}</code>  изменил адрес доставки для заказа: {delivery_data[0][0]}', reply_markup=open_edit_order(order_id=delivery_data[0][0]).as_markup())
        except:
            pass
        

        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
            
        await state.clear()







@router.callback_query(F.data.startswith('approve_'))
async def approve_join_in_channel(call: types.CallbackQuery):
    call_data = call.data # Получаем данные из коллбэка
    sale_id = call_data.split('_')[1]# Получаем id продажи, чтобы вытащить нужные данные о товаре

    product_data = db.get_sale_data(sale_id=sale_id)

    try:
        for channel in product_data[0][3]:
                try:
                    channel_data = db.get_ch_product_content(content_id=channel) # Получаем данные о канале
                    await call.bot.approve_chat_join_request(chat_id=channel_data[0][3], user_id=call.from_user.id) # Принимает заявку на канал
                except:
                    pass
    except:
        await call.answer(
            text='Нет каналов, доступ к которым можно предоставить',
            show_alert=True
        )

    await call.answer(text='✅ Заявки одобрены!', show_alert=True)