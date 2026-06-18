"""
Barre de main : cartes du joueur courant, avec scroll horizontal
quand la main dépasse la largeur de l'écran.

Navigation :
  - Flèches ◀ ▶ cliquables sur les bords de la barre
  - Molette de la souris (événement MOUSEWHEEL transmis par game.py)
  - Les cartes sont clipées à la zone centrale pour ne pas déborder
"""
from __future__ import annotations
import pygame
from src.models.card import Card
from src.views.ui.components.card_render import (
    draw_card, draw_rounded_rect,
    C_PANEL, C_BORDER, C_HIGHLIGHT, C_TEXT, C_TEXT_DIM,
    CARD_W, CARD_H
)

BAR_PAD  = 8
CARD_GAP = 8
BAR_H    = CARD_H + 32

# Largeur des zones de flèche sur chaque côté
ARROW_W  = 36
# Nombre de cartes visibles simultanément (calculé dynamiquement)


def _max_visible(screen_w: int) -> int:
    """Nombre de cartes entières tenant dans la zone centrale."""
    zone_w = screen_w - ARROW_W * 2 - 80  # 80 = label "MAIN" + marge
    return max(1, zone_w // (CARD_W + CARD_GAP))


def clamp_offset(offset: int, n: int, screen_w: int) -> int:
    """Maintient l'offset dans [0, max défilable]."""
    vis = _max_visible(screen_w)
    return max(0, min(offset, max(0, n - vis)))


def draw(
    surf: pygame.Surface,
    hand: list[Card],
    screen_w: int,
    screen_h: int,
    selected: int | None = None,
    scroll_offset: int = 0,
    just_drawn: int | None = None,
) -> tuple[list[tuple[int, pygame.Rect]], pygame.Rect | None, pygame.Rect | None]:
    """
    Dessine la barre de main avec scroll.

    Retourne :
      (rects_cartes, rect_fleche_gauche, rect_fleche_droite)
      rects_cartes : [(index_dans_hand, Rect_ecran), ...]
      Les rects de flèches sont None si la flèche n'est pas nécessaire.
    """
    bar_y  = screen_h - BAR_H - BAR_PAD
    bar_h  = BAR_H + 12
    pygame.draw.rect(surf, C_PANEL, (0, bar_y - 4, screen_w, bar_h))
    pygame.draw.line(surf, C_BORDER, (0, bar_y - 4), (screen_w, bar_y - 4), 1)

    lf = pygame.font.SysFont(None, 18)
    surf.blit(lf.render("MAIN", True, C_TEXT_DIM), (12, bar_y + 6))

    n   = len(hand)
    vis = _max_visible(screen_w)
    need_scroll = n > vis

    # ── Flèches ──────────────────────────────────────────────────────
    rect_left  = None
    rect_right = None
    card_zone_x0 = ARROW_W + 50  # début de la zone cartes (après label)
    card_zone_x1 = screen_w - ARROW_W

    if need_scroll:
        cy = bar_y + BAR_H // 2

        # Flèche gauche
        rect_left = pygame.Rect(4, bar_y, ARROW_W, BAR_H)
        active_l  = scroll_offset > 0
        col_l     = C_HIGHLIGHT if active_l else C_BORDER
        draw_rounded_rect(surf, C_PANEL, rect_left, radius=6,
                          border=2, border_color=col_l)
        af = pygame.font.SysFont(None, 26)
        lbl = af.render("◀", True, col_l)
        surf.blit(lbl, lbl.get_rect(center=rect_left.center))

        # Flèche droite
        rect_right = pygame.Rect(screen_w - ARROW_W - 4, bar_y, ARROW_W, BAR_H)
        active_r   = scroll_offset < n - vis
        col_r      = C_HIGHLIGHT if active_r else C_BORDER
        draw_rounded_rect(surf, C_PANEL, rect_right, radius=6,
                          border=2, border_color=col_r)
        lbl = af.render("▶", True, col_r)
        surf.blit(lbl, lbl.get_rect(center=rect_right.center))

        # Indicateur de position (ex: "3–6 / 9")
        end_idx = min(scroll_offset + vis, n)
        pf = pygame.font.SysFont(None, 16)
        ptxt = pf.render(f"{scroll_offset + 1}–{end_idx} / {n}", True, C_TEXT_DIM)
        surf.blit(ptxt, ptxt.get_rect(midright=(screen_w - ARROW_W - 8, bar_y - 10)))

    # ── Cartes visibles ───────────────────────────────────────────────
    rects: list[tuple[int, pygame.Rect]] = []
    if n == 0:
        return rects, rect_left, rect_right

    visible_cards = hand[scroll_offset: scroll_offset + vis]
    total_w = len(visible_cards) * (CARD_W + CARD_GAP) - CARD_GAP
    start_x = card_zone_x0 + max(0, (card_zone_x1 - card_zone_x0 - total_w) // 2)

    # Clip pour ne pas déborder dans la zone des flèches
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(card_zone_x0, bar_y - 4, card_zone_x1 - card_zone_x0, bar_h))

    for j, card in enumerate(visible_cards):
        real_idx = scroll_offset + j
        cx = start_x + j * (CARD_W + CARD_GAP)
        cy = bar_y + 6
        r  = draw_card(surf, card, cx, cy, selected=(real_idx == selected), just_drawn=(real_idx == just_drawn))
        rects.append((real_idx, r))

    surf.set_clip(old_clip)

    # ── Instruction si carte sélectionnée ────────────────────────────
    if selected is not None and 0 <= selected < n:
        tf = pygame.font.SysFont(None, 18)
        t  = tf.render("Cliquez sur une case verte pour poser la carte", True, C_HIGHLIGHT)
        surf.blit(t, t.get_rect(center=(screen_w // 2, bar_y - 14)))

    return rects, rect_left, rect_right


def bar_top(screen_h: int) -> int:
    return screen_h - BAR_H - BAR_PAD - 4