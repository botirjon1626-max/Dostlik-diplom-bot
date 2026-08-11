import os
import random
import uuid

from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "Dostlaruchundiplom_bot "

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi!")

QUESTIONS = [
    "🎂 Tug‘ilgan yilingiz nechanchi?",
    "🎨 Sevimli rangingiz qaysi?",
    "🍕 Sevimli taomingiz nima?",
    "🐶 Sevimli hayvoningiz qaysi?",
    "🎮 Sevimli o‘yiningiz qaysi?",
    "⚽ Qaysi sport turini yoqtirasiz?",
    "🌞 Sevimli faslingiz qaysi?",
    "🎬 Kino yoki serial ko‘rishni yoqtirasizmi?",
    "🎵 Sevimli musiqangiz yoki qo‘shiqchingiz kim?",
    "💭 Eng katta orzuingiz nima?"
]

TOTAL = 10
NAME, ANSWER = 1, 2
tests = {}


def friend_question(q):
    d = {
        QUESTIONS[0]: "Do‘stingizning tug‘ilgan yili nechanchi?",
        QUESTIONS[1]: "Do‘stingizning sevimli rangi qaysi?",
        QUESTIONS[2]: "Do‘stingizning sevimli taomi nima?",
        QUESTIONS[3]: "Do‘stingizning sevimli hayvoni qaysi?",
        QUESTIONS[4]: "Do‘stingizning sevimli o‘yini qaysi?",
        QUESTIONS[5]: "Do‘stingiz qaysi sport turini yoqtiradi?",
        QUESTIONS[6]: "Do‘stingizning sevimli fasli qaysi?",
        QUESTIONS[7]: "Do‘stingiz kino yoki serial ko‘rishni yoqtiradimi?",
        QUESTIONS[8]: "Do‘stingizning sevimli musiqasi yoki qo‘shiqchisi kim?",
        QUESTIONS[9]: "Do‘stingizning eng katta orzusi nima?"
    }
    return d[q]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    if context.args:
        test_id = context.args[0]

        if test_id not in tests:
            await update.message.reply_text("❌ Bu test topilmadi.")
            return ConversationHandler.END

        test = tests[test_id]

        if update.effective_user.id == test["owner_id"]:
            await update.message.reply_text(
                "😄 Bu siz yaratgan test!\n"
                "🔗 Linkni do‘stingizga yuboring."
            )
            return ConversationHandler.END

        context.user_data["test_id"] = test_id
        context.user_data["question_index"] = 0
        context.user_data["score"] = 0

        await update.message.reply_text(
            f"🎓 {test['owner_name']} siz haqingizda test yaratdi!\n\n"
            "📝 10 ta savol\n"
            "🔘 Har birida 3 ta variant\n\n"
            "🚀 Boshladik!"
        )

        await send_friend_question(update, context)
        return ConversationHandler.END

    await update.message.reply_text(
        "🎓 DO‘STLIK DIPLOMI\n\n"
        "Men sizdan 10 ta savol so‘rayman.\n"
        "Siz javoblarni yozasiz.\n\n"
        "Keyin do‘stingiz siz haqingizda test ishlaydi.\n"
        "🏆 Oxirida diplom rasmi chiqadi!\n\n"
        "Ismingizni yozing:"
    )

    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()

    context.user_data["name"] = name
    context.user_data["answers"] = []
    context.user_data["index"] = 0

    await update.message.reply_text(
        f"❓ 1/{TOTAL}\n\n"
        f"{QUESTIONS[0]}\n\n"
        "✍️ Javobingizni yozing:"
    )

    return ANSWER


