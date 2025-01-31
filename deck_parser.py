import requests
import time
import re
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
                input_card_name = " ".join(parts[1:])
            except ValueError:
                continue

            response = requests.get(f"{SCRYFALL_API}{input_card_name}")
            time.sleep(0.1)

            if response.status_code != 200:
                print(f"Error fetching {input_card_name}: {response.text}")
                continue

            card_data = response.json()
            is_mdfc = "card_faces" in card_data

            if is_mdfc:
                spell_face = None
                land_faces = []
                for face in card_data["card_faces"]:
                    if "Land" in face["type_line"]:
                        land_faces.append(face)
                    else:
                        spell_face = face

                if spell_face and land_faces:
                    spells.append(Spell(
                        name=spell_face["name"],
                        mana_cost=spell_face.get("mana_cost", ""),
                        quantity=quantity,
                        is_mdfc=True
                    ))

                    for land_face in land_faces:
                        oracle_text = land_face.get("oracle_text", "")
                        colors = land_face.get("produced_mana", [])
                        if not colors:
                            mana_symbols = re.findall(r"{([WUBRG])}", oracle_text)
                            colors = list(set(mana_symbols))
                        
                        oracle_text_lower = oracle_text.lower()
                        has_tapped_phrase = (
                            "enters the battlefield tapped" in oracle_text_lower
                            or "enters tapped" in oracle_text_lower
                        )
                        has_conditional = any(
                            phrase in oracle_text_lower
                            for phrase in ["unless", "you may", "if you don't"]
                        )
                        enters_tapped = has_tapped_phrase and not has_conditional

                        lands.append(Land(
                            name=land_face["name"],
                            colors=colors,
                            enters_tapped=enters_tapped,
                            quantity=quantity,
                            is_mdfc=True
                        ))

                elif land_faces and not spell_face:
                    combined_name = " // ".join([face["name"] for face in card_data["card_faces"]])
                    colors = []
                    enters_tapped = False
                    
                    for face in card_data["card_faces"]:
                        oracle_text = face.get("oracle_text", "")
                        face_colors = face.get("produced_mana", [])
                        if not face_colors:
                            face_colors = re.findall(r"{([WUBRG])}", oracle_text)
                        colors.extend(face_colors)
                        
                        oracle_text_lower = oracle_text.lower()
                        has_tapped_phrase = (
                            "enters the battlefield tapped" in oracle_text_lower
                            or "enters tapped" in oracle_text_lower
                        )
                        has_conditional = any(
                            phrase in oracle_text_lower
                            for phrase in ["unless", "you may", "if you don't"]
                        )
                        if has_tapped_phrase and not has_conditional:
                            enters_tapped = True
                    
                    lands.append(Land(
                        name=combined_name,
                        colors=list(set(colors)),
                        enters_tapped=enters_tapped,
                        quantity=quantity,
                        is_mdfc=True
                    ))

            else:
                if "Land" in card_data.get("type_line", ""):
                    oracle_text = card_data.get("oracle_text", "")
                    colors = card_data.get("produced_mana", [])
                    
                    if not colors:
                        mana_symbols = re.findall(r"{([WUBRG])}", oracle_text)
                        colors = list(set(mana_symbols))
                    
                    oracle_text_lower = oracle_text.lower()
                    has_tapped_phrase = (
                        "enters the battlefield tapped" in oracle_text_lower
                        or "enters tapped" in oracle_text_lower
                    )
                    has_conditional = any(
                        phrase in oracle_text_lower
                        for phrase in ["unless", "you may", "if you don't"]
                    )
                    enters_tapped = has_tapped_phrase and not has_conditional

                    lands.append(Land(
                        name=input_card_name,
                        colors=colors,
                        enters_tapped=enters_tapped,
                        quantity=quantity,
                        is_mdfc=False
                    ))
                else:
                    spells.append(Spell(
                        name=input_card_name,
                        mana_cost=card_data.get("mana_cost", ""),
                        quantity=quantity,
                        is_mdfc=False
                    ))

    return spells, lands