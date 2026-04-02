# 🤖 Telegram Bot — Орнату нұсқаулығы

## Не жасайды бұл бот?
- Клиенттің кез-келген сұрағына Claude AI арқылы қазақша жауап береді
- Бот жасату туралы заказ қабылдайды
- Заказ мәліметтерін администраторға жібереді
- 24/7 жұмыс жасайды

---

## 1. Дайындық

### Python орнату
Python 3.10+ болуы керек:
```
python --version
```

### Файлдарды папкаға салыңыз:
```
bot_folder/
├── bot.py
├── requirements.txt
└── .env
```

---

## 2. Токендерді алу

### Telegram Bot Token:
1. Telegram-да @BotFather-ға жазыңыз
2. /newbot жіберіңіз
3. Бот атын беріңіз
4. TOKEN алыңыз → `BOT_TOKEN`-ге қойыңыз

### Anthropic API Key:
1. https://console.anthropic.com тіркеліңіз
2. API Keys → Create Key
3. Кілтті → `ANTHROPIC_API_KEY`-ге қойыңыз

### Admin Chat ID (сіздің ID):
1. Telegram-да @userinfobot-қа жазыңыз
2. /start жіберіңіз
3. "Your user ID" санын → `ADMIN_CHAT_ID`-ге қойыңыз

---

## 3. .env файлын жасаңыз

`.env.example` файлын `.env` деп қайта атаңыз және толтырыңыз:
```
BOT_TOKEN=7123456789:AAHxxxxxx
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
ADMIN_CHAT_ID=123456789
```

---

## 4. Орнату және іске қосу

```bash
# Кітапханаларды орнату
pip install -r requirements.txt

# Ботты іске қосу
python bot.py
```

Консольда `Бот іске қосылуда...` шықса — бот жұмыс жасап тұр!

---

## 5. Боттың командалары

| Команда | Не жасайды |
|---------|-----------|
| /start | Қарсы алу + мәзір |
| /order | Заказ қабылдау формасы |
| /price | Баға тізімі |
| /examples | Мысалдар |
| Кез-келген мәтін | Claude AI жауабы |

---

## 6. Серверге орналастыру (опционал)

### Railway.app (тегін):
1. https://railway.app тіркеліңіз
2. New Project → Deploy from GitHub
3. .env айнымалыларын қосыңыз
4. Deploy!

### VPS сервер:
```bash
# Screen немесе PM2 арқылы фондық режим
pip install pm2
pm2 start bot.py --interpreter python3
pm2 save
```

---

## Сұрақтар болса:
Бізге жазыңыз: @bot_master_kz
