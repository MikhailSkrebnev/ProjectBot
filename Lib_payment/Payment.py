import requests
from aiohttp.web_request import Request
from aiohttp import web
import json
import hashlib
import re

from datetime import date, datetime

from Database.User_db import Database

db = Database()



# WALLET


def check_wallet_token(token): # Проверяем сможем ли отправить GET запрос на сервер, если сервер отвечает - возвращаем True, в ином случае False
    headers = {
        'Wpay-Store-Api-Key': f'{token}', 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.get('https://pay.wallet.tg/wpay/store-api/v1/reconciliation/order-amount', headers=headers)
        response.json()
        return True
    except:
        return False



def create_wallet_invoice(token, amount, description, user_id, externalId):
    headers = {
     'Wpay-Store-Api-Key': f'{token}',
     'Content-Type': 'application/json',
     'Accept': 'application/json',
    }

    payload = {
      'amount': {
        'currencyCode': 'RUB',  # выставляем счет в долларах США
        'amount': f'{amount}',
      },
      'description': f'{description}', # Указываем комментарий к заказу
      'externalId': f'{externalId}',  # ID счета на оплату в вашем боте
      'timeoutSeconds': 1800,  # время действия счета в секундах
      'customerTelegramUserId': f'{user_id}',  # ID аккаунта Telegram покупателя
    }

    response = requests.post(
      "https://pay.wallet.tg/wpay/store-api/v1/order",
      json=payload, headers=headers
    )

    data = response.json()

    try:
        return data
    except:
        return []





# Функция для удаления сообщения 
def deleteMessage(token, chat_id, message_id):
    method = 'deleteMessage'
    token = token
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url,data=data)


# Функция для отправки сообщения 
def sendMessage(token, chat_id, text, sale_id):
    try:
      method = 'sendMessage'
      token = token
      url = f"https://api.telegram.org/bot{token}/{method}"
      keyboard = json.dumps({"inline_keyboard": [[{"text": "Получить товар", "callback_data": f"usersaleid_{sale_id}"}]]})
      data = {"chat_id": chat_id,  "text": text, "parse_mode": 'HTML', "reply_markup": keyboard}
      requests.post(url,data=data)
    except:
        print('Возникла ошибка при отправке сообщения после оплаты!')


# Функция для отправки сообщения об успешной продажи админу 
def sendMessageAdmin(token, chat_id, text):
    try:
      method = 'sendMessage'
      token = token
      url = f"https://api.telegram.org/bot{token}/{method}"
      data = {"chat_id": chat_id,  "text": text, "parse_mode": 'HTML'}
      requests.post(url,data=data)
    except:
        print('Возникла ошибка при отправке сообщения после оплаты!')



