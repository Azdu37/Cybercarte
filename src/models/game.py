"""
Modèle de partie : joueurs, piles de cartes, tours, événements, victoire.

Reprend la structure de Game (Cybercarte) avec nos vrais connecteurs.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Optional
from .card import Card, load_cards
from .network import EtatCellule
from .player import Player
from .enums import CategorieCarte
from src.utils.constants import (
    PLAYER_COLORS, ACTIONS_PER_TURN, EVENT_FREQUENCY,
    INFRASTRUCTURE_VICTORY_COUNT, INITIAL_HAND_SIZE,
    ACTION_DRAW_INFRA, ACTION_DRAW_BONUS, ACTION_PLAY_CARD,
)

import os
CHEMIN_CARTES_INFRA = os.path.join(os.path.dirname(__file__), "..", "..", "data", "infrastructure_cards.json")
CHEMIN_CARTES_BONUS = os.path.join(os.path.dirname(__file__), "..", "..", "data", "bonus_malus_cards.json")
CHEMIN_CARTES_EVENT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "event_cards.json")
CHEMIN_CARTES_OBJECTIFS = os.path.join(os.path.dirname(__file__), "..", "..", "data", "objective_cards.json")


@dataclass
class Game:
    players: list[Player] = field(default_factory=list)
    current_player_index: int = 0
    round_count: int = 1          # nombre de tours complets joués (tous joueurs)
    turn_count: int = 0           # tours individuels joués depuis dernier événement

    infrastructure_deck: list[Card] = field(default_factory=list)
    bonus_malus_deck:    list[Card] = field(default_factory=list)
    event_deck:          list[Card] = field(default_factory=list)
    objective_deck:      list[Card] = field(default_factory=list)
    discard_pile:        list[Card] = field(default_factory=list)

    last_message: str = ""  # dernier message d'info à afficher dans la vue
    last_event: Optional[str] = None

    def setup(self, player_count: int) -> None:
        infra_cards = load_cards(CHEMIN_CARTES_INFRA)
        bonus_cards = self._load_cards_safe(CHEMIN_CARTES_BONUS)
        event_cards = self._load_cards_safe(CHEMIN_CARTES_EVENT)
        objective_cards = self._load_cards_safe(CHEMIN_CARTES_OBJECTIFS)

        infra_pool = [card for card in infra_cards.values()
                      if card.categorie in (CategorieCarte.INFRASTRUCTURE, CategorieCarte.PROTECTION)]
        bonus_pool = [card for card in bonus_cards if card.categorie in (CategorieCarte.BONUS, CategorieCarte.MALUS)]
        event_pool = [card for card in event_cards if card.categorie == CategorieCarte.EVENEMENT]
        objective_pool = [card for card in objective_cards if card.categorie == CategorieCarte.OBJECTIF]

        if not bonus_pool:
            for i in range(6):
                bonus_pool.append(Card(
                    id=f"bonus_def_{i}",
                    nom=f"Bonus Rapide {i}",
                    categorie=CategorieCarte.BONUS,
                    description="Répare une carte bloquée.",
                    effets={"type": "reparer", "count": "1"},
                ))

        if not event_pool:
            for i in range(3):
                event_pool.append(Card(
                    id=f"event_def_{i}",
                    nom=f"Événement {i}",
                    categorie=CategorieCarte.EVENEMENT,
                    description="Un événement global perturbe le réseau.",
                    effets={"type": "deconnecter", "target": "self", "count": "1"},
                ))

        random.shuffle(infra_pool)
        random.shuffle(bonus_pool)
        random.shuffle(event_pool)
        random.shuffle(objective_pool)

        self.players = [
            Player(player_id=i, name=f"Joueur {i+1}", color=PLAYER_COLORS[i])
            for i in range(player_count)
        ]

        for player in self.players:
            for _ in range(INITIAL_HAND_SIZE):
                if infra_pool:
                    player.add_to_hand(infra_pool.pop())

        self.infrastructure_deck = infra_pool
        self.bonus_malus_deck = bonus_pool
        self.event_deck = event_pool
        self.objective_deck = objective_pool

        for i, player in enumerate(self.players):
            if objective_pool:
                player.objectif = objective_pool[i % len(objective_pool)]

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

    def _load_cards_safe(self, chemin: str) -> list[Card]:
        if os.path.exists(chemin):
            return list(load_cards(chemin).values())
        return []

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
            self.last_event = card.nom
            for player in self.players:
                self.apply_event_effect(player, card)
            self.last_message = f"Événement : {card.nom}"

    def apply_immediate_effect(self, player: Player, card: Card) -> None:
        self.last_event = card.nom
        self._resolve_effect(player, card, source="bonus")

    def apply_event_effect(self, player: Player, card: Card) -> None:
        self._resolve_effect(player, card, source="event")

    def _resolve_effect(self, player: Player, card: Card, source: str = "bonus") -> None:
        effets = card.effets
        if not effets:
            if card.categorie == CategorieCarte.BONUS:
                self._repair_dead_cards(player, 1, card)
                return
            if card.categorie == CategorieCarte.MALUS:
                self._deconnect_cards(player, target="random_opponent", count=1, card=card)
                return
            if card.categorie == CategorieCarte.EVENEMENT:
                self._deconnect_cards(player, target="self", count=1, card=card)
                return

        effet_type = effets.get("type", "")
        count = int(effets.get("count", "1"))
        target = effets.get("target", "self")
        tag = effets.get("tag")

        if effet_type == "reparer":
            self._repair_dead_cards(player, count, card)
        elif effet_type == "deconnecter":
            self._deconnect_cards(player, target=target, count=count, tag=tag, card=card)
        elif effet_type == "pioche":
            if self.infrastructure_deck:
                player.add_to_hand(self.infrastructure_deck.pop())
        else:
            # Effet inconnu : on tente un comportement par défaut.
            if card.categorie == CategorieCarte.BONUS:
                self._repair_dead_cards(player, 1, card)
            elif card.categorie == CategorieCarte.MALUS:
                self._deconnect_cards(player, target="random_opponent", count=1, card=card)
            elif card.categorie == CategorieCarte.EVENEMENT:
                self._deconnect_cards(player, target="self", count=1, card=card)

    def _deconnect_cards(
        self,
        player: Player,
        *,
        target: str = "self",
        count: int = 1,
        tag: str | None = None,
        card: Card | None = None,
    ) -> None:
        if target == "self":
            targets = [player]
        elif target == "opponents":
            targets = [p for p in self.players if p is not player]
        elif target == "random_opponent":
            opponents = [p for p in self.players if p is not player]
            targets = [random.choice(opponents)] if opponents else []
        elif target == "all":
            targets = list(self.players)
        else:
            targets = [player]

        for target_player in targets:
            if target_player.has_protection():
                continue
            active_positions = [
                pos for pos, cel in target_player.network.grille.items()
                if cel.etat == EtatCellule.VIVANTE and (tag is None or tag in cel.carte.tags)
            ]
            if not active_positions:
                continue
            chosen = random.sample(active_positions, min(count, len(active_positions)))
            for pos in chosen:
                target_player.network.deconnecter(pos)

    def _repair_dead_cards(self, player: Player, count: int, card: Card | None = None) -> None:
        dead_positions = player.network.positions_trous()
        if not dead_positions:
            return
        chosen = random.sample(dead_positions, min(count, len(dead_positions)))
        for pos in chosen:
            player.network.reconnecter(pos)

    def check_victory(self) -> Optional[Player]:
        for player in self.players:
            player.calculate_score()
            if player.a_gagne():
                return player
        return None
