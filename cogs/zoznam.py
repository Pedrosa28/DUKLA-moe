
import discord
from discord import app_commands
from discord.ext import commands

class Zoznam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="aktualizuj_zoznam", description="Testovacia verzia príkazu")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test príkaz funguje ✅", ephemeral=True)

async def setup(bot):
    cog = Zoznam(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.aktualizuj_zoznam)
    print("✅ Testovací zoznam.py načítaný a slash príkaz zaregistrovaný")
