"""Journal de log : affiche les derniers messages de jeu."""
from __future__ import annotations
import pygame
from src.views.ui.components.card_render import (
    C_PANEL, C_BORDER, C_HIGHLIGHT, C_TEXT_DIM, draw_rounded_rect
)

MAX_LINES = 16


def wrap_text(text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
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

    def add(self, msg: str) -> None:
        self.messages.append(msg)

    def draw(self, surf: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
        draw_rounded_rect(surf, C_PANEL, (x, y, w, h), radius=8,
                          border=1, border_color=C_BORDER)
        tf = pygame.font.SysFont(None, 18)
        hf = pygame.font.SysFont(None, 18)
        surf.blit(hf.render("Journal", True, C_TEXT_DIM), (x + 8, y + 6))
        visible = self.messages[-MAX_LINES:]
        line_y = y + 24
        for msg in visible:
            color = C_HIGHLIGHT if msg.startswith("►") else C_TEXT_DIM
            for line in wrap_text(msg, tf, w - 18):
                t = tf.render(line, True, color)
                surf.blit(t, (x + 8, line_y))
                line_y += 14
                if line_y > y + h - 16:
                    return
