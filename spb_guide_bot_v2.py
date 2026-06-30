"""
Telegram-бот для воронки продаж гайда «Куда бы я пошла, если бы только переехала в Петербург»
Версия 2 — упрощённая логика без ConversationHandler
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN   = "8874441025:AAEAwTWU8J8LaUTf78fKqn1StUnrH1O30Ec"
PAYMENT_URL = "https://t.me/Masha_Mich"
GUIDE_PRICE = "790 ₽"
AUTHOR_NAME = "Мария"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── ПОДБОРКИ ПО ОТВЕТАМ ──────────────────────────────────

def get_places(q1, q2, q3):
    if q3 == "intro":
        if q2 == "places":
            return ["📚 *Подписные издания* — лучший книжный для тихого утра в одиночестве",
                    "🌿 *Юсуповский сад* — найди место на газоне и почувствуй что город принял тебя",
                    "🎬 *Кинотеатр Аврора* — исторический кинотеатр, идеально прийти одному"]
        elif q2 == "people":
            return ["📖 *Книжный клуб «Не дочитал»* — близкие по духу без давления «надо познакомиться»",
                    "🎨 *Скетч-прогулки* — знакомишься через совместное действие",
                    "📚 *Библиотека Маяковского* — клубы и лекции, уютно и по-своему"]
        else:
            return ["📚 *Подписные издания* — здесь бывают встречи с авторами и читательские клубы",
                    "🌿 *Юсуповский сад* — иногда достаточно выйти и дать городу познакомить тебя с ним",
                    "🎨 *Скетч-прогулки* — тихое творчество и новые знакомые без лишнего шума"]
    else:
        if q2 == "places":
            return ["🏝 *Новая Голландия* — арт-остров где всегда что-то происходит",
                    "⚡ *Севкабель Порт* — маркеты, концерты, живая атмосфера у залива",
                    "🍽 *Вокзал 1853* — фудмолл на любой вкус, идеально для первого вечера"]
        elif q2 == "people":
            return ["🤝 *Right People* — нетворкинг-мероприятия, билеты разлетаются быстро",
                    "🏃 *Беговые клубы* — сообщество любителей, вход очень простой",
                    "🏝 *Новая Голландия* — маркеты и ивенты где легко знакомиться"]
        else:
            return ["🏝 *Новая Голландия* — пространство где встречаются интересные люди и классные места",
                    "🤝 *Right People* — живой нетворкинг с петербуржцами",
                    "⚡ *Севкабель Порт* — летом здесь можно провести весь день и познакомиться с кем угодно"]

# ─── ТЕКСТЫ ───────────────────────────────────────────────

WELCOME = f"""👋 Привет! Меня зовут {AUTHOR_NAME}.

Я переехала в Петербург подростком — без знакомых, без ориентиров. За 13 лет нашла здесь дом, любимые места и своих людей.

Теперь я собрала всё это в гайд — *проверенные места, советы по адаптации и подсказки где найти своих*.

Ответь на 3 вопроса — и я пришлю тебе *персональную подборку* мест с которых стоит начать 👇"""

FREE_FRAGMENT = """🎁 *Фрагмент из гайда — как пережить первые недели:*

→ *Обустрой пространство* — сначала кухня и ванная, быстрый доступ к привычным вещам снижает тревогу

→ *Найди свой якорь* — любимая кружка, фото, открытка с тёплым воспоминанием

→ *Выходи без цели* — веди блокнот что нравится, что нет. Это учит замечать город

→ *Разговаривай с людьми* — сосед в лифте, бариста, кассир. Люди любят быть нужными

→ *Дай себе время* — адаптация занимает от полугода до года. Это норма

_Иногда нужно заблудиться, чтобы найтись._"""

GUIDE_CONTENTS = f"""📖 *Что внутри полного гайда:*

