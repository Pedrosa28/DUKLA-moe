import os
import json
import threading
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import discord
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv

# Načítanie tokenu
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
bot.moe_data = []

# Flask keep-alive
app = Flask(__name__)
@app.route('/')
def home():
    return "MoE Discord bot is running!"

def keep_alive():
    app.run(host="0.0.0.0", port=8080)

# Načítanie dát
def update_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            bot.moe_data = [t for t in json.load(f) if "Tank" in t]
        print("✅ Data loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load data.json: {e}")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot je online ako: {bot.user}")

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.stats")

# Spustenie Flask servera
threading.Thread(target=keep_alive).start()

# Spustenie plánovača
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, "interval", hours=24)
scheduler.start()
update_data()

bot.run(DISCORD_TOKEN)