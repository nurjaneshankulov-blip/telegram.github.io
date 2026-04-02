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

# ===== ТОКЕНДЕРДІ .env немесе тікелей қойыңыз =====
BOT_TOKEN = os.getenv("8754227384:AAEUXtTBoOVajScixmGg-ccRV086mUQ5zrw")
OPENAI API_KEY = os.getenv("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"")
ADMIN_CHAT_ID = os.getenv("1313252587")

# ===== Anthropic клиент =====
claude_client = OPENAI.OPENAI (api_key=OPENAI_API_KEY)

# ===== Бот ақпараты =====
BOT_INFO = """
Мен — Бот Шебері компаниясының AI-ассистентімін! 🤖

Біз жасайтын боттар:
• Клиенттермен автоматты сөйлесу
• Заказ қабылдау және өңдеу
• FAQ жауаптары
• Мазмұн жеткізу
• CRM интеграция
• Онлайн дүкен боттары
• Бронь жүйелері

Бот жасату үшін: /order
Баға туралы: /price
Мысалдар: /examples
"""

PRICE_INFO = """
💰 Баға тізімі:

🟢 Базалық — 50,000 тг
• Сұрақ-жауап боты
• FAQ автоматизация
• 1 тіл
• 14 күн техқолдау

🔵 Стандарт — 120,000 тг
• Барлық базалық мүмкіндіктер
• AI интеграция (ChatGPT/Claude)
• Заказ жүйесі
• 2 тіл
• 30 күн техқолдау

🟣 Премиум — 250,000 тг
• Барлық стандарт мүмкіндіктер
• CRM интеграция
• Төлем жүйесі
• 3 тіл
• 90 күн техқолдау
• Безлимитті өзгерістер

📞 Жеке жоба — бағасы кеңеседе
"""

EXAMPLES_INFO = """
✅ Жасалған боттар мысалдары:

🛍️ Дүкен боты
→ Каталог, себет, төлем, жеткізу

🏥 Дәрігерге бронь
→ Кезек алу, еске салу, нәтижелер

🍕 Тамақ жеткізу
→ Мәзір, заказ, жеткізу трекинг

🏋️ Фитнес клуб
→ Кесте, жазылу, төлем

💇 Сұлулық салоны
→ Қызмет таңдау, шебер, уақыт

🎓 Онлайн мектеп
→ Сабақтар, тест

Жасату үшін: /order
"""

# ===== Диалог тарихы (жад) =====
user_conversations = {}

# ===== FSM States =====
class OrderState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_description = State()
    waiting_budget = State()
    confirm = State()

# ===== Негізгі меню =====
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🤖 Бот жасату"), KeyboardButton(text="💰 Баға")],
            [KeyboardButton(text="✅ Мысалдар"), KeyboardButton(text="📞 Байланыс")],
            [KeyboardButton(text="💬 AI Ассистент")]
        ],
        resize_keyboard=True
    )
    return keyboard

