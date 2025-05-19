import os
import discord
from discord.ext import commands
import asyncio
from aiohttp import web

# Inicializácia bota s potrebnými intentmi
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
    cogs = ["admin", "moe", "stats", "update", "help",]
    for cog in cogs:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"✅ Načítaný cog: {cog}.py")
        except Exception as e:
            print(f"❌ Chyba pri načítaní cogu {cog}.py: {e}")

async def start_web_server():
    app = web.Application()
    async def handle(request):
        return web.Response(text="Bot je online")
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()
    print("✅ Web server je spustený.")

async def main():
    await load_cogs()
    await start_web_server()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ Chyba: DISCORD_TOKEN nie je nastavený v environmentálnych premenných.")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
