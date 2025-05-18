
import discord
from discord.ext import tasks, commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

DATA_FILE = "data.json"
UPDATE_INTERVAL_DAYS = 14
MOE_URL = "https://wotconsole.info/marks"

class UpdateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("🔄 Načítavam modul update.py")
        self.auto_update_task = self.auto_update
        self.auto_update_task.start()

    @app_commands.command(name="update", description="Aktualizuje data.json so všetkými tankami a MoE hodnotami")
    async def update_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send("📦 Načítavam nové dáta zo stránky wotconsole.info/marks...")
        await self.update_data(interaction)

    @app_commands.command(name="start_auto_update", description="Zapne automatickú aktualizáciu dát")
    async def start_auto_update_command(self, interaction: discord.Interaction):
        if not self.auto_update_task.is_running():
            self.auto_update_task.start()
            await interaction.response.send_message("🔄 Automatická aktualizácia zapnutá. Dáta budú aktualizované každé 14 dní.")
        else:
            await interaction.response.send_message("🔄 Automatická aktualizácia už je zapnutá.")

    @app_commands.command(name="stop_auto_update", description="Zastaví automatickú aktualizáciu dát")
    async def stop_auto_update_command(self, interaction: discord.Interaction):
        if self.auto_update_task.is_running():
            self.auto_update_task.stop()
            await interaction.response.send_message("🛑 Automatická aktualizácia zastavená.")
        else:
            await interaction.response.send_message("🛑 Automatická aktualizácia už je zastavená.")

    @tasks.loop(days=UPDATE_INTERVAL_DAYS)
    async def auto_update(self):
        print("🔄 Automaticky aktualizujem data.json...")
        await self.update_data()
        print("✅ Automatická aktualizácia dokončená.")

    async def update_data(self, interaction=None):
        try:
            response = requests.get(MOE_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            tank_entries = []

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

            for row in soup.select("#table1 tbody tr"):
                cells = row.find_all('td')
                tier = int(cells[0].get('data-text', '0'))
                type_key = cells[1].get('data-text', 'unknown')
                nation_img = cells[2].find('img')['alt']
                premium = bool(cells[3].text.strip())
                name = cells[4].find('span').text.strip()
                moe_values = [int(td.text.strip()) for td in cells[5:9]]

                tank_type = type_mapping.get(type_key, 'Unknown')
                nation = nation_mapping.get(nation_img.lower(), 'Unknown')

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

            # Uloženie dát
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(tank_entries, f, ensure_ascii=False, indent=4)

            if interaction:
                await interaction.followup.send(f"✅ Dáta úspešne aktualizované ({len(tank_entries)} tankov).")
            print(f"✅ Dáta úspešne aktualizované ({len(tank_entries)} tankov).")

        except requests.RequestException as e:
            error_message = f"❌ Chyba pri sťahovaní dát: {e}"
            if interaction:
                await interaction.followup.send(error_message)
            print(error_message)

async def setup(bot: commands.Bot):
    await bot.add_cog(UpdateCog(bot))
