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
                self.view.draw_game(self.game, self.selected_card_index)
            clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                player = self.game.get_current_player()
                
                # Clic sur la main ?
                bar_h = 126 + 30 # CARD_H + margin
                bar_y = 720 - bar_h - 10 # SCREEN_HEIGHT - bar_h - 10
                
                if my >= bar_y:
                    for i in range(len(player.hand)):
                        cx = 20 + i * (90 + 15) # CARD_W + spacing
                        cy = bar_y + 20
                        rect = pygame.Rect(cx, cy, 90, 126)
                        if rect.collidepoint(mx, my):
                            if self.selected_card_index == i:
                                self.selected_card_index = None
                            else:
                                self.selected_card_index = i
                            return

                # Clic sur la grille ?
                for i, p in enumerate(self.game.players):
                    ox = 20 + i * (3 * (90 + 10) + 10 + 40)
                    oy = 40
                    grid_w = 3 * (90 + 10) + 10
                    grid_h = 3 * (126 + 10) + 10 + 24
                    
                    if pygame.Rect(ox, oy, grid_w, grid_h).collidepoint(mx, my):
                        # On est dans la grille du joueur i
                        # Calculer la case
                        for row in range(3):
                            for col in range(3):
                                cx = ox + 10 + col * (90 + 10)
                                cy = oy + 24 + 10 + row * (126 + 10)
                                if pygame.Rect(cx, cy, 90, 126).collidepoint(mx, my):
                                    if self.selected_card_index is not None and i == self.game.current_player_index:
                                        success = self.handle_play_card(self.selected_card_index, col, row)
                                        if success:
                                            self.selected_card_index = None
                                            # Si plus d'actions, tour suivant automatique ? 
                                            # Pour le moment on laisse le joueur finir son tour manuellement ou via les règles
                                            if player.actions_left == 0:
                                                self.handle_end_turn()
                                    return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.handle_end_turn()
                elif event.key == pygame.K_i:
                    self.handle_draw_infra()
                elif event.key == pygame.K_b:
                    self.handle_draw_bonus()

    def handle_draw_infra(self):
        success, message = self.game.perform_action(ACTION_DRAW_INFRA)
        self.view.set_message(message if not success else "Vous avez pioché une infrastructure")
        return success

    def handle_draw_bonus(self):
        success, message = self.game.perform_action(ACTION_DRAW_BONUS)
        self.view.set_message(message)
        return success

    def handle_play_card(self, card_index, x, y, target_player=None):
        success, message = self.game.perform_action(ACTION_PLAY_CARD, card_index=card_index, x=x, y=y)
        if not success:
            self.view.set_message(message)
        return success

    def apply_attack_effect(self, target_player, card):
        # Ici on implémentera les différents effets d'attaque (vol, destruction, déconnexion)
        # Exemple : déconnecter une carte aléatoire
        if target_player.grid:
            pos = random.choice(list(target_player.grid.keys()))
            target_player.grid[pos].disconnect()
            print(f"La carte à la position {pos} de {target_player.name} a été déconnectée !")

    def handle_end_turn(self):
        messages = self.game.next_turn()
        current_player = self.game.get_current_player()
        
        if messages:
            # Pour l'instant on concatène les messages
            full_msg = " | ".join(messages)
            self.view.set_message(full_msg)
        else:
            self.view.set_message(f"Tour de {current_player.name}")

    def update(self):
        winner = self.game.check_victory()
        if winner:
            self.view.set_message(f"Le gagnant est {winner.name}!")
            # On pourrait ajouter un petit délai avant de quitter
            # self.running = False
