import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN ='8975033616:AAGecO3C4IxQYnbcBEFsoo-Hf6aUYKpj1Qk'
GROUP_ID = -1003936925533


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

active_questions = {}
question_counter = 0
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
            "Merhaba! Bu bot üzerinden gruba tamamen anonim sorular gönderebilir "
            "ve gelen anonim cevapları alabilirsin.\n\n"
            "Gruba anonim soru göndermek için /soru komutunu kullanabilirsin."
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
            text=f"#{soru_id} numaralı soruya cevap vermek için lütfen mesajını buraya yaz:"
        )




async def soru_gonder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global question_counter
    chat = update.message.chat
    keyboard = [[InlineKeyboardButton("Cevapla", callback_data=f"cevap_{question_counter}")]]

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
    if chat.type == "private":
        if update.message.text and update.message.text.startswith('/'):
            return
            
        soru_id_str = context.user_data.get("answering_to") or context.user_data.get("answering_to_question")
        if soru_id_str:
            soru_id = int(soru_id_str)
            cevap_metni = update.message.text
            
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=f"#{soru_id} numaralı soruya gelen anonim cevap:\n\n{cevap_metni}"
            )
            
            await update.message.reply_text("Cevabınız anonim olarak gruba iletildi!")
            context.user_data.pop("answering_to", None)
            context.user_data.pop("answering_to_question", None)
            return

        await update.message.reply_text("Gruba anonim soru göndermek için /soru [mesajın] komutunu kullanabilirsin.")

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
async def cevap_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat
    user = update.message.from_user
    
    if chat.type == "private":
        if update.message.text.startswith('/'):
            return
            
        if "answering_to_question" in context.user_data:
            soru_id_str = context.user_data["answering_to_question"]
            if soru_id_str:
                soru_id = int(soru_id_str)
                cevap_metni = update.message.text
                
                try:
                    await context.bot.send_message(
                        chat_id=GROUP_ID,
                        text=f"#{soru_id} numaralı soruya gelen anonim cevap:\n\n{cevap_metni}"
                    )
                    await update.message.reply_text("Cevabınız anonim olarak gruba iletildi!")
                    context.user_data["answering_to_question"] = None
                except Exception:
                    await update.message.reply_text("❌ Cevap gönderilemedi.")
                    context.user_data["answering_to_question"] = None
        else:
            await update.message.reply_text("Gruba anonim soru göndermek için /soru [mesajın] komutunu kullanabilirsin.")
if __name__ == '__main__':
token = TOKEN
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('soru', soru))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cevap_al))

    print("Anonim Soru-Cevap botu çalışıyor...")
    application.run_polling()
