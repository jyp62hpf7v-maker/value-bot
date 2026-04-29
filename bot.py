import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DAILY_RISK = 2000

def implied_prob(odd):
    return 1 / odd

def value_score(my_prob, odd):
    return (my_prob * odd) - 1

def stake_amount(v):
    if v >= 0.15:
        return DAILY_RISK * 0.35
    if v >= 0.08:
        return DAILY_RISK * 0.25
    if v >= 0.03:
        return DAILY_RISK * 0.15
    return 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot aktif ✅\n\n"
        "Kullanım:\n"
        "/value maç_adı oran tahmin_yüzde\n\n"
        "Örnek:\n"
        "/value Braga-KGVar 1.63 68"
    )

async def value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mac = context.args[0]
        oran = float(context.args[1])
        tahmin = float(context.args[2]) / 100

        piyasa = implied_prob(oran)
        v = value_score(tahmin, oran)
        stake = stake_amount(v)

        karar = "✅ OYNANABİLİR" if stake > 0 else "❌ OYNAMA"

        msg = (
            f"📊 VALUE ANALİZ\n\n"
            f"Maç/Bahis: {mac}\n"
            f"Oran: {oran}\n"
            f"Piyasa olasılığı: %{round(piyasa*100,2)}\n"
            f"Senin tahminin: %{round(tahmin*100,2)}\n"
            f"Value: %{round(v*100,2)}\n"
            f"Karar: {karar}\n"
            f"Önerilen bahis: {round(stake)} TL"
        )

        await update.message.reply_text(msg)

    except:
        await update.message.reply_text(
            "Hatalı format ❌\n\n"
            "Doğru kullanım:\n"
            "/value Braga-KGVar 1.63 68"
        )

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("value", value))
    app.run_polling()

if __name__ == "__main__":
    main()