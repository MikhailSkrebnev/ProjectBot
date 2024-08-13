from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext


from Database.User_db import Database


from Keyboards.user_keyboards.products_keyboards import(
    counter_kb,
    payment_methods,
    payment_methods_not_delivery,
    choose_delivery_methods_kb,
    delivery_method_kb,
    payment_methods_delivery,
    BuyGoods,
    DVMehtods
)


db = Database()
router = Router()





# Покупка товара

@router.callback_query(BuyGoods.filter(F.action == 'buy_goods'))
async def button_buy_goods(call: types.CallbackQuery, callback_data: BuyGoods, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username.username)

    product_data = db.get_product_data(product_id=callback_data.product_id)

    try: 
        caption = f'''
Какое количество товара ты хочешь заказать?

<b>Стоимость:</b> {product_data[0][6] if product_data[0][7] == 0 else product_data[0][6] - product_data[0][6] / 100 * product_data[0][7]} 🇷🇺RUB
'''
    except:
        await call.answer(text='Что-то пошло не так', show_alert=True)

    if (product_data[0][2] == 'inf' and product_data[0][4]) or product_data[0][2] == 'delivery': # Если товар является количественным, нужно выбрать кол-во товара, которые ты хочешь купить
        try:
            await call.message.edit_text(
                text=caption,
                reply_markup=counter_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, quantity='1').as_markup()
            )
        except:
            await call.message.delete()

            await call.message.answer(
                text=caption,
                reply_markup=counter_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, quantity='1').as_markup()
            )
    else: # Если товар не является количественным, то переходит к выбору способа оплаты
        try:
            await call.message.edit_text(
                text='Выберите способ оплаты:',
                reply_markup=payment_methods(project_id=project_id, product_id=callback_data.product_id, group_id=callback_data.group_id).as_markup()
            )

            try:
                process_data = db.get_payment_process_data(process_id=callback_data.process)
                if db.get_product_data(product_id=process_data[7])[0][4]:
                    content = db.get_product_contents(product_id=process_data[7]) # Получаем весь список контента
                    new_content = process_data[9] + content
                    db.update_list_contents(product_id=process_data[7], content=new_content) # Обновляем список контента на товаре
                    db.delete_process(process_id=callback_data.process) # Удаляем платеж из базы данных
                else:
                    db.plus_quantity_of_goods(product_id=process_data[7], quantity=process_data[10])
                    db.delete_process(process_id=callback_data.process)
            except:
                pass
        except:
            await call.message.delete()

            await call.message.answer(
                text='Выберите способ оплаты:',
                reply_markup=payment_methods(project_id=project_id, product_id=callback_data.product_id, group_id=callback_data.group_id).as_markup()
            )

            try:
                process_data = db.get_payment_process_data(process_id=callback_data.process)
                if db.get_product_data(product_id=process_data[7])[0][4]:
                    content = db.get_product_contents(product_id=process_data[7]) # Получаем весь список контента
                    new_content = process_data[9] + content
                    db.update_list_contents(product_id=process_data[7], content=new_content) # Обновляем список контента на товаре
                    db.delete_process(process_id=callback_data.process) # Удаляем платеж из базы данных
                else:
                    db.plus_quantity_of_goods(product_id=process_data[7], quantity=process_data[10])
                    db.delete_process(process_id=callback_data.process)
            except:
                pass

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
                                        
    await state.clear()



@router.callback_query(BuyGoods.filter(F.action == 'counter'))
async def button_counter(call: types.CallbackQuery, callback_data: BuyGoods):
    product_data = db.get_product_data(product_id=callback_data.product_id)

    quantity = int(callback_data.quantity)

    try:
        if callback_data.count == 'plus':
            if quantity < product_data[0][11]:
                quantity += 1

                caption = f'''
Какое количество товара ты хочешь заказать?

<b>Стоимость:</b> {round(product_data[0][6] * quantity if product_data[0][7] == 0 else (product_data[0][6] - product_data[0][6] / 100 * product_data[0][7]) * quantity)} 🇷🇺RUB
    '''
                await call.message.edit_text(
                    text=caption,
                    reply_markup=counter_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, quantity=str(quantity)).as_markup()
                )
            else:
                await call.answer(text='Это максимальное кол-во товара!')

        elif callback_data.count == 'minus':
            if quantity > 1:
                quantity -= 1

                caption = f'''
Какое количество товара ты хочешь заказать?

<b>Стоимость:</b> {product_data[0][6] * quantity if product_data[0][7] == 0 else (product_data[0][6] - product_data[0][6] / 100 * product_data[0][7]) * quantity} 🇷🇺RUB
'''
                await call.message.edit_text(
                    text=caption,
                    reply_markup=counter_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, quantity=str(quantity)).as_markup()
                )
            else:
                await call.answer(text='Нельзя купить меньше 1 единицы товара!')
        elif callback_data.count == 'none':
            caption = f'''
Какое количество товара ты хочешь заказать?

<b>Стоимость:</b> {product_data[0][6] * quantity if product_data[0][7] == 0 else (product_data[0][6] - product_data[0][6] / 100 * product_data[0][7]) * quantity} 🇷🇺RUB
    '''
            await call.message.edit_text(
                text=caption,
                reply_markup=counter_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, quantity=str(quantity)).as_markup()
            )
        else:
            await call.answer(show_alert=True)
    except:
        await call.answer(text='Что-то пошло не так 😔', show_alert=True)



