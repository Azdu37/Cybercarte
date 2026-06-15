from src.utils.constants import ACTIONS_PER_TURN

class Player:
    def __init__(self, player_id, name, color):
        self.player_id = player_id
        self.name = name
        self.color = color
        self.hand = []
        self.grid = {}  # {(x, y): Card}
        self.personal_objective_accomplished = False
        self.score = 0
        self.actions_left = ACTIONS_PER_TURN

    def add_to_hand(self, card):
        self.hand.append(card)

    def can_place_card(self, card, x, y):
        # On peut mettre une carte sur une carte déconnectée
        if (x, y) in self.grid:
            if not self.grid[(x, y)].is_flipped:
                return False
        
        if not self.grid:
            return True # Première carte
            
        adjacents = {
            'top': (x, y - 1),
            'bottom': (x, y + 1),
            'left': (x - 1, y),
            'right': (x + 1, y)
        }
        
        has_neighbor = False
        for direction, pos in adjacents.items():
            if pos in self.grid:
                has_neighbor = True
                neighbor = self.grid[pos]
                
                # Vérification des connecteurs
                if direction == 'top' and card.connections['top'] != neighbor.connections['bottom']:
                    return False
                if direction == 'bottom' and card.connections['bottom'] != neighbor.connections['top']:
                    return False
                if direction == 'left' and card.connections['left'] != neighbor.connections['right']:
                    return False
                if direction == 'right' and card.connections['right'] != neighbor.connections['left']:
                    return False
        
        return has_neighbor

    def play_card(self, card_index, x, y):
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]
            
            # Si c'est une carte de protection, on peut soit la poser normalement,
            # soit l'attacher à une machine existante.
            # Ici on implémente le placement sur la grille.
            if self.can_place_card(card, x, y):
                # Si on place sur une carte déconnectée, elle est détruite
                self.grid[(x, y)] = card
                self.hand.pop(card_index)
                return True
        return False

    def attach_protection_to_card(self, card_index, x, y):
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]
            if card.category.name == "PROTECTION" and (x, y) in self.grid:
                target_card = self.grid[(x, y)]
                if not target_card.is_flipped:
                    target_card.attach_protection(card)
                    self.hand.pop(card_index)
                    return True
        return False

    def calculate_score(self):
        # Chaque carte connectée compte pour 1 point
        # On considère comme connectées les cartes non retournées
        base_score = sum(1 for card in self.grid.values() if not card.is_flipped)
        bonus = 5 if self.personal_objective_accomplished else 0
        self.score = base_score + bonus
        return self.score

    def has_protection(self):
        # Vérifie si une carte de protection est présente et active dans le réseau
        # Soit comme carte indépendante, soit attachée à une machine
        for card in self.grid.values():
            if not card.is_flipped:
                if card.category.name == "PROTECTION":
                    return True
                if card.attached_protection is not None:
                    return True
        return False

    def __repr__(self):
        return f"Player({self.name}, score={self.score}, cards={len(self.grid)})"
