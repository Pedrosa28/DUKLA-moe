import os
import json
import threading
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import discord
from discord.ext import commands
from discord import Intents
from discord import app_commands
from dotenv import load_dotenv

# Načítanie tokenu
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Intenty a bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # pre slash príkazy

# Flask keep-alive
app = Flask(__name__)
@app.route('/')
def home():
    return "MoE Discord bot is running!"

def keep_alive():
    app.run(host="0.0.0.0", port=8080)

# Načítanie MoE dát
moe_data = []

def update_data():
    global moe_data
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        moe_data = [t for t in data if "Tank" in t]
        print("✅ Data loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load data.json: {e}")

# COG: Slash príkazy
class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Odpovie Pong!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong!")

    @app_commands.command(name="moe", description="Vyhľadaj MoE údaje podľa názvu tanku")
    @app_commands.describe(tank_name="Názov tanku alebo jeho časť")
    async def moe(self, interaction: discord.Interaction, tank_name: str):
        try:
            matches = [t for t in moe_data if tank_name.lower() in t["Tank"].lower()]

            if not matches:
                await interaction.response.send_message(f"❌ Tank `{tank_name}` sa nenašiel.", ephemeral=True)
                return

            for match in matches[:5]:
                embed = discord.Embed(
                    title=f"{match['Tank']}",
                    description=f"{match['Nation']} • Tier {match['Tier']} • {match['Class']}",
                    color=0x3498db
                )
                embed.add_field(name="3 MoE", value=match["3 MoE"], inline=True)
                embed.add_field(name="2 MoE", value=match["2 MoE"], inline=True)
                embed.add_field(name="1 MoE", value=match["1 MoE"], inline=True)
                await interaction.channel.send(embed=embed)

            await interaction.response.send_message(f"🔍 Zobrazené výsledky pre: `{tank_name}`", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Chyba:\n```{e}```", ephemeral=True)

# Bot pripravený
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot je online ako: {bot.user}")

# Spustenie Flask servera
threading.Thread(target=keep_alive).start()

# Spustenie aktualizácie údajov
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, "interval", hours=24)
scheduler.start()
update_data()

# Pridanie Cogu
bot.add_cog(GeneralCommands(bot))

# Spustenie bota
bot.run(DISCORD_TOKEN)
