import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(level=logging.INFO)

CATEGORY, BRAND, MODEL, YEAR, CONDITION, PRICE, COMMENT, PHOTOS = range(8)
user_data = {}
CHANNEL_ID = ''  # Замінити на ваш канал

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Давай створимо твоє оголошення.\nЯке обладнання продаєш? (кайт, дошка, трапеція...)")
    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await update.message.reply_text("Бренд?")
    return BRAND

async def brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['brand'] = update.message.text
    await update.message.reply_text("Модель?")
    return MODEL

async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['model'] = update.message.text
    await update.message.reply_text("Рік виробництва?")
    return YEAR

async def year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['year'] = update.message.text
    await update.message.reply_text("Стан (новий, б/у, як новий...)?")
    return CONDITION

async def condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['condition'] = update.message.text
    await update.message.reply_text("Ціна в євро?")
    return PRICE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    await update.message.reply_text("Коментарі (можеш пропустити, напиши -)")
    return COMMENT

async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['comment'] = update.message.text
    context.user_data['photos'] = []
    await update.message.reply_text("Завантаж до 5 фото. Коли завершиш - напиши /done")
    return PHOTOS

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = context.user_data['photos']
    if len(photos) < 5:
        photos.append(update.message.photo[-1].file_id)
    else:
        await update.message.reply_text("Максимум 5 фото. Напиши /done, щоб продовжити")
    return PHOTOS

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    caption = f"📌 Тип: {data['category']}\n🏷️ Бренд: {data['brand']}\n🔢 Модель: {data['model']}\n📅 Рік: {data['year']}\n⚙️ Стан: {data['condition']}\n💰 Ціна: {data['price']} €\n📝 Коментар: {data['comment']}\n📞 Контакт: @{update.message.from_user.username or 'Немає'}"

    media = [InputMediaPhoto(photo, caption=caption if i == 0 else '') for i, photo in enumerate(data['photos'])]
    await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media)
    await update.message.reply_text("Оголошення опубліковано в каналі!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оголошення скасовано")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token('').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
            BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, brand)],
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, model)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year)],
            CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, condition)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment)],
            PHOTOS: [
                MessageHandler(filters.PHOTO, photo),
                CommandHandler('done', done)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()
