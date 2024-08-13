from aiogram import types, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext



from Database.Admin_db import Database
from Lib_payment import(
    Payment
)

from Keyboards.admin_keyboards.menu_keyboards import(
    method_payments
)

from Keyboards.admin_keyboards.payment_methods_keyboards import(
    user_payment_methods_kb,
    cancel_add_manual_payment_method,
    manual_payment_method_kb,
    delete_manual_payment_method,
    cancel_edit_manual_payment_method,
    return_manual_payment_method_kb,
    user_auto_payment_methods_kb,
    add_new_auto_payment_method,
    cancel_add_new_auto_payment_method,
    auto_payment_method_kb,
    cancel_edit_auto_payment_method,
    delete_auto_payment_method,
    return_auto_payment_method_kb,
    finis_add_new_auto_payment_method,
    cancel_add_new_yoomoney_payment_method,
    PaymentMethods,
    EditPaymentMethod,
    AutoPaymentMethods
)

db = Database()
router = Router()




class Add_manual_method(StatesGroup):
    payment_method_name = State()
    payment_method_description = State()

class Edit_manual_method(StatesGroup):
    what_to_edit_payment = State()
    payment_method_id = State()


class Add_auto_method(StatesGroup):
    add_new_auto_method = State()
    what_do_we_add = State()
    yoomoney_number = State()
    yoomoney_secret = State()

class Edit_auto_method(StatesGroup):
    what_to_edit_payment = State()
    payment_method_id = State()


@router.callback_query(F.data == 'payment_methods')
async def call_payment_methods(call: types.CallbackQuery):

    caption = '''
Какой способ оплаты хотите добавить?
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=method_payments()
    )



@router.callback_query(F.data == 'manual_payment_method')
async def call_manual_payment_method(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = '''
<b>Добавляйте свои способы оплаты с ручной проверкой!</b>

Укажите название платежной системы и реквизиты для оплаты.
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=user_payment_methods_kb(project_id=project_id).as_markup()
    )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()



# Добавить новый способ оплаты (ручной)

@router.callback_query(PaymentMethods.filter(F.action == 'add_new_manual_payment_method'))
async def call_add_new_manual_method(call: types.CallbackQuery, callback_data: PaymentMethods, state: FSMContext):
    
    if db.get_quantity_pay_methods(callback_data.method_id) < 20:
        await state.set_state(Add_manual_method.payment_method_name)

        await call.message.edit_text(
            text='Пришли название способа оплаты',
            reply_markup=cancel_add_manual_payment_method().as_markup()
        )
    else:
        await call.answer(text='Нельзя добавить больше 20 способов оплаты!', show_alert=True)



@router.message(Add_manual_method.payment_method_name, F.text)
async def get_name_payment_method(msg: types.Message, state: FSMContext):

    if len(msg.text) > 24:
        await msg.answer(
            text='Название не должно превышать 24 символа', 
            reply_markup=cancel_add_manual_payment_method().as_markup()
        )
    else:
        await state.update_data(payment_method_name=msg.text)
        await state.set_state(Add_manual_method.payment_method_description)

        await msg.answer(
            text='Пришли инструкцию для оплаты твоим способом оплаты',
            reply_markup=cancel_add_manual_payment_method().as_markup()
        )


@router.message(Add_manual_method.payment_method_description, F.text)
async def get_description_payment_method(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)
    getFSM = await state.get_data()


    if len(msg.html_text) > 2000:
        await msg.answer(
            text='Инструкция не должна превышать 2000 символа', 
            reply_markup=cancel_add_manual_payment_method().as_markup()
        )
    else:
        db.add_manual_payment_method(
            project_id=project_id,
            method_name=getFSM.get('payment_method_name'),
            method_description=msg.html_text
        )

        payment_method_data = db.get_last_manual_payment_method(project_id=project_id)

        caption = f'''
Название: {payment_method_data[0][4]}
Описание: {payment_method_data[0][5]}
'''

        await msg.answer(
            text=caption,
            reply_markup=manual_payment_method_kb(method_id=payment_method_data[0][0]).as_markup()
        )


# Открыть способ оплаты

