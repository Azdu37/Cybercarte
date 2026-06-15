import random
from src.models.player import Player
from src.models.card import Card, CardType

class Game:
    def __init__(self, player_count):
        self.players = []
        self.current_player_index = 0
        self.turn_count = 0
        self.round_count = 0
        
        # Pioches
        self.infrastructure_deck = []
        self.bonus_malus_deck = []
        self.event_deck = []
        
        self.setup_game(player_count)

    def setup_game(self, player_count):
        # Initialisation des joueurs
        from src.utils.constants import PLAYER_COLORS
        for i in range(player_count):
            self.players.append(Player(i, f"Joueur {i+1}", PLAYER_COLORS[i]))
        
        # Initialisation des pioches (à remplir avec de vraies cartes)
        self.initialize_decks()
        
        # Distribution initiale : 4 cartes infrastructure par joueur
        for player in self.players:
            for _ in range(4):
                if self.infrastructure_deck:
                    player.add_to_hand(self.infrastructure_deck.pop())

    def initialize_decks(self):
        # Logique de création des cartes
        pass

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            self.round_count += 1
            self.handle_end_of_round()

    def handle_end_of_round(self):
        # Une manche sur deux (ou trois), tirer une carte événement
        if self.round_count % 2 == 0:
            self.trigger_event()

    def trigger_event(self):
        if self.event_deck:
            event_card = self.event_deck.pop()
            # Appliquer l'effet à tous les joueurs
            pass

    def check_victory(self):
        for player in self.players:
            connected_cards = sum(1 for card in player.infrastructure if card.is_connected)
            if connected_cards >= 9: # À ajuster selon les besoins
                return player
        return None
