import discord
from discord import app_commands
from discord.ext import commands
import json

class MoE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tank_data = self.load_data()

    def load_data(self):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Chyba pri načítaní data.json: {e}")
            return []

    @app_commands.command(name="moe", description="Zobrazí hodnoty Marks of Excellence pre daný tank alebo top 5 tankov.")
    @app_commands.describe(nazov="Názov tanku (alebo nechaj prázdne pre top 5)")
    async def moe(self, interaction: discord.Interaction, nazov: str = None):
        if nazov:
            matches = [t for t in self.tank_data if nazov.lower() in t["Name"].lower()]
            if not matches:
                await interaction.response.send_message(f"❌ Nenašiel sa žiadny tank so zadaným názvom: **{nazov}**", ephemeral=True)
                return

            tank = matches[0]  # zoberie prvý zhodný výsledok
            embed = discord.Embed(
                title=f"Marks of Excellence pre {tank['Name']}",
                color=discord.Color.dark_gold()
            )
            embed.add_field(name="Tier", value=tank.get("Tier", "N/A"), inline=True)
            embed.add_field(name="Bitiek", value=tank.get("Battles", "N/A"), inline=True)
            embed.add_field(name="1 MoE", value=tank.get("1 MoE", "N/A"), inline=True)
            embed.add_field(name="2 MoE", value=tank.get("2 MoE", "N/A"), inline=True)
            embed.add_field(name="3 MoE", value=tank.get("3 MoE", "N/A"), inline=True)

            await interaction.response.send_message(embed=embed)

        else:
            top5 = sorted(self.tank_data, key=lambda x: int(x.get("3 MoE", 0)), reverse=True)[:5]
            embed = discord.Embed(
                title="🔝 Top 5 tankov podľa 3 MoE hodnoty",
                color=discord.Color.blue()
            )

            for i, tank in enumerate(top5, start=1):
                embed.add_field(
                    name=f"{i}. {tank['Name']}",
                    value=f"3 MoE: {tank['3 MoE']}, Tier: {tank['Tier']}, Bitiek: {tank['Battles']}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MoE(bot))