# ===== Claude AI жауабы =====
async def get_claude_response(user_id: int, user_message: str) -> str:
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    user_conversations[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Тек соңғы 10 хабарды сақтау (жад үнемдеу)
    if len(user_conversations[user_id]) > 20:
        user_conversations[user_id] = user_conversations[user_id][-20:]
    
    system_prompt = """Сен — «Бот Шебері» компаниясының AI-ассистентісің. 
Компания Telegram, WhatsApp, Instagram боттары жасайды.

Міндеттерің:
1. Клиенттің барлық сұрағына қазақша жане орысша жауап бер
2. Боттың пайдасын айт: уақыт үнемдеу, 24/7 жұмыс, шығын азайту
3. Клиентті бот жасатуға ынталандыр
4. /order командасы арқылы заказ бере алатынын айт
5. Достық, жылы тонда сөйлес
6. Нақты, қысқа жауап бер (200 сөзден аспа)

Компания мүмкіндіктері:
- Telegram, WhatsApp, Instagram боттары
- AI интеграция (ChatGPT, Claude)
- CRM, 1С, Bitrix24 интеграция
- Төлем жүйелері (Kaspi, Click, Payme)
- Бот дамыту және техқолдау

Баға: 50,000 тг-дан бастап
Байланыс: @bot_master_kz"""

    try:
        response = claude_client.messages.create(
            model="claude-opus-4-5",
            max_tokens=500,
            system=system_prompt,
            messages=user_conversations[user_id]
        )
        
        assistant_message = response.content[0].text
        user_conversations[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return "Кешіріңіз, қазір техникалық мәселе бар. Бізге тікелей жазыңыз: @bot_master_kz"

# ===== Bot және Dispatcher =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ===== /start =====
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_name = message.from_user.first_name or "Сізбен"
    
    welcome_text = f"""👋 Сәлем, {user_name}!

Мен — **Бот Шебері** компаниясының ақылды ассистентімін! 🤖

Мен сізге көмектесемін:
✅ Бот жасату туралы толық ақпарат беремін
✅ Кез-келген сұрағыңызға жауап беремін  
✅ Заказыңызды қабылдаймын

Төменгі мәзірді қолданыңыз немесе тікелей сұрағыңызды жазыңыз!

🔥 **Неліктен бот пайдалы?**
→ 24/7 жұмыс жасайды
→ Адам уакытын үнемдейді  
→ Заказды автоматты қабылдайды
→ Клиент қанағатын арттырады"""

    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ===== /order =====
@dp.message(Command("order"))
@dp.message(F.text == "🤖 Бот жасату")
async def cmd_order(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.waiting_name)
    await message.answer(
        "📝 **Заказ рәсімдеу**\n\nСізбен байланысу үшін атыңызды жазыңыз:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

@dp.message(OrderState.waiting_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Нөмерімді жіберу", request_contact=True)]],
        resize_keyboard=True
    )
    await state.set_state(OrderState.waiting_phone)
    await message.answer(
        f"Жақсы, {message.text}! 👍\n\n📱 Телефон нөміріңізді жіберіңіз:",
        reply_markup=phone_keyboard
    )

@dp.message(OrderState.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text
    
    await state.update_data(phone=phone)
    await state.set_state(OrderState.waiting_description)
    await message.answer(
        "🤔 Қандай бот керек?\n\nАйтыңыз: не үшін, қандай функция болуы керек?",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(OrderState.waiting_description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(OrderState.waiting_budget)
    
    budget_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 50-100к тг", callback_data="budget_50")],
        [InlineKeyboardButton(text="🔵 100-200к тг", callback_data="budget_100")],
        [InlineKeyboardButton(text="🟣 200к+ тг", callback_data="budget_200")],
        [InlineKeyboardButton(text="💬 Кеңес алғым келеді", callback_data="budget_consult")]
    ])
    
    await message.answer("💰 Шамамен бюджет:", reply_markup=budget_keyboard)

@dp.callback_query(F.data.startswith("budget_"))
async def process_budget(callback: types.CallbackQuery, state: FSMContext):
    budget_map = {
        "budget_50": "50,000 — 100,000 тг",
        "budget_100": "100,000 — 200,000 тг",
        "budget_200": "200,000+ тг",
        "budget_consult": "Кеңес алғысы келеді"
    }
    
    budget = budget_map.get(callback.data, "Белгісіз")
    await state.update_data(budget=budget)
    
    data = await state.get_data()
    
    confirm_text = f"""📋 **Заказ мәліметтері:**

👤 Аты: {data['name']}
📱 Телефон: {data['phone']}
📝 Тапсырма: {data['description']}
💰 Бюджет: {budget}

Жіберейін бе?"""

    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Иә, жібер", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Жоқ", callback_data="confirm_no")
        ]
    ])
    
    await callback.message.edit_text(confirm_text, reply_markup=confirm_keyboard, parse_mode="Markdown")
    await state.set_state(OrderState.confirm)
    await callback.answer()

@dp.callback_query(F.data == "confirm_yes")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Администраторға хабарлама
    admin_text = f"""🆕 **ЖАҢА ЗАКАЗ**

👤 Клиент: {data['name']}
📱 Телефон: {data['phone']}
🆔 Telegram: @{callback.from_user.username or 'жоқ'} (ID: {callback.from_user.id})
📝 Тапсырма: {data['description']}
💰 Бюджет: {data['budget']}
📅 Уақыт: {datetime.now().strftime('%d.%m.%Y %H:%M')}"""

    try:
        await bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Admin notification error: {e}")
    
    await callback.message.edit_text(
        "✅ **Заказыңыз қабылданды!**\n\n"
        "Менеджеріміз 1-2 сағат ішінде хабарласады.\n\n"
        "Сұрағыңыз болса, жазыңыз! 😊",
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.message.answer("Негізгі мәзір:", reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "confirm_no")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заказ жойылды.")
    await callback.message.answer("Мәзір:", reply_markup=get_main_keyboard())
    await callback.answer()

# ===== Баға =====
@dp.message(Command("price"))
@dp.message(F.text == "💰 Баға")
async def cmd_price(message: types.Message):
    await message.answer(PRICE_INFO, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ===== Мысалдар =====
@dp.message(Command("examples"))
@dp.message(F.text == "✅ Мысалдар")
async def cmd_examples(message: types.Message):
    await message.answer(EXAMPLES_INFO, reply_markup=get_main_keyboard())

# ===== Байланыс =====
@dp.message(F.text == "📞 Байланыс")
async def cmd_contact(message: types.Message):
    await message.answer(
        "📞 **Байланыс:**\n\n"
        "💬 Telegram: @bot_master_kz\n"
        "📱 WhatsApp: +7 700 000 0000\n"
        "📧 Email: info@botmaster.kz\n"
        "🕐 Жұмыс уақыты: 09:00–19:00\n\n"
        "Немесе /order арқылы заказ беріңіз!",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ===== AI Ассистент режимі =====
@dp.message(F.text == "💬 AI Ассистент")
async def cmd_ai_mode(message: types.Message):
    await message.answer(
        "🤖 **AI Ассистент режимі**\n\n"
        "Кез-келген сұрағыңызды жазыңыз!\n"
        "Мен бот жасату, баға, мерзім туралы толық ақпарат беремін.\n\n"
        "_Мәзірге қайту үшін /start_",
        parse_mode="Markdown"
    )

# ===== Барлық басқа хабарлар → Claude AI =====
@dp.message()
async def handle_all_messages(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        return
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    response = await get_claude_response(message.from_user.id, message.text)
    
    await message.answer(response, reply_markup=get_main_keyboard())

# ===== Запуск =====
async def main():
    logger.info("Бот іске қосылуда...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
