"""
Modèle de partie : joueurs, piles de cartes, tours, événements, victoire.

Reprend la structure de Game (Cybercarte) avec nos vrais connecteurs.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Optional
from .card import Card, load_cards
from .player import Player
from src.utils.constants import (
    PLAYER_COLORS, ACTIONS_PER_TURN, EVENT_FREQUENCY,
    INFRASTRUCTURE_VICTORY_COUNT, INITIAL_HAND_SIZE,
    ACTION_DRAW_INFRA, ACTION_DRAW_BONUS, ACTION_PLAY_CARD,
)

import os
CHEMIN_CARTES = os.path.join(os.path.dirname(__file__), "..", "..", "data", "infrastructure_cards.json")


@dataclass
class Game:
    players: list[Player] = field(default_factory=list)
    current_player_index: int = 0
    round_count: int = 1          # nombre de tours complets joués (tous joueurs)
    turn_count: int = 0           # tours individuels joués depuis dernier événement

    infrastructure_deck: list[Card] = field(default_factory=list)
    bonus_malus_deck:    list[Card] = field(default_factory=list)
    event_deck:          list[Card] = field(default_factory=list)
    discard_pile:        list[Card] = field(default_factory=list)

    last_message: str = ""  # dernier message d'info à afficher dans la vue

    def setup(self, player_count: int) -> None:
        all_cards = load_cards(CHEMIN_CARTES)
        deck = list(all_cards.values())
        random.shuffle(deck)

        self.players = [
            Player(player_id=i, name=f"Joueur {i+1}", color=PLAYER_COLORS[i])
            for i in range(player_count)
        ]

        # Distribution initiale
        idx = 0
        for player in self.players:
            for _ in range(INITIAL_HAND_SIZE):
                player.add_to_hand(deck[idx])
                idx += 1
        self.infrastructure_deck = deck[idx:]

        self.start_turn()

    # ------------------------------------------------------------------
    # Tour / actions
    # ------------------------------------------------------------------
    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def start_turn(self) -> None:
        self.current_player.reset_actions()
        # Pioche automatique d'une carte infrastructure en début de tour
        if self.infrastructure_deck:
            self.current_player.add_to_hand(self.infrastructure_deck.pop())

    def perform_action(self, action_type: str, **kwargs) -> tuple[bool, str]:
        player = self.current_player
        if player.actions_left <= 0:
            return False, "Plus d'actions disponibles ce tour"

        success, msg = False, ""

        if action_type == ACTION_DRAW_INFRA:
            if self.infrastructure_deck:
                player.add_to_hand(self.infrastructure_deck.pop())
                success, msg = True, "Carte infrastructure piochée"
            else:
                msg = "Pioche infrastructure vide"

        elif action_type == ACTION_DRAW_BONUS:
            if self.bonus_malus_deck:
                card = self.bonus_malus_deck.pop()
                self.apply_immediate_effect(player, card)
                success, msg = True, f"Carte bonus/malus : {card.nom}"
            else:
                msg = "Pioche bonus/malus vide"

        elif action_type == ACTION_PLAY_CARD:
            card_index = kwargs.get("card_index")
            pos = kwargs.get("pos")
            if player.play_card(card_index, pos):
                success, msg = True, "Carte posée"
            else:
                msg = "Placement impossible"

        if success:
            player.actions_left -= 1

        self.last_message = msg
        return success, msg

    def next_turn(self) -> None:
        """Passe au joueur suivant, déclenche un événement si besoin."""
        self.turn_count += 1
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # Un "tour complet" = tous les joueurs ont joué
        if self.current_player_index == 0:
            self.round_count += 1
            if self.round_count % EVENT_FREQUENCY == 0:
                self.trigger_event()

        self.start_turn()

    def trigger_event(self) -> None:
        if self.event_deck:
            card = self.event_deck.pop()
            for player in self.players:
                self.apply_event_effect(player, card)
            self.last_message = f"Événement : {card.nom}"

    def apply_immediate_effect(self, player: Player, card: Card) -> None:
        pass  # sera implémenté dans effects.py

    def apply_event_effect(self, player: Player, card: Card) -> None:
        pass  # sera implémenté dans effects.py

    def check_victory(self) -> Optional[Player]:
        for player in self.players:
            player.calculate_score()
            if player.a_gagne():
                return player
        return None
