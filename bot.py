import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

DAILY_RISK = 2000
SPORT_KEY = "soccer_turkey_super_league"

def implied_prob(odd):
    return 1 / odd

def value_score(my_prob, odd):
    return (my_prob * odd) - 1

def my_probability(odd):
    return min(implied_prob(odd) + 0.05, 0.90)

def stake_amount(v):
    if v >= 0.15:
        return DAILY_RISK * 0.35
    if v >= 0.08:
        return DAILY_RISK * 0.25
    if v >= 0.03:
        return DAILY_RISK * 0.15
    return 0

def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h,totals,btts",
        "oddsFormat": "decimal"
    }
    r = requests.get(url, params=params)
    return r.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif ✅ /analiz yaz")

async def analiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_odds()

    if isinstance(data, dict) and "message" in data:
        await update.message.reply_text(f"API hatası: {data['message']}")
        return

    results = []

    for game in data:
        home = game.get("home_team")
        away = game.get("away_team")

        for bookmaker in game.get("bookmakers", [])[:1]:
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    odd = outcome.get("price")

                    if not odd or odd < 1.50:
                        continue

                    prob = my_probability(odd)
                    v = value_score(prob, odd)
                    stake = stake_amount(v)

                    if stake > 0:
                        results.append((v, home, away, market.get("key"), outcome.get("name"), odd, prob, stake))

    results.sort(reverse=True)

    if not results:
        await update.message.reply_text("Bugün value yok ❌")
        return

    msg = "📊 VALUE ANALİZ\n\n"

    for v, home, away, market, pick, odd, prob, stake in results[:10]:
        msg += (
            f"⚽ {home} - {away}\n"
            f"{market} | {pick}\n"
            f"Oran: {odd}\n"
            f"Value: %{round(v*100,2)}\n"
            f"Öneri: {round(stake)} TL\n\n"
        )

    await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analiz", analiz))
    app.run_polling()

if __name__ == "__main__":
    main()