@router.callback_query(PaymentMethods.filter(F.action == 'open_payment_method'))
async def call_open_payment_method(call: types.CallbackQuery, callback_data: PaymentMethods, state: FSMContext):
    payment_method_data = db.get_manual_paymetn_method_data(method_id=callback_data.method_id)

    caption = f'''
Название: {payment_method_data[0][4]}
Описание: {payment_method_data[0][5]}
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=manual_payment_method_kb(method_id=payment_method_data[0][0]).as_markup()
    )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()




# Редактирование способа оплаты (ручной)

@router.callback_query(EditPaymentMethod.filter(F.action == 'edit_manual_payment_method'))
async def call_edit_manual_payment_method(call: types.CallbackQuery, callback_data: EditPaymentMethod, state: FSMContext):

    if callback_data.what_to_edit == 'payment_name':
        await state.set_state(Edit_manual_method.payment_method_id)
        await state.update_data(what_to_edit='payment_name')
        await state.update_data(payment_method_id=callback_data.method_id)
        await call.message.edit_text(
            text='Пришлите новое название способа оплаты:',
            reply_markup=cancel_edit_manual_payment_method(method_id=callback_data.method_id).as_markup()
        )
    elif callback_data.what_to_edit == 'payment_description':
        await state.set_state(Edit_manual_method.payment_method_id)
        await state.update_data(what_to_edit='payment_description')
        await state.update_data(payment_method_id=callback_data.method_id)
        await call.message.edit_text(
            text='Пришлите новую инструкцию способа оплаты:',
            reply_markup=cancel_edit_manual_payment_method(method_id=callback_data.method_id).as_markup()
        )
    elif callback_data.what_to_edit == 'payment_method_off':
        db.update_status_payment_method(method_id=callback_data.method_id, method_status='false')
        await call.message.edit_reply_markup(reply_markup=manual_payment_method_kb(method_id=callback_data.method_id).as_markup())
        await call.answer(text='Способ оплаты больше недоступен для оплаты!', show_alert=True)
    elif callback_data.what_to_edit == 'payment_method_on':
        db.update_status_payment_method(method_id=callback_data.method_id, method_status='true')
        await call.message.edit_reply_markup(reply_markup=manual_payment_method_kb(method_id=callback_data.method_id).as_markup())
        await call.answer(text='Способ оплаты снова доступен для оплаты!', show_alert=True)
    elif callback_data.what_to_edit == 'want_to_delete':
        await call.message.edit_text(
            text='Вы уверены, что хотите удалить способ оплаты?',
            reply_markup=delete_manual_payment_method(callback_data.method_id).as_markup()
        )


@router.message(Edit_manual_method.payment_method_id, F.text)
async def get_new_data_payment_method(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()

    if getFSM.get('what_to_edit') == 'payment_name':
        if len(msg.text) > 24:
            await msg.answer(text='Название не должно превышать 24 символа', reply_markup=cancel_edit_manual_payment_method(method_id=getFSM.get('payment_method_id')).as_markup())
        else:
            db.edit_payment_method(method_id=getFSM.get('payment_method_id'), what_to_edit='method_name', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены!',
                reply_markup=return_manual_payment_method_kb(method_id=getFSM.get('payment_method_id')).as_markup()
            )

            current_state = await state.get_state()

            if current_state is None:
                return
                
            await state.clear()
    else:
        if len(msg.html_text) > 2000:
            await msg.answer(text='Инструкция не должна превышать 2000 символов', reply_markup=cancel_edit_manual_payment_method(method_id=getFSM.get('payment_method_id')).as_markup())
        else:
            db.edit_payment_method(method_id=getFSM.get('payment_method_id'), what_to_edit='method_description', new_data=msg.html_text)
            await msg.answer(
                text='✅ Готово! Изменения применены!',
                reply_markup=return_manual_payment_method_kb(method_id=getFSM.get('payment_method_id')).as_markup()
            )

            current_state = await state.get_state()

            if current_state is None:
                return
                
            await state.clear()

# Удаление способа оплаты (ручной)

@router.callback_query(EditPaymentMethod.filter(F.action == 'delete_manual_payment_method'))
async def call_delete_manual_payment_method(call: types.CallbackQuery, callback_data: EditPaymentMethod, state: FSMContext):
    db.delete_payment_method(callback_data.method_id)

    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = '''
<b>Добавляйте свои способы оплаты с ручной проверкой!</b>

Укажите название платежной системы и реквизиты для оплаты.
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=user_payment_methods_kb(project_id=project_id).as_markup()
    )

    await call.answer(text='Способ оплаты удален!', show_alert=True)

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()



