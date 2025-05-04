import discord
from discord.ext import commands
import json
from apscheduler.schedulers.background import BackgroundScheduler
from keep_alive import keep_alive
import requests
from bs4 import BeautifulSoup
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

# Automatická aktualizácia údajov z webu (dočasne zakázaná)
def update_data():
    print("Aktualizujem údaje z wotconsole.info...")
    url = "https://wotconsole.info/marks/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'tankTable'})

    if not table:
        print("❌ Tabuľka sa nenašla.")
        return

    rows = table.find_all('tr')
    all_data = []

    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) >= 4:
            name = cols[0].text.strip()
            mark1 = cols[1].text.strip()
            mark2 = cols[2].text.strip()
            mark3 = cols[3].text.strip()
            all_data.append({
                "name": name,
                "mark1": mark1,
                "mark2": mark2,
                "mark3": mark3
            })

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("Údaje boli aktualizované.")

@bot.event
async def on_ready():
    print(f'✅ Bot je online ako {bot.user}')
    # update_data()  # dočasne vypnuté
    print("Bot je online a pripravený.")

@bot.command()
async def moe(ctx, *, search: str):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            tanks = json.load(f)

        def normalize(text):
            return text.lower().replace(" ", "").replace("-", "")

        matches = [t for t in tanks if normalize(search) in normalize(t["name"])]

        if not matches:
            await ctx.send("❌ Nenašli sa žiadne tanky.")
            return

        for tank in matches[:5]:
            embed = discord.Embed(
                title=f"Marks of Excellence – {tank['name']}",
                color=discord.Color.blue()
            )
            embed.add_field(name="1. mark", value=tank["mark1"], inline=False)
            embed.add_field(name="2. mark", value=tank["mark2"], inline=False)
            embed.add_field(name="3. mark", value=tank["mark3"], inline=False)
            await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"⚠️ Nastala chyba: {e}")

# Spusti keep_alive server (potrebný pre hosting)
keep_alive()

# Automatické aktualizovanie raz denne (dočasne aktívne, ale nebude fungovať bez tabuľky)
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, "interval", hours=24)
scheduler.start()

# Spustenie bota s tokenom
bot.run(os.environ["DISCORD_BOT_TOKEN"])