async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text.strip()

    if not answer:
        return ANSWER

    index = context.user_data["index"]
    context.user_data["answers"].append(answer)

    if index + 1 == TOTAL:
        test_id = uuid.uuid4().hex[:12]

        tests[test_id] = {
            "owner_id": update.effective_user.id,
            "owner_name": context.user_data["name"],
            "answers": context.user_data["answers"].copy()
        }

        link = f"https://t.me/{BOT_USERNAME}?start={test_id}"

        share = f"https://t.me/share/url?url={link}"

        await update.message.reply_text(
            "🎉 TEST TAYYOR!\n\n"
            f"🔗 {link}\n\n"
            "Do‘stingiz shu link orqali testni ishlaydi.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📤 DO‘STGA YUBORISH",
                    url=share
                )]
            ])
        )

        return ConversationHandler.END

    context.user_data["index"] += 1
    i = context.user_data["index"]

    await update.message.reply_text(
        f"❓ {i + 1}/{TOTAL}\n\n"
        f"{QUESTIONS[i]}\n\n"
        "✍️ Javobingizni yozing:"
    )

    return ANSWER


def make_options(index, correct):

    if index == 0:
        try:
            year = int(correct)
            pool = [
                correct,
                str(year - 1),
                str(year + 1)
            ]
        except:
            pool = [correct, "2011", "2013"]

    elif index == 1:
        pool = ["Qizil", "Ko‘k", "Yashil", "Sariq", "Qora", "Oq"]

    elif index == 2:
        pool = ["Osh", "Pizza", "Burger", "Lavash", "Somsa", "Manti"]

    elif index == 3:
        pool = ["Mushuk", "It", "Quyon", "Ot", "Sher"]

    elif index == 4:
        pool = ["Roblox", "Minecraft", "PUBG", "Free Fire", "Brawl Stars"]

    elif index == 5:
        pool = ["Futbol", "Basketbol", "Tennis", "Voleybol"]

    elif index == 6:
        pool = ["Bahor", "Yoz", "Kuz", "Qish"]

    elif index == 7:
        pool = ["Ha", "Yo‘q", "Ba’zan"]

    elif index == 8:
        pool = ["Pop", "Rap", "Klassik", "Rock", "Milliy musiqa"]

    else:
        pool = [
            "Sayohat qilish",
            "Mashhur bo‘lish",
            "Yaxshi kasb egallash",
            "Katta biznes qilish"
        ]

    other = [
        x for x in pool
        if x.casefold() != correct.casefold()
    ]

    random.shuffle(other)

    result = [correct] + other[:2]
    random.shuffle(result)

    return result


