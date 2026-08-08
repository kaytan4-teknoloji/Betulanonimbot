import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROUP_ID = -1003936925533
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
active_questions = {}
async def soru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        await update.message.reply_text("Lütfen botu özel mesajda (DM) kullanın.")
        return
    
    if not context.args:
        await update.message.reply_text("Lütfen sorunuzu komutla birlikte yazın. Örnek: /soru Selamlar")
        return
        
    soru_metni = " ".join(context.args)
    soru_id = len(active_questions) + 1
    active_questions[soru_id] = update.message.from_user.id
    
    keyboard = [[InlineKeyboardButton("Cevap Ver", callback_data=f"cevap_{soru_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"Anonim Soru #{soru_id}:\n\n{soru_metni}",
        reply_markup=reply_markup
    )
    await update.message.reply_text(f"Sorunuz anonim olarak gruba iletildi! (Soru ID: #{soru_id})")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text(
            "Merhaba! Bu bot üzerinden gruba anonim soru gönderebilir "
            "ve gelen anonim cevapları alabilirsin.\n"
            "Gruba anonim soru göndermek için /soru [mesajın] komutunu kullanabilirsin."
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("cevap_"):
        soru_id = data.split("_")[1]
        context.user_data["answering_to"] = soru_id
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"#{soru_id} numaralı soruya vermek istediğin cevabı buraya yazabilirsin:"
        )

async def cevap_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat
    if chat.type == "private":
        if update.message.text and update.message.text.startswith('/'):
            return

        soru_id_str = context.user_data.get("answering_to")
        if soru_id_str:
            soru_id = int(soru_id_str)
            cevap_metni = update.message.text

            try:
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=f"#{soru_id} numaralı soruya gelen cevap:\n\n{cevap_metni}"
                )
                await update.message.reply_text("Cevabınız gruba iletildi!")
                context.user_data["answering_to"] = None
            except Exception:
                await update.message.reply_text("Cevap gönderilirken bir hata oluştu.")
                context.user_data["answering_to"] = None
        else:
            await update.message.reply_text("Gruba anonim soru göndermek için /soru [mesajın] komutunu kullanabilirsin.")

if __name__ == '__main__':
    token = TOKEN
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('soru', soru))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cevap_al))

    print("Anonim Soru-Cevap botu çalışıyor...")
    application.run_polling()
