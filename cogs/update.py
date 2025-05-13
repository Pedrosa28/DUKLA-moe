
import discord
from discord.ext import tasks, commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class UpdateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("🔄 Načítavam modul update.py")

    @app_commands.command(name="update", description="Aktualizuje data.json so všetkými tankami a MoE hodnotami")
    async def update_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send("📦 Načítavam nové dáta zo stránky wotconsole.info/marks...")
        await self.update_data(interaction)

    @app_commands.command(name="start_auto_update", description="Zapne automatickú aktualizáciu dát")
    async def start_auto_update_command(self, interaction: discord.Interaction):
        self.auto_update.start()
        await interaction.response.send_message("🔄 Automatická aktualizácia zapnutá. Dáta budú aktualizované každé 2 týždne.")

    @app_commands.command(name="stopupdate", description="Zastaví automatickú aktualizáciu dát")
    async def stop_auto_update_command(self, interaction: discord.Interaction):
        self.auto_update.stop()
        await interaction.response.send_message("🛑 Automatická aktualizácia zastavená.")

    @tasks.loop(weeks=2)
    async def auto_update(self):
        channel = self.bot.get_channel(1326498619779715107)
        if channel:
            await channel.send("📦 Automaticky aktualizujem data.json...")
        await self.update_data()
        if channel:
            await channel.send("✅ Automatická aktualizácia dokončená.")

    async def update_data(self, interaction=None):
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

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(tank_entries, f, ensure_ascii=False, indent=4)

            if interaction:
                await interaction.followup.send(f"✅ Data úspešne aktualizované ({len(tank_entries)} tankov).")
            else:
                print(f"✅ Data úspešne aktualizované ({len(tank_entries)} tankov).")

        except requests.RequestException as e:
            if interaction:
                await interaction.followup.send(f"❌ Chyba pri sťahovaní dát: {e}")
            else:
                print(f"❌ Chyba pri sťahovaní dát: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(UpdateCog(bot))
    await bot.tree.sync()
