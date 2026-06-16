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
    surf.blit(t, t.get_rect(center=(screen_w // 2, screen_h // 2 - 120)))

    # Classement
    cf = pygame.font.SysFont(None, 28)
    for i, p in enumerate(classement):
        y = screen_h // 2 - 60 + i * 40
        pygame.draw.circle(surf, p.color, (screen_w // 2 - 140, y + 10), 8)
        texte = f"{i+1}.  {p.name}   —   {p.score} pt(s)"
        col = C_HIGHLIGHT if p is winner else C_TEXT
        surf.blit(cf.render(texte, True, col), (screen_w // 2 - 120, y))

    # Boutons
    mx, my = pygame.mouse.get_pos()
    btn_w, btn_h = 160, 40
    
    rect_rejouer = pygame.Rect(screen_w // 2 - btn_w - 10, screen_h // 2 + 100, btn_w, btn_h)
    rect_quitter = pygame.Rect(screen_w // 2 + 10, screen_h // 2 + 100, btn_w, btn_h)

    _draw_button(surf, "Rejouer", rect_rejouer, rect_rejouer.collidepoint(mx, my))
    _draw_button(surf, "Quitter", rect_quitter, rect_quitter.collidepoint(mx, my))


def _draw_button(surf: pygame.Surface, text: str, rect: pygame.Rect, hover: bool) -> None:
    color = C_HIGHLIGHT if hover else C_PANEL
    draw_rounded_rect(surf, color, rect, radius=6, border=1, border_color=C_BORDER)
    
    font = pygame.font.SysFont(None, 24)
    txt_surf = font.render(text, True, C_BG if hover else C_TEXT)
    surf.blit(txt_surf, txt_surf.get_rect(center=rect.center))


def handle_click(pos: tuple[int, int], screen_w: int, screen_h: int) -> str | None:
    """Retourne 'rejouer', 'quitter' ou None."""
    btn_w, btn_h = 160, 40
    rect_rejouer = pygame.Rect(screen_w // 2 - btn_w - 10, screen_h // 2 + 100, btn_w, btn_h)
    rect_quitter = pygame.Rect(screen_w // 2 + 10, screen_h // 2 + 100, btn_w, btn_h)

    if rect_rejouer.collidepoint(pos):
        return "rejouer"
    if rect_quitter.collidepoint(pos):
        return "quitter"
    return None
