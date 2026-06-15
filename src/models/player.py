class Player:
    def __init__(self, player_id, name, color):
        self.player_id = player_id
        self.name = name
        self.color = color
        self.hand = []
        self.infrastructure = []  # Liste de cartes posées ou structure de grille
        self.personal_objective_accomplished = False
        self.score = 0

    def add_to_hand(self, card):
        self.hand.append(card)

    def play_card(self, card_index, position):
        # Logique pour poser une carte dans l'infrastructure
        pass

    def calculate_score(self):
        # Chaque carte connectée compte pour 1 point
        # Objectif personnel +5 points
        base_score = sum(1 for card in self.infrastructure if card.is_connected)
        bonus = 5 if self.personal_objective_accomplished else 0
        self.score = base_score + bonus
        return self.score

    def __repr__(self):
        return f"Player({self.name}, score={self.score})"
