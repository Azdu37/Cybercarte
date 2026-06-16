"""Écran d'accueil dans le style visuel des camarades."""
from __future__ import annotations
import pygame
from src.views.ui.components.card_render import (
    C_BG, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT, C_TEXT, C_TEXT_DIM,
    draw_rounded_rect
)


def _btn(surf, text, rect, hover=False):
    bc = C_HIGHLIGHT if hover else C_BORDER
    draw_rounded_rect(surf, C_PANEL_LIGHT, rect, radius=8, border=2, border_color=bc)
    f = pygame.font.SysFont(None, 28)
    t = f.render(text, True, C_HIGHLIGHT if hover else C_TEXT)
    surf.blit(t, t.get_rect(center=rect.center))


def _rects(screen_w):
    cx = screen_w // 2
    cases = {nb: pygame.Rect(cx - 140 + i * 100, 330, 80, 80) for i, nb in enumerate((2, 3, 4))}
    bouton = pygame.Rect(cx - 100, 460, 200, 54)
    return cases, bouton


def draw(surf: pygame.Surface, nb_sel: int, screen_w: int, screen_h: int) -> None:
    surf.fill(C_BG)
    cases, bouton = _rects(screen_w)
    mx, my = pygame.mouse.get_pos()

    tf = pygame.font.SysFont(None, 64)
    surf.blit(tf.render("Network Codex", True, C_HIGHLIGHT),
              tf.render("Network Codex", True, C_HIGHLIGHT).get_rect(center=(screen_w // 2, 160)))

    sf = pygame.font.SysFont(None, 24)
    s = sf.render("Partie locale · chacun joue à son tour sur cet écran", True, C_TEXT_DIM)
    surf.blit(s, s.get_rect(center=(screen_w // 2, 210)))

    lf = pygame.font.SysFont(None, 24)
    surf.blit(lf.render("Nombre de joueurs :", True, C_TEXT),
              lf.render("Nombre de joueurs :", True, C_TEXT).get_rect(center=(screen_w // 2, 285)))

    for nb, rect in cases.items():
        sel = (nb == nb_sel)
        bc = C_HIGHLIGHT if sel or rect.collidepoint(mx, my) else C_BORDER
        bg = C_PANEL_LIGHT if sel else C_PANEL
        draw_rounded_rect(surf, bg, rect, radius=10, border=2, border_color=bc)
        nf = pygame.font.SysFont(None, 36)
        t = nf.render(str(nb), True, C_HIGHLIGHT if sel else C_TEXT)
        surf.blit(t, t.get_rect(center=rect.center))

    hover_btn = bouton.collidepoint(mx, my)
    _btn(surf, "Commencer", bouton, hover=hover_btn)


def handle_click(pixel: tuple[int, int], nb_sel: int, screen_w: int) -> tuple[int, bool]:
    cases, bouton = _rects(screen_w)
    for nb, rect in cases.items():
        if rect.collidepoint(pixel):
            return nb, False
    if bouton.collidepoint(pixel):
        return nb_sel, True
    return nb_sel, False
