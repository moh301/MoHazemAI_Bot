import os
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# بنجيب المفاتيح السرية من الـ environment variables (مش مكتوبة هنا مباشرة، للأمان)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Render بيديها تلقائيًا لأي Web Service شغال عندها
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

# Render بيحدد رقم البورت المسموح بيه تلقائيًا في متغير اسمه PORT
PORT = int(os.environ.get("PORT", 5000))

# بننشئ عميل Groq
groq_client = Groq(api_key=GROQ_API_KEY)


# دالة هتتنفذ تلقائيًا كل ما حد يبعت رسالة للبوت
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بناخد نص الرسالة اللي بعتها المستخدم على تليجرام
    user_text = update.message.text

    # بنبعت نص الرسالة لـ Groq ونستنى الرد
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "user", "content": user_text}
        ]
    )

    # بناخد رد الموديل كنص
    reply_text = response.choices[0].message.content

    # بنبعت الرد ده للمستخدم تاني على تليجرام
    await update.message.reply_text(reply_text)


# بننشئ التطبيق اللي هيدير البوت
app = Application.builder().token(TELEGRAM_TOKEN).build()

# بنقول للتطبيق: أي رسالة نصية توصل، شغّل دالة handle_message عليها
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# بدل ما نسأل تليجرام باستمرار (polling)، بنقوله: "ابعتلي على اللينك ده لما توصل رسالة" (webhook)
# ده اللي بيخلي الكود يشتغل كـ "Web Service" مجاني بدل Background Worker المدفوع
print("البوت شغال بنظام Webhook...")
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TELEGRAM_TOKEN,
    webhook_url=f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}"
)
