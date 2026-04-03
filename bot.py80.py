import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
  )
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
BOT_TOKEN = "8618074108:AAF5jl5Z_1u2BE5LdZzyFXRD0bPj9QpJks"           
ANTHROPIC_API_KEY = "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"
ADMIN_CHAT_ID = 1313252587                
# ============================================================

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

user_conversations = {}

class OrderState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_description = State()
    waiting_budget = State()
    confirm = State()

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Bot yasatu"), KeyboardButton(text="Baga")],
            [KeyboardButton(text="Mysaldar"),    KeyboardButton(text="Baylanys")],
            [KeyboardButton(text="Suraq qoyu")]
        ],
        resize_keyboard=True
    ),
async def ask_claude(user_id: int, text: str) -> str:
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    user_conversations[user_id].append({"role": "user", "content": text})

    if len(user_conversations[user_id]) > 20:
        user_conversations[user_id] = user_conversations[user_id][-20:]

    system = (
        "Sen - bot jasajtin kompaniyanyn aqyldy assistentisisn. "
        "Tek qazaq tilinde jawap ber. "
        "Klientke bot jasatudyn pajdasyn ajt: 24/7 jumys, shygyndy azajtu, zakazdy avtomatty qabyldau. "
        "Zakas beru ushin /order dep jazw kerek ekenin eskerт. "
        "Jawap 150 sozden aspasyn. Dostyk tonda sojles."
    )
    try:
        resp = claude_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=400,
            system=system,
            messages=user_conversations[user_id]
    )
        answer = resp.content[0].text
        user_conversations[user_id].append({"role": "assistant", "content": answer})
        return answer
    except Exception as e:
        logger.error(f"Claude error: {e}")
        return "Keshiriniz, qazir tehnikaly uzilis. Bizge tikelej jazyngyz: @bot_master_kz"

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    name = message.from_user.first_name or "Qonaq"
    text = (
        f"Salam, {name}!\n\n"
        "Men - bot jasajtin kompaniyanyn AI-assistentimin.\n\n"
        "Ne jasaj alamyn:\n"
        "- Kez-kelgen suraqqa jawap beremyn\n"
        "- Bot jasatu turaly tolyk aqparat beremyn\n"
        "- Zakazynyzdy qabyldajmyn\n\n"
        "Bot nelige pajdaly?\n"
        "- 24/7 jumys jasajdy\n"
        "- Adam ornyna jawap beredi\n"
        "- Zakazdy avtomatty qabyldajdy\n"
        "- Shygyndy 3 ese azajtady"
    )
    await message.answer(text, reply_markup=main_menu())

@dp.message(F.text == "Bot yasatu")
@dp.message(Command("order"))
async def cmd_order(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.waiting_name)
    await message.answer(
        "Zakaz rasimdeу\n\nAtynyzdy jazyngyz:",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(OrderState.waiting_name)
async def step_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Nomerimdi zhiberу", request_contact=True)]],
        resize_keyboard=True
    )
    await state.set_state(OrderState.waiting_phone)
    await message.answer(
        f"Zhaqsy, {message.text}!\n\nTelefon nomiringiz:",
        reply_markup=kb
    )

@dp.message(OrderState.waiting_phone)
async def step_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    await state.set_state(OrderState.waiting_description)
    await message.answer(
        "Qandaj bot kerek?\n(ne ushin, qandaj funkcialar bolsyn)",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(OrderState.waiting_description)
async def step_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(OrderState.waiting_budget)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="50-100k tg",          callback_data="b_50")],
        [InlineKeyboardButton(text="100-200k tg",         callback_data="b_100")],
        [InlineKeyboardButton(text="200k+ tg",            callback_data="b_200")],
        [InlineKeyboardButton(text="Kenes algym keledi",  callback_data="b_consult")]
    ])
    await message.answer("Shamamen budget:", reply_markup=kb)

