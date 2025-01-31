from typing import List
from card_classes import Spell, Land
from deck_parser import parse_deck
from casting_simulation import CastingSimulator

def print_deck_summary(spells: List[Spell], lands: List[Land]):
    print("=== Deck Summary ===")
    print("\nSpells:")
    for spell in spells:
        mdfc_note = " (MDFC)" if spell.is_mdfc else ""
        print(f"{spell.quantity}x {spell.name}{mdfc_note}: {spell.mana_cost}")
    
    print("\nLands:")
    for land in lands:
        tapped_status = "Tapped" if land.enters_tapped else "Untapped"
        mdfc_note = " (MDFC)" if land.is_mdfc else ""
        print(f"{land.quantity}x {land.name}{mdfc_note}: {land.colors}, {tapped_status}")

def main():
    # Parse deck
    spells, lands = parse_deck("deck.txt")
    
    # Print summary
    print_deck_summary(spells, lands)
    
    # Run simulation
    simulator = CastingSimulator(spells, lands)
    analysis_results = simulator.analyze_deck()
    
    # Print analysis
    print("\n=== Casting Analysis ===")
    for name, turn, prob in analysis_results:
        print(f"{name} (Turn {turn}): {prob:.1%}")

if __name__ == "__main__":
    main()