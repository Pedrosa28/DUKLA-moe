
import aiohttp
import json
from datetime import datetime
from bs4 import BeautifulSoup

async def update_data():
    URL = "https://wotconsole.info/marks"
    DATA_FILE = "data.json"

    type_mapping = {
        "lightTank": "Light Tank",
        "mediumTank": "Medium Tank",
        "heavyTank": "Heavy Tank",
        "AT-SPG": "Tank Destroyer",
        "SPG": "Artillery"
    }

    nation_mapping = {
        "china": "China",
        "czech": "Czechoslovakia",
        "france": "France",
        "germany": "Germany",
        "italy": "Italy",
        "japan": "Japan",
        "merc": "Mercenaries",
        "poland": "Poland",
        "sweden": "Sweden",
        "uk": "UK",
        "usa": "USA",
        "ussr": "USSR",
        "xn": "Independent"
    }

    try:
        start_time = datetime.now()
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                response_text = await response.text()
                response.raise_for_status()
                print("✅ Dáta úspešne načítané zo stránky.")

        soup = BeautifulSoup(response_text, 'html.parser')
        tank_entries = []

        for row in soup.select("#table1 tbody tr"):
            cells = row.find_all('td')
            tier = int(cells[0].get('data-text', '0'))
            type_key = cells[1].get('data-text', 'unknown')
            nation_img = cells[2].find('img')['alt']
            premium = bool(cells[3].text.strip())
            name = cells[4].find('span').text.strip()
            moe_values = [int(td.text.strip().replace(',', '')) for td in cells[5:9]]

            tank_type = type_mapping.get(type_key, 'Unknown')
            nation = nation_mapping.get(nation_img.lower(), 'Unknown')

            tank_entries.append({
                "name": name,
                "nation": nation,
                "type": tank_type,
                "tier": min(tier, 13),
                "premium": premium,
                "moe": {
                    "1 MoE": moe_values[0] if len(moe_values) > 0 else 0,
                    "2 MoE": moe_values[1] if len(moe_values) > 1 else 0,
                    "3 MoE": moe_values[2] if len(moe_values) > 2 else 0,
                    "4 MoE": moe_values[3] if len(moe_values) > 3 else 0
                }
            })

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tank_entries, f, ensure_ascii=False, indent=4)

        end_time = datetime.now()
        duration = end_time - start_time
        update_time = end_time.strftime('%Y-%m-%d %H:%M:%S')

        print(f"✅ Dáta úspešne aktualizované ({len(tank_entries)} tankov).")
        print(f"🕒 Čas aktualizácie: {update_time}")
        print(f"⏱️ Trvanie: {duration}")

    except Exception as e:
        print(f"❌ Chyba pri sťahovaní dát: {e}")

# Spustenie funkcie
import asyncio
asyncio.run(update_data())
