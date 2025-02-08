from flask import Flask, render_template
import plotly.graph_objs as go
import re
from typing import List, Dict, Tuple
from deck_parser import parse_deck

app = Flask(__name__)

def parse_analysis_results() -> List[Tuple[str, int, float]]:
    results = []
    with open('analysis.txt', 'r') as f:
        for line in f:
            match = re.match(r"(.+) \(Turn (\d+)\): (\d+\.\d+)%", line.strip())
            if match:
                name = match.group(1)
                turn = int(match.group(2))
                prob = float(match.group(3)) / 100
                results.append((name, turn, prob))
    return results

def get_mana_sources(lands: List[Dict]) -> Dict[str, int]:
    colors = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'C': 0}
    for land in lands:
        for color in land['colors']:
            if color in colors:
                colors[color] += land['quantity']
    return colors

@app.route('/')
def dashboard():
    # Load analysis results
    casting_probs = parse_analysis_results()
    
    # Get parsed deck data
    _, lands = parse_deck('deck.txt')
    
    # Create mana source data
    mana_sources = get_mana_sources([
        {'colors': land.colors, 'quantity': land.quantity} 
        for land in lands
    ])
    
    # Prepare chart data with safe key names
    charts = {
        'mana_sources': {
            'data_values': [v for v in mana_sources.values() if v > 0],
            'data_labels': [k for k, v in mana_sources.items() if v > 0],
            'title': 'Mana Source Distribution'
        },
        'casting_probs': {
            'spell_names': [x[0] for x in casting_probs],
            'probabilities': [x[2]*100 for x in casting_probs],
            'title': 'Casting Probabilities by Turn'
        }
    }
    
    return render_template('dashboard.html', 
                         charts=charts,
                         casting_probs=casting_probs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)