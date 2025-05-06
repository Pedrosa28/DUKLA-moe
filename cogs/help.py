import discord
from discord.ext import commands
from discord import app_commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Zobrazí zoznam dostupných slash príkazov")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📘 Dostupné Slash príkazy", color=0x00bcd4)

        embed.add_field(name="/moe <tank>", value="Zobrazí MoE hodnoty pre zadaný tank", inline=False)
        embed.add_field(name="/moe_search <slovo>", value="Vyhľadá všetky tanky obsahujúce daný výraz", inline=False)
        embed.add_field(name="/top_moe <tier>", value="Zobrazí top 5 tankov podľa 3 MoE pre zvolený tier", inline=False)
        embed.add_field(name="/nation_stats", value="Zobrazí počet tankov rozdelený podľa národa", inline=False)
        embed.add_field(name="/reload_data", value="(admin) Znovu načíta súbor data.json", inline=False)
        embed.add_field(name="/sync", value="(admin) Synchronizuje slash príkazy bota", inline=False)

        embed.set_footer(text="DUKLA-moe | Autor: PEDROSA_SVK")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
