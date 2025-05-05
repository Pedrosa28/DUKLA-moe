import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from moe import MoECog
from flask import Flask
import threading

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f"✅ Prihlásený ako {bot.user}")

bot.add_cog(MoECog(bot))

# Web server pre udržanie aktivity na Renderi
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot je aktívny."

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)
