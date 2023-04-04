import logging
from aiogram import types
from aiogram.utils.executor import start_webhook
from config import bot, dp, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from db import database, save_message, read_messages, save_chat_mapping, get_sender_id

YOUR_CHAT_ID = -1001915443747

async def on_startup(dispatcher):
    await database.connect()
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(dispatcher):
    await database.disconnect()
    await bot.delete_webhook()

@dp.message_handler()
async def handle_message(message: types.Message):
    if message.chat.id == YOUR_CHAT_ID and message.reply_to_message:
        sender_id = await get_sender_id(message.reply_to_message.message_id)
        if sender_id:
            await bot.send_message(chat_id=sender_id, text=message.text)
    elif message.chat.id != YOUR_CHAT_ID:
        forwarded_message = await message.forward(chat_id=YOUR_CHAT_ID)
        await save_chat_mapping(forwarded_message.message_id, message.from_user.id)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
