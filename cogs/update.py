
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
        self.auto_update.start()

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

        try:
            response = requests.get(URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Parsing logic here
            tank_entries = [{"name": "Example Tank"}]  # Replace with actual parsing logic

            # Save data to file
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(tank_entries, f, ensure_ascii=False, indent=4)

            if interaction:
                await interaction.followup.send(f"✅ Data úspešne aktualizované ({len(tank_entries)} tankov).")
            else:
                print(f"✅ Data úspešne aktualizované ({len(tank_entries)} tankov).")

        except Exception as e:
            if interaction:
                await interaction.followup.send(f"❌ Chyba pri sťahovaní dát: {e}")
            else:
                print(f"❌ Chyba pri sťahovaní dát: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(UpdateCog(bot))
    await bot.tree.sync()