# АВТОМАТИЧЕСКИЙ СПОСОБ ОПЛАТЫ

@router.callback_query(F.data == 'automatic_payment_method')
async def call_automatic_payment_method(call: types.CallbackQuery, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = '''
<b>Добавленные способы оплаты:</b>
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=user_auto_payment_methods_kb(project_id=project_id).as_markup()
    )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()


@router.callback_query(F.data == 'add_new_auto_payment_method')
async def call_add_new_auto_payment_method(call: types.CallbackQuery, state: FSMContext):

    caption = '''
<b>Доступные способы оплаты:</b>

<b>1. CryptoBot:</b> Оплата криптовалютой через @CryptoBot.
<b>2. WalletPay:</b> Оплата криптовалютой из кошелька @wallet.
<b>3. ЮMoney:</b> Оплата картой (до 15,000₽) или из кошелька ЮMoney.
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=add_new_auto_payment_method().as_markup()
    )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()

    


# Открываем способ оплаты

@router.callback_query(AutoPaymentMethods.filter(F.action == 'open_auto_payment_method'))
async def call_open_auto_payment_method(call: types.CallbackQuery, callback_data: AutoPaymentMethods, state: FSMContext):
    method_data = db.get_data_auto_payment_method(method_id=callback_data.method_id)

    caption = f'''
<b>Название:</b> {method_data[0][4]}
<b>Описание:</b> {method_data[0][5]}
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=auto_payment_method_kb(method_id=callback_data.method_id).as_markup()
    )

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()





#  Добавление нового способы оплаты

@router.callback_query(AutoPaymentMethods.filter(F.action == 'add_new_auto_payment_method'))
async def call_add_cryptobot_payment_method(call: types.CallbackQuery, callback_data: AutoPaymentMethods, state: FSMContext):
    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    if callback_data.data == 'CryptoBot':
        if db.check_auto_method(project_id=project_id, method_type='auto_CryptoBot')  == []:
            caption = f'''
1. Откройте <b><a href='https://t.me/send?start=r-ehesz'>CryptoBot</a></b> и введите /start
2. В разделе <b>Crypto Pay</b> нажмите <b>Создать приложение</b>
3. В разделе <b>Вебхуки</b> нажмите <b>Включить вебхуки</b>
4. Вставьте ссылку: <code>https://justmakebot.ru/cryptobot/{project_id}</code>
5. Перейдите в раздел <b>API-токен</b> 
6. Скопируйте и отправьте токен мне
'''

            await call.message.edit_text(
                text=caption,
                reply_markup=cancel_add_new_auto_payment_method().as_markup()
            )
            
            await state.set_state(Add_auto_method.add_new_auto_method)
            await state.update_data(what_do_we_add='CryptoBot')
        else:
            await call.answer(text='Данный способ оплаты уже добавлен!', show_alert=True)
    elif callback_data.data == 'WalletPay':
        if db.check_auto_method(project_id=project_id, method_type='auto_WalletPay')  == []:
            caption = f'''
<b>1. Чтобы принимать платежи на кошелек @wallet, вам нужно получить <a href='https://walletru.helpscoutdocs.com/article/195-verification-integrationru'>токен</a></b>

<b>2. В разделе "Webhooks" в поле для ввода нужно вставить следующую ссылку:</b> <code>https://justmakebot.ru/wallet/{project_id}</code>


<b><i>⚠️ Начиная с 12 июня, все платежи за цифровые товары и услуги в Telegram необходимо проводить с помощью <a href='https://t.me/BotNews/91'>Telegram Stars</a></i></b>

<i>Ожидаю сообщение с токеном😉</i>

'''

            await call.message.edit_text(
                text=caption,
                reply_markup=cancel_add_new_auto_payment_method().as_markup()
            )

            await state.set_state(Add_auto_method.add_new_auto_method)
            await state.update_data(what_do_we_add='WalletPay')
        else:
            await call.answer(text='Данный способ оплаты уже добавлен!', show_alert=True)
    elif callback_data.data == 'Yoomoney':
        if db.check_auto_method(project_id=project_id, method_type='auto_Yoomoney')  == []:
            caption = '''
<b><i>⚠️ чтобы принимать платежи, вам нужно получить <a href='https://yoomoney.ru/id/levels'>Именной или Идентифицированный</a> статус </i></b>
<b><i>⚠️ минимальная сумма платежа на ЮMoney составляет 2 руб.</i></b>
<b><i>⚠️ комиссия 3%, если пользователь платит картой, и 1%, если он платит из кошелька ЮMoney</i></b>

