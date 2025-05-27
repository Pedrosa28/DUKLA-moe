
import json
from bs4 import BeautifulSoup

def extract_members_from_html(html_path, output_json="clan_members.json"):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    members = []
    rows = soup.select("table tr[data-id]")

    for row in rows:
        name = row.get("data-name", "").strip()
        role = row.get("data-role-name", "").strip()
        if name and role:
            members.append({"name": name, "role": role})

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=4)

    print(f"Extracted {len(members)} members to {output_json}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Použitie: python extract_clan_members.py <html_súbor>")
    else:
        extract_members_from_html(sys.argv[1])
