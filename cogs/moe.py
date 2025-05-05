import discord
from discord.ext import commands
from discord import app_commands

class MoeSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="moe", description="Vyhľadaj tank a zobraz MoE hodnoty")
    @app_commands.describe(tank_name="Zadaj celý alebo časť názvu tanku")
    async def moe(self, interaction: discord.Interaction, tank_name: str):
        results = [t for t in self.bot.moe_data if tank_name.lower() in t["Tank"].lower()]
        
        if not results:
            await interaction.response.send_message(f"❌ Nenašiel sa žiadny tank s názvom `{tank_name}`.", ephemeral=True)
            return

        tank = results[0]  # vezmeme prvý najbližší
        embed = discord.Embed(title=f"{tank['Tank']}", color=0x3498db)
        embed.add_field(name="🇳🇪 Národ", value=tank["Nation"], inline=True)
        embed.add_field(name="🛡️ Trieda", value=tank["Class"], inline=True)
        embed.add_field(name="⭐ Tier", value=tank["Tier"], inline=True)
        embed.add_field(name="🎯 3 MoE", value=tank["3 MoE"], inline=True)
        embed.add_field(name="🎯 2 MoE", value=tank["2 MoE"], inline=True)
        embed.add_field(name="🎯 1 MoE", value=tank["1 MoE"], inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MoeSearch(bot))