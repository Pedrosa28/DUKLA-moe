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
        current_path = "new_clan_members.json"
        history_path = "zmeny.json"

        if not os.path.exists(current_path):
            await interaction.response.send_message("❌ Súbor new_clan_members.json neexistuje.", ephemeral=True)
            return

        # Načítanie aktuálnych členov
        with open(current_path, "r", encoding="utf-8") as f:
            current_members = json.load(f)

        current_names = {member["name"] for member in current_members}

        # Načítanie histórie zmien
        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        else:
            history_data = {"joined": [], "left": []}

        # Vytvorenie súboru pre porovnanie (last state)
        previous_names = {entry["name"] for entry in history_data["joined"]}
        for entry in history_data["left"]:
            previous_names.discard(entry["name"])

        # Porovnanie
        new_joined = sorted(list(current_names - previous_names))
        new_left = sorted(list(previous_names - current_names))

        now = datetime.utcnow().strftime("%Y-%m-%d")

        for name in new_joined:
            history_data["joined"].append({"name": name, "date": now})
        for name in new_left:
            history_data["left"].append({"name": name, "date": now})

        # Uloženie
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4, ensure_ascii=False)

        # Výstup
        embed = discord.Embed(title="🧵 História zmien v členstve klanu", color=discord.Color.blue())
        joined_str = "\n".join([f"{item['name']} – `{item['date']}`" for item in history_data["joined"]]) or "Žiadni"
        left_str = "\n".join([f"{item['name']} – `{item['date']}`" for item in history_data["left"]]) or "Žiadni"

        embed.add_field(name="🆕 Noví členovia", value=joined_str, inline=False)
        embed.add_field(name="❌ Odišli z klanu", value=left_str, inline=False)

        await interaction.response.send_message(embed=embed)