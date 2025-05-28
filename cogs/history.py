import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class HistoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="zmeny", description="Zobrazí históriu zmien v členstve klanu")
    async def zmeny(self, interaction: discord.Interaction):
        with open("zmeny.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        new_members = data.get("joined", [])
        left_members = data.get("left", [])

        embed = discord.Embed(
            title="🧵 História zmien v členstve klanu",
            color=discord.Color.blue()
        )

        def split_into_chunks(title, emoji, members):
            chunks = []
            chunk = ""
            counter = 1

            for name in members:
                line = f"• {name}\n"
                if len(chunk + line) > 1024:
                    chunks.append((f"{title} {counter}", chunk))
                    chunk = ""
                    counter += 1
                chunk += line

            if chunk:
                chunks.append((f"{title} {counter}", chunk))
            return chunks

        if new_members:
            for name, content in split_into_chunks("🆕 Noví členovia", "🆕", new_members):
                embed.add_field(name=name, value=content, inline=False)
        else:
            embed.add_field(name="🆕 Noví členovia", value="Žiadni", inline=False)

        if left_members:
            for name, content in split_into_chunks("❌ Odišli z klanu", "❌", left_members):
                embed.add_field(name=name, value=content, inline=False)
        else:
            embed.add_field(name="❌ Odišli z klanu", value="Žiadni", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HistoryCog(bot))
