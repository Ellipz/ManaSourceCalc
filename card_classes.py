from dataclasses import dataclass
from typing import List

@dataclass
class Spell:
    name: str
    mana_cost: str
    quantity: int
    is_mdfc: bool  

@dataclass
class Land:
    name: str
    colors: List[str]
    enters_tapped: bool
    quantity: int
    is_mdfc: bool