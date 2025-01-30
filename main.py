from typing import List
from card_classes import Spell, Land
from deck_parser import parse_deck

def print_deck(spells: List[Spell], lands: List[Land]):
    print("=== Spells ===")
    for spell in spells:
        mdfc_note = " (MDFC)" if spell.is_mdfc else ""
        print(f"{spell.quantity}x {spell.name}{mdfc_note}: {spell.mana_cost}")
    
    print("\n=== Lands ===")
    for land in lands:
        tapped_status = "Tapped" if land.enters_tapped else "Untapped"
        mdfc_note = " (MDFC)" if land.is_mdfc else ""
        print(f"{land.quantity}x {land.name}{mdfc_note}: {land.colors}, {tapped_status}")

    # Calculate totals (exclude MDFC spells from spell count)
    total_spells = sum(spell.quantity for spell in spells if not spell.is_mdfc)
    total_lands = sum(land.quantity for land in lands)
    total_cards = total_spells + total_lands

    print("\n=== Totals ===")
    print(f"Non-MDFC Spells: {total_spells}")
    print(f"Lands (including MDFCs): {total_lands}")
    print(f"Total Cards: {total_cards}")

if __name__ == "__main__":
    spells, lands = parse_deck("deck.txt")
    print_deck(spells, lands)