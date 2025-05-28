import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class Zoznam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="aktualizuj_zoznam", description="Aktualizuje embed so zoznamom členov klanu")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        # Cesta k HTML výpisu (alebo JSON dátam)
        source_path = "dukla_clenovia.json"
        output_path = "members.json"

        # Načítanie dát
        if not os.path.exists(source_path):
            await interaction.response.send_message("❌ Súbor dukla_clenovia.json neexistuje.", ephemeral=True)
            return

        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        members = data.get("members", [])
        # Zapíš aktuálny zoznam do members.json (nie zmeny.json)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(members, f, indent=4, ensure_ascii=False)

        # Príprava embed správy
        embed = discord.Embed(
            title="🛡️ DUKLA Československo [DUKL4] – Členovia",
            description=f"Počet členov: {len(members)}",
            color=discord.Color.green()
        )

        lines = [f"✅ {m['name']} – {m['role']}" for m in members]
        chunks = []
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) + 1 > 1024:
                chunks.append(chunk)
                chunk = ""
            chunk += line + "\n"
        if chunk:
            chunks.append(chunk)

        for i, ch in enumerate(chunks):
            name = "Zoznam členov" if i == 0 else f"Pokračovanie {i}"
            embed.add_field(name=name, value=ch, inline=False)

        # Zverejnenie embed správy
        await interaction.response.send_message("✅ Embed správa bola aktualizovaná.", ephemeral=True)

        # Pokus o nájdenie a aktualizáciu poslednej embed správy v kanáli
        channel = interaction.channel
        async for msg in channel.history(limit=50):
            if msg.author == self.bot.user and msg.embeds:
                await msg.edit(embed=embed)
                return

async def setup(bot):
    await bot.add_cog(Zoznam(bot))
