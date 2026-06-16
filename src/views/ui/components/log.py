"""Journal de log : affiche les derniers messages de jeu."""
from __future__ import annotations
import pygame
from src.views.ui.components.card_render import (
    C_PANEL, C_BORDER, C_HIGHLIGHT, C_TEXT_DIM, draw_rounded_rect
)

MAX_LINES = 14


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
        for i, msg in enumerate(visible):
            color = C_HIGHLIGHT if msg.startswith("►") else C_TEXT_DIM
            t = tf.render(msg[:42], True, color)
            surf.blit(t, (x + 8, y + 24 + i * 14))
