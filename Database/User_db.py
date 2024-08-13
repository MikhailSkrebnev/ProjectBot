import psycopg2
from psycopg2 import Error




class Database:
    def __init__(self) -> None:
        try:
            self.connection = psycopg2.connect(
                host='dalotekal.beget.app',
                port=5432,
                sslmode='disable',
                dbname='*********',
                user='*********',
                password='*********',
                target_session_attrs='read-write'
            )

            self.cursor = self.connection.cursor()
        except(Exception, Error) as error:
            print('Возникла ошибка в БД!', error)

        
        # try:
        #     self.connection = psycopg2.connect(
        #         host="127.0.0.1",
        #         database="*********",
        #         user="postgres",
        #         password="*********"
        #     )

        #     self.cursor = self.connection.cursor()
        # except(Exception, Error) as error:
        #     print('Возникла ошибка в БД!', error)


        
    
    def get_project_id(self, bot_username):
        self.cursor.execute(f"SELECT project_id FROM bots WHERE bot_username = '{bot_username}'")
        return self.cursor.fetchall()[0][0]

        

        
    def check_user_id_admin(self, bot_username):
        self.cursor.execute(f"SELECT user_id FROM bots WHERE bot_username = '{bot_username}'")
        return self.cursor.fetchall()[0][0]

    def get_bot_data(self, project_id):
        self.cursor.execute(f"SELECT * FROM bots WHERE project_id = {project_id}")
        return self.cursor.fetchall()
  
    
    def get_caption(self, caption, bot_username):
        self.cursor.execute(f"SELECT uc.{caption} FROM user_captions uc JOIN bots b ON uc.project_id = b.project_id WHERE b.bot_username = '{bot_username}'")
        caption = self.cursor.fetchall()

        if caption == []:
            return ''
        else:
            return caption[0][0]
        
    
    def get_admin_id(self, project_id):
        self.cursor.execute(f"SELECT user_id FROM bots WHERE project_id = {project_id}")
        return self.cursor.fetchall()
    

    def get_tokens(self):
        self.cursor.execute(f"SELECT * FROM bots")
        return self.cursor.fetchall()
        
    

    # Регистрация новый пользователей

    def check_reg_user(self, project_id, user_id):
        self.cursor.execute(f"SELECT * FROM user_clients WHERE project_id = {project_id} AND user_id = {user_id}")
        return self.cursor.fetchall()

    def reg_new_user(self, project_id, user_id, fullname, username, date_reg, time_reg, job_title):
        self.cursor.execute(f"INSERT INTO user_clients (user_id, project_id, user_fullname, user_username, date_reg, time_reg, status_user, job_title)  VALUES ({user_id}, {project_id}, '{fullname}', '{username}', '{date_reg}', '{time_reg}', True, '{job_title}')")
        self.connection.commit()

    def update_user_data(self, user_id, fullname, username):
        self.cursor.execute(f"UPDATE user_clients SET user_fullname = '{fullname}', user_username = '{username}' WHERE user_id = {user_id}")
        self.connection.commit()

    def get_user_data(self, user_id, project_id):
        sql_request = f'''
SELECT 
    uc.user_id,
	uc.date_reg,
	uc.time_reg,
	uc.user_fullname,
	uc.user_username,
    COUNT(us.sale_id) AS total_purchases, 
    SUM(us.product_price) AS total_amount 
FROM
    user_clients uc
LEFT JOIN
    user_sales us
ON 
    uc.user_id = us.user_id AND uc.project_id = us.project_id 
WHERE uc.user_id = {user_id} AND uc.project_id = {project_id}
GROUP BY uc.user_id, uc.date_reg, uc.time_reg, uc.user_fullname, uc.user_username
'''

        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()


    # Запросы для отобржания групп и товаров

    def get_user_groups(self, project_id, parent_id):
        self.cursor.execute(f"SELECT * FROM user_groups WHERE project_id = {project_id} AND parent_id = {parent_id} ORDER BY group_id")
        return self.cursor.fetchall()
    
    def get_all_groups(self, project_id):
        self.cursor.execute(f"SELECT * FROM user_groups WHERE project_id = {project_id} AND parent_id = -1")
        return self.cursor.fetchall()
    
    def list_of_displayed_products_no_group(self, project_id):
        sql_request = f'''
SELECT ug.group_id, pr.*
FROM user_groups ug, unnest(group_products) AS selected
JOIN products pr ON CAST(selected AS INTEGER) = pr.product_id
WHERE ug.parent_id = -1 AND ug.project_id = {project_id} AND pr.display_status = 'включен' AND pr.quantity > 0
ORDER BY pr.product_id
'''

        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()
    

    def get_product_data(self, product_id):
        self.cursor.execute(f"SELECT * FROM products WHERE product_id = {product_id} AND display_status = 'включен' AND quantity > 0")
        return self.cursor.fetchall()
    
    def get_product_photos(self, product_id):
        sql_request = f'''
SELECT array_agg(pi.content_id) AS list_photos
FROM products pr, unnest(product_photo) AS photos
JOIN pictures pi ON CAST(photos AS INTEGER) = pi.picture_id
WHERE pr.product_id = {product_id}
''' 
        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()[0][0]


    def get_group_from_group(self, parent_id, project_id):
        sql_request = f'''
SELECT *
FROM user_groups
WHERE parent_id = {parent_id} AND project_id = {project_id}
'''
        self.cursor.execute(f"{sql_request}")
        # if self.cursor.fetchall() == []:
        #     return [()]
        # else:
        return self.cursor.fetchall()
    
    def get_group_data(self, group_id):
        self.cursor.execute(f"SELECT * FROM user_groups WHERE group_id = {group_id}")
        return self.cursor.fetchall()
    

    def list_products_in_a_group(self, group_id):
        sql_request = f'''
SELECT ug.group_id, pr.*
FROM user_groups ug, unnest(group_products) AS selected
JOIN products pr ON CAST(selected AS INTEGER) = pr.product_id
WHERE group_id = {group_id} AND pr.display_status = 'включен' AND pr.quantity > 0
ORDER BY pr.product_id
'''
        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()
    
    def check_quantity_product(self, product_id, quantity):
        self.cursor.execute(f"SELECT * FROM products WHERE product_id = {product_id} AND quantity >= {quantity}")
        return self.cursor.fetchall()



