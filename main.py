
import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import keep_alive  # Ensure the server stays alive on Render

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

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"✅ Načítané rozšírenie: {cog}")
        except Exception as e:
            print(f"❌ Chyba pri načítaní rozšírenia {cog}: {e}")

async def main():
    keep_alive.keep_alive()  # Start the web server to keep the bot alive on Render
    await load_cogs()
    await bot.start(TOKEN)

asyncio.run(main())
