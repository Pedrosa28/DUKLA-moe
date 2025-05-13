import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

COGS_DIR = "./cogs"

@bot.event
async def on_ready():
    print(f"✅ Bot je pripravený ako {bot.user}.")
    print("🔄 Načítavam cogs...\n")
    for filename in os.listdir(COGS_DIR):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                print(f"✅ Načítaný cog: {filename}")
            except Exception as e:
                print(f"❌ Chyba pri načítaní cogu {filename}: {e}")
    print("\n✅ Všetky cogs načítané. Bot je pripravený na použitie.")

@bot.event
async def on_guild_join(guild):
    print(f"🆕 Bot bol pridaný na server: {guild.name}")

@bot.event
async def on_guild_remove(guild):
    print(f"🗑️ Bot bol odstránený zo servera: {guild.name}")

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        print("❌ DISCORD_TOKEN nie je definovaný v environmentálnych premenných.")
        return
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Chyba pri štarte bota: {e}")

if __name__ == "__main__":
    asyncio.run(main())
