from aiohttp import web



from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.webhook.aiohttp_server import (
    TokenBasedRequestHandler,
    setup_application,
)


from Database.User_db import Database
from Handlers.user_handlers import (
    my_purchases_handlers,
    start_handlers,
    showcase_handlers,
    purchase_handlers,
    payment_handlers,
    goods_delivery_handlers,
    deeplink_handlers
)
from Handlers.admin_handlers import (
    ch_products_handlers,
    design_handlers, 
    menu_handlers, 
    groups_handlers,
    newsletter_handlers, 
    payment_methods_handlers, 
    resources_handlers, 
    inf_products_handlers, 
    dv_products_handlers, 
    statistics_handlers
)


from Lib_payment.Payment import check_payment_processing_wallet, check_payment_processing_cryptobot, check_payment_processing_yoomoney



router = Router()
db = Database()

session = AiohttpSession()
app = web.Application()


SERVER_HOST= "0.0.0.0"
SERVER_PORT= 8080

BASE_URL= "https://justmakebot.ru"
MINION_WEBHOOK= "/webhook/minion/{bot_token}"

OTHER_BOTS_URL = f"{BASE_URL}{MINION_WEBHOOK}"
 
 

 
async def feed_multibot() -> None:
        for token in db.get_tokens():
            try:
                minion = Bot(token=token[6], session=session)

                await minion.delete_webhook(drop_pending_updates=True)
                await minion.set_webhook(
                    url=OTHER_BOTS_URL.format(bot_token=token[6]),
                    max_connections=100,
                )

                app.router.add_post(f"/wallet/{token[2]}", check_payment_processing_wallet)
                app.router.add_post(f"/cryptobot/{token[2]}", check_payment_processing_cryptobot)
                app.router.add_post(f"/yoomoney/{token[2]}", check_payment_processing_yoomoney)
            except:
                pass
 
 
def main():
    
    bot_settings = {
        "session": session, 'parse_mode': 'HTML', "disable_web_page_preview": True
    }
    

    minion_dp = Dispatcher()
    minion_dp.startup.register(feed_multibot)

    # роутера для user панели
    minion_dp.include_router(deeplink_handlers.router)
    minion_dp.include_router(my_purchases_handlers.router)
    minion_dp.include_router(start_handlers.router)
    minion_dp.include_router(showcase_handlers.router)
    minion_dp.include_router(purchase_handlers.router)
    minion_dp.include_router(payment_handlers.router)
    minion_dp.include_router(goods_delivery_handlers.router)


    # роутера для админ панели
    minion_dp.include_router(menu_handlers.router)
    minion_dp.include_router(groups_handlers.router)
    minion_dp.include_router(ch_products_handlers.router)
    minion_dp.include_router(resources_handlers.router)
    minion_dp.include_router(design_handlers.router)
    minion_dp.include_router(inf_products_handlers.router)
    minion_dp.include_router(dv_products_handlers.router)
    minion_dp.include_router(payment_methods_handlers.router)
    minion_dp.include_router(newsletter_handlers.router)
    minion_dp.include_router(statistics_handlers.router)
 
 
    TokenBasedRequestHandler(
        dispatcher=minion_dp,
        bot_settings=bot_settings,
    ).register(
        app,
        path=MINION_WEBHOOK
    )

    setup_application(app, minion_dp)

 
    web.run_app(
        app=app,
        host=SERVER_HOST,
        port=SERVER_PORT,
    )


if __name__ == "__main__":
    main()
