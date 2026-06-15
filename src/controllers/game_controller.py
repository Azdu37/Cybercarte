import pygame
import sys
import random
from src.models.game import Game
from src.views.game_view import GameView
from src.models.card import CardCategory
from src.utils.constants import ACTION_DRAW_INFRA, ACTION_DRAW_BONUS, ACTION_PLAY_CARD

class GameController:
    def __init__(self):
        self.view = GameView()
        self.game = None
        self.running = True
        self.selected_card_index = None

    def start_new_game(self, player_count):
        self.game = Game(player_count)
        self.run()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            if self.game:
                self.update()
                self.view.draw_game(self.game)
            clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Cette partie sera affinée avec la vue réelle
                # simulation d'interaction
                pass

    def handle_draw_infra(self):
        success, message = self.game.perform_action(ACTION_DRAW_INFRA)
        if not success:
            print(message)
        return success

    def handle_draw_bonus(self):
        success, message = self.game.perform_action(ACTION_DRAW_BONUS)
        if not success:
            print(message)
        return success

    def handle_play_card(self, card_index, x, y, target_player=None):
        player = self.game.get_current_player()
        card = player.hand[card_index]

        # Logique d'attaque spécifique
        if card.category == CardCategory.ATTACK:
            if target_player is None:
                print("Choisissez une cible pour l'attaque")
                return False
            
            # Vérification de la protection avant application
            if target_player.has_protection():
                print(f"L'attaque de {card.name} est bloquée par la protection de {target_player.name}!")
                # L'action est quand même consommée ? Selon les règles, on joue la carte.
                player.hand.pop(card_index)
                player.actions_left -= 1
                return True
            
            # Appliquer l'effet d'attaque si pas de protection
            self.apply_attack_effect(target_player, card)
            player.hand.pop(card_index)
            player.actions_left -= 1
            return True

        # Placement normal pour les autres types de cartes
        success, message = self.game.perform_action(ACTION_PLAY_CARD, card_index=card_index, x=x, y=y)
        if not success:
            print(message)
        return success

    def apply_attack_effect(self, target_player, card):
        # Ici on implémentera les différents effets d'attaque (vol, destruction, déconnexion)
        # Exemple : déconnecter une carte aléatoire
        if target_player.grid:
            pos = random.choice(list(target_player.grid.keys()))
            target_player.grid[pos].disconnect()
            print(f"La carte à la position {pos} de {target_player.name} a été déconnectée !")

    def handle_end_turn(self):
        self.game.next_turn()

    def update(self):
        winner = self.game.check_victory()
        if winner:
            print(f"Le gagnant est {winner.name}!")
            # Ici on pourrait appeler la vue pour afficher l'écran de fin
            self.running = False
