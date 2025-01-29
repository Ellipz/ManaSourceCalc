from card_classes import Spell, Land
from deck_parser import parse_deck

def print_deck(spells: list[Spell], lands: list[Land]):
    print("\n=== Deck List with Mana Symbols ===")
    print("\nSpells:")
    for spell in spells:
        print(f"{spell.quantity}x {spell.name}: {spell.mana_cost}")
    
    print("\nLands:")
    for land in lands:
        tapped_status = "Tapped" if land.enters_tapped else "Untapped"
        print(f"{land.quantity}x {land.name} (Colors: {land.colors}, {tapped_status})")

if __name__ == "__main__":
    spells, lands = parse_deck("deck.txt")
    print_deck(spells, lands)