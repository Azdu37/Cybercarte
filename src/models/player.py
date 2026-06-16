"""
Représentation d'un joueur.

Reprend l'idée de `actions_left` et `color` du projet Cybercarte,
combinée avec notre vrai système de réseau tentaculaire.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from .card import Card
from .network import Network
from src.utils.constants import ACTIONS_PER_TURN, INFRASTRUCTURE_VICTORY_COUNT

Position = tuple[int, int]


@dataclass
class Player:
    player_id: int
    name: str
    color: tuple[int, int, int]

    hand: list[Card] = field(default_factory=list)
    network: Network = field(default_factory=Network)
    score: int = 0
    actions_left: int = ACTIONS_PER_TURN
    personal_objective_accomplished: bool = False
    objectif: Optional[Card] = None

    def add_to_hand(self, carte: Card) -> None:
        self.hand.append(carte)

    def can_place_card(self, carte: Card, pos: Position) -> bool:
        return self.network.peut_poser(carte, pos)

    def valid_positions(self, carte: Card) -> list[Position]:
        return self.network.positions_valides(carte)

    def play_card(self, card_index: int, pos: Position) -> bool:
        if not (0 <= card_index < len(self.hand)):
            return False
        carte = self.hand[card_index]
        if not self.can_place_card(carte, pos):
            return False
        self.network.poser_carte(carte, pos)
        self.hand.pop(card_index)
        return True

    def has_protection(self) -> bool:
        """Vérifie si une carte de protection active est présente (repris de Cybercarte)."""
        for cel in self.network.grille.values():
            if cel.etat.value == "vivante":
                if cel.carte.categorie.value == "protection":
                    return True
                if cel.protection is not None:
                    return True
        return False

    def nombre_cartes_actives(self) -> int:
        return self.network.nombre_cartes_actives()

    def calculate_score(self) -> int:
        base = self.nombre_cartes_actives()
        bonus = 5 if self.personal_objective_accomplished else 0
        self.score = base + bonus
        return self.score

    def reset_actions(self) -> None:
        self.actions_left = ACTIONS_PER_TURN

    def a_gagne(self) -> bool:
        return self.nombre_cartes_actives() >= INFRASTRUCTURE_VICTORY_COUNT

    def __repr__(self) -> str:
        return f"Player({self.name}, score={self.score}, cartes={self.nombre_cartes_actives()})"
