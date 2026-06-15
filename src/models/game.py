import random
from src.models.player import Player
from src.models.card import Card, CardType, CardCategory, Connection
from src.utils.constants import (
    PLAYER_COLORS, ACTIONS_PER_TURN, EVENT_FREQUENCY, 
    INFRASTRUCTURE_VICTORY_COUNT, INITIAL_HAND_SIZE,
    ACTION_DRAW_INFRA, ACTION_DRAW_BONUS, ACTION_PLAY_CARD
)

class Game:
    def __init__(self, player_count):
        self.players = []
        self.current_player_index = 0
        self.round_count = 1
        
        # Pioches
        self.infrastructure_deck = []
        self.bonus_malus_deck = []
        self.event_deck = []
        self.discard_pile = []
        
        self.setup_game(player_count)
        self.start_turn() # Le premier joueur commence son tour

    def setup_game(self, player_count):
        # Initialisation des joueurs
        for i in range(player_count):
            self.players.append(Player(i, f"Joueur {i+1}", PLAYER_COLORS[i]))
        
        # Initialisation des pioches
        self.initialize_decks()
        
        # Distribution initiale
        for player in self.players:
            for _ in range(INITIAL_HAND_SIZE):
                if self.infrastructure_deck:
                    player.add_to_hand(self.infrastructure_deck.pop())

    def initialize_decks(self):
        # Cette méthode sera remplacée par le chargement CSV
        # Création de quelques cartes pour test
        for i in range(40):
            # Exemple de carte machine avec des connexions partout
            connections = {
                'top': Connection.LINK,
                'bottom': Connection.LINK,
                'left': Connection.LINK,
                'right': Connection.LINK
            }
            c = Card(i, f"Machine {i}", CardType.INFRASTRUCTURE, CardCategory.MACHINE, connections)
            self.infrastructure_deck.append(c)
        
        for i in range(10):
            c = Card(i+100, f"Protection {i}", CardType.INFRASTRUCTURE, CardCategory.PROTECTION, category=CardCategory.PROTECTION)
            self.infrastructure_deck.append(c)
            
        random.shuffle(self.infrastructure_deck)

    def load_from_csv(self, infrastructure_csv, bonus_csv, events_csv):
        # Sera implémenté quand les fichiers seront dispos
        pass

    def get_current_player(self):
        return self.players[self.current_player_index]

    def start_turn(self):
        player = self.get_current_player()
        player.actions_left = ACTIONS_PER_TURN
        # Pioche automatique au début du tour
        if self.infrastructure_deck:
            player.add_to_hand(self.infrastructure_deck.pop())

    def perform_action(self, action_type, **kwargs):
        player = self.get_current_player()
        if player.actions_left <= 0:
            return False, "Plus d'actions disponibles"

        success = False
        message = ""

        if action_type == ACTION_DRAW_INFRA:
            if self.infrastructure_deck:
                player.add_to_hand(self.infrastructure_deck.pop())
                success = True
            else:
                message = "Pioche infrastructure vide"

        elif action_type == ACTION_DRAW_BONUS:
            if self.bonus_malus_deck:
                card = self.bonus_malus_deck.pop()
                self.apply_immediate_effect(player, card)
                success = True
            else:
                message = "Pioche bonus/malus vide"

        elif action_type == ACTION_PLAY_CARD:
            card_index = kwargs.get('card_index')
            x = kwargs.get('x')
            y = kwargs.get('y')
            if player.play_card(card_index, x, y):
                success = True
            else:
                message = "Placement impossible"

        if success:
            player.actions_left -= 1
            if player.actions_left == 0:
                # On pourrait passer au tour suivant automatiquement ou attendre un input
                pass
        
        return success, message

    def apply_immediate_effect(self, player, card):
        # Logique pour les cartes bonus/malus (effet immédiat)
        pass

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            self.round_count += 1
            if self.round_count % EVENT_FREQUENCY == 0:
                self.trigger_event()
        
        self.start_turn()

    def trigger_event(self):
        if self.event_deck:
            event_card = self.event_deck.pop()
            # Appliquer l'effet à tous les joueurs
            for player in self.players:
                self.apply_event_effect(player, event_card)

    def apply_event_effect(self, player, event_card):
        pass

    def check_victory(self):
        for player in self.players:
            player.calculate_score()
            # On vérifie si le joueur a 9 cartes connectées
            connected_count = sum(1 for card in player.grid.values() if not card.is_flipped)
            if connected_count >= INFRASTRUCTURE_VICTORY_COUNT:
                return player
        return None
