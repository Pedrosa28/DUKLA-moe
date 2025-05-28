import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import date

ROLES_PRIORITY = {
    "Commander": 1,
    "Executive Officer": 2,
    "Recruitment Officer": 3,
    "Private": 4
}

class ZoznamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "clan_members.json"
        self.message_id_file = "message_id.json"
        self.history_file = "zmeny.json"

    def load_members(self):
        if not os.path.exists(self.data_file):
            return []
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_members(self, members):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=4)

    def update_history(self, old, new):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {"joined": [], "left": []}

        old_names = {member["name"] for member in old}
        new_names = {member["name"] for member in new}

        joined = new_names - old_names
        left = old_names - new_names

        today = str(date.today())

        for name in joined:
            if not any(entry["name"] == name for entry in history["joined"]):
                history["joined"].append({"name": name, "date": today})
        for name in left:
            if not any(entry["name"] == name for entry in history["left"]):
                history["left"].append({"name": name, "date": today})

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    @app_commands.command(name="aktualizuj_zoznam", description="Aktualizuje embed so zoznamom členov klanu")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        with open("clan_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        members = data.get("members", [])
        members.sort(key=lambda x: ROLES_PRIORITY.get(x["role"], 99))

        old_members = self.load_members()
        self.update_history(old_members, members)
        self.save_members(members)

        # Formatovanie výstupu
        chunks = []
        chunk = ""
        for i, member in enumerate(members, 1):
            line = f"✅ {member['name']} – {member['role']}
"
            if len(chunk + line) > 1024:
                chunks.append(chunk)
                chunk = ""
            chunk += line
        if chunk:
            chunks.append(chunk)

        embed = discord.Embed(
            title="🛡️ DUKLA Československo [DUKL4] – Členovia",
            description=f"Počet členov: {len(members)}",
            color=discord.Color.green()
        )
        embed.add_field(name="Zoznam členov", value=chunks[0], inline=False)
        for idx, chunk in enumerate(chunks[1:], 2):
            embed.add_field(name=f"Pokračovanie {idx - 1}", value=chunk, inline=False)

        await interaction.response.send_message("✅ Embed správa bola aktualizovaná.", ephemeral=True)