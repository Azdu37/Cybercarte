"""
Journal de log : affiche les messages de jeu avec scroll complet.

Navigation :
  - Flèches ▲ ▼ cliquables (à appeler via handle_click depuis game.py)
  - Molette via handle_scroll() (appelée depuis game.py quand la souris survole)
  - Auto-scroll vers le bas à chaque nouveau message
"""
from __future__ import annotations
import pygame
from src.views.ui.components.card_render import (
    C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT, C_TEXT_DIM, draw_rounded_rect
)

LINE_H = 14
PAD    = 8


def wrap_text(text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Log:
    def __init__(self) -> None:
        self.messages: list[str] = ["► Début de la partie !"]
        self._scroll: int = 0
        self._rect:     pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._btn_up:   pygame.Rect | None = None
        self._btn_down: pygame.Rect | None = None
        self._max_scroll: int = 0

    def add(self, msg: str) -> None:
        self.messages.append(msg)
        # Auto-scroll vers le bas : on ira corriger au prochain draw()
        self._scroll = 999999  # sera clampé dans draw()

    def scroll(self, delta: int) -> None:
        """delta > 0 = vers le bas."""
        self._scroll = max(0, min(self._scroll + delta, self._max_scroll))

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Retourne True si le clic a été consommé (flèche ▲▼)."""
        if self._btn_up and self._btn_up.collidepoint(pos):
            self.scroll(-3)
            return True
        if self._btn_down and self._btn_down.collidepoint(pos):
            self.scroll(3)
            return True
        return False

    def is_hovered(self, pos: tuple[int, int]) -> bool:
        return self._rect.collidepoint(pos)

    def draw(self, surf: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
        self._rect = pygame.Rect(x, y, w, h)

        draw_rounded_rect(surf, C_PANEL, (x, y, w, h),
                          radius=8, border=1, border_color=C_BORDER)

        tf = pygame.font.SysFont(None, 18)

        # En-tête
        surf.blit(tf.render("Journal", True, C_TEXT_DIM), (x + PAD, y + 5))

        # Flèches ▲ ▼
        self._btn_up   = pygame.Rect(x + w - 20, y + 4,  16, 18)
        self._btn_down = pygame.Rect(x + w - 20, y + 24, 16, 18)

        # Construire toutes les lignes wrappées
        all_lines: list[tuple[str, tuple]] = []
        for msg in self.messages:
            color = C_HIGHLIGHT if msg.startswith("►") else C_TEXT_DIM
            for line in wrap_text(msg, tf, w - PAD * 2 - 8):
                all_lines.append((line, color))

        text_y0   = y + 48
        text_h    = h - 52
        lines_vis = max(1, text_h // LINE_H)
        self._max_scroll = max(0, len(all_lines) - lines_vis)
        self._scroll     = min(self._scroll, self._max_scroll)

        # Rendu des flèches
        for btn, symbol, active in (
            (self._btn_up,   "▲", self._scroll > 0),
            (self._btn_down, "▼", self._scroll < self._max_scroll),
        ):
            col = C_HIGHLIGHT if active else C_BORDER
            draw_rounded_rect(surf, C_PANEL_LIGHT, btn, radius=3,
                              border=1, border_color=col)
            af = pygame.font.SysFont(None, 14)
            at = af.render(symbol, True, col)
            surf.blit(at, at.get_rect(center=btn.center))

        # Clip + affichage des lignes
        clip = pygame.Rect(x + PAD, text_y0, w - PAD * 2 - 8, text_h)
        old  = surf.get_clip()
        surf.set_clip(clip)
        visible = all_lines[self._scroll: self._scroll + lines_vis]
        for i, (line, color) in enumerate(visible):
            surf.blit(tf.render(line, True, color), (x + PAD, text_y0 + i * LINE_H))
        surf.set_clip(old)

        # Scrollbar
        if self._max_scroll > 0:
            ratio  = lines_vis / max(1, len(all_lines))
            bar_h  = max(14, int(text_h * ratio))
            bar_y  = text_y0 + int((self._scroll / self._max_scroll) * (text_h - bar_h))
            bar_x  = x + w - 6
            pygame.draw.rect(surf, C_BORDER,    (bar_x, text_y0, 4, text_h), border_radius=2)
            pygame.draw.rect(surf, C_HIGHLIGHT, (bar_x, bar_y,   4, bar_h),  border_radius=2)