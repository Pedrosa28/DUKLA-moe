import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime

class History(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="zmeny", description="Zobrazí zmeny v členstve klanu")
    async def zmeny(self, interaction: discord.Interaction):
        # Cesty k súborom
        zmeny_path = "zmeny.json"
        members_path = "members.json"

        # Načítanie starých zmien
        if os.path.exists(zmeny_path):
            with open(zmeny_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        else:
            history_data = {"joined": [], "left": []}

        # Načítanie aktuálnych členov
        if os.path.exists(members_path):
            with open(members_path, "r", encoding="utf-8") as f:
                current_members = json.load(f)
        else:
            await interaction.response.send_message("❌ Súbor members.json neexistuje.", ephemeral=True)
            return

        current_names = [m["name"] for m in current_members]
        previous_names = [entry["name"] for entry in history_data["joined"] if entry["name"] not in [l["name"] for l in history_data["left"]]]

        today = datetime.today().strftime('%Y-%m-%d')

        # Zistenie nových a odídených členov
        new_joined = [name for name in current_names if name not in previous_names]
        new_left = [name for name in previous_names if name not in current_names]

        for name in new_joined:
            if not any(entry["name"] == name for entry in history_data["joined"]):
                history_data["joined"].append({"name": name, "date": today})

        for name in new_left:
            if not any(entry["name"] == name for entry in history_data["left"]):
                history_data["left"].append({"name": name, "date": today})

        # Uloženie zmien
        with open(zmeny_path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4, ensure_ascii=False)

        # Príprava výpisu
        embed = discord.Embed(title="🧵 História zmien v členstve klanu", color=discord.Color.blurple())

        def format_entries(entries):
            return "\n".join([f"• {e['name']} ({e['date']})" for e in entries]) if entries else "Žiadni"

        embed.add_field(name="🆕 Noví členovia", value=format_entries(history_data["joined"]), inline=False)
        embed.add_field(name="❌ Odišli z klanu", value=format_entries(history_data["left"]), inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(History(bot))
