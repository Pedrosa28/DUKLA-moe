
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime

class History(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="zmeny", description="Zobrazí trvalé zmeny v členstve klanu (noví/odišli)")
    async def zmeny(self, interaction: discord.Interaction):
        current_path = "new_clan_members.json"
        history_path = "zmeny.json"

        if not os.path.exists(current_path):
            await interaction.response.send_message("❌ Súbor new_clan_members.json neexistuje.", ephemeral=True)
            return

        # Načítaj aktuálnych členov
        with open(current_path, "r", encoding="utf-8") as f:
            current_members = json.load(f)

        current_names = {member["name"] for member in current_members}

        # Načítaj históriu alebo priprav novú
        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {"joined": [], "left": [], "last_known": list(current_names)}

        last_known_set = set(history.get("last_known", []))

        # Urči nové zmeny
        newly_joined = list(current_names - last_known_set)
        newly_left = list(last_known_set - current_names)

        # Ulož nové záznamy, ak existujú
        if newly_joined:
            history["joined"].extend([{"name": name, "date": datetime.now().strftime("%Y-%m-%d")} for name in newly_joined])
        if newly_left:
            history["left"].extend([{"name": name, "date": datetime.now().strftime("%Y-%m-%d")} for name in newly_left])

        # Aktualizuj stav
        history["last_known"] = list(current_names)

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        # Vytvor embed
        embed = discord.Embed(title="📋 Zmeny v členstve klanu", color=discord.Color.orange())
        if newly_joined:
            embed.add_field(name="🟢 Noví členovia", value="\n".join(f"{i+1}. {name}" for i, name in enumerate(newly_joined)), inline=False)
        if newly_left:
            embed.add_field(name="🔴 Odišli", value="\n".join(f"{i+1}. {name}" for i, name in enumerate(newly_left)), inline=False)

        if not newly_joined and not newly_left:
            embed.description = "Žiadne nové zmeny v členstve."

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(History(bot))
