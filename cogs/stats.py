import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict

class StatsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="top_moe", description="Top 5 tankov podľa 3 MoE hodnoty v zadanom tieri")
    @app_commands.describe(tier="Tier od 1 po 10")
    async def top_moe(self, interaction: discord.Interaction, tier: int):
        if not (1 <= tier <= 10):
            await interaction.response.send_message("❌ Zadaj platný tier od 1 do 10.", ephemeral=True)
            return

        tanks = [t for t in self.bot.moe_data if int(t.get("Tier", 0)) == tier]
        tanks.sort(key=lambda t: int(t["3 MoE"].replace(",", "")), reverse=True)

        if not tanks:
            await interaction.response.send_message("❌ Nenašli sa žiadne tanky pre tento tier.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Top 5 tankov Tier {tier} podľa 3 MoE",
            color=0x2ecc71
        )
        for i, t in enumerate(tanks[:5], 1):
            embed.add_field(
                name=f"#{i}: {t['Tank']}",
                value=f"{t['Nation']} • {t['Class']}\n3 MoE: {t['3 MoE']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nation_stats", description="Počet tankov podľa národa")
    async def nation_stats(self, interaction: discord.Interaction):
        count = defaultdict(int)
        for t in self.bot.moe_data:
            count[t["Nation"]] += 1

        embed = discord.Embed(title="📊 Počet tankov podľa národa", color=0xf39c12)
        for nation, num in sorted(count.items(), key=lambda x: -x[1]):
            embed.add_field(name=nation, value=str(num), inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(StatsCommands(bot))