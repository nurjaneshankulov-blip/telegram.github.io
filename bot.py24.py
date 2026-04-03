print("STARTED")
Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
... import asyncio
... import logging
... import sqlite3
... from datetime import datetime
... 
... from aiogram import Bot, Dispatcher, types, F
... from aiogram.filters import CommandStart, Command
... from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
... from aiogram.fsm.context import FSMContext
... from aiogram.fsm.storage.memory import MemoryStorage
... 
... # ================= CONFIG =================
... BOT_TOKEN = "8618074108:AAF5jl5Z_1u2BE5LdZzyFXRD0bPj9QpJks"  
... ADMIN_CHAT_ID =1313252587 
... # ==========================================
... 
... logging.basicConfig(level=logging.INFO)
... 
... bot = Bot(token=BOT_TOKEN)
... dp = Dispatcher(storage=MemoryStorage())
... 
... # ================= DATABASE =================
... conn = sqlite3.connect("bot.db")
... cursor = conn.cursor()
... 
... cursor.execute("""
... CREATE TABLE IF NOT EXISTS orders (
...     id INTEGER PRIMARY KEY AUTOINCREMENT,
...     user_id INTEGER,
...     name TEXT,
...     phone TEXT,
...     description TEXT,
...     budget TEXT,
...     created_at TEXT
... )
""")
conn.commit()

def add_order(user_id, name, phone, desc, budget):
    cursor.execute(
        "INSERT INTO orders (user_id, name, phone, description, budget, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, phone, desc, budget, datetime.now().strftime("%d.%m.%Y %H:%M"))
    )
    conn.commit()

def get_orders():
    return cursor.execute("SELECT * FROM orders").fetchall()

# ================= MENU =================
def menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Zakaz beru")],
            [KeyboardButton(text="Baga"), KeyboardButton(text="Baylanys")]
        ],
        resize_keyboard=True
    )

# ================= START =================
@dp.message(CommandStart())
async def start(msg: types.Message, state: FSMContext):
    await state.clear()

    await msg.answer(
        "Salam! 🤖\n\n"
        "Biz Telegram bot jasaymyz.\n\n"
        "👉 Zakaz beru batyrmasyn basynyz",
        reply_markup=menu()
    )

# ================= ORDER =================
@dp.message(F.text == "Zakaz beru")
async def order_start(msg: types.Message, state: FSMContext):
    await state.set_state("name")
    await msg.answer("Atynyz:", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text, state="name")
async def get_name(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await state.set_state("phone")
    await msg.answer("Telefon nomeriniz:")

@dp.message(F.text, state="phone")
async def get_phone(msg: types.Message, state: FSMContext):
    await state.update_data(phone=msg.text)
    await state.set_state("desc")
    await msg.answer("Qandai bot kerek?")

@dp.message(F.text, state="desc")
async def get_desc(msg: types.Message, state: FSMContext):
    await state.update_data(desc=msg.text)
    await state.set_state("budget")
    await msg.answer("Budget (50k / 120k / 250k):")

@dp.message(F.text, state="budget")
async def finish(msg: types.Message, state: FSMContext):
    data = await state.get_data()

    add_order(
        msg.from_user.id,
        data["name"],
        data["phone"],
        data["desc"],
        msg.text
    )

    # ADMIN-ге жіберу
    text = (
        "📥 JANA ZAKAZ\n\n"
        f"Aty: {data['name']}\n"
        f"Telefon: {data['phone']}\n"
        f"User ID: {msg.from_user.id}\n"
        f"Bot: {data['desc']}\n"
        f"Budget: {msg.text}\n"
    )

    await bot.send_message(ADMIN_CHAT_ID, text)

    await msg.answer(
        "✅ Zakazyngyz qabyldandy!\n\n"
        "Tez arada habarlasamyz.",
        reply_markup=menu()
    )

    await state.clear()

# ================= ADMIN =================
@dp.message(Command("admin"))
async def admin(msg: types.Message):
    if msg.from_user.id != ADMIN_CHAT_ID:
        return

    orders = get_orders()

    if not orders:
        await msg.answer("Zakaz joq")
        return

    text = "Zakazdar:\n\n"

    for o in orders:
        text += (
            f"ID: {o[0]}\n"
            f"Aty: {o[2]}\n"
            f"Tel: {o[3]}\n"
            f"Bot: {o[4]}\n"
            f"Budget: {o[5]}\n"
            f"Waqyt: {o[6]}\n"
            "------\n"
        )

    await msg.answer(text)

# ================= SIMPLE SALES AI =================
@dp.message()
async def simple_ai(msg: types.Message):
    text = msg.text.lower()

    if "баға" in text or "қанша" in text:
        await msg.answer(
            "Baga bottyn murdeliligine baylanysty.\n\n"
            "Kop klientterimiz satysyn 2-3 ese osirdi 🚀\n\n"
            "👉 Zakaz beru batyrmasyn basynyz"
        )
        return

    if "не үшін" in text or "пайда" in text:
        await msg.answer(
            "Bot sizge klient zhogaltpau ushin kerek.\n\n"
            "Ol 24/7 jumys isteydi 🤖\n"
            "Zakazdy avtomat qabyldaydy\n\n"
            "👉 Zakaz beriniz"
        )
        return

    await msg.answer(
        "Suraqtynyzdy tusindim 👍\n\n"
        "Sizge arnap bot jasap bere alamyz.\n\n"
        "👉 Zakaz beru batyrmasyn basynyz"
    )

# ================= RUN =================
async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
