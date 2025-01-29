from dataclasses import dataclass
from typing import List

@dataclass
class Spell:
    name: str
    mana_cost: str  # Mana symbols (e.g., "{B/G}")
    quantity: int

@dataclass
class Land:
    name: str
    colors: List[str]
    enters_tapped: bool
    quantity: int