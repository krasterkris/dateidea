import os
import random

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

IDEAS = [
    "приготовить ужин",
    "посмотреть фильм дома",
    "покататься на велосипедах",
    "активность дома (лего, раскраски и т.п.)",
    "сходить в кафе",
    "сходить в парк/музей/театр/боулинг",
    "сходить в кино",
]

WAITING_FOR_NAME = 1


def _read_bot_token_from_env_file(env_file_path: str = ".env") -> str:
    if not os.path.exists(env_file_path):
        return ""

    with open(env_file_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            if key.strip() == "BOT_TOKEN":
                return value.strip().strip('"').strip("'")

    return ""


def load_token() -> str:
    token = os.getenv("BOT_TOKEN", "").strip()
    if token:
        return token

    for env_file_path in (".env", ".env.example"):
        token_from_file = _read_bot_token_from_env_file(env_file_path)
        if token_from_file:
            return token_from_file

    raise ValueError(
        "Не найден BOT_TOKEN. Добавь токен в переменную окружения или файл "
        ".env/.env.example в формате: BOT_TOKEN=твой_токен"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    saved_name = context.user_data.get("name")
    if saved_name and update.message:
        idea = random.choice(IDEAS)
        await update.message.reply_text(
            f"С возвращением, {saved_name}! Идея для свидания: {idea}"
        )
        return ConversationHandler.END

    if update.message:
        await update.message.reply_text("Привет! Как тебя зовут?")
    return WAITING_FOR_NAME


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message:
        return WAITING_FOR_NAME

    user_name = update.message.text.strip() or "друг"
    context.user_data["name"] = user_name
    idea = random.choice(IDEAS)
    await update.message.reply_text(f"Приятно познакомиться, {user_name}! Идея для свидания: {idea}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    del context
    if update.message:
        await update.message.reply_text("Окей, отменил. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END


def main() -> None:
    try:
        token = load_token()
    except ValueError as error:
        print(error)
        return

    app = ApplicationBuilder().token(token).build()
    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conversation)
    app.run_polling()


if __name__ == "__main__":
    main()
