
import discord
from discord import app_commands
from discord.ext import commands

print("🔍 zoznam.py bol importovaný")

class Zoznam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("🔧 Zoznam Cog inicializovaný")

    @app_commands.command(name="aktualizuj_zoznam", description="Testovací debug príkaz")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        print("📥 Slash príkaz aktivovaný")
        await interaction.response.send_message("Debug verzia: príkaz funguje ✅", ephemeral=True)

async def setup(bot):
    print("🛠️ setup() vo zoznam.py sa spúšťa...")
    cog = Zoznam(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.aktualizuj_zoznam)
    print("✅ zoznam.py načítaný a príkaz zaregistrovaný")
