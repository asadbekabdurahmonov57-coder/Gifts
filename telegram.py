import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatMemberStatus
from aiohttp import web

# ================= Настройки =================
BOT_TOKEN = "8838437074:AAHKx-OeRcV0MUBepifw0rh81NsPRAfgsSI"
CHANNEL_ID = "@freedom_gifts_channel"
WEBAPP_URL = "https://webapp-saytingiz-manzili.com"
PORT = int(os.environ.get("PORT", 8080)) # Server bergan port yoki standart 8080
# =============================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🌐 Server uxlab qolmasligi uchun Web-Ping tizimi (Health Check)
async def handle_ping(request):
    return web.Response(text="Я работаю! Бот активен. 🚀", content_type="text/plain")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/ping', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Веб-сервер успешно запущен на порту {PORT}...")

# 🛡️ Проверка подписки на канал
async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        return False

# 🏁 Команда /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    start_args = message.text.split()
    inviter_id = None
    if len(start_args) > 1 and start_args[1].startswith("ref_"):
        inviter_id = start_args[1].replace("ref_", "")

    subscribed = await is_user_subscribed(user_id)
    kb = InlineKeyboardBuilder()
    
    if not subscribed:
        kb.button(text="📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")
        kb.button(text="✅ Проверить подписку", callback_data=f"check_sub_{inviter_id if inviter_id else 'none'}")
        kb.adjust(1)
        
        await message.answer(
            f"Привет, {first_name}! 👋\n\n"
            f"Чтобы открывать бесплатные кейсы и выигрывать TON, вам необходимо подписаться на наш официальный канал!",
            reply_markup=kb.as_markup()
        )
    else:
        web_url = f"{WEBAPP_URL}?start=ref_{inviter_id}" if inviter_id else WEBAPP_URL
        kb.button(text="🧸 Открыть Барабан Удачи 🎡", web_app=types.WebAppInfo(url=web_url))
        kb.adjust(1)
        
        welcome_text = f"Добро пожаловать, {first_name}! 🎉\n\nВы успешно подписаны на канал. Нажмите на кнопку ниже, чтобы запустить игру 👇"
        if inviter_id:
            welcome_text += f"\n\n*(Вы зашли по приглашению друга ID: {inviter_id})*"
            
        await message.answer(welcome_text, parse_mode="Markdown", reply_markup=kb.as_markup())

# 🔄 Обработка кнопки "Проверить подписку"
@dp.callback_query(lambda c: c.data.startswith('check_sub_'))
async def process_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    inviter_id = callback_query.data.replace('check_sub_', '')
    
    subscribed = await is_user_subscribed(user_id)
    
    if subscribed:
        await callback_query.message.delete()
        
        web_url = f"{WEBAPP_URL}?start=ref_{inviter_id}" if inviter_id != 'none' else WEBAPP_URL
        kb = InlineKeyboardBuilder()
        kb.button(text="🧸 Открыть Барабан Удачи 🎡", web_app=types.WebAppInfo(url=web_url))
        
        await callback_query.message.answer(
            f"Поздравляем, {first_name}! ✅ Подписка подтверждена.\n\nТеперь вы можете начать игру 👇",
            reply_markup=kb.as_markup()
        )
    else:
        await callback_query.answer("Вы все еще не подписались на канал! ❌", show_alert=True)

# 🚀 Главная функция запуска
async def main():
    # 1. Запускаем веб-сервер для удержания пинга (Рендер/Хостинг)
    await start_web_server()
    
    # 2. Запускаем самого Telegram бота
    print("Бот успешно запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
