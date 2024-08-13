import asyncio
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


from datetime import date, datetime
import time
from random import randint

from Database.User_db import Database
import random

from Lib_payment import(
    Payment
)


from Keyboards.user_keyboards.products_keyboards import(
    payment_for_goods_kb,
    back_to_menu_kb,
    proof_payment_kb,
    receive_paid_goods_kb,
    cancel_send_proof,
    PaymentForGoods
)


db = Database()
router = Router()



def discount_calculation(price, discount):
    total_price = price - price / 100 * discount
    text = '<s>' + str(price)+'</s> ' + str(round(total_price))
    return text

def discount_cal(price, discount):
    total_price = price - price / 100 * discount
    return total_price


class Proof_Payment(StatesGroup):
    process_id = State()



# Выставление счета на оплату

@router.callback_query(PaymentForGoods.filter(F.action == 'payment_for_goods'))
async def button_payment_for_goods(call: types.CallbackQuery, callback_data: PaymentForGoods, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    payment_method_data = db.get_payment_method_data(method_id=callback_data.payment_method_id)

    if callback_data.delivery_method_id != 'none':
        delivery_method_data = db.get_delivery_method_data(method_id=callback_data.delivery_method_id)
    else:
        delivery_method_data = ['none']

    if callback_data.quantity == 'none': # так как на товары с подпиской на канал пользователь не вибирает кол-во товара, то присваиваем кол-во 1
        quantity = 1
    else:
        quantity = int(callback_data.quantity)

    product_data = db.get_product_data(product_id=callback_data.product_id)


    # (payment_method_data != []) and (db.check_status_sub(project_id=project_id)[0][0] != 0) Проверяем доступен ли способ оплаты и оплачена ли подписка у админа бота

    if payment_method_data != []: # Проверяем доступен ли способ оплаты и оплачена ли подписка у админа бота
        if product_data != []: # Проверяем доступен ли сам товар
            if db.check_quantity_product(product_id=callback_data.product_id, quantity=quantity) != []: # Проверяем, есть ли нужно кол-во товара
                if delivery_method_data != []: # Проверяем доступен ли еще способ доставки, если это товар с доставкой

                    if product_data[0][2] != 'delivery':
                        total_price = round((product_data[0][6] if product_data[0][7] == 0 else discount_cal(price=product_data[0][6], discount=product_data[0][7])) * quantity)
                    else:
                        total_price = round((product_data[0][6] if product_data[0][7] == 0 else discount_cal(price=product_data[0][6], discount=product_data[0][7])) * quantity + delivery_method_data[0][4])

                    if product_data[0][2] == 'inf' or product_data[0][2] == 'channel': # Проверяем, является ли товар информационным или подпиской на канал(ы)
                        if product_data[0][4]: # Если каждая еденица товара уникальная, то берем нужное кол-во контента
                            content = db.get_product_contents(product_id=product_data[0][0]) # Получаем весь список контента
                            db.update_list_contents(product_id=product_data[0][0], content=content[quantity:]) # Обновляем список контента на товаре
                            contents = content[:quantity] # Берем нужно кол-во товара
                        else:
                            contents = db.get_product_contents(product_id=product_data[0][0]) # Если товар является подпиской на канал или инфо-товар с неуникальной еденицой товара
                    else:
                        contents = [delivery_method_data[0][0]] # Если это товар с доставкой, то передаем выбранный способ доставки

                    if payment_method_data[0][2] == 'auto_CryptoBot': # Создание счета для Криптобота
                        payment_data = Payment.create_cryptobot_invoice(token=f'{payment_method_data[0][6]}', amount=total_price) # Создали счет на оплату

                        link = payment_data['result']['pay_url']
                        payment_id = payment_data['result']['invoice_id']
                        payment_method = 'auto_CryptoBot'

                    elif payment_method_data[0][2] == 'auto_WalletPay': # Создание счета для Wallet
                        current_time = time.localtime()
                        current_day = date.today()
                        externalId = f'{call.from_user.id}:{product_data[0][0]}:{current_day}_{time.strftime("%H:%M:%S", current_time)}'
                        payment_data = Payment.create_wallet_invoice(token= f'{payment_method_data[0][6]}', amount=total_price, description=f'Оплата товара {product_data[0][8]}', user_id=call.from_user.id, externalId=externalId) # Создали счет на оплату
                        
                        link = payment_data['data']['payLink']
                        payment_id = payment_data['data']['id']
                        payment_method = 'auto_WalletPay'

                    elif payment_method_data[0][2] == 'auto_Yoomoney': # Создание счета для Yoomoney
                        bot_username = await call.bot.get_me()
                        redirect_url = f'https://t.me/{bot_username.username}'

                        payment_id = f'{call.message.from_user.id}:{str(random.randint(0, 10000000000))}'

                        link = f'https://yoomoney.ru/quickpay/confirm?receiver={payment_method_data[0][7]}&quickpay-form=button&paymentType=AC&sum={total_price}&label={payment_id}&successURL={redirect_url}'
                        payment_method = 'auto_Yoomoney'
                        
                    else: # Создание счета для Ручных способов оплаты
                        link = 'none'
                        payment_id = randint(0, 999999999)
                        payment_method = 'manual'
                

                    caption = f'''
<b>Способ оплаты:</b> {payment_method_data[0][4]}

{payment_method_data[0][5]}

<b>Итоговая стоимость:</b> {total_price} 🇷🇺RUB

⚠️ <i>у вас есть 30 минут на оплату товара</i>
'''
                    
                    if link == []: # Если вдруг ссылку на оплату не получится получить, то скорее всего что-то не так с токеном
                        await call.answer(text='Способ оплаты недоступен, обратитесь к администратору!', show_alert=True)
                    else:
                        db.minus_quantity_of_goods(product_id=product_data[0][0], quantity=quantity)
                        db.add_new_payment_processing( # Добавляем новый платеж в систему и ставим в статус ожидание оплаты
                            project_id=product_data[0][1],
                            user_id=call.from_user.id,
                            payment_id=payment_id,
                            payment_method_id=payment_method_data[0][0],
                            payment_method_type=payment_method,
                            product_id=product_data[0][0],
                            product_price=total_price,
                            contents=contents,
                            product_quantity=quantity,
                            message_id=0
                        )
                        message_id = await call.message.edit_text(
                                text=caption,
                                reply_markup=payment_for_goods_kb(
                                    product_id=callback_data.product_id,
                                    group_id=callback_data.group_id,
                                    quantity=callback_data.quantity,
                                    delivery_method_id=callback_data.delivery_method_id,
                                    payment_method_id=callback_data.payment_method_id,
                                    url=f'{link}',
                                    process_id=db.get_last_process_id(user_id=call.from_user.id, product_id=callback_data.product_id)
                                ).as_markup()
                            )
                        
                        process_id = db.get_last_process_id(user_id=call.from_user.id, product_id=callback_data.product_id)
                        
                        await state.update_data(process_id=process_id)
                        
                        db.update_message_id(message_id=message_id.message_id, process_id=process_id)
                        
                    await asyncio.sleep(1800) # Если в течение 30 минут платеж не будет выполнен, то сообщение редактируется и счет оплаты удаляется из БД
                    try:
                        if db.get_payment_process_data(process_id=process_id)[11] != 0: # Это проверка нужна для ручного способа оплаты. Если message_id = 0 - значит платеж на проверке
                            try:
                                if product_data[0][4]: # Если товар многочисленный и уникальный, то обновляем список товаров
                                    content = db.get_product_contents(product_id=product_data[0][0]) # Получаем весь список контента на товаре
                                    new_content = contents + content # Прибавляем то что забирали ранее
                                    db.update_list_contents(product_id=product_data[0][0], content=new_content) # Обновляем список контента на товаре

                                db.delete_process(process_id=db.get_last_process_id(user_id=call.from_user.id, product_id=callback_data.product_id))
                                db.plus_quantity_of_goods(product_id=product_data[0][0], quantity=quantity)
                                await call.message.edit_text(
                                    text='Срок действия данного платежа истек!\n\nВозвращайся обратно в магазин и оформи покупку заново',
                                    reply_markup=back_to_menu_kb()
                                )

                                # Сбрасываем текущее состояния
                                current_state = await state.get_state()

                                if current_state is None:
                                    return
                                        
                                await state.clear()
                            except:
                                pass
                    except:
                        pass
                else:
                    await call.answer(
                        text='Ранее выбранный способ доставки больше недоступен',
                        show_alert=True
                    )
            else:
                await call.answer(
                    text='Товар в нужном количестве закончился',
                    show_alert=True
                )
        else:
            await call.answer(
                text='Продукт больше недоступен для покупки',
                show_alert=True
            )
    else:
        await call.answer(
            text='К сожалению, данный способ оплаты больше недоступен для оплаты',
            show_alert=True
        )


# Запрашивает чек об оплате, при ручном способе оплаты 

@router.callback_query(F.data == 'proof_of_payment')
async def call_proof_of_payment(call: types.CallbackQuery, state: FSMContext):

    await call.message.edit_text(
        text='Пожалуйста, пришли чек в формате фото или скриншота. 📸 Спасибо! 😊'
    )

    await state.set_state(Proof_Payment.process_id)


# Получаем чек об оплате

@router.message(Proof_Payment.process_id)
async def get_proof_of_payment(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    getFSM = await state.get_data()

    if msg.content_type == types.ContentType.PHOTO:
        process_data = db.get_payment_process_data(process_id=getFSM.get('process_id'))
        product_data = db.get_sale_product_data(product_id=process_data[7])
        payment_data = db.get_payment_method(method_id=process_data[5])
        user_data = db.check_reg_user(project_id=project_id, user_id=process_data[3])

        db.update_message_id(message_id=0, process_id=getFSM.get('process_id'))


        if product_data[0][2] == 'channel':
            product_type = "подписка на канал"
        elif product_data[0][2] == 'delivery':
            product_type = "товар с доставкой"
            delivery_data = db.delivery_method_data(method_id=product_data[0][5][0])
        else:
            product_type = "инфо-товар"

        caption = f'''
💰 <b>ПРИШЕЛ НОВЫЙ ПЛАТЕЖ</b>

<b>Покупатель:</b> <code>{user_data[0][3]}</code>
<b>* ID:</b> <code>{user_data[0][1]}</code>
<b>* USERNAME:</b> {"<code>" + "@" + user_data[0][4] + "</code>" if {user_data[0][3]} != "None" else "не указан"}

<b>Товар:</b> {product_data[0][8]} ({product_type})
<b>Кол-во:</b> {process_data[10]} 
{"<b>Способ доставки: </b>" + delivery_data[0][2] if product_data[0][2] == "delivery" else ""}
<b>К оплате:</b> {process_data[8]} 🇷🇺 RUB
<b>Способ оплаты:</b> {payment_data[0][4]}
'''

        try:
            await msg.bot.send_photo(
                    chat_id=db.who_is_admin(project_id=process_data[2]), 
                    photo=msg.photo[-1].file_id, 
                    caption=caption,
                    reply_markup=proof_payment_kb(process_id=process_data[0]).as_markup()
                )

            await msg.answer(
                    text='Отлично! Твой платеж на проверке. ⏳ Как только продавец его подтвердит, мы тебя уведомим. 📩'
                )
        except:
            await msg.answer(
                text='Не удалось отправить твой платеж продавцу. 😔 Свяжись с ним для получения товара! 📞'
            )


        # Сбрасываем текущее состояния
        current_state = await state.get_state()

        if current_state is None:
            return
                
        await state.clear()
    else:
        await msg.answer(
            text='Пожалуйста, пришли чек в формате фото или скриншота. 📸 Спасибо! 😊',
            reply_markup=cancel_send_proof()
        )




@router.callback_query(F.data.startswith('confirmpayment_'))
async def call_confirm_payment(call: types.CallbackQuery):
    call_data = call.data # Получаем данные из коллбэка
    process_id = call_data.split('_')[1]# Получаем id продажи, чтобы вытащить нужные данные о товаре

    process_data = db.get_payment_process_data(process_id=process_id)
    product_data = db.get_sale_product_data(process_data[7])

    now = datetime.now() 
    time = now.strftime("%H:%M:%S")

    await call.message.edit_caption(
        caption=f'<b>✅ Платеж был одобрен!</b>\n\n<b>ID покупателя:</b> <code>{process_data[3]}</code>\n<b>Сумма оплаты:</b> {process_data[8]} RUB',
        reply_markup=None
    )

    db.add_new_sale( # Добавляем новую продажу
              project_id=process_data[2],
              sale_date=date.today(),
              sale_time=time,
              user_id=process_data[3],
              payment_method=process_data[6],
              product_id=process_data[7],
              product_name=f'{product_data[0][8]}',
              product_type=f'{product_data[0][2]}',
              product_content=process_data[9] if product_data[0][2] != 'delivery' else '',
              quantity=process_data[11],
              product_price=process_data[8]
          )
    
    db.update_sales_product(product_id=process_data[7]) # Добавляем 1 продажу к товару
    db.delete_process(process_id=db.get_last_process_id(user_id=process_data[3], product_id=process_data[7])) # Удаляем оплаченный платеж из БД
    sale_id = db.get_last_sale_user(user_id=process_data[3], product_id=process_data[7])[0][0] # Получаем sale_id последней покупки клиента, чтобы передать в коллбэк
    delivery_data = db.delivery_method_data(method_id=process_data[9][0])


    if product_data[0][2] == 'delivery': # Если товар с доставкой, то добавляем данные о доставке
            db.add_new_delivery_order(
               sale_id=sale_id,
               user_id=process_data[3],
               project_id=product_data[0][1],
               product_name=product_data[0][8],
               product_price=product_data[0][6],
               product_quantity=process_data[10],
               delivery_method=delivery_data[0][2],
               delivery_price=delivery_data[0][4]
            )

    # Отправляем сообщение об успешной покупке клиенту
    try:

        caption_user = f'''
{db.get_after_payment_caption(project_id=process_data[3])[0][0]}

<i>Нажми на кнопку ниже, чтобы получить товар</i>
  '''

        await call.bot.send_message(
            chat_id=process_data[3],
            text=caption_user,
            reply_markup=receive_paid_goods_kb(sale_id=sale_id).as_markup()
        )
    except:
        pass


    # Отправляем сообщение об успешной продаже админу

    user_data = db.get_user_data(user_id=process_data[3], project_id=process_data[2]) # Получаем данные о покупателе
    payment_data = db.get_payment_method(method_id=process_data[5])

    caption_admin = f'''
<b>💰 НОВАЯ ПРОДАЖА!</b>

<b>Товар:</b> {product_data[0][8]} 
<b>Прибыль:</b> {process_data[8]} 🇷🇺 RUB


<b>Данные покупателя:</b>
<b>🔹 ID покупателя:</b> {process_data[3]}
<b>🔹 Username:</b> {'@' + str(user_data[0][4]) if user_data[0][4] != 'None' else 'не указано'}
<b>🔹 Fullname покупателя:</b> {user_data[0][3]}
<b>🔹 Дата регистрации:</b> {user_data[0][1]} {user_data[0][2]}
<b>🔹 Кол-во покупок:</b> {user_data[0][5]}
<b>🔹 Сумма покупок:</b> {user_data[0][6]} 🇷🇺 RUB
<b>Способ оплаты:</b> {payment_data[0][4]}

Поздравляем с новой продажей! 🎉
'''

    await call.bot.send_message(
        chat_id=db.who_is_admin(process_data[2]),
        text=caption_admin
    )


@router.callback_query(F.data.startswith('rejectpayment_'))
async def call_confirm_payment(call: types.CallbackQuery):
    call_data = call.data # Получаем данные из коллбэка
    process_id = call_data.split('_')[1]# Получаем id продажи, чтобы вытащить нужные данные о товаре

    await call.message.edit_caption(
        caption='<b>⛔️ Платеж был отклонен!</b>',
        reply_markup=None
    )

    try:
        process_data = db.get_payment_process_data(process_id=process_id)
        if db.get_product_data(product_id=process_data[7])[0][4]:
            content = db.get_product_contents(product_id=process_data[7]) # Получаем весь список контента
            new_content = process_data[9] + content
            db.update_list_contents(product_id=process_data[7], content=new_content) # Обновляем список контента на товаре
            db.delete_process(process_id=process_id) # Удаляем платеж из базы данных
        else:
            db.plus_quantity_of_goods(product_id=process_data[7], quantity=process_data[10])
            db.delete_process(process_id=process_id)
    except:
        pass


    # Отправляем сообщение, что платеж был отклонен продавцом
    try:

        caption_user = '''
<b>Уведомление об отказе оплаты 🚫</b>

Здравствуйте! К сожалению, ваш платёж не прошёл.

<i>Пожалуйста, проверьте ваши платёжные данные и попробуйте снова.</i>
  '''

        await call.bot.send_message(
            chat_id=process_data[3],
            text=caption_user,
        )
    except:
        pass
