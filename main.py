
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Flask server for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"✅ Slash commands synchronized. Logged in as {bot.user}")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded extension: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
