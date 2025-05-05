import discord
from discord import app_commands
from discord.ext import commands
import json
import re

class MoE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("data.json", "r", encoding="utf-8") as f:
            self.tanks = json.load(f)

    @app_commands.command(name="moe", description="Zobrazí MoE hodnoty pre zadaný tank")
    @app_commands.describe(name="Názov tanku (napr. is7, tiger, e100)")
    async def moe(self, interaction: discord.Interaction, name: str):
        normalized_input = re.sub(r"[^a-zA-Z0-9]", "", name).lower()

        matches = [
            tank for tank in self.tanks
            if normalized_input in re.sub(r"[^a-zA-Z0-9]", "", tank["Name"]).lower()
        ]

        if not matches:
            await interaction.response.send_message("❌ Nenašiel sa žiadny tank s týmto názvom.")
            return

        # Ak je viacero výsledkov, zober len prvý najrelevantnejší
        tank = matches[0]

        embed = discord.Embed(
            title=f"{tank['Name']} – MoE hodnoty",
            description=(
                f"**Tier:** {tank['Tier']}\n"
                f"**1 MoE:** {tank['1 MoE']}\n"
                f"**2 MoE:** {tank['2 MoE']}\n"
                f"**3 MoE:** {tank['3 MoE']}\n"
                f"**Počet bitiek:** {tank['Battles']}"
            ),
            color=discord.Color.dark_gold()
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MoE(bot))