# Выбор способа доставки

@router.callback_query(BuyGoods.filter(F.action == 'choose_delivery_method'))
async def button_choose_delivery_methods(call: types.CallbackQuery, callback_data: BuyGoods):

    await call.message.edit_text(
        text='Выберите способ доставки:',
        reply_markup=choose_delivery_methods_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, quantity=callback_data.quantity).as_markup()
    )


@router.callback_query(DVMehtods.filter(F.action == 'open_DVmethod'))
async def button_open_DVmethod(call: types.CallbackQuery, callback_data: DVMehtods):

    dv_method_data = db.get_delivery_method_data(method_id=callback_data.method_id)

    caption = f'''
<b>{dv_method_data[0][2]}</b>

{dv_method_data[0][3]}

<b>Стоимость доставки:</b> {dv_method_data[0][4]} 🇷🇺RUB
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=delivery_method_kb(product_id=callback_data.product_id, group_id=callback_data.group_id, quantity=callback_data.quantity, method_id=dv_method_data[0][0]).as_markup()
    )


# Выбор способа оплаты для количественных товаров (Без доставки)

@router.callback_query(BuyGoods.filter(F.action == 'buy_goods_not_delivery'))
async def button_buy_goods_not_delivery(call: types.CallbackQuery, callback_data: BuyGoods, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    await call.message.edit_text(
        text='Выберите способ оплаты:',
        reply_markup=payment_methods_not_delivery(project_id=project_id, product_id=callback_data.product_id, group_id=callback_data.group_id, quantity=callback_data.quantity).as_markup()
    )
    
    try:
        process_data = db.get_payment_process_data(process_id=callback_data.process)
        if db.get_product_data(product_id=process_data[7])[0][4]:
            content = db.get_product_contents(product_id=process_data[7]) # Получаем весь список контента
            new_content = process_data[9] + content
            db.update_list_contents(product_id=process_data[7], content=new_content) # Обновляем список контента на товаре
            db.delete_process(process_id=callback_data.process) # Удаляем платеж из базы данных
        else:
            db.plus_quantity_of_goods(product_id=process_data[7], quantity=process_data[10])
            db.delete_process(process_id=callback_data.process)
    except:
        pass

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
                                        
    await state.clear()


# Выбор способа оплаты для количественных товаров (С доставкой)

@router.callback_query(BuyGoods.filter(F.action == 'buy_goods_delivery'))
async def button_buy_goods_delivery(call: types.CallbackQuery, callback_data: BuyGoods, state:FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    await call.message.edit_text(
        text='Выберите способ оплаты:',
        reply_markup=payment_methods_delivery(project_id=project_id, product_id=callback_data.product_id, group_id=callback_data.group_id, quantity=callback_data.quantity, method_id=callback_data.count).as_markup()
    )
    try:
        process_data = db.get_payment_process_data(process_id=callback_data.process)
        if db.get_product_data(product_id=process_data[7])[0][4]:
            content = db.get_product_contents(product_id=process_data[7]) # Получаем весь список контента
            new_content = process_data[9] + content
            db.update_list_contents(product_id=process_data[7], content=new_content) # Обновляем список контента на товаре
            db.delete_process(process_id=callback_data.process) # Удаляем платеж из базы данных
        else:
            db.plus_quantity_of_goods(product_id=process_data[7], quantity=process_data[10])
            db.delete_process(process_id=callback_data.process)
    except:
        pass

    # Сбрасываем текущее состояния
    current_state = await state.get_state()

    if current_state is None:
        return
                                        
    await state.clear()