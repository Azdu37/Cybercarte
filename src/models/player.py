from src.utils.constants import ACTIONS_PER_TURN

class Player:
    def __init__(self, player_id, name, color):
        self.player_id = player_id
        self.name = name
        self.color = color
        self.hand = []
        self.grid = {}  # {(x, y): Card}
        self.objective = None
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
        
        # Limite de la grille 3x3
        if x < 0 or x >= 3 or y < 0 or y >= 3:
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
            
            # Cas spécial : réparation d'une carte déconnectée
            if (x, y) in self.grid and self.grid[(x, y)].is_flipped:
                # On ne peut réparer qu'avec une carte du même type ou si c'est autorisé
                # Pour simplifier, on remplace la carte
                if self.can_place_card(card, x, y):
                    self.grid[(x, y)] = card
                    self.hand.pop(card_index)
                    return True
                return False

            if self.can_place_card(card, x, y):
                self.grid[(x, y)] = card
                self.hand.pop(card_index)
                return True
        return False

    def remove_card(self, x, y):
        if (x, y) in self.grid:
            return self.grid.pop((x, y))
        return None

    def attach_protection_to_card(self, card_index, x, y):
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]
            if card.category.name == "PROTECTION" and (x, y) in self.grid:
                target_card = self.grid[(x, y)]
                if not target_card.is_flipped:
                    if target_card.attached_protection is None:
                        target_card.attach_protection(card)
                        self.hand.pop(card_index)
                        return True
        return False

    def calculate_score(self):
        # Vérification de l'objectif
        self.check_objective_accomplished()
        
        # Chaque carte connectée compte pour 1 point
        base_score = sum(1 for card in self.grid.values() if not card.is_flipped)
        bonus = 5 if self.personal_objective_accomplished else 0
        self.score = base_score + bonus
        return self.score

    def check_objective_accomplished(self):
        if not self.objective:
            return
            
        obj_id = self.objective["id"]
        if obj_id == "SHIELD_WALL":
            protections = sum(1 for card in self.grid.values() if not card.is_flipped and card.category.name == "PROTECTION")
            # Aussi compter les protections attachées
            attached = sum(1 for card in self.grid.values() if not card.is_flipped and card.attached_protection)
            if protections + attached >= 3:
                self.personal_objective_accomplished = True
        
        elif obj_id == "VERTICAL_LINK":
            for x in range(3):
                if all((x, y) in self.grid and not self.grid[(x, y)].is_flipped for y in range(3)):
                    self.personal_objective_accomplished = True
                    break
        
        elif obj_id == "HORIZONTAL_LINK":
            for y in range(3):
                if all((x, y) in self.grid and not self.grid[(x, y)].is_flipped for x in range(3)):
                    self.personal_objective_accomplished = True
                    break
                    
        elif obj_id == "DIVERSITY":
            machines = set()
            for card in self.grid.values():
                if not card.is_flipped and card.category.name == "MACHINE":
                    machines.add(card.name) # Utilise le nom pour la diversité
            if len(machines) >= 3:
                self.personal_objective_accomplished = True

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
