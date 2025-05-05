import discord
from discord.ext import commands
from discord import app_commands
import json

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reload_data", description="Ručne znovu načíta data.json")
    async def reload_data(self, interaction: discord.Interaction):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                self.bot.moe_data = [t for t in json.load(f) if "Tank" in t]
            await interaction.response.send_message("✅ Data boli úspešne znovu načítané.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Chyba pri načítaní:\n```{e}```", ephemeral=True)

    @app_commands.command(name="sync", description="Manuálne synchronizuje slash príkazy")
    async def sync_commands(self, interaction: discord.Interaction):
        try:
            await self.bot.tree.sync()
            await interaction.response.send_message("🔄 Slash príkazy boli úspešne synchronizované.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Sync zlyhal:\n```{e}```", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))