01 · Эмоциональная адаптация — первые шаги
02 · Культурные места — 30+ адресов с личными комментариями
03 · Гастрономия — кафе и рестораны на любой бюджет
04 · Природа Ленобласти — куда выбраться за город
05 · Где найти своих — клубы, сообщества, места
06 · Типичные ошибки — что я хотела бы знать раньше
07 · Вопросы для рефлексии

📄 Формат: PDF-гайд + чек-лист первого месяца
💛 Цена: *{GUIDE_PRICE}*"""

# ─── ОБРАБОТЧИКИ ──────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    kb = [[InlineKeyboardButton("Начать →", callback_data="quiz_start")]]
    await update.message.reply_text(WELCOME, parse_mode="Markdown",
                                    reply_markup=InlineKeyboardMarkup(kb))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "quiz_start":
        kb = [
            [InlineKeyboardButton("Только что (до месяца)", callback_data="q1_soon")],
            [InlineKeyboardButton("Недавно (1–6 месяцев)",  callback_data="q1_recent")],
            [InlineKeyboardButton("Пока только планирую",   callback_data="q1_plan")],
        ]
        await query.edit_message_text("*Вопрос 1 из 3*\n\nКогда ты переехал(а) в Петербург?",
                                      parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("q1_"):
        context.user_data["q1"] = data.replace("q1_", "")
        kb = [
            [InlineKeyboardButton("Найти любимые места",           callback_data="q2_places")],
            [InlineKeyboardButton("Познакомиться с людьми",        callback_data="q2_people")],
            [InlineKeyboardButton("И то, и другое",                callback_data="q2_both")],
        ]
        await query.edit_message_text("*Вопрос 2 из 3*\n\nЧто тебе сейчас важнее всего?",
                                      parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("q2_"):
        context.user_data["q2"] = data.replace("q2_", "")
        kb = [
            [InlineKeyboardButton("Интроверт — люблю тишину",     callback_data="q3_intro")],
            [InlineKeyboardButton("Экстраверт — хочу компанию",   callback_data="q3_extro")],
            [InlineKeyboardButton("Зависит от настроения",        callback_data="q3_intro")],
        ]
        await query.edit_message_text("*Вопрос 3 из 3*\n\nКакой ты человек?",
                                      parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("q3_"):
        context.user_data["q3"] = data.replace("q3_", "")
        q1 = context.user_data.get("q1", "soon")
        q2 = context.user_data.get("q2", "both")
        q3 = context.user_data.get("q3", "intro")
        places = get_places(q1, q2, q3)
        places_text = "\n".join(places)
        msg = f"""✨ *Специально для тебя — 3 места с которых стоит начать:*

{places_text}

Это только малая часть гайда. В полной версии — *30+ мест* с личными комментариями, раздел про адаптацию и чек-лист первого месяца."""
        kb = [
            [InlineKeyboardButton("🎁 Получить бесплатный фрагмент", callback_data="free")],
            [InlineKeyboardButton(f"📖 Купить гайд — {GUIDE_PRICE}", url=PAYMENT_URL)],
        ]
        await query.edit_message_text(msg, parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(kb))

    elif data == "free":
        kb = [
            [InlineKeyboardButton(f"📖 Купить гайд — {GUIDE_PRICE}", url=PAYMENT_URL)],
            [InlineKeyboardButton("❓ Что внутри?", callback_data="inside")],
        ]
        await query.edit_message_text(FREE_FRAGMENT, parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(kb))

    elif data == "inside":
        kb = [
            [InlineKeyboardButton(f"✅ Купить гайд — {GUIDE_PRICE}", url=PAYMENT_URL)],
            [InlineKeyboardButton("🎁 Получить фрагмент",            callback_data="free")],
        ]
        await query.edit_message_text(GUIDE_CONTENTS, parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(kb))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("Пройти квиз", callback_data="quiz_start")]]
    await update.message.reply_text("Напиши /start чтобы начать квиз 👇",
                                    reply_markup=InlineKeyboardMarkup(kb))

# ─── ЗАПУСК ───────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_cmd))
    app.add_handler(CallbackQueryHandler(handle_callback))
    logger.info("Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
