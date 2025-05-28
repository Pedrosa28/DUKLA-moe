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
        if not os.path.exists("zmeny.json"):
            await interaction.response.send_message("❌ Súbor zmeny.json neexistuje.", ephemeral=True)
            return

        with open("zmeny.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        new_members = data.get("joined", [])
        left_members = data.get("left", [])

        embed = discord.Embed(
            title="🧵 História zmien v členstve klanu",
            color=discord.Color.blue()
        )

        def format_members(members):
            chunks = []
            current = ""
            counter = 1
            for m in members:
                line = f"• {m['name']} ({m['date']})
"
                if len(current + line) > 1024:
                    chunks.append(current)
                    current = ""
                    counter += 1
                current += line
            if current:
                chunks.append(current)
            return chunks

        joined_chunks = format_members(new_members)
        left_chunks = format_members(left_members)

        for i, chunk in enumerate(joined_chunks):
            embed.add_field(name=f"🆕 Noví členovia {i+1}" if len(joined_chunks) > 1 else "🆕 Noví členovia", value=chunk, inline=False)
        for i, chunk in enumerate(left_chunks):
            embed.add_field(name=f"❌ Odišli z klanu {i+1}" if len(left_chunks) > 1 else "❌ Odišli z klanu", value=chunk, inline=False)

        await interaction.response.send_message(embed=embed)