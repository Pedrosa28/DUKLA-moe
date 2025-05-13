import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, application_id=int(os.getenv("DISCORD_APPLICATION_ID")))

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Načítaný modul: {filename}")
            except Exception as e:
                print(f"❌ Chyba pri načítavaní modulu {filename}: {e}")

async def main():
    try:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))
    except Exception as e:
        print(f"❌ Chyba pri spustení bota: {e}")

if __name__ == "__main__":
    asyncio.run(main())
