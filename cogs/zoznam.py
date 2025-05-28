import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class Zoznam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="aktualizuj_zoznam", description="Aktualizuje embed so zoznamom členov klanu")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        source_path = "dukla_clenovia.json"
        output_path = "new_clan_members.json"

        if not os.path.exists(source_path):
            await interaction.response.send_message("❌ Súbor dukla_clenovia.json neexistuje.", ephemeral=True)
            return

        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        members = data.get("members", [])

        # Zapíš nový zoznam do new_clan_members.json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(members, f, indent=4, ensure_ascii=False)

        await interaction.response.send_message("✅ Embed správa bola aktualizovaná.", ephemeral=True)