<i>Ожидаю от тебя токен...</i>
'''

            await call.message.edit_text(
                text=caption,
                reply_markup=cancel_add_new_auto_payment_method().as_markup()
            )

            await state.set_state(Add_auto_method.add_new_auto_method)
            await state.update_data(what_do_we_add='Yoomoney')
        else:
            await call.answer(text='Данный способ оплаты уже добавлен!', show_alert=True)




@router.message(Add_auto_method.add_new_auto_method, F.text)
async def get_token_payment_method(msg: types.Message, state: FSMContext):
    bot_username = await msg.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    getFSM = await state.get_data()

    if getFSM.get('what_do_we_add') == 'CryptoBot':
        if Payment.check_cryptobot_token(token=msg.text):
            db.add_auto_payment_method(
                project_id=project_id,
                method_type='auto_CryptoBot',
                method_name='CryptoBot',
                method_description='✅ Счет на оплату сформирован! Оплата будет производиться через платежную систему @CryptoBot',
                method_token=msg.text,
                method_number='no number'
            )
            await msg.delete()

            method_data = db.get_last_auto_payment_method(project_id=project_id)
            

            caption = f'''
<b>Название:</b> {method_data[0][4]}
<b>Описание:</b> {method_data[0][5]}
'''

            await msg.answer(
                text=caption,
                reply_markup=auto_payment_method_kb(method_id=method_data[0][0]).as_markup()
            )

            current_state = await state.get_state()

            if current_state is None:
                return
                
            await state.clear()
        else:
            await msg.answer(
                text='Ты прислал что-то не то...', 
                reply_markup=cancel_add_new_auto_payment_method().as_markup()
            )
    elif getFSM.get('what_do_we_add') == 'WalletPay':
        if Payment.check_wallet_token(token=msg.text):
            db.add_auto_payment_method(
                project_id=project_id,
                method_type='auto_WalletPay',
                method_name='👛 WalletPay',
                method_description='✅ Счет на оплату сформирован! Оплата будет производиться через платежную систему @wallet',
                method_token=msg.text,
                method_number='no number'
            )
            await msg.delete()

            method_data = db.get_last_auto_payment_method(project_id=project_id)

            caption = f'''
<b>Название:</b> {method_data[0][4]}
<b>Описание:</b> {method_data[0][5]}
'''

            await msg.answer(
                text=caption,
                reply_markup=auto_payment_method_kb(method_id=method_data[0][0]).as_markup()
            )

            current_state = await state.get_state()

            if current_state is None:
                return
                
            await state.clear()
        else:
            await msg.answer(
                text='Ты прислал что-то не то...', 
                reply_markup=cancel_add_new_auto_payment_method().as_markup()
            )
    elif getFSM.get('what_do_we_add') == 'Yoomoney':
        bot_username = await msg.bot.get_me()
        project_id = db.get_project_id(bot_username=bot_username.username)

        if msg.text.startswith('41'):
            if db.check_yoomoney_number(msg.text.replace(' ', '')) == []:
                caption = f'''
<b>Настройка автоплатежей ЮMoney</b>

1. Нажмите кнопку <b>НАСТРОИТЬ АВТОПЛАТЕЖИ</b> и войдите в свой аккаунт.
2. В поле ввода адреса вставьте ссылку: https://justmakebot.ru/yoomoney/3
3. Включите галочку <b>Отправлять уведомления</b>.
4. Нажмите <b>ГОТОВО</b> внизу страницы для сохранения настроек.
5. Нажмите <b>Показать секрет</b>, скопируйте появившийся набор символов (пример секретного слова: KP+jsgzlYebUXQl2Fj0Kt9vT) и отправьте его мне.


