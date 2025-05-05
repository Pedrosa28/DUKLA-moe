import os
import json
import threading
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import discord  # pre Embed

# Načítanie tokenu z .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Inicializácia Discord bota
intents = Intents.default()
intents.message_content = True
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

# !ping príkaz na test
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# !moe príkaz – embed + čiastočné vyhľadávanie + filtrovanie
@bot.command()
async def moe(ctx, *, tank_name: str):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            tanks = json.load(f)

        # Vyfiltruj len platné záznamy (ktoré majú kľúč "Tank")
        tanks = [t for t in tanks if "Tank" in t]

        # Čiastočné vyhľadanie
        matches = [t for t in tanks if tank_name.lower() in t["Tank"].lower()]

        if not matches:
            await ctx.send(f"❌ Tank s názvom `{tank_name}` sa nenašiel.")
            return

        for match in matches[:5]:
            embed = discord.Embed(
                title=f"{match['Tank']}",
                description=f"{match['Nation']} • Tier {match['Tier']} • {match['Class']}",
                color=0x3498db
            )
            embed.add_field(name="3 MoE", value=match["3 MoE"], inline=True)
            embed.add_field(name="2 MoE", value=match["2 MoE"], inline=True)
            embed.add_field(name="1 MoE", value=match["1 MoE"], inline=True)
            await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Chyba pri načítaní údajov:\n```{e}```")

# Potvrdenie spustenia
@bot.event
async def on_ready():
    print(f"✅ Bot je online ako: {bot.user}")

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
