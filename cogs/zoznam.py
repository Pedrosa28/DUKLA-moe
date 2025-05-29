
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import date
import requests
from bs4 import BeautifulSoup

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

    def fetch_clan_members_from_web(self):
        url = "https://modernarmor.worldoftanks.com/en/clans/DUKL4/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("table tr[data-name][data-role-name]")

        members = []
        for row in rows:
            name = row["data-name"].strip()
            role = row["data-role-name"].strip()
            members.append({"name": name, "role": role})
        return members

    def load_members(self):
        if not os.path.exists(self.data_file):
            return []
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_members(self, members):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=4)

    def load_message_id(self):
        if not os.path.exists(self.message_id_file):
            return None
        with open(self.message_id_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("message_id")

    def save_message_id(self, message_id):
        with open(self.message_id_file, "w", encoding="utf-8") as f:
            json.dump({"channel_id": 1374105106185719970, "message_id": message_id}, f, indent=4)

    def sort_members(self, members):
        return sorted(members, key=lambda x: (ROLES_PRIORITY.get(x['role'], 99), x['name'].lower()))

    def format_member_list(self, members):
        return [f"✅ {member['name']} – {member['role']}" for member in members]

    def compare_members(self, old, new):
        def normalize(name):
            return name.strip().lower()

        old_map = {normalize(m['name']): m['name'] for m in old}
        new_map = {normalize(m['name']): m['name'] for m in new}

        old_keys = set(old_map.keys())
        new_keys = set(new_map.keys())

        joined = [new_map[k] for k in new_keys - old_keys]
        left = [old_map[k] for k in old_keys - new_keys]

        print("==== DEBUG COMPARE MEMBERS ====")
        print("OLD:", old_keys)
        print("NEW:", new_keys)
        print("JOINED:", joined)
        print("LEFT:", left)

        return joined, left

    def chunk_text(self, lines, limit=1024, max_fields=5):
        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 > limit:
                chunks.append(current)
                current = ""
            current += line + "\n"
        if current:
            chunks.append(current)

        if len(chunks) > max_fields:
            print("⚠️ POZOR: Embed prekročil počet polí. Niektoré mená sa nezobrazia!")
            for i, chunk in enumerate(chunks[max_fields:]):
                print(f"❗ Nezobrazené pole {i+1}:")
                print(chunk)
            return chunks[:max_fields]
        return chunks

    def update_history(self, joined, left):
        today = str(date.today())
        if not os.path.exists(self.history_file):
            history = {"joined": [], "left": []}
        else:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

        for name in joined:
            history["joined"].append({"name": name, "date": today})
        for name in left:
            history["left"].append({"name": name, "date": today})

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    @app_commands.command(name="aktualizuj_zoznam", description="Aktualizuje zoznam členov z webu a prepíše správu v kanáli")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        try:
            new_members = self.fetch_clan_members_from_web()
        except Exception as e:
            await interaction.response.send_message(f"❌ Chyba pri načítaní členov z webu: {e}", ephemeral=True)
            return

        old_members = self.load_members()
        self.save_members(new_members)

        sorted_members = self.sort_members(new_members)
        lines = self.format_member_list(sorted_members)

        print("==== DEBUG FULL MEMBER LIST ====")
        for line in lines:
            print(line)

        embed = discord.Embed(
            title="🛡️ DUKLA Československo [DUKL4] – Členovia",
            description=f"Počet členov: {len(new_members)}",
            color=discord.Color.dark_gold()
        )

        for i, chunk in enumerate(self.chunk_text(lines)):
            name = "Zoznam členov" if i == 0 else f"Pokračovanie {i}"
            embed.add_field(name=name, value=chunk.strip(), inline=False)

        joined, left = self.compare_members(old_members, new_members)
        if joined or left:
            changes = []
            if joined:
                changes += [f"✅ Nový člen: {name}" for name in joined]
            if left:
                changes += [f"❌ Odišiel: {name}" for name in left]
            embed.add_field(name="📝 Zmeny", value="\n".join(changes), inline=False)
            self.update_history(joined, left)

        try:
            channel = self.bot.get_channel(1374105106185719970)
            if not channel:
                await interaction.response.send_message("❌ Kanál nebol nájdený.", ephemeral=True)
                return

            message_id = self.load_message_id()
            if message_id:
                try:
                    message = await channel.fetch_message(message_id)
                    await message.edit(embed=embed)
                    await interaction.response.send_message("✅ Embed správa bola aktualizovaná.", ephemeral=True)
                    return
                except Exception:
                    pass

            new_message = await channel.send(embed=embed)
            self.save_message_id(new_message.id)
            await interaction.response.send_message("✅ Nová embed správa bola odoslaná a ID uložené.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Chyba pri aktualizácii správy: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ZoznamCog(bot))
