
import os
import discord
from discord.ext import commands
from discord import app_commands
import keep_alive
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

COGS = ["admin", "moe", "help", "stats", "update"]

@bot.event
async def on_ready():
    print(f"Bot je prihlásený ako {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synchronizovaných príkazov: {len(synced)}")
    except Exception as e:
        print(f"❌ Chyba pri synchronizácii príkazov: {e}")

async def setup_bot():
    for cog in COGS:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"✅ Načítané rozšírenie: {cog}")
        except Exception as e:
            print(f"❌ Chyba pri načítaní rozšírenia {cog}: {e}")

async def main():
    keep_alive.keep_alive()  # Use original keep_alive without Flask
    await setup_bot()
    await bot.start(TOKEN)

asyncio.run(main())
