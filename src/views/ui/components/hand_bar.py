"""Barre de main : cartes du joueur courant affichées en bas d'écran."""
from __future__ import annotations
import pygame
from src.models.card import Card
from src.views.ui.components.card_render import (
    draw_card, draw_rounded_rect,
    C_PANEL, C_BORDER, C_HIGHLIGHT, C_TEXT_DIM,
    CARD_W, CARD_H
)

BAR_PAD  = 8
CARD_GAP = 8
BAR_H    = CARD_H + 32


def draw(surf: pygame.Surface, hand: list[Card], screen_w: int, screen_h: int,
         selected: int | None = None) -> list[tuple[int, pygame.Rect]]:
    """
    Dessine la barre de main et renvoie [(index, rect), ...] pour la détection de clics.
    """
    bar_y = screen_h - BAR_H - BAR_PAD
    pygame.draw.rect(surf, C_PANEL, (0, bar_y - 4, screen_w, BAR_H + 12))
    pygame.draw.line(surf, C_BORDER, (0, bar_y - 4), (screen_w, bar_y - 4), 1)

    lf = pygame.font.SysFont(None, 18)
    surf.blit(lf.render("MAIN", True, C_TEXT_DIM), (12, bar_y + 6))

    rects: list[tuple[int, pygame.Rect]] = []
    n = len(hand)
    if n == 0:
        return rects

    total_w = n * (CARD_W + CARD_GAP) - CARD_GAP
    start_x = max(80, screen_w // 2 - total_w // 2)

    for i, card in enumerate(hand):
        cx = start_x + i * (CARD_W + CARD_GAP)
        cy = bar_y + 6
        r = draw_card(surf, card, cx, cy, selected=(i == selected))
        rects.append((i, r))

    # Instruction si une carte est sélectionnée
    if selected is not None and 0 <= selected < len(hand):
        tf = pygame.font.SysFont(None, 18)
        t = tf.render("Cliquez sur une case verte pour poser la carte", True, C_HIGHLIGHT)
        surf.blit(t, t.get_rect(center=(screen_w // 2, bar_y - 14)))

    return rects


def bar_top(screen_h: int) -> int:
    """Coordonnée y du haut de la barre (utile pour délimiter la zone plateau)."""
    return screen_h - BAR_H - BAR_PAD - 4
