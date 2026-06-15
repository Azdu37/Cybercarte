from enum import Enum, auto

class CardType(Enum):
    INFRASTRUCTURE = auto()
    BONUS_MALUS = auto()
    EVENT = auto()

class CardCategory(Enum):
    MACHINE = auto()     # Permet de construire le réseau
    PROTECTION = auto()  # Protège contre les attaques
    ATTACK = auto()      # Attaque les autres joueurs
    UTILITY = auto()     # Autres effets (bonus de pioche, etc.)

class Connection(Enum):
    NONE = 0
    LINK = 1  # Connecteur standard
    # On peut ajouter d'autres types si nécessaire

class Card:
    def __init__(self, card_id, name, card_type, category, connections=None, effect_id=None, description=""):
        self.id = card_id
        self.name = name
        self.card_type = card_type
        self.category = category
        self.description = description
        self.effect_id = effect_id
        
        # connections: dict { 'top': Connection, 'right': Connection, 'bottom': Connection, 'left': Connection }
        self.connections = connections or {
            'top': Connection.NONE,
            'right': Connection.NONE,
            'bottom': Connection.NONE,
            'left': Connection.NONE
        }
        
        self.is_connected = True
        self.is_flipped = False # Pour les cartes déconnectées
        self.attached_protection = None

    def attach_protection(self, protection_card):
        self.attached_protection = protection_card

    def disconnect(self):
        self.is_connected = False
        self.is_flipped = True
        self.attached_protection = None

    def __repr__(self):
        status = "Connected" if self.is_connected else "Disconnected"
        return f"Card({self.name}, {self.category.name}, {status})"
