import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatMemberStatus

# ================= Sozlamalar (O'zgartirishingiz shart) =================
BOT_TOKEN = "8838437074:AAHKx-OeRcV0MUBepifw0rh81NsPRAfgsSI"       # @BotFather bergan token
CHANNEL_ID = "@freedom_gifts_channel"               # Majburiy obuna kanali useri
WEBAPP_URL = "https://webapp-saytingiz-manzili.com"  # index.html yuklangan sayt manzili
# =========================================================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Obunani tekshirish funksiyasi
async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        return False

# /start komandasi
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Referal mantiqini aniqlash
    start_args = message.text.split()
    inviter_id = None
    if len(start_args) > 1 and start_args[1].startswith("ref_"):
        inviter_id = start_args[1].replace("ref_", "")

    subscribed = await is_user_subscribed(user_id)
    kb = InlineKeyboardBuilder()
    
    if not subscribed:
        # Obuna bo'lmagan bo'lsa chiqadigan tugmalar
        kb.button(text="📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")
        kb.button(text="✅ Проверить подписку", callback_data=f"check_sub_{inviter_id if inviter_id else 'none'}")
        kb.adjust(1)
        
        await message.answer(
            f"Привет, {first_name}! 👋\n\n"
            f"Чтобы открывать бесплатные кейсы и выигрывать TON, вам необходимо подписаться на наш официальный канал!",
            reply_markup=kb.as_markup()
        )
    else:
        # Obuna bo'lgan bo'lsa chiqadigan o'yin tugmasi
        web_url = f"{WEBAPP_URL}?start=ref_{inviter_id}" if inviter_id else WEBAPP_URL
        kb.button(text="🧸 Открыть Барабан Удачи 🎡", web_app=types.WebAppInfo(url=web_url))
        kb.adjust(1)
        
        welcome_text = f"Добро пожаловать, {first_name}! 🎉\n\nВы успешно подписаны на канал. Нажмите на кнопку ниже, чтобы запустить игру 👇"
        if inviter_id:
            welcome_text += f"\n\n*(Вы зашли по приглашению друга ID: {inviter_id})*"
            
        await message.answer(welcome_text, parse_mode="Markdown", reply_markup=kb.as_markup())

# "Obunani tekshirish" tugmasi bosilganda
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

# Botni ishga tushirish
async def main():
    print("Бот успешно запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
