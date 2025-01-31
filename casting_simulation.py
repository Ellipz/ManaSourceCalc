import random
from datetime import datetime
import re
from typing import List, Dict, Tuple
from card_classes import Spell, Land

class CastingSimulator:
    def __init__(self, spells: List[Spell], lands: List[Land], deck_size: int = 60):
        self.spells = spells
        self.lands = lands
        self.deck_size = deck_size
        self.total_lands = sum(land.quantity for land in lands)
        self.color_sources = self._calculate_color_sources()
        
    def _calculate_color_sources(self) -> Dict[str, int]:
        color_counts = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0}
        for land in self.lands:
            for color in land.colors:
                if color in color_counts:
                    color_counts[color] += land.quantity
        return color_counts

    def _parse_mana_cost(self, cost: str) -> Dict[str, int]:
        requirements = {
            'generic': 0,
            'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0
        }
        
        if not cost:
            return requirements
            
        symbols = re.findall(r"{([WUBRGCX/\d]+)}", cost)
        for symbol in symbols:
            if '/' in symbol:
                options = symbol.split('/')
                for color in options:
                    if color in requirements:
                        requirements[color] += 1
            elif symbol.isdigit():
                requirements['generic'] += int(symbol)
            elif symbol in requirements:
                requirements[symbol] += 1
                
        return requirements

    # CHANGED: Added colorless ('C') handling
    def _simulate_mana_availability(self, turn: int) -> Tuple[int, Dict[str, int]]:
        """Simulate mana development through specified turn"""
        deck = []
        for land in self.lands:
            deck += [land] * land.quantity
        deck += [None] * (self.deck_size - self.total_lands)
        random.shuffle(deck)
        
        # Initialize mana tracking with colorless support
        available_mana = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'C': 0}  # Added 'C'
        total_lands_played = 0
        
        # Mulligan logic (unchanged)
        hand_size = 7
        keep_hand = False
        for mulligans in range(4):
            hand = [c for c in deck[:hand_size] if c is not None]
            land_count = len([c for c in hand if isinstance(c, Land)])
            
            if 2 <= land_count <= 5:
                keep_hand = True
                break
                
            hand_size -= 1
            deck = deck[hand_size:]
            
        if not keep_hand:
            return 0, {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'C': 0}  # Added 'C'

        # Land processing with colorless support
        drawn_cards = deck[:7 + turn - 1]
        for card in drawn_cards:
            if isinstance(card, Land) and total_lands_played < turn:
                total_lands_played += 1
                for color in card.colors:
                    # CHANGED: Handle colorless mana
                    if color == 'C':
                        available_mana['C'] += 1
                    elif color in available_mana:
                        available_mana[color] += 1
                        
        return total_lands_played, available_mana

    # CHANGED: Updated casting probability calculation
    def calculate_cast_probability(self, spell: Spell, turn: int, simulations: int = 10000) -> float:
        requirements = self._parse_mana_cost(spell.mana_cost)
        successes = 0
        
        # Get colored requirements (excluding generic)
        colored_reqs = {c: requirements[c] for c in ['W', 'U', 'B', 'R', 'G']}
        total_required = requirements['generic'] + sum(colored_reqs.values())
        
        for _ in range(simulations):
            lands_available, mana = self._simulate_mana_availability(turn)
            
            # Check color requirements
            color_ok = all(mana[c] >= req for c, req in colored_reqs.items() if req > 0)
            
            # Check total mana requirements (generic can be any color)
            total_ok = lands_available >= total_required
            
            if color_ok and total_ok:
                successes += 1
                
        return successes / simulations

    def analyze_deck(self, output_file: str = 'analysis.txt'):
        report = [
            f"Mana Base Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Lands: {self.total_lands}",
            "Color Sources:",
            f"- White: {self.color_sources['W']}",
            f"- Blue: {self.color_sources['U']}",
            f"- Black: {self.color_sources['B']}",
            f"- Red: {self.color_sources['R']}",
            f"- Green: {self.color_sources['G']}",
            "\nCasting Probabilities:"
        ]
        
        results = []
        for spell in self.spells:
            if spell.is_mdfc:
                continue  # Skip MDFC spell sides
                
            cmc = sum(self._parse_mana_cost(spell.mana_cost).values())
            target_turn = max(1, cmc)
            probability = self.calculate_cast_probability(spell, target_turn)
            results.append((spell.name, target_turn, probability))
            
            report.append(f"{spell.name} (Turn {target_turn}): {probability:.1%}")

        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
            
        return sorted(results, key=lambda x: x[2], reverse=True)