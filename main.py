import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} je prihlásený.")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash príkazy synchronizované: {len(synced)}")
    except Exception as e:
        print(f"❌ Chyba pri synchronizácii slash príkazov: {e}")

# Načítaj cog moe
@bot.event
async def setup_hook():
    await bot.load_extension("moe")

# Flask keep-alive
app = Flask("")

@app.route("/")
def home():
    return "Bot beží."

def run():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run(TOKEN)
