import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
logging.basicConfig(level=logging.INFO)

token = os.getenv("DISCORD_TOKEN")

data_update_event = asyncio.Event()

async def reload_cogs():
    for cog in list(bot.cogs):
        try:
            await bot.reload_extension(f"cogs.{cog}")
            logging.info(f"Cog reloaded: {cog}")
        except Exception as e:
            logging.error(f"Failed to reload cog {cog}: {e}")

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        logging.info(f"Bot prihlásený ako {bot.user} s {len(synced)} synchronizovanými príkazmi")
        await reload_cogs()
    except Exception as e:
        logging.error(f"Chyba pri synchronizácii príkazov: {e}")

@bot.tree.command(name="reload", description="Reload all cogs")
async def reload(interaction: discord.Interaction):
    try:
        await reload_cogs()
        await interaction.response.send_message("✅ Všetky cogy boli úspešne načítané.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Chyba pri načítaní cogov: {e}", ephemeral=True)

@bot.tree.command(name="update", description="Manual update of data")
async def update(interaction: discord.Interaction):
    try:
        data_update_event.set()
        await interaction.response.send_message("🔄 Spustená manuálna aktualizácia dát.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Chyba pri spustení aktualizácie: {e}", ephemeral=True)

async def main():
    async with bot:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    logging.info(f"Cog načítaný: {filename}")
                except Exception as e:
                    logging.error(f"Chyba pri načítaní cogu {filename}: {e}")
        await bot.start(token)

asyncio.run(main())