# Обработка вебхука от платженой системы Wallet
async def check_payment_processing_wallet(request: Request):

    data = await request.json()

  
    if data[0]['type'] == 'ORDER_PAID': # Проверяем, что платеж действительно прошел успешно
        try:
          data_process = db.check_payment_processing(data[0]['payload']['id']) # Получаем данные из истории платежей
          
          deleteMessage(token=f'{data_process[0][0]}', chat_id=data_process[0][4], message_id=data_process[0][12])
          
          
          caption_user = f'''
{db.get_after_payment_caption(project_id=data_process[0][3])[0][0]}

<i>Нажми на кнопку ниже, чтобы получить товар</i>
  '''

          now = datetime.now() 
          time = now.strftime("%H:%M:%S")

          product_data = db.get_sale_product_data(data_process[0][8])

          # Добавляем новую продажу
          db.add_new_sale(
              project_id=data_process[0][3],
              sale_date=date.today(),
              sale_time=time,
              user_id=data_process[0][4],
              payment_method=data_process[0][7],
              product_id=data_process[0][8],
              product_name=f'{product_data[0][8]}',
              product_type=f'{product_data[0][2]}',
              product_content=data_process[0][10] if product_data[0][2] != 'delivery' else '',
              quantity=data_process[0][11],
              product_price=data_process[0][9]
          )
          db.update_sales_product(product_id=data_process[0][8]) # Добавляем 1 продажу к товару
          db.delete_process(process_id=db.get_last_process_id(user_id=data_process[0][4], product_id=data_process[0][8])) # Удаляем оплаченный платеж из БД
          sale_id = db.get_last_sale_user(user_id=data_process[0][4], product_id=data_process[0][8])[0][0] # Получаем sale_id последней покупки клиента, чтобы передать в коллбэк
          delivery_data = db.delivery_method_data(method_id=data_process[0][10][0])


          if product_data[0][2] == 'delivery': # Если товар с доставкой, то добавляем данные о доставке
            db.add_new_delivery_order(
               sale_id=sale_id,
               user_id=data_process[0][4],
               project_id=product_data[0][1],
               product_name=product_data[0][8],
               product_price=product_data[0][6],
               product_quantity=data_process[0][11],
               delivery_method=delivery_data[0][2],
               delivery_price=delivery_data[0][4]
            )

          sendMessage(token=f'{data_process[0][0]}', chat_id=data_process[0][4], text=caption_user, sale_id=sale_id) # Отправляем сообщение об успешной оплате юзеру


          
          user_data = db.get_user_data(user_id=data_process[0][4], project_id=data_process[0][3]) # Получаем данные о покупателе

          caption_admin = f'''
<b>💰 НОВАЯ ПРОДАЖА!</b>

<b>Товар:</b> {product_data[0][8]} 
<b>Прибыль:</b> {data_process[0][9]} 🇷🇺 RUB

<b>Данные покупателя:</b>
<b>🔹 ID покупателя:</b> <code>{data_process[0][4]}</code>
<b>🔹 Username:</b> {'@' + str(user_data[0][4]) if user_data[0][4] != 'None' else 'не указано'}
<b>🔹 Fullname покупателя:</b> <code>{user_data[0][3]}</code>
<b>🔹 Дата регистрации:</b> {user_data[0][1]} {user_data[0][2]}
<b>🔹 Кол-во покупок:</b> {user_data[0][5]}
<b>🔹 Сумма покупок:</b> {user_data[0][6]} 🇷🇺 RUB
<b>🔹 Способ оплаты:</b> WalletPay

Поздравляем с новой продажей! 🎉
'''

          sendMessageAdmin(token=f'{data_process[0][0]}', chat_id=db.get_admin_id(data_process[0][3]), text=caption_admin) # Отправляем сообщение об успешной продаже админу

          return web.Response(status=200)
        except:
          return web.Response(status=200)
    else:
        return web.Response(status=200)
  





#CRYPTOBOT

# Авторизация токена

