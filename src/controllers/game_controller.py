"""Contrôleur principal : boucle Pygame, machine à états."""
from __future__ import annotations
import pygame, sys
from src.models.game import Game
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.views.ui.screen import menu, game, end
from src.views.ui.screen.dictionary_screen import DictionaryScreen


class GameController:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Network Codex")
        self.clock  = pygame.time.Clock()

        self.state      = "menu"   # menu | game | end | dico
        self.prev_state = "menu"   # état d'où on vient (pour le retour du dico)
        self.nb_joueurs = 2

        self.game_model:  Game | None = None
        self.game_screen: game.GameScreen | None = None
        self.winner = None
        self.dico   = DictionaryScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)
                if event.type == pygame.MOUSEWHEEL:
                    if self.state == "game" and self.game_screen and self.game_model:
                        self.game_screen.handle_scroll(event.y, self.game_model)
                    elif self.state == "dico":
                        self.dico.handle_scroll(event.y)
            self._draw()
            self.clock.tick(60)

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            if self.state == "dico":
                self.state = self.prev_state
            else:
                pygame.quit(); sys.exit()
        if self.state == "dico":
            self.dico.handle_key(key)

    def _open_dico(self) -> None:
        self.prev_state = self.state
        self.dico.reset()
        self.state = "dico"

    def _handle_click(self, pos: tuple[int, int]) -> None:
        if self.state == "menu":
            self.nb_joueurs, commencer, ouvrir_dico = menu.handle_click(
                pos, self.nb_joueurs, SCREEN_WIDTH
            )
            if commencer:
                self.game_model  = Game()
                self.game_model.setup(self.nb_joueurs)
                self.game_screen = game.GameScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.state = "game"
                self.game_screen.log.add(f"► Tour de {self.game_model.current_player.name}")
                for player in self.game_model.players:
                    if player.objectif:
                        self.game_screen.log.add(f"Objectif {player.name} : {player.objectif.nom}")
            elif ouvrir_dico:
                self._open_dico()

        elif self.state == "game" and self.game_model and self.game_screen:
            result = self.game_screen.handle_click(pos, self.game_model)
            if result == "open_dico":
                self._open_dico()
            elif result is True:
                for p in self.game_model.players:
                    p.calculate_score()
                self.winner = max(self.game_model.players, key=lambda p: p.score)
                self.state = "end"

        elif self.state == "end":
            action = end.handle_click(pos, SCREEN_WIDTH, SCREEN_HEIGHT)
            if action == "rejouer":
                self.state = "menu"
                self.game_model = None
                self.game_screen = None
                self.winner = None
            elif action == "quitter":
                pygame.quit(); sys.exit()

        elif self.state == "dico":
            result = self.dico.handle_click(pos)
            if result == "back":
                self.state = self.prev_state

    def _draw(self) -> None:
        if self.state == "menu":
            menu.draw(self.screen, self.nb_joueurs, SCREEN_WIDTH, SCREEN_HEIGHT)
        elif self.state == "game" and self.game_model and self.game_screen:
            self.game_screen.draw(self.screen, self.game_model)
        elif self.state == "end" and self.game_model and self.winner:
            end.draw(self.screen, self.game_model, self.winner, SCREEN_WIDTH, SCREEN_HEIGHT)
        elif self.state == "dico":
            self.dico.draw(self.screen)
        pygame.display.flip()