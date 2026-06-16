"""Contrôleur principal : boucle Pygame, machine à états menu → jeu → victoire."""
from __future__ import annotations
import pygame
import sys
from src.models.game import Game
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.views.ui.screen import menu, game, end


class GameController:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Network Codex")
        self.clock = pygame.time.Clock()

        self.state = "menu"
        self.nb_joueurs = 2

        self.game_model: Game | None = None
        self.game_screen: game.GameScreen | None = None
        self.winner = None

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            self._draw()
            self.clock.tick(60)

    def _handle_click(self, pos: tuple[int, int]) -> None:
        if self.state == "menu":
            self.nb_joueurs, commencer = menu.handle_click(pos, self.nb_joueurs, SCREEN_WIDTH)
            if commencer:
                self.game_model = Game()
                self.game_model.setup(self.nb_joueurs)
                self.game_screen = game.GameScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.game_screen.log.add(f"► Tour de {self.game_model.current_player.name}")
                self.state = "game"

        elif self.state == "game" and self.game_model and self.game_screen:
            victoire = self.game_screen.handle_click(pos, self.game_model)
            if victoire:
                for p in self.game_model.players:
                    p.calculate_score()
                self.winner = max(self.game_model.players, key=lambda p: p.score)
                self.state = "end"

        elif self.state == "end":
            self.state = "menu"
            self.game_model = None
            self.game_screen = None

    def _draw(self) -> None:
        if self.state == "menu":
            menu.draw(self.screen, self.nb_joueurs, SCREEN_WIDTH, SCREEN_HEIGHT)
        elif self.state == "game" and self.game_model and self.game_screen:
            self.game_screen.draw(self.screen, self.game_model)
        elif self.state == "end" and self.game_model and self.winner:
            end.draw(self.screen, self.game_model, self.winner, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.flip()
