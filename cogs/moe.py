import discord
from discord import app_commands
from discord.ext import commands
import json
import re

class MoECog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("data_with_corrected_tiers.json", "r", encoding="utf-8") as f:
            self.tanks = json.load(f)

    @app_commands.command(name="moe", description="Zobrazí MoE hodnoty pre zadaný tank")
    @app_commands.describe(nazov="Názov tanku (napr. is7, tiger, e100)")
    async def moe(self, interaction: discord.Interaction, nazov: str):
        normalized_input = re.sub(r"[^a-zA-Z0-9]", "", nazov).lower()

        matches = [
            tank for tank in self.tanks
            if normalized_input in re.sub(r"[^a-zA-Z0-9]", "", tank["name"]).lower()
        ]

        if not matches:
            await interaction.response.send_message("❌ Nenašiel sa žiadny tank s týmto názvom.", ephemeral=True)
            return

        if len(matches) == 1:
            tank = matches[0]
            premium_status = "Áno" if tank["premium"] else "Nie"
            embed = discord.Embed(
                title=f"{tank['name']} – MoE hodnoty",
                description=(
                    f"**Národ:** {tank['nation']}\n"
                    f"**Typ:** {tank['type']}\n"
                    f"**Tier:** {tank['tier']}\n"
                    f"**Prémiový:** {premium_status}\n"
                    f"**1 MoE:** {tank['moe']['1 MoE']}\n"
                    f"**2 MoE:** {tank['moe']['2 MoE']}\n"
                    f"**3 MoE:** {tank['moe']['3 MoE']}\n"
                    f"**4 MoE:** {tank['moe']['4 MoE']}"
                ),
                color=discord.Color.dark_gold()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("🔎 Našiel som viac tankov, posielam výsledky:", ephemeral=True)
            for tank in matches[:10]:
                premium_status = "Áno" if tank["premium"] else "Nie"
                embed = discord.Embed(
                    title=f"{tank['name']} – MoE hodnoty",
                    description=(
                        f"**Národ:** {tank['nation']}\n"
                        f"**Typ:** {tank['type']}\n"
                        f"**Tier:** {tank['tier']}\n"
                        f"**Prémiový:** {premium_status}\n"
                        f"**1 MoE:** {tank['moe']['1 MoE']}\n"
                        f"**2 MoE:** {tank['moe']['2 MoE']}\n"
                        f"**3 MoE:** {tank['moe']['3 MoE']}\n"
                        f"**4 MoE:** {tank['moe']['4 MoE']}"
                    ),
                    color=discord.Color.dark_gold()
                )
                await interaction.followup.send(embed=embed, ephemeral=True, wait=True)

            if len(matches) > 10:
                await interaction.followup.send("⚠️ Zobrazených je iba prvých 10 výsledkov.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MoECog(bot))
