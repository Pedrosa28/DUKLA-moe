import os
import json
import threading
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from discord.ext import commands
from discord import Intents  # ← Toto patrí sem hore
from dotenv import load_dotenv

# Načítanie tokenu z .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Inicializácia Discord bota
intents = Intents.default()  # ← Tu je čisté priradenie
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask server na udržanie aktivity (pre Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "MoE Discord bot is running!"

def keep_alive():
    app.run(host="0.0.0.0", port=8080)

# Funkcia na načítanie údajov z data.json
def update_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print("Data successfully loaded from data.json.")
    except Exception as e:
        print(f"Failed to load data.json: {e}")

# Jednoduchý príkaz na test
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Spustenie Flask servera v samostatnom vlákne
threading.Thread(target=keep_alive).start()

# Spustenie plánovača pre aktualizáciu údajov každých 24 hodín
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, "interval", hours=24)
scheduler.start()

# Načítanie dát hneď pri štarte
update_data()

# Spustenie bota
bot.run(DISCORD_TOKEN)
