import pygame
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK

class GameView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Network Codex")
        self.font = pygame.font.SysFont("Arial", 24)

    def draw_game(self, game):
        self.screen.fill(WHITE)
        
        # Affichage des informations de base pour le moment
        y_offset = 20
        for i, player in enumerate(game.players):
            color_indicator = " (Tour actuel)" if i == game.current_player_index else ""
            text = self.font.render(f"{player.name} - Score: {player.score}{color_indicator}", True, player.color)
            self.screen.blit(text, (20, y_offset))
            y_offset += 30

        round_text = self.font.render(f"Manche: {game.round_count}", True, BLACK)
        self.screen.blit(round_text, (SCREEN_WIDTH - 150, 20))

        pygame.display.flip()

    def show_menu(self):
        # Menu pour choisir le nombre de joueurs
        pass
