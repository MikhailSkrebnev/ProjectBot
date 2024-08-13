import psycopg2
from psycopg2 import Error




class Database:
    def __init__(self) -> None:
        try:
            self.connection = psycopg2.connect(
                host='dalotekal.beget.app',
                port=5432,
                sslmode='disable',
                dbname='JustMakeBot',
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
        #         password="l*********"
        #     )

        #     self.cursor = self.connection.cursor()
        # except(Exception, Error) as error:
        #     print('Возникла ошибка в БД!', error)


    def check_user_id_admin(self, bot_username):
        self.cursor.execute(f"SELECT user_id FROM bots WHERE bot_username = '{bot_username}'")
        return self.cursor.fetchall()[0][0]
    
    
    def get_project_id(self, bot_username):
        self.cursor.execute(f"SELECT project_id FROM bots WHERE bot_username = '{bot_username}'")
        return self.cursor.fetchall()[0][0]
       
    
    
    
    


# Запросы для раздела Design

    def get_menu_picture(self, project_id):
        self.cursor.execute(f"SELECT * FROM pictures WHERE identifier = {project_id} AND path_to_the_image = 'menu'")
        return self.cursor.fetchall()
    
    def get_pic(self, pic_id):
        self.cursor.execute(f"SELECT * FROM pictures WHERE picture_id = {pic_id}")
        return self.cursor.fetchall()
    
    def add_menu_picture(self, project_id, photo):
        self.cursor.execute(f"INSERT INTO pictures (identifier, path_to_the_image, content_id, content_type) VALUES ({project_id}, 'menu', '{photo}', 'photo')")
        self.connection.commit()

    def delete_menu_picture(self, picture_id):
        self.cursor.execute(f"DELETE FROM pictures WHERE picture_id = {picture_id}")
        self.connection.commit()




    
# Запросы связанные с описаниями
    def get_caption(self, caption, bot_username):
        self.cursor.execute(f"SELECT uc.{caption} FROM user_captions uc JOIN bots b ON uc.project_id = b.project_id WHERE b.bot_username = '{bot_username}'")
        caption = self.cursor.fetchall()

        if caption == []:
            return ''
        else:
            return caption[0][0]
        
    def edit_caption(self, project_id, caption, new_caption):
        self.cursor.execute(f"UPDATE user_captions SET {str(caption)} = '{new_caption}' WHERE project_id = {project_id}")
        self.connection.commit()


# Запросы для раздела РЕСУРСЫ
    def get_list_resources(self, bot_username):
        self.cursor.execute(f"SELECT r.* FROM resources r JOIN bots b ON r.project_id = b.project_id WHERE b.bot_username = '{bot_username}' ORDER BY resource_id DESC")
        return self.cursor.fetchall()
    
    def check_resource(self, channel_id, bot_username):
        self.cursor.execute(f"SELECT r.* FROM resources r JOIN bots b ON r.project_id = b.project_id WHERE r.channel_id = {channel_id} AND b.bot_username = '{bot_username}'")
        return self.cursor.fetchall()
    
    def add_resourse(self, project_id, channel_name, channel_id):
        self.cursor.execute(f"INSERT INTO resources (project_id, channel_name, channel_id) VALUES ({project_id}, '{channel_name}', {channel_id})")
        self.connection.commit()

    def get_data_resources(self, resource_id):
        self.cursor.execute(f"SELECT * FROM resources WHERE resource_id = {resource_id}")
        return self.cursor.fetchall()
    
    def update_data_resource(self, channel_id, new_name):
        self.cursor.execute(f"UPDATE resources SET channel_name = '{new_name}' WHERE channel_id = {channel_id}")
        self.connection.commit()

    def get_list_content_ch_product(self, project_id):
        self.cursor.execute(f"SELECT contents, product_name FROM products  WHERE project_id = {project_id} AND product_type = 'channel'")
        return self.cursor.fetchall()
    
    def delete_resource(self, resource_id):
        self.cursor.execute(f"DELETE FROM resources WHERE resource_id = {resource_id}")
        self.connection.commit()



# Запросы связанные с разделом ГРУППЫ
    def get_list_groups(self, bot_username, parent_id):
        self.cursor.execute(f"SELECT g.* FROM user_groups g JOIN bots b ON g.project_id = b.project_id WHERE b.bot_username = '{bot_username}' AND g.parent_id = {parent_id} ORDER BY g.group_id")
        return self.cursor.fetchall()
    
    def get_group_data(self, group_id):
        self.cursor.execute(f"SELECT * FROM user_groups WHERE group_id = {group_id}")
        return self.cursor.fetchall()
    
    def get_parent_groups(self, group_id):
        self.cursor.execute(f"SELECT * FROM user_groups WHERE parent_id = {group_id} ORDER BY group_id")
        return self.cursor.fetchall()
    
    def add_new_group(self, parent_id, group_lvl, group_name, group_description, project_id):
        empty_list = "{" + "}"
        self.cursor.execute(f"INSERT INTO user_groups (parent_id, project_id, group_name, group_description, group_photo, group_products, group_lvl) VALUES ({parent_id}, {project_id}, '{group_name}', '{group_description}', '{empty_list}', '{empty_list}', {group_lvl})")
        self.connection.commit()

    def get_last_group(self, project_id):
        self.cursor.execute(f"SELECT * FROM user_groups WHERE project_id = {project_id} ORDER BY group_id DESC LIMIT 1")
        return self.cursor.fetchall()
    
    def edit_group(self, group_id, new_data, set):
        self.cursor.execute(f"UPDATE user_groups SET {set} = '{new_data}' WHERE group_id = {group_id}")
        self.connection.commit()

    def get_list_products_to_groups(self, project_id, product_type):
        self.cursor.execute(f"SELECT * FROM products WHERE project_id = {project_id} AND product_type = '{product_type}' ORDER BY product_id DESC")
        return self.cursor.fetchall()
    
    def get_showcase_id(self, project_id):
        self.cursor.execute(f"SELECT group_id FROM user_groups WHERE project_id = {project_id} AND parent_id = -1")
        return self.cursor.fetchall()[0][0]
    
    def get_active_list_products_to_groups(self, group_id):
        self.cursor.execute(f"SELECT group_products FROM user_groups WHERE group_id = {group_id}")
        return self.cursor.fetchall()[0][0]
    
    def update_list_product_to_group(self, group_id, selected):
        list_product = ''

        for product in selected:
            list_product += '"' + f'{product}' + '"' + ','

        list_product = '{' + list_product[:-1] + '}'

        self.cursor.execute(f"UPDATE user_groups SET group_products = '{list_product}' WHERE group_id = {group_id}")
        self.connection.commit()

    def delete_group(self, group_id):
        sql_request = f'''
WITH RECURSIVE GroupHierarchy AS (
SELECT group_id FROM user_groups
WHERE group_id = {group_id}
UNION ALL
SELECT g.group_id FROM user_groups g
JOIN GroupHierarchy gh ON g.parent_id = gh.group_id
)
DELETE FROM user_groups
WHERE group_id IN (SELECT group_id FROM GroupHierarchy)
'''
        self.cursor.execute(f"{sql_request}")
        self.connection.commit()


    def get_all_groups(self, project_id):
        self.cursor.execute(f"SELECT * FROM user_groups WHERE project_id = {project_id} AND parent_id = -1")
        return self.cursor.fetchall()
    
    def get_parent_id(self, project_id):
        self.cursor.execute(f"SELECT group_id FROM user_groups WHERE project_id = {project_id} AND group_lvl = 0")
        return self.cursor.fetchall()
    

    def get_group_pictures(self, group_id):
        self.cursor.execute(f"SELECT * FROM pictures WHERE path_to_the_image = 'group' AND identifier = {group_id}")
        return self.cursor.fetchall()
    
    def add_new_group_picture(self, group_id, photo):
        self.cursor.execute(f"INSERT INTO pictures (identifier, path_to_the_image, content_id, content_type) VALUES ({group_id}, 'group', '{photo}', 'photo')")
        self.connection.commit()

    def get_group_picture(self, group_id):
        self.cursor.execute(f"SELECT * FROM pictures WHERE identifier = {group_id} AND path_to_the_image = 'group'")
        return self.cursor.fetchall()
    
    def delete_group_picture(self, picture_id):
        self.cursor.execute(f"DELETE FROM pictures WHERE picture_id = {picture_id}")
        self.connection.commit()
    
    


    

    
# Запросы для раздела товары 

    def check_list_resources(self, project_id):
        self.cursor.execute(f"SELECT * FROM resources WHERE project_id = {project_id}")
        return self.cursor.fetchall()

    def add_product(self, project_id, product_type, reusable, contents, product_price, product_name, product_description, product_photo):
        list_contents = ''
        list_photo = ''

        for content in contents:
            list_contents += '"' + f'{content}' + '"' + ','

        for photo in product_photo:
            list_photo += '"' + f'{photo}' + '"' + ','

        list_contents = '{' + list_contents[:-1] + '}'
        list_photo = '{' + list_photo[:-1] + '}'

        quantity = 0
        if product_type == 'channel':
            quantity = 999999999

        
        sql_request = f'''
INSERT INTO products(
project_id,
product_type,
display_status,
reusable,
contents,
price,
discount,
product_name,
product_description,
product_photo,
quantity
)
VALUES (
{project_id},
'{product_type}',
'включен',
{reusable},
'{list_contents}',
{product_price},
0,
'{product_name}',
'{product_description}',
'{list_photo}',
{quantity}
)
'''
        self.cursor.execute(f"{sql_request}")
        self.connection.commit()

    def get_product_data(self, product_id):
        self.cursor.execute(f"SELECT * FROM products WHERE product_id = {product_id}")
        return self.cursor.fetchall()

    def get_last_product(self, project_id, product_type):
        self.cursor.execute(f"SELECT * FROM products WHERE project_id = {project_id} AND product_type = '{product_type}' ORDER BY product_id DESC LIMIT 1")
        return self.cursor.fetchall()
    
    def get_list_products(self, project_id, product_type):
        self.cursor.execute(f"SELECT * FROM products WHERE project_id = {project_id} AND product_type = '{product_type}' ORDER BY product_id DESC")
        return self.cursor.fetchall()
    
    def update_display_status(self, product_id, status):
        self.cursor.execute(f"UPDATE products SET display_status = '{status}' WHERE product_id = {product_id}")
        self.connection.commit()

    def edit_product(self, product_id, set, new_data):

        if set == ('price' or 'discount' or 'quantity'):
            self.cursor.execute(f"UPDATE products SET {set} = {new_data} WHERE product_id = {product_id}")
            self.connection.commit()
        elif set == ('product_photo' or 'contents'):
            list_contents = ''

            for content in new_data:
                list_contents += '"' + f'{content}' + '"' + ','
            
            list_contents = '{' + list_contents[:-1] + '}'

            self.cursor.execute(f"UPDATE products SET {set} = '{list_contents}' WHERE product_id = {product_id}")
            self.connection.commit()
        else:
            self.cursor.execute(f"UPDATE products SET {set} = '{new_data}' WHERE product_id = {product_id}")
            self.connection.commit()

    def delete_product(self, product_id):
        self.cursor.execute(f"DELETE FROM products WHERE product_id = {product_id}")
        self.connection.commit()

    def get_product_dv_methods(self, project_id):
        self.cursor.execute(f"SELECT product_id, contents, product_name FROM products WHERE project_id = {project_id} AND product_type = 'delivery'")
        return self.cursor.fetchall()
    
    def get_list_pictures(self, product_id):
        self.cursor.execute(f"SELECT * FROM pictures WHERE path_to_the_image = 'products' AND identifier = {product_id} ORDER BY picture_id")
        return self.cursor.fetchall()
    
    def add_new_picture_product(self, product_id, picture_id):
        self.cursor.execute(f"INSERT INTO pictures (identifier, path_to_the_image, content_id, content_type) VALUES ({product_id}, 'products', '{picture_id}', 'photo')")
        self.connection.commit()

    def get_picture_product(self, picture_id):
        self.cursor.execute(f"SELECT * FROM pictures WHERE picture_id = {picture_id}")
        return self.cursor.fetchall()
    
    def delete_picture_product(self, picture_id):
        self.cursor.execute(f"DELETE FROM pictures WHERE picture_id = {picture_id}")
        self.connection.commit()



# Запросы для работы с ресурсами
    def get_list_active_resources(self, product_id):
        self.cursor.execute(f"SELECT contents FROM products WHERE product_id = {product_id}")
        return self.cursor.fetchall()

    def update_resources_product_channel(self, product_id, resources):
        list_resources = ''

        for resource in resources:
            list_resources += '"' + f'{resource}' + '"' + ','

        list_resources = '{' + list_resources[:-1] + '}'

        self.cursor.execute(f"UPDATE products SET contents = '{list_resources}' WHERE product_id = {product_id}")
        self.connection.commit()


# Запросы для работы с контентом товаров

    def add_product_content(self, product_id, content, product_type):
        self.cursor.execute(f"INSERT INTO product_content (product_id, product, product_type) VALUES ({product_id}, '{content}', '{product_type}')")
        self.connection.commit()

    def get_list_product_content(self, product_id):
        self.cursor.execute(f"SELECT * FROM products WHERE product_id = {product_id} ORDER BY product_id")
        return self.cursor.fetchall()
    
    def get_last_product_content(self, product_id):
        self.cursor.execute(f"SELECT content_id FROM product_content WHERE product_id = {product_id} ORDER BY content_id DESC LIMIT 1")
        return self.cursor.fetchall()
    
    def update_list_contents(self, product_id, contents_id, quantity):

        list_contents = ''

        for resource in contents_id:
            list_contents += '"' + f'{resource}' + '"' + ','

        list_contents = '{' + list_contents[:-1] + '}'

        if quantity == 'no':
            self.cursor.execute(f"UPDATE products SET contents = '{list_contents}' WHERE product_id = {product_id}")
        else:
            self.cursor.execute(f"UPDATE products SET contents = '{list_contents}', quantity = {len(contents_id)} WHERE product_id = {product_id}")

        self.connection.commit()

    def get_product_content(self, content_id):
        self.cursor.execute(f"SELECT * FROM product_content WHERE content_id = {content_id} ORDER BY content_id")
        return self.cursor.fetchall()
    
    def delete_content(self, content_id):
        self.cursor.execute(f"DELETE FROM product_content  WHERE content_id = {content_id}")
        self.connection.commit()


# Запросы для работы с методами доставки

    def add_delivery_method(self, project_id, name, description, price):
        self.cursor.execute(f"INSERT INTO delivery_methods (project_id, method_name, method_description, cost_of_delivery, method_status) VALUES ({project_id}, '{name}', '{description}', '{price}', True)")
        self.connection.commit()
    
    def get_last_delivery_method(self, project_id):
        self.cursor.execute(f"SELECT * FROM delivery_methods WHERE project_id = {project_id} ORDER BY method_id DESC LIMIT 1")
        return self.cursor.fetchall()
    
    def get_method_data(self, method_id):
        self.cursor.execute(f"SELECT * FROM delivery_methods WHERE method_id = {method_id}")
        return self.cursor.fetchall()

    
    def get_list_delivery_methods(self, project_id):
        self.cursor.execute(f"SELECT * FROM delivery_methods WHERE project_id = {project_id} ORDER BY method_id DESC")
        return self.cursor.fetchall()
    
    def update_list_method(self, product_id, methods_id):

        list_methods = ''

        for method in methods_id:
            list_methods += '"' + f'{method[0]}' + '"' + ','

        list_methods = '{' + list_methods[:-1] + '}'

        self.cursor.execute(f"UPDATE products SET contents = '{list_methods}' WHERE product_id = {product_id}")
        self.connection.commit()

    def update_list_dv_method(self, product_id, methods_id):

        list_methods = ''

        for method in methods_id:
            list_methods += '"' + f'{method}' + '"' + ','

        list_methods = '{' + list_methods[:-1] + '}'

        self.cursor.execute(f"UPDATE products SET contents = '{list_methods}' WHERE product_id = {product_id}")
        self.connection.commit()
    
    def get_list_active_dv_methods(self, product_id):
        self.cursor.execute(f"SELECT contents FROM products WHERE product_id = {product_id}")
        return self.cursor.fetchall()
    
    def edit_dv_method(self, method_id, set, new_data):

        if set == ('method_name' or 'method_desription'):
            self.cursor.execute(f"UPDATE delivery_methods SET {set} = '{new_data}' WHERE method_id = {method_id}")
            self.connection.commit()
        else:
            self.cursor.execute(f"UPDATE delivery_methods SET {set} = {new_data} WHERE method_id = {method_id}")
            self.connection.commit()

    
    def method_display_status(self, method_id, status):
        self.cursor.execute(f"UPDATE delivery_methods SET method_status = {status} WHERE method_id = {method_id}")
        self.connection.commit()

    def delete_method_dv(self, method_id):
        self.cursor.execute(f"DELETE FROM delivery_methods WHERE method_id = {method_id}")
        self.connection.commit()


# Запросы для раздела ЗАКАЗЫ    

    def get_list_delivery_orders(self, project_id, order_status):
        self.cursor.execute(f"SELECT * FROM delivery_orders WHERE project_id = {project_id} AND order_status = '{order_status}' ORDER BY order_id DESC")
        return self.cursor.fetchall()
    
    def get_order_data(self, order_id):
        self.cursor.execute(f"SELECT * FROM delivery_orders WHERE order_id = {order_id}")
        return self.cursor.fetchall()
    

    def get_user_data(self, project_id, user_id):
        self.cursor.execute(f"SELECT * FROM user_clients WHERE project_id = {project_id} AND user_id = {user_id}")
        return self.cursor.fetchall()
    

    def update_order_status(self, order_id, status):
        self.cursor.execute(f"UPDATE delivery_orders SET order_status = '{status}' WHERE order_id = {order_id}")
        self.connection.commit()

    def update_order_data(self, order_id, what_to_edit, data):
        self.cursor.execute(f"UPDATE delivery_orders SET {what_to_edit} = '{data}' WHERE order_id = {order_id}")
        self.connection.commit()




# Запросы для раздела СПОСОБЫ ОПЛАТЫ

    def get_list_manual_payment_methods(self, project_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE project_id = {project_id} AND method_type = 'manual'")
        return self.cursor.fetchall()
    
    def get_quantity_pay_methods(self, project_id):
        self.cursor.execute(f"SELECT COUNT(method_id) FROM payment_methods WHERE project_id = {project_id}")
        return self.cursor.fetchall()[0][0]
    

    def add_manual_payment_method(self, project_id, method_name, method_description):
        self.cursor.execute(f"INSERT INTO payment_methods (project_id, method_type, method_name, method_description) VALUES ({project_id}, 'manual', '{method_name}', '{method_description}')")
        self.connection.commit()

    
    def get_last_manual_payment_method(self, project_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE project_id = {project_id} AND method_type = 'manual' ORDER BY method_id DESC LIMIT 1")
        return self.cursor.fetchall()
    
    def get_manual_paymetn_method_data(self, method_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE method_id = {method_id}")
        return self.cursor.fetchall()
    
    def update_status_payment_method(self, method_id, method_status):
        self.cursor.execute(f"UPDATE payment_methods SET method_status = {method_status} WHERE method_id = {method_id}")
        self.connection.commit()

    def edit_payment_method(self, method_id, what_to_edit, new_data):
        self.cursor.execute(f"UPDATE payment_methods SET {what_to_edit} = '{new_data}' WHERE method_id = {method_id}")
        self.connection.commit()

    def delete_payment_method(self, method_id):
        self.cursor.execute(f"DELETE FROM payment_methods WHERE method_id = {method_id}")
        self.connection.commit()


    
    def add_auto_payment_method(self, project_id, method_type, method_name, method_description, method_token, method_number):
        self.cursor.execute(f"INSERT INTO payment_methods (project_id, method_type, method_name, method_description, method_token, method_number) VALUES ({project_id}, '{method_type}', '{method_name}', '{method_description}', '{method_token}', '{method_number}')")
        self.connection.commit()

    def get_list_auto_payment_methods(self, project_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE project_id = {project_id} AND method_type != 'manual'")
        return self.cursor.fetchall()
    
    def get_last_auto_payment_method(self, project_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE project_id = {project_id} AND method_type != 'manual' ORDER BY method_id DESC LIMIT 1")
        return self.cursor.fetchall()
    
    def check_auto_method(self, project_id, method_type):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE project_id = {project_id} AND method_type = '{method_type}'")
        return self.cursor.fetchall()
    
    def get_data_auto_payment_method(self, method_id):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE method_id = {method_id}")
        return self.cursor.fetchall()
    
    def check_yoomoney_number(self, yoomoney_number):
        self.cursor.execute(f"SELECT * FROM payment_methods WHERE method_number = '{yoomoney_number}'")
        return self.cursor.fetchall()
    



# Запросы для раздела РАССЫЛКА

    def get_list_users(self, project_id):
        self.cursor.execute(f"SELECT * FROM user_clients WHERE project_id = {project_id} AND job_title != 'Admin'")
        return self.cursor.fetchall()

    def update_status_user_client(self, user_id, status):
        self.cursor.execute(f"UPDATE user_clients SET status_user = {status} WHERE client_id = {user_id}")
        self.connection.commit()

    def get_statistic_newsletter(self, project_id):
        sql_request = f'''
SELECT 
	(SELECT COUNT(client_id) FROM user_clients WHERE status_user = true AND job_title = 'User' AND project_id = {project_id}) AS user_true,
	(SELECT COUNT(client_id) FROM user_clients WHERE status_user = false AND job_title = 'User' AND project_id = {project_id}) AS user_false
FROM user_clients
'''
        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()



# Запросы для раздела СТАТИСТИКА

    def get_products_statistics(self, project_id):
        sql_request = f'''
SELECT product_id, product_name, SUM(product_price) AS total_sum, COUNT(product_id) AS quantity
FROM user_sales
WHERE project_id = {project_id}
GROUP BY product_id, product_name
ORDER BY SUM(product_price)
LIMIT 10
'''

        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()
    

    def get_statistics_on_customers(self, project_id):
        sql_request = f'''
SELECT uc.user_fullname, uc.user_id, uc.user_username, COUNT(sale_id) AS quantity, SUM(product_price) AS total_sum
FROM user_sales us
JOIN user_clients uc ON us.user_id = uc.user_id AND us.project_id = uc.project_id
WHERE us.project_id = {project_id}
GROUP BY uc.user_fullname, uc.user_id, uc.user_username
ORDER BY SUM(product_price)
LIMIT 10
'''

        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()
    

    def get_total_statistics(self, project_id):
        sql_request = f'''
SELECT 
    (SELECT COUNT(*) FROM user_clients WHERE project_id = {project_id} ) AS total_users, -- Общее количество пользователей
    (SELECT COUNT(DISTINCT user_id) FROM user_sales WHERE project_id = {project_id}) AS buyers, -- Количество покупателей
    SUM(product_price) AS total_sales -- Общая сумма продаж
FROM user_sales
WHERE project_id = {project_id}
'''

        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()
    
    def get_statistics_over_time(self, project_id, date):

        sql_request = f'''
SELECT 
    (SELECT COUNT(*) FROM user_clients WHERE project_id = {project_id} AND date_reg = '{date}') AS total_users, -- Количество пользователей за 24 часа
    (SELECT COUNT(DISTINCT user_id) FROM user_sales WHERE project_id = {project_id} AND sale_date = '{date}') AS buyers, -- Количество покупателей за 24 часа
    SUM(product_price) AS total_sales -- Сумма продаж за 24 часа
FROM user_sales
WHERE project_id = {project_id} AND sale_date = '{date}'
'''

        self.cursor.execute(f"{sql_request}")
        return self.cursor.fetchall()




# Запросы с payments_in_processing

    def get_all_processing(self, project_id):
        self.cursor.execute(f"SELECT * FROM payments_in_processing WHERE project_id = {project_id}")
        return self.cursor.fetchall()







# test = Database()

# print(test.get_active_list_products_to_groups(group_id=44))


