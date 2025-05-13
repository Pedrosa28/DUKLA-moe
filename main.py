import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading
import asyncio

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot je online"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, application_id=os.getenv("DISCORD_APPLICATION_ID"))

@bot.event
async def on_ready():
    print(f"✅ Prihlásený ako {bot.user.name}")
    try:
        await bot.tree.sync()
        print("✅ Slash príkazy synchronizované.")
    except Exception as e:
        print(f"❌ Chyba pri synchronizácii príkazov: {e}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Načítaný cog: {filename}")
            except Exception as e:
                print(f"❌ Chyba pri načítaní cogu {filename}: {e}")

thread = threading.Thread(target=run_flask)
thread.start()

async def main():
    await load_cogs()
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

asyncio.run(main())
