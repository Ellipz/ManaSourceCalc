import random
from datetime import datetime

def simulate_mana_base(
    deck_size=60,
    total_lands=24,
    good_lands=12,
    turn_requirement=4,
    colored_mana_needed=2,
    simulations=100000,
    output_file='ManaSimResults.txt'
):
    """
    Monte Carlo simulator for MTG mana base consistency
    
    Parameters:
        deck_size (int): Total cards in deck
        total_lands (int): Total number of lands
        good_lands (int): Number of colored sources
        turn_requirement (int): Target turn to cast spell
        colored_mana_needed (int): Required colored mana symbols
        simulations (int): Number of iterations
        output_file (str): Results file name
    """
    
    # Input validation
    if total_lands > deck_size:
        raise ValueError("Total lands cannot exceed deck size")
    if good_lands > total_lands:
        raise ValueError("Colored sources cannot exceed total lands")
    if colored_mana_needed > turn_requirement:
        raise ValueError("Colored mana needed cannot exceed turn requirement")
    
    # Initialize deck composition
    other_lands = total_lands - good_lands
    non_land_cards = deck_size - total_lands
    
    deck = {
        'Spell': non_land_cards,
        'Good Land': good_lands,
        'Other Land': other_lands
    }
    
    # Configure output
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result_header = (
        f"\n\n===== Simulation Results ({timestamp}) =====\n"
        f"Deck Size: {deck_size}\n"
        f"Total Lands: {total_lands}\n"
        f"Colored Sources: {good_lands}\n"
        f"Target Turn: {turn_requirement}\n"
        f"Colored Mana Needed: {colored_mana_needed}\n"
        f"Simulations: {simulations:,}\n"
    )
    
    # Core simulation functions
    def put_lands_on_bottom(hand, num_to_bottom):
        """Prioritize keeping colored sources when bottoming lands"""
        bottom_other = min(hand['Other Land'], num_to_bottom)
        hand['Other Land'] -= bottom_other
        bottom_good = min(hand['Good Land'], num_to_bottom - bottom_other)
        hand['Good Land'] -= bottom_good
    
    def total_lands_in_hand(hand):
        return hand['Good Land'] + hand['Other Land']
    
    def simulate_game():
        """Run one complete game simulation"""
        keep_hand = False
        hand = {'Spell': 0, 'Good Land': 0, 'Other Land': 0}
        
        # Mulligan logic sequence
        for mulligan_step in ['initial', 7, 6, 5, 4]:
            if keep_hand:
                break
                
            # Build and shuffle library
            library = []
            for card, count in deck.items():
                library += [card] * count
            random.shuffle(library)
            
            # Draw initial hand
            hand = {'Spell': 0, 'Good Land': 0, 'Other Land': 0}
            for _ in range(7):
                card = library.pop(0)
                hand[card] += 1
            
            # Commander special mulligan (free first mulligan)
            if mulligan_step == 'initial' and deck_size == 99:
                keep_hand = 3 <= total_lands_in_hand(hand) <= 5
                continue
            
            # Regular mulligan decisions
            if mulligan_step == 7:
                keep_hand = 2 <= total_lands_in_hand(hand) <= 5
            elif mulligan_step == 6:
                if hand['Spell'] > 3:
                    hand['Spell'] -= 1
                else:
                    put_lands_on_bottom(hand, 1)
                keep_hand = 2 <= total_lands_in_hand(hand) <= 4
            elif mulligan_step == 5:
                if hand['Spell'] > 3:
                    hand['Spell'] -= 2
                elif hand['Spell'] == 3:
                    put_lands_on_bottom(hand, 1)
                    hand['Spell'] -= 1
                else:
                    put_lands_on_bottom(hand, 2)
                keep_hand = 2 <= total_lands_in_hand(hand) <= 4
            elif mulligan_step == 4:
                if hand['Spell'] > 3:
                    hand['Spell'] -= 3
                elif hand['Spell'] == 3:
                    put_lands_on_bottom(hand, 1)
                    hand['Spell'] -= 2
                elif hand['Spell'] == 2:
                    put_lands_on_bottom(hand, 2)
                    hand['Spell'] -= 1
                else:
                    put_lands_on_bottom(hand, 3)
                keep_hand = True
        
        # Commander opening draw
        if deck_size == 99:
            hand[library.pop(0)] += 1
        
        # Draw for subsequent turns
        for turn in range(2, turn_requirement + 1):
            hand[library.pop(0)] += 1
        
        # Determine outcome
        total = total_lands_in_hand(hand)
        if total < turn_requirement:
            return 'not_enough_lands'
        return 'success' if hand['Good Land'] >= colored_mana_needed else 'color_failure'
    
    # Run simulations
    results = {'success': 0, 'color_failure': 0, 'not_enough_lands': 0}
    
    for _ in range(simulations):
        outcome = simulate_game()
        results[outcome] += 1
    
    # Calculate probabilities
    relevant_games = results['success'] + results['color_failure']
    success_rate = (results['success'] / relevant_games * 100) if relevant_games > 0 else 0
    
    # Generate report
    report = (
        f"Success Rate: {success_rate:.2f}%\n"
        f"Breakdown:\n"
        f"- Able to cast: {results['success']:,} ({results['success']/simulations*100:.1f}%)\n"
        f"- Wrong colors: {results['color_failure']:,} ({results['color_failure']/simulations*100:.1f}%)\n"
        f"- Not enough lands: {results['not_enough_lands']:,} ({results['not_enough_lands']/simulations*100:.1f}%)\n"
    )
    
    # Write to file and console
    with open(output_file, 'a') as f:
        f.write(result_header)
        f.write(report)
    
    print(result_header)
    print(report)
    return success_rate

# Example usage
if __name__ == "__main__":
    # Standard 60-card deck
    simulate_mana_base(
        deck_size=60,
        total_lands=24,
        good_lands=15,
        turn_requirement=4,
        colored_mana_needed=2,
        simulations=100000
    )

    # Commander deck
    simulate_mana_base(
        deck_size=99,
        total_lands=41,
        good_lands=18,
        turn_requirement=3,
        colored_mana_needed=1,
        simulations=50000
    )

    # Aggro deck example
    simulate_mana_base(
        deck_size=60,
        total_lands=20,
        good_lands=14,
        turn_requirement=3,
        colored_mana_needed=2,
        simulations=100000
    )