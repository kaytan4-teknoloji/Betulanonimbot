import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN ='8975033616:AAGUU0e3t4rwkPXbz4np1NqVGF9fgbNZOss'
GROUP_ID = -1003936925533


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

active_questions = {}
question_counter = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text(
            "Merhaba! Bu bot üzerinden gruba tamamen anonim sorular gönderebilir "
            "ve gelen anonim cevapları alabilirsin.\n\n"
            "Gruba anonim soru göndermek için /soru komutunu kullanabilirsin."
        )
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def soru_gonder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global question_counter
    chat = update.message.chat
    keyboard = [[InlineKeyboardButton("Cevapla", callback_data="cevapla")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if chat.type == "private":
        text_args = context.args
        if not text_args:
            await update.message.reply_text("Lütfen sorunu komutla birlikte yaz. Örnek: /soru Bugün hava nasıl?")
            return
            
        soru_metni = " ".join(text_args)
        question_counter += 1
        soru_id = question_counter
        
        active_questions[soru_id] = {
            "author": update.message.from_user.id,
            "text": soru_metni
        }
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"Anonim Soru:\n\n{soru_metni}",
        reply_markup=reply_markup
    )
    
    await update.message.reply_text("✅ Anonim sorunuz gruba iletildi!")

    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("cevap_"):
        soru_id = int(data.split("_")[1])
        context.user_data["answering_to_question"] = soru_id
        await query.message.reply_text(
            "✏️ Bu soruya vermek istediğin **anonim cevabı** şimdi buraya yazıp gönder. "
            "Cevabın soru sahibine tamamen gizli olarak iletilecektir."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat
    user = update.message.from_user

    if chat.type == "private":
        if update.message.text.startswith('/'):
            return

        if "answering_to_question" in context.user_data:
            soru_id = context.user_data["answering_to_question"]
            cevap_metni = update.message.text
            
            soru_bilgisi = active_questions.get(soru_id)
            if soru_bilgisi:
                soru_sahibi_id = soru_bilgisi["author"]
                
                try:
                    await context.bot.send_message(
                        chat_id=soru_sahibi_id,
                        text=f"📩 **#{soru_id} Numaralı Sorunuza Anonim Cevap Geldi:**\n\n{cevap_metni}"
                    )
                    await update.message.reply_text("✅ Cevabınız soru sahibine anonim olarak iletildi!")
                except Exception:
                    await update.message.reply_text("❌ Cevap gönderilemedi.")
            
            del context.user_data["answering_to_question"]
        else:
            await update.message.reply_text("Gruba anonim soru göndermek için /soru [mesajın] komutunu kullanabilirsin.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('soru', soru_gonder))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Anonim Soru-Cevap botu çalışıyor...")
    application.run_polling()
