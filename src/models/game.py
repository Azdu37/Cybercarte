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
            # 4 cartes infra
            for _ in range(INITIAL_HAND_SIZE):
                if self.infrastructure_deck:
                    player.add_to_hand(self.infrastructure_deck.pop())
            
            # Attribution d'un objectif
            objectives = [
                {"id": "SHIELD_WALL", "name": "Mur de Feu", "desc": "Avoir 3 protections"},
                {"id": "VERTICAL_LINK", "name": "Lien Vertical", "desc": "Une colonne complète"},
                {"id": "HORIZONTAL_LINK", "name": "Lien Horizontal", "desc": "Une ligne complète"},
                {"id": "DIVERSITY", "name": "Diversité", "desc": "3 machines différentes"}
            ]
            player.objective = random.choice(objectives)

    def initialize_decks(self):
        # Cartes Machine (Infrastructure)
        for i in range(30):
            # Variété de connexions
            c_type = random.choice([
                {'top': Connection.LINK, 'bottom': Connection.LINK, 'left': Connection.LINK, 'right': Connection.LINK},
                {'top': Connection.LINK, 'bottom': Connection.LINK, 'left': Connection.NONE, 'right': Connection.NONE},
                {'top': Connection.NONE, 'bottom': Connection.NONE, 'left': Connection.LINK, 'right': Connection.LINK},
                {'top': Connection.LINK, 'bottom': Connection.NONE, 'left': Connection.NONE, 'right': Connection.LINK},
            ])
            c = Card(i, f"Machine {i}", CardType.INFRASTRUCTURE, CardCategory.MACHINE, c_type)
            self.infrastructure_deck.append(c)
        
        # Cartes Protection
        for i in range(10):
            c = Card(i+100, f"Firewall {i}", CardType.INFRASTRUCTURE, CardCategory.PROTECTION)
            self.infrastructure_deck.append(c)

        # Cartes Attaque (mises dans la pioche bonus pour le moment)
        for i in range(10):
            c = Card(i+200, f"Attaque {i}", CardType.BONUS_MALUS, CardCategory.ATTACK, effect_id="DISCONNECT_RANDOM")
            self.bonus_malus_deck.append(c)
        
        for i in range(5):
            c = Card(i+250, f"Virus {i}", CardType.BONUS_MALUS, CardCategory.ATTACK, effect_id="STEAL_CARD")
            self.bonus_malus_deck.append(c)

        # Cartes Utilitaires
        for i in range(10):
            c = Card(i+300, f"Scanner {i}", CardType.BONUS_MALUS, CardCategory.UTILITY, effect_id="DRAW_2")
            self.bonus_malus_deck.append(c)

        # Cartes Événement
        events = [
            ("Mise à jour", "UPGRADE", "Tout le monde pioche 1 carte"),
            ("Cyber-attaque", "CYBER_ATTACK", "Une carte au hasard déconnectée (sauf protection)"),
            ("Maintenance", "MAINTENANCE", "Tout le monde répare une carte"),
            ("Surcharge", "OVERLOAD", "Perte d'une action au prochain tour")
        ]
        for i, (name, eid, desc) in enumerate(events):
            c = Card(i+400, name, CardType.EVENT, CardCategory.UTILITY, effect_id=eid, description=desc)
            self.event_deck.append(c)
            
        random.shuffle(self.infrastructure_deck)
        random.shuffle(self.bonus_malus_deck)
        random.shuffle(self.event_deck)

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
                success, message = self.apply_immediate_effect(player, card)
            else:
                message = "Pioche bonus/malus vide"

        elif action_type == ACTION_PLAY_CARD:
            card_index = kwargs.get('card_index')
            x = kwargs.get('x')
            y = kwargs.get('y')
            card = player.hand[card_index] if 0 <= card_index < len(player.hand) else None
            
            if card and card.category == CardCategory.PROTECTION:
                # Protection peut être attachée ou posée
                if (x, y) in player.grid:
                    if player.attach_protection_to_card(card_index, x, y):
                        success = True
                    else:
                        message = "Impossible d'attacher ici"
                else:
                    if player.play_card(card_index, x, y):
                        success = True
                    else:
                        message = "Placement impossible"
            elif player.play_card(card_index, x, y):
                success = True
            else:
                message = "Placement impossible"

        if success:
            player.actions_left -= 1
        
        return success, message

    def apply_immediate_effect(self, player, card):
        message = f"Carte tirée: {card.name}"
        if card.effect_id == "DISCONNECT_RANDOM":
            # Cible un autre joueur au hasard
            targets = [p for p in self.players if p != player]
            if targets:
                target = random.choice(targets)
                if target.grid:
                    pos = random.choice(list(target.grid.keys()))
                    target_card = target.grid[pos]
                    if target.has_protection():
                        message = f"Attaque sur {target.name} bloquée par un Firewall!"
                    else:
                        target_card.disconnect()
                        message = f"Attaque réussie! Une carte de {target.name} est déconnectée."
                else:
                    message = f"Attaque sur {target.name} a échoué (grille vide)."
            else:
                message = "Aucune cible pour l'attaque."
        
        elif card.effect_id == "STEAL_CARD":
            targets = [p for p in self.players if p != player]
            if targets:
                target = random.choice(targets)
                if target.hand:
                    stolen = target.hand.pop(random.randint(0, len(target.hand)-1))
                    player.add_to_hand(stolen)
                    message = f"Virus! Vous avez volé une carte à {target.name}."
                else:
                    message = f"Le virus sur {target.name} a échoué (main vide)."
            else:
                message = "Aucune cible pour le virus."

        elif card.effect_id == "DRAW_2":
            for _ in range(2):
                if self.infrastructure_deck:
                    player.add_to_hand(self.infrastructure_deck.pop())
            message = "Scanner: vous piochez 2 cartes infrastructure."
            
        return True, message

    def next_turn(self):
        messages = []
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            if self.round_count % EVENT_FREQUENCY == 0:
                event_msgs = self.trigger_event()
                messages.extend(event_msgs)
            self.round_count += 1
        
        self.start_turn()
        return messages

    def trigger_event(self):
        if self.event_deck:
            event_card = self.event_deck.pop()
            # Appliquer l'effet à tous les joueurs
            for player in self.players:
                self.apply_event_effect(player, event_card)
            return [f"ÉVÉNEMENT: {event_card.name}", event_card.description]
        return ["Pas d'événement cette fois."]

    def apply_event_effect(self, player, event_card):
        if event_card.effect_id == "UPGRADE":
            if self.infrastructure_deck:
                player.add_to_hand(self.infrastructure_deck.pop())
        
        elif event_card.effect_id == "CYBER_ATTACK":
            if not player.has_protection() and player.grid:
                pos = random.choice(list(player.grid.keys()))
                player.grid[pos].disconnect()
        
        elif event_card.effect_id == "MAINTENANCE":
            for card in player.grid.values():
                if card.is_flipped:
                    card.repair()
                    break
        
        elif event_card.effect_id == "OVERLOAD":
            player.actions_left = max(0, player.actions_left - 1)

    def check_victory(self):
        for player in self.players:
            player.calculate_score()
            # On vérifie si le joueur a 9 cartes connectées
            connected_count = sum(1 for card in player.grid.values() if not card.is_flipped)
            if connected_count >= INFRASTRUCTURE_VICTORY_COUNT:
                return player
        return None