<b>Ожидаю секретное слово...</b>
'''

                await msg.answer(
                    text=caption,
                    reply_markup=cancel_add_new_yoomoney_payment_method().as_markup()
                )

                await state.update_data(yoomoney_number=msg.text)
                await state.update_data(what_do_we_add='get_secret')
            else:
                await msg.answer(
                    text='Такой кошелек уже используется в другом боте!',
                    reply_markup=cancel_add_new_auto_payment_method().as_markup()
                )
        else:
            await msg.answer(
                text='Ты прислал что-то не то...\n\nНомер кошелька должен начинаться на 41', 
                reply_markup=cancel_add_new_auto_payment_method().as_markup()
            )
    elif getFSM.get('what_do_we_add') == 'get_secret':
        await msg.delete()

        

        db.add_auto_payment_method(
            project_id=project_id,
            method_type='auto_Yoomoney',
            method_name='Юмани/Карта',
            method_description='✅ Счет на оплату сформирован! Оплата будет производиться через платежную систему ЮMoney.',
            method_token=str(msg.text).replace(' ', ''),
            method_number=str(getFSM.get('yoomoney_number')).replace(' ', '')
        )

        caption = '''
<b>Отлично! 🥳 Почти все готово! 👍</b>

Теперь в тех же настройках нажми на кнопку <b>"Протестировать". </b>

