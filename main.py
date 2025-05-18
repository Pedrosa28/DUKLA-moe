
import os
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

COGS = ["admin", "moe", "help", "stats", "update"]

@bot.event
async def on_ready():
    print(f"Bot je prihlásený ako {{bot.user}}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synchronizovaných príkazov: {{len(synced)}}")
    except Exception as e:
        print(f"❌ Chyba pri synchronizácii príkazov: {{e}}")

# Načítanie všetkých cogs
for cog in COGS:
    try:
        bot.load_extension(f"cogs.{cog}")
        print(f"✅ Načítané rozšírenie: {{cog}}")
    except Exception as e:
        print(f"❌ Chyba pri načítaní rozšírenia {{cog}}: {{e}}")

bot.run(TOKEN)
