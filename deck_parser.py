import requests
import time
from typing import Tuple, List
from card_classes import Spell, Land

SCRYFALL_API = "https://api.scryfall.com/cards/named?exact="

def parse_deck(file_path: str) -> Tuple[List[Spell], List[Land]]:
    spells = []
    lands = []
    reading_deck = False

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.lower().startswith("deck"):
                reading_deck = True
                continue
            elif line.lower().startswith("sideboard"):
                break

            if not reading_deck:
                continue

            parts = line.split()
            if not parts:
                continue
            try:
                quantity = int(parts[0])
                card_name = " ".join(parts[1:])
            except ValueError:
                continue

            response = requests.get(f"{SCRYFALL_API}{card_name}")
            time.sleep(0.1)

            if response.status_code != 200:
                print(f"Error fetching {card_name}: {response.text}")
                continue

            card_data = response.json()
            is_land = False
            oracle_text = ""
            colors = []
            mana_cost = ""

            if "card_faces" in card_data:
                for face in card_data["card_faces"]:
                    if "Land" in face["type_line"]:
                        is_land = True
                        oracle_text = face.get("oracle_text", "")
                        colors = face.get("produced_mana", [])
                        card_name = face["name"]
                        break
                    else:
                        # Get mana cost from the spell face
                        mana_cost = face.get("mana_cost", "")
            else:
                is_land = "Land" in card_data.get("type_line", "")
                oracle_text = card_data.get("oracle_text", "")
                colors = card_data.get("produced_mana", [])
                mana_cost = card_data.get("mana_cost", "")

            if is_land:
                enters_tapped = "enters the battlefield tapped" in oracle_text.lower()
                lands.append(Land(card_name, colors, enters_tapped, quantity))
            else:
                spells.append(Spell(card_name, mana_cost, quantity))

    return spells, lands