# Запросы для получения способов доставки товара

    def get_delivery_methods(self, product_id):
        sql_request = f'''
SELECT dm.*
FROM products pr, unnest(contents) AS methods
JOIN delivery_methods dm ON CAST(methods AS INTEGER) = dm.method_id
WHERE pr.product_id = {product_id} AND dm.method_status = true
'''

        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()
    
    def get_delivery_method_data(self, method_id):
        self.cursor.execute(f"SELECT * FROM delivery_methods WHERE method_id = {method_id} AND method_status = true")
        return self.cursor.fetchall()



# Запросы для оплаты

    def get_payment_methods(self, project_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE project_id = {project_id} AND method_status = true ORDER BY method_id")
        return self.cursor.fetchall()
    

    def get_payment_method_data(self, method_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE method_id = {method_id} AND method_status = true")
        return self.cursor.fetchall()

    def add_new_payment_processing(self, project_id, user_id, payment_id, payment_method_id, payment_method_type, product_id, product_price, contents, product_quantity, message_id):
        list_contents = ''

        for content in contents:
            list_contents += '"' + f'{content}' + '"' + ','

        list_contents = '{' + list_contents[:-1] + '}'


        sql_request = f'''
INSERT INTO payments_in_processing 
(project_id, user_id, payment_id, payment_method_id, payment_method_type, product_id, product_price, contents, product_quantity, message_id)
VALUES
({project_id}, {user_id}, '{payment_id}', {payment_method_id}, '{payment_method_type}', {product_id}, {product_price}, '{list_contents}', {product_quantity}, {message_id})
'''

        self.cursor.execute(f"{sql_request}")
        self.connection.commit()

    def get_product_contents(self, product_id):
        self.cursor.execute(f"SELECT contents FROM products WHERE product_id = {product_id}")
        return self.cursor.fetchall()[0][0]
    
    def update_list_contents(self, product_id, content):

        list_contents = ''

        for item in content:
            list_contents += '"' + f'{item}' + '"' + ','

        list_contents = '{' + list_contents[:-1] + '}'

        self.cursor.execute(f"UPDATE products SET contents = '{list_contents}', quantity = {len(content)} WHERE product_id = {product_id}")
        self.connection.commit()

    def get_sale_product_data(self, product_id):
        self.cursor.execute(f"SELECT * FROM products WHERE product_id = {product_id}")
        return self.cursor.fetchall()


    def get_last_process_id(self, user_id, product_id):
        self.cursor.execute(f"SELECT * FROM payments_in_processing WHERE user_id = {user_id} AND product_id = {product_id} ORDER BY process_id DESC LIMIT 1")
        return self.cursor.fetchall()[0][0]
    
    def delete_process(self, process_id):
        self.cursor.execute(f"DELETE FROM payments_in_processing WHERE process_id = {process_id}")
        self.connection.commit()

    def minus_quantity_of_goods(self, product_id, quantity):
        self.cursor.execute(f"UPDATE products SET quantity = quantity - {quantity} WHERE product_id = {product_id} AND reusable = false")
        self.connection.commit()

    def plus_quantity_of_goods(self, product_id, quantity):
        self.cursor.execute(f"UPDATE products SET quantity = quantity + {quantity} WHERE product_id = {product_id} AND reusable = false")
        self.connection.commit()

    def get_payment_process_data(self, process_id):
        self.cursor.execute(f"SELECT * FROM payments_in_processing WHERE process_id = {process_id}")
        return self.cursor.fetchall()[0]
    
    def update_message_id(self, message_id, process_id):
        self.cursor.execute(f"UPDATE payments_in_processing SET message_id = {message_id} WHERE process_id = {process_id}")
        self.connection.commit()
    
    def check_payment_processing(self, payment_id):
        self.cursor.execute(f"SELECT b.bot_token, pp.* FROM payments_in_processing pp JOIN bots b ON pp.project_id = b.project_id WHERE payment_id = '{payment_id}'")
        return self.cursor.fetchall()
    

    def get_payment_method(self, method_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE method_id = {method_id}")
        return self.cursor.fetchall()
    

    def get_yoomoney_method(self, project_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE project_id = {project_id} AND method_type = 'auto_Yoomoney'")
        return self.cursor.fetchall()
    
    def check_status_sub(self, project_id):
        sql_req = f'''
SELECT cl.user_subscription
FROM clients cl
JOIN bots b ON cl.user_id = b.user_id
WHERE b.project_id = {project_id}
'''
        
        self.cursor.execute(f"{sql_req}")
        return self.cursor.fetchall()
        


# Запросы для работы с успешными покупками
    def add_new_sale(self, project_id, sale_date, sale_time, user_id, payment_method, product_id, product_name, product_type, product_content, quantity, product_price):
        list_contents = ''

        for content in product_content:
            list_contents += '"' + f'{content}' + '"' + ','

        list_contents = '{' + list_contents[:-1] + '}'

        sql_request = f'''
INSERT INTO user_sales (project_id, sale_date, sale_time, user_id, payment_method, product_id, product_name, product_type, product_content, quantity, product_price)
VALUES (
{project_id},
'{sale_date}',
'{sale_time}',
{user_id},
'{payment_method}',
{product_id},
'{product_name}',
'{product_type}',
'{list_contents}',
{quantity},
{product_price}
)
'''

        self.cursor.execute(f"{sql_request}")
        self.connection.commit()

    def add_new_delivery_order(self, sale_id, user_id, project_id, product_name, product_price, product_quantity, delivery_method, delivery_price):
        sql_request = f'''
INSERT INTO delivery_orders (sale_id, user_id, project_id, product_name, product_price, product_quantity, delivery_method, delivery_price)
VALUES (
{sale_id},
{user_id},
{project_id},
'{product_name}',
{product_price},
{product_quantity},
'{delivery_method}',
{delivery_price}
)
'''
        self.cursor.execute(f"{sql_request}")
        self.connection.commit()

    def delivery_method_data(self, method_id):
        self.cursor.execute(f"SELECT * FROM delivery_methods WHERE method_id = {method_id}")
        return self.cursor.fetchall()

    def update_sales_product(self, product_id):
        self.cursor.execute(f"UPDATE products SET sales = sales + 1 WHERE product_id = {product_id}")
        self.connection.commit()

    def get_last_sale_user(self, user_id, product_id):
        self.cursor.execute(f"SELECT * FROM user_sales WHERE user_id = {user_id} AND product_id = {product_id} ORDER BY sale_id DESC LIMIT 1")
        return self.cursor.fetchall()
    
    def get_after_payment_caption(self, project_id):
        self.cursor.execute(f"SELECT after_payment_caption FROM user_captions")
        return self.cursor.fetchall()
    
    


# Запросы для работы с таблицей продаж

    def get_sale_data(self, sale_id):
        sql_request = f'''
SELECT pr.product_id, pr.product_type, pr.reusable, us.product_content
FROM products pr
JOIN user_sales us ON pr.product_id = us.product_id
WHERE us.sale_id = {sale_id}
'''

        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()
    
    def get_inf_product_content(self, content_id):
        self.cursor.execute(f"SELECT * FROM product_content WHERE content_id = {content_id}")
        return self.cursor.fetchall()
    
    def get_ch_product_content(self, content_id):
        self.cursor.execute(f"SELECT * FROM resources WHERE resource_id = {content_id}")
        return self.cursor.fetchall()
    
    def get_dv_product_content(self, sale_id):
        self.cursor.execute(f"SELECT * FROM delivery_orders WHERE sale_id = {sale_id}")
        return self.cursor.fetchall()
    

# Запросы для редактирования адреса доставки заказа

    def get_delivery_data(self, order_id):
        self.cursor.execute(f"SELECT * FROM delivery_orders WHERE order_id = {order_id}")
        return self.cursor.fetchall()

    def update_delivery_address(self, order_id, new_address):
        self.cursor.execute(f"UPDATE delivery_orders SET delivery_address = '{new_address}' WHERE order_id = {order_id}")
        self.connection.commit()

    def who_is_admin(self, project_id):
        self.cursor.execute(f"SELECT user_id FROM bots WHERE project_id = {project_id}")
        return self.cursor.fetchall()[0][0]






# Запросы для раздела ПОКУПКИ

    def get_paid_items(self, user_id, project_id):
        self.cursor.execute(f"SELECT * FROM user_sales WHERE project_id = {project_id} AND user_id = {user_id}")
        return self.cursor.fetchall()
    

    def get_purchase_data(self, purchase_id):
        self.cursor.execute(f"SELECT * FROM user_sales WHERE sale_id = {purchase_id}")
        return self.cursor.fetchall()
    

    def get_delivery_order(self, sale_id):
        self.cursor.execute(f"SELECT * FROM delivery_orders WHERE sale_id = {sale_id}")
        return self.cursor.fetchall()
    




    def get_group_photo(self, identifier, path):
        self.cursor.execute(f"SELECT * FROM pictures WHERE identifier = {identifier} AND path_to_the_image = '{path}'")
        return self.cursor.fetchall()







# test = Database()
# print(test.get_sale_product_data(product_id=53))
