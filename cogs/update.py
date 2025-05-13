
import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update", help="Aktualizuje data.json so všetkými tankami a MoE hodnotami")
    async def start_auto_update(self, ctx):
        self.auto_update.start()
        await ctx.send("🔄 Automatická aktualizácia zapnutá. Dáta budú aktualizované každé 2 týždne.")

    @commands.command(name="stopupdate", help="Zastaví automatickú aktualizáciu dát")
    async def stop_auto_update(self, ctx):
        self.auto_update.stop()
        await ctx.send("🛑 Automatická aktualizácia zastavená.")

    @tasks.loop(weeks=2)
    async def auto_update(self):
        channel = self.bot.get_channel(1326498619779715107)
        if channel:
            await channel.send("📦 Automaticky aktualizujem data.json...")
        await self.update_data()
        if channel:
            await channel.send("✅ Automatická aktualizácia dokončená.")

    async def update(self, ctx):
        await ctx.send("📦 Načítavam nové dáta zo stránky wotconsole.info/marks...")

        URL = "https://wotconsole.info/marks"
        DATA_FILE = "data.json"

        type_mapping = {
            "lightTank": "Light Tank",
            "mediumTank": "Medium Tank",
            "heavyTank": "Heavy Tank",
            "AT-SPG": "Tank Destroyer",
            "SPG": "Artillery"
        }

        nation_mapping = {
            "china": "China",
            "czech": "Czechoslovakia",
            "france": "France",
            "germany": "Germany",
            "italy": "Italy",
            "japan": "Japan",
            "merc": "Mercenaries",
            "poland": "Poland",
            "sweden": "Sweden",
            "uk": "UK",
            "usa": "USA",
            "ussr": "USSR",
            "xn": "Independent"
        }

        try:
            start_time = datetime.now()
            response = requests.get(URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            tank_entries = []

            for row in soup.select("#table1 tbody tr"):
                tier = int(row.find('td', {'data-text': True}).get('data-text'))
                type_key = row.find_all('td')[1].get('data-text')
                nation_img = row.find_all('td')[2].find('img')['alt']
                premium = bool(row.find_all('td')[3].text.strip())
                name = row.find_all('td')[4].find('span').text.strip()
                moe_values = [int(td.text.strip()) for td in row.find_all('td', class_='mark')]

                tank_type = type_mapping.get(type_key, 'Unknown')
                nation = nation_mapping.get(nation_img, 'Unknown')

                tank_entries.append({
                    "name": name,
                    "nation": nation,
                    "type": tank_type,
                    "tier": min(tier, 13),
                    "premium": premium,
                    "moe": {
                        "1 MoE": moe_values[0] if len(moe_values) > 0 else 0,
                        "2 MoE": moe_values[1] if len(moe_values) > 1 else 0,
                        "3 MoE": moe_values[2] if len(moe_values) > 2 else 0,
                        "4 MoE": moe_values[3] if len(moe_values) > 3 else 0
                    }
                })

            # Kontrola poklesu počtu tankov
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    old_tank_count = len(old_data)
            except FileNotFoundError:
                old_tank_count = 0

            new_tank_count = len(tank_entries)
            tank_difference = new_tank_count - old_tank_count

            # Uloženie dát
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(tank_entries, f, ensure_ascii=False, indent=4)

            end_time = datetime.now()
            duration = end_time - start_time
            update_time = end_time.strftime('%Y-%m-%d %H:%M:%S')

            warning_message = ""
            if tank_difference < 0:
                warning_message = f"⚠️ UPOZORNENIE: Počet tankov sa znížil o {abs(tank_difference)}. Skontroluj, či nechýbajú niektoré tanky."

            await ctx.send(f"✅ Data úspešne aktualizované ({new_tank_count} tankov).\n🕒 Čas aktualizácie: {update_time}\n⏱️ Trvanie: {duration}\n{warning_message}")
        
        except requests.RequestException as e:
            await ctx.send(f"❌ Chyba pri sťahovaní dát: {e}")

async def setup(bot):
    await bot.add_cog(UpdateCog(bot))
