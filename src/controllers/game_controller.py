import pygame
import sys
from src.models.game import Game
from src.views.game_view import GameView

class GameController:
    def __init__(self):
        self.view = GameView()
        self.game = None
        self.running = True

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
            
            # Exemple de gestion de clic pour passer le tour
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game:
                    self.game.next_turn()

    def update(self):
        winner = self.game.check_victory()
        if winner:
            print(f"Le gagnant est {winner.name}!")
            self.running = False