@dp.callback_query(F.data.startswith("b_"))
async def step_budget(cb: types.CallbackQuery, state: FSMContext):
    budgets = {
        "b_50":      "50 000 - 100 000 tg",
        "b_100":     "100 000 - 200 000 tg",
        "b_200":     "200 000+ tg",
        "b_consult": "Kenes algany keledi"
    }
    budget = budgets.get(cb.data, "Belgisiz")
    await state.update_data(budget=budget)
    data = await state.get_data()

    text = (
        "Zakaz maliwmettери:\n\n"
        f"Aty: {data['name']}\n"
        f"Telefon: {data['phone']}\n"
        f"TapSyrma: {data['description']}\n"
        f"Budget: {budget}\n\n"
        "Zhiberejin be?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ia, zhiber", callback_data="yes"),
        InlineKeyboardButton(text="Zhoq",       callback_data="no")
    ]])
    await cb.message.edit_text(text, reply_markup=kb)
    await state.set_state(OrderState.confirm)
    await cb.answer()

@dp.callback_query(F.data == "yes")
async def order_yes(cb: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    username = cb.from_user.username or "zhoq"
    admin_msg = (
        "ZHANA ZAKAZ\n\n"
        f"Aty: {data['name']}\n"
        f"Telefon: {data['phone']}\n"
        f"Telegram: @{username} (ID: {cb.from_user.id})\n"
        f"Tapсырma: {data['description']}\n"
        f"Budget: {data['budget']}\n"
        f"Waqyt: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    try:
        await bot.send_message(ADMIN_CHAT_ID, admin_msg)
    except Exception as e:
        logger.error(f"Admin notify error: {e}")

    await cb.message.edit_text(
        "Zakazyngyz qabyldandy!\n\n"
        "Menedzher 1-2 sagat ishinde habarlasady.\n"
        "Rakhmet!"
    )
    await state.clear()
    await cb.message.answer("Negizgi mazir:", reply_markup=main_menu())
    await cb.answer()

@dp.callback_query(F.data == "no")
async def order_no(cb: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Zakaz zhojyldy.")
    await cb.message.answer("Mazir:", reply_markup=main_menu())
    await cb.answer()

@dp.message(F.text == "Baga")
@dp.message(Command("price"))
async def cmd_price(message: types.Message):
    text = (
        "Baga тizimi:\n\n"
        "Bazalyk - 50 000 tg\n"
        "  Suraq-zhawap boty, FAQ, 14 kun qoldaw\n\n"
        "Standart - 120 000 tg\n"
        "  AI integraciya, zakaz zhujesi, 30 kun qoldaw\n\n"
        "Premium - 250 000 tg\n"
        "  CRM, tolem zhujesi, 90 kun qoldaw\n\n"
        "Zheke zhoba - bагасы kelisіledi\n\n"
        "Zakaz beru: /order"
    )
    await message.answer(text, reply_markup=main_menu())

@dp.message(F.text == "Mysaldar")
@dp.message(Command("examples"))
async def cmd_examples(message: types.Message):
    text = (
        "Zhasalgan bottar mysaldary:\n\n"
        "Dukan boty - katalog, sebet, tolem\n"
        "Дарiгerhana - kezek alu, eske salu\n"
        "Tamaq zhetkizu - mazir, zakaz, treking\n"
        "Fitnes klub - keste, zhazylu, tolem\n"
        "Sulylyk salony - sheber, waqyt tandaw\n"
        "Onlajn mektep - sabaq, test, kualik\n\n"
        "Zakaz beru: /order"
    )
    await message.answer(text, reply_markup=main_menu())

@dp.message(F.text == "Baylanys")
async def cmd_contact(message: types.Message):
    text = (
        "Bajlanys:\n\n"
        "Telegram: @bot_master_kz\n"
        "WhatsApp: +7 700 000 0000\n"
        "Jumys: 09:00 - 19:00\n\n"
        "Nemese /order arkyly zakaz beringiz!"
    )
    await message.answer(text, reply_markup=main_menu())

@dp.message(F.text == "Suraq qoyu")
async def cmd_ask(message: types.Message):
    await message.answer("Suraqynyzdy zhazyngyz, zhawap beremyn!")

@dp.message()
async def handle_text(message: types.Message, state: FSMContext):
    if await state.get_state():
        return
    if not message.text:
        return

    await bot.send_chat_action(message.chat.id, "typing")
    answer = await ask_claude(message.from_user.id, message.text)
    await message.answer(answer, reply_markup=main_menu())

async def main():
    logger.info("Bot iske qosyluda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
