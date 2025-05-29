
import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class HistoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.history_file = "zmeny.json"

    @app_commands.command(name="zmeny", description="Zobrazí prehľad všetkých zmien v členstve klanu")
    async def zmeny(self, interaction: discord.Interaction):
        # Bezpečný defer
        if not interaction.response.is_done():
            await interaction.response.defer()

        content = None
        try:
            if not os.path.exists(self.history_file):
                content = "❌ Súbor `zmeny.json` neexistuje."
            else:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)

                joined = history.get("joined", [])
                left = history.get("left", [])

                embed = discord.Embed(
                    title="📜 História zmien v členstve klanu",
                    color=discord.Color.blue()
                )

                if joined:
                    joined_lines = [f"✅ {entry['name']} ({entry['date']})" for entry in joined]
                    embed.add_field(name="Noví členovia", value="\n".join(joined_lines), inline=False)
                else:
                    embed.add_field(name="Noví členovia", value="Žiadni", inline=False)

                if left:
                    left_lines = [f"❌ {entry['name']} ({entry['date']})" for entry in left]
                    embed.add_field(name="Odišli z klanu", value="\n".join(left_lines), inline=False)
                else:
                    embed.add_field(name="Odišli z klanu", value="Žiadni", inline=False)

                await interaction.followup.send(embed=embed)
                return
        except Exception as e:
            content = f"❌ Chyba pri spracovaní: `{str(e)}`"

        # Poslať textovú správu len ak nebol embed
        if content:
            await interaction.followup.send(content)

async def setup(bot):
    await bot.add_cog(HistoryCog(bot))
