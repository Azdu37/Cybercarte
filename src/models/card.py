from enum import Enum, auto

class CardType(Enum):
    INFRASTRUCTURE = auto()
    BONUS_MALUS = auto()
    EVENT = auto()
    MACHINE = auto()
    PROTECTION = auto()

class Connection(Enum):
    NONE = 0
    TYPE_A = 1
    TYPE_B = 2
    # À définir selon le design final des connecteurs

class Card:
    def __init__(self, name, card_type, connections=None):
        self.name = name
        self.card_type = card_type
        # connections: dict { 'top': Connection, 'right': Connection, 'bottom': Connection, 'left': Connection }
        self.connections = connections or {
            'top': Connection.NONE,
            'right': Connection.NONE,
            'bottom': Connection.NONE,
            'left': Connection.NONE
        }
        self.is_connected = True
        self.attached_protection = None

    def disconnect(self):
        self.is_connected = False
        self.attached_protection = None

    def __repr__(self):
        return f"Card({self.name}, {self.card_type.name}, connected={self.is_connected})"
