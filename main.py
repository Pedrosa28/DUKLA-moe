import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from cogs.moe import MoECog
from flask import Flask
import threading
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Flask server pre Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Spustenie Flasku v samostatnom vlákne
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Synchronizácia príkazov pri štarte bota
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"✅ Slash commands synchronized. Logged in as {bot.user}")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

# Spustenie bota asynchrónne
async def main():
    await bot.add_cog(MoECog(bot))
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
