import asyncio
import random
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import database  # Sizning database.py faylingiz

TOKEN = "YOUR_TOKEN_HERE"
ADMIN_ID = ADMIN_ID  # Sizning Telegram ID'ingiz

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Tugmalarni yaratish
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/arise"), KeyboardButton(text="/myprofile")],
        [KeyboardButton(text="/spendcoins"), KeyboardButton(text="/leaderboard")],
        [KeyboardButton(text="/stats"), KeyboardButton(text="/help")]
    ],
    resize_keyboard=True
)

lang_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ]
)

async def get_user_language(user_id: int):
    database.get_user(user_id)  # foydalanuvchi yo‘q bo‘lsa yaratadi
    return database.get_language(user_id)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    lang = await get_user_language(message.from_user.id)
    text = texts["start"][lang]
    await message.answer(text, reply_markup=main_keyboard)

@dp.callback_query(lambda c: c.data and c.data.startswith("lang_"))
async def callback_lang_change(callback_query: types.CallbackQuery):
    new_lang = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    database.update_language(user_id, new_lang)
    await callback_query.message.edit_text(
        texts["lang_set"][new_lang] + texts["lang_now"][new_lang] + new_lang,
        reply_markup=None
    )
    await callback_query.answer("Til o‘zgartirildi.")

@dp.message(Command(commands=["ban"]))
async def cmd_ban(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("Bu buyruq guruhlarda ishlaydi.")
        return

    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizda guruhni boshqarish huquqi yo'q.")
        return

    if not message.reply_to_message:
        await message.answer("Iltimos, banlash uchun foydalanuvchini javob sifatida tanlang.")
        return

    user_to_ban = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_to_ban)
        await message.answer(f"Foydalanuvchi {user_to_ban} guruhdan banlandi.")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

@dp.message(Command(commands=["arise"]))
async def cmd_arise(message: Message):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)

    if not database.can_use_arise(user_id):
        last_arise_str = database.get_last_arise(user_id)
        last_arise = datetime.fromisoformat(last_arise_str)
        diff = timedelta(hours=24) - (datetime.now() - last_arise)
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes = remainder // 60
        await message.answer(texts["arise_wait"][lang].format(hours=hours, minutes=minutes))
        return

    bonus = random.randint(1, 10)
    database.use_arise(user_id, bonus)
    await message.answer(texts["arise_power"][lang].format(bonus=bonus))

@dp.message(Command(commands=["myprofile"]))
async def cmd_myprofile(message: Message):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    profile = database.get_profile(user_id)

    text = texts["profile"][lang].format(power=profile["power"], coins=profile["coins"])
    await message.answer(text)

@dp.message(Command(commands=["spendcoins"]))
async def cmd_spendcoins(message: Message):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Qo‘llanishi: /spendcoins <miqdor>")
        return

    try:
        amount = int(args[1])
    except ValueError:
        await message.answer("Iltimos, to‘g‘ri raqam kiriting.")
        return

    success = database.spend_coins(user_id, amount)
    if success:
        await message.answer(f"{amount} MAARISE koin sarflandi.")
    else:
        await message.answer("Yetarli MAARISE koiningiz yo‘q.")

@dp.message(Command(commands=["leaderboard"]))
async def cmd_leaderboard(message: Message):
    lang = await get_user_language(message.from_user.id)
    top_users = database.get_top_users()

    if not top_users:
        await message.answer("Hali hech kim reytingda yo‘q.")
        return

    lines = []
    for i, (user_id, power, coins) in enumerate(top_users, start=1):
        profile = database.get_profile(user_id)
        full_name = profile.get("full_name") or f"Foydalanuvchi {user_id}"
        lines.append(
            f"{i}. <a href='tg://user?id={user_id}'>{full_name}</a>\n"
            f"   💪 Kuch: <b>{power}</b>\n"
            f"   🪙 MAARISE: <b>{coins}</b>"
        )

    text = "\n".join(lines)
    await message.answer(text, parse_mode="HTML")

@dp.message(Command(commands=["stats"]))
async def cmd_stats(message: Message):
    lang = await get_user_language(message.from_user.id)
    total_users = database.get_total_users()
    total_arise = database.get_total_arises()

    await message.answer(
        f"📊 Statistikalar:\n"
        f"Foydalanuvchilar soni: {total_users}\n"
        f"Kuch oshirishlar soni: {total_arise}",
        reply_markup=main_keyboard
    )

async def main():
    database.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