async def send_friend_question(update, context):

    test = tests[context.user_data["test_id"]]

    i = context.user_data["question_index"]

    correct = test["answers"][i]

    options = make_options(i, correct)

    context.user_data["options"] = options

    keyboard = []

    for n, option in enumerate(options):
        keyboard.append([
            InlineKeyboardButton(
                option,
                callback_data=f"answer|{i}|{n}"
            )
        ])

    await update.message.reply_text(
        f"❓ {i + 1}/{TOTAL}\n\n"
        f"{friend_question(QUESTIONS[i])}\n\n"
        "👇 Variantni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def friend_answer(update, context):

    query = update.callback_query
    await query.answer()

    _, i, selected = query.data.split("|")

    i = int(i)
    selected = int(selected)

    test = tests[context.user_data["test_id"]]

    options = context.user_data["options"]

    correct = test["answers"][i]

    if options[selected].casefold() == correct.casefold():
        context.user_data["score"] += 1
        await query.message.reply_text("✅ To‘g‘ri!")
    else:
        await query.message.reply_text("❌ Noto‘g‘ri!")

    context.user_data["question_index"] += 1

    if context.user_data["question_index"] >= TOTAL:
        await finish(update, context)
    else:
        await next_question(update, context)


async def next_question(update, context):

    test = tests[context.user_data["test_id"]]

    i = context.user_data["question_index"]

    correct = test["answers"][i]

    options = make_options(i, correct)

    context.user_data["options"] = options

    keyboard = []

    for n, option in enumerate(options):
        keyboard.append([
            InlineKeyboardButton(
                option,
                callback_data=f"answer|{i}|{n}"
            )
        ])

    await update.callback_query.message.reply_text(
        f"❓ {i + 1}/{TOTAL}\n\n"
        f"{friend_question(QUESTIONS[i])}\n\n"
        "👇 Variantni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def create_diploma(owner, friend, score):

    percent = score * 10

    image = Image.new(
        "RGB",
        (1400, 900),
        "white"
    )

    draw = ImageDraw.Draw(image)

    font_path = (
        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSerif-Bold.ttf"
    )

    if os.path.exists(font_path):
        title = ImageFont.truetype(font_path, 100)
        name = ImageFont.truetype(font_path, 55)
        big = ImageFont.truetype(font_path, 110)
        normal = ImageFont.truetype(font_path, 40)
    else:
        title = name = big = normal = ImageFont.load_default()

    draw.rectangle(
        (25, 25, 1375, 875),
        outline="gold",
        width=15
    )

    draw.rectangle(
        (50, 50, 1350, 850),
        outline="navy",
        width=5
    )

    def center(text, y, font, fill):

        box = draw.textbbox(
            (0, 0),
            text,
            font=font
        )

        w = box[2] - box[0]

        draw.text(
            ((1400 - w) / 2, y),
            text,
            font=font,
            fill=fill
        )

    center(
        "DO‘STLIK DIPLOMI",
        90,
        title,
        "navy"
    )

    draw.text(
        (150, 280),
        f"F.I.Sh.: {owner}",
        font=name,
        fill="black"
    )

    draw.text(
        (150, 370),
        f"Do‘sti: {friend}",
        font=name,
        fill="black"
    )

    center(
        f"{percent}%",
        480,
        big,
        "green"
    )

    center(
        f"10 ta savoldan {score} tasi to‘g‘ri",
        650,
        normal,
        "black"
    )

    center(
        "DO‘STLIK TESTI",
        750,
        normal,
        "navy"
    )

    filename = f"diplom_{uuid.uuid4().hex}.png"

    image.save(filename)

    return filename


async def finish(update, context):

    test = tests[context.user_data["test_id"]]

    score = context.user_data["score"]

    percent = score * 10

    owner_id = test["owner_id"]
    owner_name = test["owner_name"]

    friend = update.effective_user
    friend_name = friend.first_name or "Do‘stingiz"

    text = (
        "🎓 DO‘STLIK TESTI NATIJASI\n\n"
        f"👤 Do‘stingiz: {owner_name}\n"
        f"🤝 Test ishlagan: {friend_name}\n\n"
        f"✅ To‘g‘ri: {score}/{TOTAL}\n"
        f"📊 Natija: {percent}%"
    )

    await update.callback_query.message.reply_text(text)

    filename = create_diploma(
        owner_name,
        friend_name,
        score
    )

    try:

        with open(filename, "rb") as photo:
            await context.bot.send_photo(
                chat_id=friend.id,
                photo=photo,
                caption=f"🏆 DO‘STLIK DIPLOMI\n📊 {percent}%"
            )

        await context.bot.send_message(
            chat_id=owner_id,
            text=text
        )

        with open(filename, "rb") as photo:
            await context.bot.send_photo(
                chat_id=owner_id,
                photo=photo,
                caption=f"🏆 DO‘STLIK DIPLOMI\n📊 {percent}%"
            )

    finally:

        if os.path.exists(filename):
            os.remove(filename)


async def cancel(update, context):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Bekor qilindi."
    )

    return ConversationHandler.END


async def error_handler(update, context):

    print(
        "BOT XATOSI:",
        repr(context.error)
    )


def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    conversation = ConversationHandler(

        entry_points=[
            CommandHandler(
                "start",
                start
            )
        ],

        states={

            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name
                )
            ],

            ANSWER: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_answer
                )
            ]

        },

        fallbacks=[
            CommandHandler(
                "cancel",
                cancel
            )
        ]
    )

    app.add_handler(conversation)

    app.add_handler(
        CallbackQueryHandler(
            friend_answer,
            pattern=r"^answer\|"
        )
    )

    app.add_error_handler(
        error_handler
    )

    print(
        "🎓 DOSTLIK DIPLOM BOT ISHGA TUSHDI!"
    )

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