def check_cryptobot_token(token):
    headers = {
        'Crypto-Pay-API-Token': f'{token}', 
        'content_type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.post('https://pay.crypt.bot/api/getMe', headers=headers)

    data = response.json()

    if response.status_code == 200: # Если токен валидный, то вернет True, в ином случае будет возвращено False
        return True
    else:
        return False
    


def create_cryptobot_invoice(token, amount):
    headers = {
        'Crypto-Pay-API-Token': f'{token}', 
        'content_type': 'application/json',
        'Accept': 'application/json'
    }

    params = {
        'currency_type': 'fiat',
        'fiat': 'RUB',
        'accepted_assets': 'USDT, TON, BTC, ETH, LTC, BNB, TRX',
        'amount': {amount},
        'expires_in': 1800
    }

    response = requests.get(url='https://pay.crypt.bot/api/createInvoice', params=params, headers=headers)

    data = response.json()

    try:
        return data
    except:
        return []






# Обработка вебхука от платженой системы
async def check_payment_processing_cryptobot(request: Request):

    data = await request.json()

  
    if data['payload']['status'] == 'paid': # Проверяем, что платеж действительно прошел успешно
        try:
          data_process = db.check_payment_processing(data['payload']['invoice_id']) # Получаем данные из истории платежей
          
          deleteMessage(token=f'{data_process[0][0]}', chat_id=data_process[0][4], message_id=data_process[0][12])
          
          
          caption_user = f'''
{db.get_after_payment_caption(project_id=data_process[0][3])[0][0]}

<i>Нажми на кнопку ниже, чтобы получить товар</i>
  '''

          now = datetime.now() 
          time = now.strftime("%H:%M:%S")

          product_data = db.get_sale_product_data(data_process[0][8])

          # Добавляем новую продажу
          db.add_new_sale(
              project_id=data_process[0][3],
              sale_date=date.today(),
              sale_time=time,
              user_id=data_process[0][4],
              payment_method=data_process[0][7],
              product_id=data_process[0][8],
              product_name=f'{product_data[0][8]}',
              product_type=f'{product_data[0][2]}',
              product_content=data_process[0][10] if product_data[0][2] != 'delivery' else '',
              quantity=data_process[0][11],
              product_price=data_process[0][9]
          )
             
          db.update_sales_product(product_id=data_process[0][8]) # Добавляем 1 продажу к товару
          db.delete_process(process_id=db.get_last_process_id(user_id=data_process[0][4], product_id=data_process[0][8])) # Удаляем оплаченный платеж из БД
          sale_id = db.get_last_sale_user(user_id=data_process[0][4], product_id=data_process[0][8])[0][0] # Получаем sale_id последней покупки клиента, чтобы передать в коллбэк
          delivery_data = db.delivery_method_data(method_id=data_process[0][10][0])


          if product_data[0][2] == 'delivery': # Если товар с доставкой, то добавляем данные о доставке
            db.add_new_delivery_order(
               sale_id=sale_id,
               user_id=data_process[0][4],
               project_id=product_data[0][1],
               product_name=product_data[0][8],
               product_price=product_data[0][6],
               product_quantity=data_process[0][11],
               delivery_method=delivery_data[0][2],
               delivery_price=delivery_data[0][4]
            )

          sendMessage(token=f'{data_process[0][0]}', chat_id=data_process[0][4], text=caption_user, sale_id=sale_id) # Отправляем сообщение об успешной оплате юзеру


          
          user_data = db.get_user_data(user_id=data_process[0][4], project_id=data_process[0][3]) # Получаем данные о покупателе

          caption_admin = f'''
<b>💰 НОВАЯ ПРОДАЖА!</b>

<b>Товар:</b> {product_data[0][8]} 
<b>Прибыль:</b> {data_process[0][9]} 🇷🇺 RUB

<b>Данные покупателя:</b>
<b>🔹 ID покупателя:</b> <code>{data_process[0][4]}</code>
<b>🔹 Username:</b> {'@' + str(user_data[0][4]) if user_data[0][4] != 'None' else 'не указано'}
<b>🔹 Fullname покупателя:</b> <code>{user_data[0][3]}</code>
<b>🔹 Дата регистрации:</b> {user_data[0][1]} {user_data[0][2]}
<b>🔹 Кол-во покупок:</b> {user_data[0][5]}
<b>🔹 Сумма покупок:</b> {user_data[0][6]} 🇷🇺 RUB
<b>🔹 Способ оплаты:</b> CryptoBot

Поздравляем с новой продажей! 🎉
'''

          sendMessageAdmin(token=f'{data_process[0][0]}', chat_id=db.get_admin_id(data_process[0][3]), text=caption_admin) # Отправляем сообщение об успешной продаже админу

          return web.Response(status=200)
        except(Exception) as error:
          print(error)
          return web.Response(status=200)
    else:
        return web.Response(status=200)






#YOOMONEY


# Функция для отправки сообщения 
def sendPush(token, chat_id, text):
    try:
      method = 'sendMessage'
      token = token
      url = f"https://api.telegram.org/bot{token}/{method}"
      data = {"chat_id": chat_id,  "text": text, "parse_mode": 'HTML'}
      requests.post(url,data=data)
    except:
        print('Возникла ошибка при отправке пуша!')





def check_operation(post, secret):
    
    sha1 = ''

    sha1 += post['notification_type'] + '&'
    sha1 += post['operation_id'] + '&'
    sha1 += post['amount'] + '&'
    sha1 += post['currency'] + '&'
    sha1 += post['datetime'] + '&'
    sha1 += post['sender'] + '&'
    sha1 += post['codepro'] + '&'
    sha1 += str(secret) + '&'
    sha1 += post['label']

    sha1 = hashlib.sha1(str(sha1).encode('utf-8'))
    hex = sha1.hexdigest()

    if hex == post['sha1_hash']:
       return True
    else:
       return False

    


# Обработка вебхука от платженой системы Yoomoney
async def check_payment_processing_yoomoney(request: Request):
  data = await request.post()

  text = str(request)
  text_split = text.split('<Request POST /yoomoney/')

  project_id = int((text_split[1])[:-2])
  bot_data = db.get_bot_data(project_id=project_id)


  text1 = '✅ Уведомления о платежах настроены!'
  text2 = '''
<b>⚠️ У меня возникла проблема с обработкой уведомления от ЮMoney!</b>

Проверь, актуальное ли секретное слово у тебя установлено в настройках ЮMoney, а также убедись, что стоит галочка возле "Отправлять HTTP-уведомления".
'''
  text3 = '🚫 Пожалуйста, пришлите мне секретное слово, которое позволит мне корректно обрабатывать сообщения от ЮMoney'



  try:
    secret = db.get_yoomoney_method(project_id=project_id)

    if check_operation(data, secret=secret[0][6]):
        if data['label'] == '':
          sendPush(token=bot_data[0][6], chat_id=bot_data[0][1], text=text1)
        else:
          try:
            data_process = db.check_payment_processing(data['label']) # Получаем данные из истории платежей


            if "{:.2f}".format(data_process[0][9]) == data['withdraw_amount']:
              
              deleteMessage(token=f'{data_process[0][0]}', chat_id=data_process[0][4], message_id=data_process[0][12])
              
              
              caption_user = f'''
{db.get_after_payment_caption(project_id=data_process[0][3])[0][0]}

<i>Нажми на кнопку ниже, чтобы получить товар</i>
  '''

              now = datetime.now() 
              time = now.strftime("%H:%M:%S")

              product_data = db.get_sale_product_data(data_process[0][8])

              # Добавляем новую продажу
              db.add_new_sale(
                  project_id=data_process[0][3],
                  sale_date=date.today(),
                  sale_time=time,
                  user_id=data_process[0][4],
                  payment_method=data_process[0][7],
                  product_id=data_process[0][8],
                  product_name=f'{product_data[0][8]}',
                  product_type=f'{product_data[0][2]}',
                  product_content=data_process[0][10] if product_data[0][2] != 'delivery' else '',
                  quantity=data_process[0][11],
                  product_price=data_process[0][9]
              )
                
              db.update_sales_product(product_id=data_process[0][8]) # Добавляем 1 продажу к товару
              db.delete_process(process_id=db.get_last_process_id(user_id=data_process[0][4], product_id=data_process[0][8])) # Удаляем оплаченный платеж из БД
              sale_id = db.get_last_sale_user(user_id=data_process[0][4], product_id=data_process[0][8])[0][0] # Получаем sale_id последней покупки клиента, чтобы передать в коллбэк
              delivery_data = db.delivery_method_data(method_id=data_process[0][10][0])


              if product_data[0][2] == 'delivery': # Если товар с доставкой, то добавляем данные о доставке
                db.add_new_delivery_order(
                  sale_id=sale_id,
                  user_id=data_process[0][4],
                  project_id=product_data[0][1],
                  product_name=product_data[0][8],
                  product_price=product_data[0][6],
                  product_quantity=data_process[0][11],
                  delivery_method=delivery_data[0][2],
                  delivery_price=delivery_data[0][4]
                )

              sendMessage(token=f'{data_process[0][0]}', chat_id=data_process[0][4], text=caption_user, sale_id=sale_id) # Отправляем сообщение об успешной оплате юзеру


              
              user_data = db.get_user_data(user_id=data_process[0][4], project_id=data_process[0][3]) # Получаем данные о покупателе

              caption_admin = f'''
<b>💰 НОВАЯ ПРОДАЖА!</b>

<b>Товар:</b> {product_data[0][8]} 
<b>Прибыль:</b> {data_process[0][9]} 🇷🇺 RUB

<b>Данные покупателя:</b>
<b>🔹 ID покупателя:</b> <code>{data_process[0][4]}</code>
<b>🔹 Username:</b> {'@' + str(user_data[0][4]) if user_data[0][4] != 'None' else 'не указано'}
<b>🔹 Fullname покупателя:</b> <code>{user_data[0][3]}</code>
<b>🔹 Дата регистрации:</b> {user_data[0][1]} {user_data[0][2]}
<b>🔹 Кол-во покупок:</b> {user_data[0][5]}
<b>🔹 Сумма покупок:</b> {user_data[0][6]} 🇷🇺 RUB
<b>🔹 Способ оплаты:</b> YooMoney

Поздравляем с новой продажей! 🎉
'''

              sendMessageAdmin(token=f'{data_process[0][0]}', chat_id=db.get_admin_id(data_process[0][3]), text=caption_admin) # Отправляем сообщение об успешной продаже админу

              return web.Response(status=200)
            else:
              print('Была попытка выставить поддельный счет')
              return web.Response(status=200)
          except(Exception) as error:
            print(error)
            return web.Response(status=200)
    else:
      sendPush(token=bot_data[0][6], chat_id=bot_data[0][1], text=text2)
  except:
    sendPush(token=bot_data[0][6], chat_id=bot_data[0][1], text=text3)


  
  return web.Response(status=200)