Если придет сообщение, что сообщение работают неправильно ⚠️, перейди в настройки и проверь, верно ли указан secret. 😉
'''


        method_data = db.get_last_auto_payment_method(project_id=project_id)

        await msg.answer(
            text=caption,
            reply_markup=finis_add_new_auto_payment_method(method_id=method_data[0][0]).as_markup()
        )

        current_state = await state.get_state()

        if current_state is None:
            return
                
        await state.clear()


# Редактирование способа оплаты (автоматический)

@router.callback_query(AutoPaymentMethods.filter(F.action == 'edit_auto_payment_method'))
async def call_edit_auto_payment_method(call: types.CallbackQuery, callback_data: AutoPaymentMethods, state: FSMContext):


    if callback_data.data == 'method_name':
        await call.message.edit_text(
            text='Пришли новое название способа оплаты',
            reply_markup=cancel_edit_auto_payment_method(method_id=callback_data.method_id).as_markup()
        )
        await state.update_data(what_to_edit='auto_method_name')
        await state.update_data(payment_method_id=callback_data.method_id)
        await state.set_state(Edit_auto_method.payment_method_id)
    elif callback_data.data == 'method_description':
        await call.message.edit_text(
            text='Пришли новое описание способа оплаты',
            reply_markup=cancel_edit_auto_payment_method(method_id=callback_data.method_id).as_markup()
        )
        await state.update_data(what_to_edit='auto_method_description')
        await state.update_data(payment_method_id=callback_data.method_id)
        await state.set_state(Edit_auto_method.payment_method_id)
    elif callback_data.data == 'method_token':
        await call.message.edit_text(
            text='Пришли новый токен/секретное слово',
            reply_markup=cancel_edit_auto_payment_method(method_id=callback_data.method_id).as_markup()
        )
        await state.update_data(what_to_edit='auto_method_token')
        await state.update_data(payment_method_id=callback_data.method_id)
        await state.set_state(Edit_auto_method.payment_method_id)
    elif callback_data.data == 'method_off':
        db.update_status_payment_method(method_id=callback_data.method_id, method_status='false')
        await call.message.edit_reply_markup(
            reply_markup=auto_payment_method_kb(method_id=callback_data.method_id).as_markup()
        )
        await call.answer(text='Способ оплаты больше не доступен для оплаты!', show_alert=True)
    elif callback_data.data == 'method_on':
        db.update_status_payment_method(method_id=callback_data.method_id, method_status='true')
        await call.message.edit_reply_markup(
            reply_markup=auto_payment_method_kb(method_id=callback_data.method_id).as_markup()
        )
        await call.answer(text='Способ оплаты снова доступен для оплаты!', show_alert=True)
    elif callback_data.data == 'delete_auto_method':
        await call.message.edit_text(
            text='Вы уверены, что хотите удалить способ оплаты?', 
            reply_markup=delete_auto_payment_method(method_id=callback_data.method_id).as_markup()
        )



@router.message(Edit_auto_method.payment_method_id, F.text)
async def get_new_data_auto_payment_method(msg: types.Message, state: FSMContext):
    getFSM = await state.get_data()

    if getFSM.get('what_to_edit') == 'auto_method_name':
        if len(msg.text) > 24:
            await msg.answer(
                text='Пришли название, которое не будет превышать 24 символа',
                reply_markup=cancel_edit_auto_payment_method(method_id=getFSM.get('payment_method_id')).as_markup()
            )
        else:
            db.edit_payment_method(method_id=getFSM.get('payment_method_id'), what_to_edit='method_name', new_data=msg.text)
            await msg.answer(
                text='✅ Готово! Изменения применены!',
                reply_markup=return_auto_payment_method_kb(method_id=getFSM.get('payment_method_id')).as_markup()
            )

            current_state = await state.get_state()

            if current_state is None:
                return
                
            await state.clear()
    elif getFSM.get('what_to_edit') == 'auto_method_description':
        if len(msg.html_text) > 2000:
                await msg.answer(text='Описание не должно превышать 2000 символов', reply_markup=cancel_edit_auto_payment_method(method_id=getFSM.get('payment_method_id')).as_markup())
        else:
            db.edit_payment_method(method_id=getFSM.get('payment_method_id'), what_to_edit='method_description', new_data=msg.html_text)
            await msg.answer(
                text='✅ Готово! Изменения применены!',
                reply_markup=return_auto_payment_method_kb(method_id=getFSM.get('payment_method_id')).as_markup()
            )

            current_state = await state.get_state()

            if current_state is None:
                return
                    
            await state.clear()
    elif getFSM.get('what_to_edit') == 'auto_method_token':
        method_data = db.get_data_auto_payment_method(method_id=getFSM.get('payment_method_id')) # Получаем данные о способе оплаты, чтобы понять токен к какой платежной системы нам ожидать

        if method_data[0][2] == 'auto_CryptoBot':
            if Payment.check_cryptobot_token(token=msg.text):
                db.edit_payment_method(method_id=getFSM.get('payment_method_id'), what_to_edit='method_token', new_data=msg.text)
                await msg.delete()
                await msg.answer(
                    text='✅ Готово! Изменения применены!',
                    reply_markup=return_auto_payment_method_kb(method_id=getFSM.get('payment_method_id')).as_markup()
                )

                current_state = await state.get_state()

                if current_state is None:
                    return
                        
                await state.clear()
            else:
                await msg.answer(
                    text='Судя по всему, с токеном что-то не так, либо вы отправили неверные данные',
                    reply_markup=cancel_edit_auto_payment_method(method_id=getFSM.get('payment_method_id')).as_markup()
                )
        elif method_data[0][2] == 'auto_WalletPay':
            if Payment.check_token(token=msg.text):
                db.edit_payment_method(method_id=getFSM.get('payment_method_id'), what_to_edit='method_token', new_data=msg.text)
                await msg.delete()
                await msg.answer(
                    text='✅ Готово! Изменения применены!',
                    reply_markup=return_auto_payment_method_kb(method_id=getFSM.get('payment_method_id')).as_markup()
                )
                current_state = await state.get_state()

                if current_state is None:
                    return
                        
                await state.clear()
            else:
                await msg.answer(
                    text='Судя по всему, с токеном что-то не так, либо вы отправили неверные данные',
                    reply_markup=cancel_edit_auto_payment_method(method_id=getFSM.get('payment_method_id')).as_markup()
                )
        elif method_data[0][2] == 'auto_Yoomoney':
            db.edit_payment_method(method_id=getFSM.get('payment_method_id'), what_to_edit='method_token', new_data=msg.text)
            await msg.delete()
            await msg.answer(
                text='✅ Готово! Изменения применены😉\n\nОтправь тестовое уведомление, чтобы проверить корректность работы',
                reply_markup=return_auto_payment_method_kb(method_id=getFSM.get('payment_method_id')).as_markup()
            )




# Удаление способа оплаты (auto)

@router.callback_query(AutoPaymentMethods.filter(F.action == 'delete_auto_payment_method'))
async def call_delete_auto_payment_method(call: types.CallbackQuery, callback_data: AutoPaymentMethods, state: FSMContext):
    db.delete_payment_method(callback_data.method_id)

    bot_username = await call.bot.get_me()
    project_id = db.get_project_id(bot_username=bot_username.username)

    caption = '''
<b>Доступные способы оплаты:</b>

<b>1. CryptoBot:</b> Оплата криптовалютой через @CryptoBot.
<b>2. WalletPay:</b> Оплата криптовалютой из кошелька @wallet.
<b>3. ЮMoney:</b> Оплата картой (до 15,000₽) или из кошелька ЮMoney.
'''

    await call.message.edit_text(
        text=caption,
        reply_markup=user_auto_payment_methods_kb(project_id=project_id).as_markup()
    )

    await call.answer(text='🗑 Способ оплаты удален!', show_alert=True)

    current_state = await state.get_state()

    if current_state is None:
        return
        
    await state.clear()