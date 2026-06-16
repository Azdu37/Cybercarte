"""Écran de fin de partie — affiche le vainqueur et le classement."""
from __future__ import annotations
import pygame
from src.models.game import Game
from src.models.player import Player
from src.views.ui.components.card_render import (
    C_BG, C_PANEL, C_BORDER, C_HIGHLIGHT, C_TEXT, C_TEXT_DIM,
    draw_rounded_rect
)


def draw(surf: pygame.Surface, game: Game, winner: Player, screen_w: int, screen_h: int) -> None:
    surf.fill(C_BG)

    # Calcul des scores finaux
    for p in game.players:
        p.calculate_score()
    classement = sorted(game.players, key=lambda p: p.score, reverse=True)

    # Titre
    tf = pygame.font.SysFont(None, 56)
    t = tf.render(f"{winner.name} a gagné !", True, C_HIGHLIGHT)
    surf.blit(t, t.get_rect(center=(screen_w // 2, screen_h // 2 - 100)))

    # Classement
    cf = pygame.font.SysFont(None, 28)
    for i, p in enumerate(classement):
        y = screen_h // 2 - 30 + i * 40
        pygame.draw.circle(surf, p.color, (screen_w // 2 - 140, y + 10), 8)
        texte = f"{i+1}.  {p.name}   —   {p.score} pt(s)"
        col = C_HIGHLIGHT if p is winner else C_TEXT
        surf.blit(cf.render(texte, True, col), (screen_w // 2 - 120, y))

    # Instruction
    sf = pygame.font.SysFont(None, 22)
    t2 = sf.render("Cliquez n'importe où pour revenir au menu", True, C_TEXT_DIM)
    surf.blit(t2, t2.get_rect(center=(screen_w // 2, screen_h // 2 + 140)))
