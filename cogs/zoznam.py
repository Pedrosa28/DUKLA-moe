
import discord
from discord import app_commands
from discord.ext import commands
import json
import os

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

    def load_members(self):
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
        lines = []
        for member in members:
            lines.append(f"✅ {member['name']} – {member['role']}")
        return lines

    def compare_members(self, old, new):
        old_names = {m['name'] for m in old}
        new_names = {m['name'] for m in new}
        joined = new_names - old_names
        left = old_names - new_names
        return list(joined), list(left)

    def chunk_text(self, lines, limit=1024):
        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 > limit:
                chunks.append(current)
                current = ""
            current += line + "\n"
        if current:
            chunks.append(current)
        return chunks

    @app_commands.command(name="aktualizuj_zoznam", description="Aktualizuje zoznam členov a prepíše správu v kanáli")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        try:
            with open("new_clan_members.json", "r", encoding="utf-8") as f:
                new_members = json.load(f)
        except FileNotFoundError:
            await interaction.response.send_message("❌ Súbor `new_clan_members.json` nebol nájdený.", ephemeral=True)
            return

        try:
            old_members = self.load_members()
        except Exception:
            old_members = []

        self.save_members(new_members)
        sorted_members = self.sort_members(new_members)
        lines = self.format_member_list(sorted_members)

        embed = discord.Embed(
            title="🛡️ DUKLA Československo [DUKL4] – Členovia",
            description=f"Počet členov: {len(new_members)}",
            color=discord.Color.dark_gold()
        )

        chunks = self.chunk_text(lines)
        # print(f"Počet chunkov: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            name = "Zoznam členov" if i == 0 else f"Pokračovanie {i}"
            # print(f"[Field {i}] {name} – {len(chunk)} znakov")
            embed.add_field(name=name, value=chunk.strip(), inline=False)

        joined, left = self.compare_members(old_members, new_members)
        if joined or left:
            changes = []
            if joined:
                changes.extend([f"✅ Nový člen: {name}" for name in joined])
            if left:
                changes.extend([f"❌ Odišiel: {name}" for name in left])
            field_text = "\n".join(changes)
            # print(f"[Zmeny] {len(field_text)} znakov")
            embed.add_field(name="📝 Zmeny", value=field_text, inline=False)

        # print(f"Celkový počet embed fieldu: {len(embed.fields)}")

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
                except Exception as e:
                    # print("Úprava embed správy zlyhala:", e)

            new_message = await channel.send(embed=embed)
            self.save_message_id(new_message.id)
            await interaction.response.send_message("✅ Nová embed správa bola odoslaná a ID uložené.", ephemeral=True)

        except Exception as e:
            # print("Chyba pri odosielaní embed správy:", e)
            await interaction.response.send_message("❌ Vyskytla sa chyba pri odosielaní embed správy.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ZoznamCog(bot))
