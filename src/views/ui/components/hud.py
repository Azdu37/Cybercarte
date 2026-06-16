"""HUD : barre supérieure — nom du joueur, actions restantes, compteurs de piles."""
from __future__ import annotations
import pygame
from src.models.game import Game
from src.views.ui.components.card_render import (
    C_BG, C_PANEL, C_BORDER, C_HIGHLIGHT, C_TEXT, C_TEXT_DIM,
    C_INFRA, C_BONUS, C_EVENT, draw_rounded_rect
)

HUD_H = 44


def draw(surf: pygame.Surface, game: Game, screen_w: int) -> None:
    pygame.draw.rect(surf, C_PANEL, (0, 0, screen_w, HUD_H))
    pygame.draw.line(surf, C_BORDER, (0, HUD_H), (screen_w, HUD_H), 1)

    hf = pygame.font.SysFont(None, 22)
    sf = pygame.font.SysFont(None, 18)
    cp = game.current_player

    # Tour
    surf.blit(hf.render(f"Tour {game.round_count}", True, C_TEXT), (14, 14))

    # Joueur courant
    surf.blit(hf.render(f"► {cp.name}", True, C_HIGHLIGHT), (110, 14))

    # Cercles d'actions (reprend l'idée des camarades)
    for i in range(2):
        color = C_HIGHLIGHT if i < cp.actions_left else C_BORDER
        pygame.draw.circle(surf, color, (340 + i * 22, HUD_H // 2), 7)
    surf.blit(sf.render("actions", True, C_TEXT_DIM), (372, 16))

    # Indicateurs couleurs tous les joueurs
    
    for i, p in enumerate(game.players):
        mx = 460 + i * 36
        my = HUD_H // 2
        pygame.draw.circle(surf, p.color, (mx, my), 7)
        if i == game.current_player_index:
            pygame.draw.circle(surf, C_HIGHLIGHT, (mx, my), 7, 2)
        lbl = pygame.font.SysFont(None, 14).render(str(p.nombre_cartes_actives()), True, C_TEXT)
        surf.blit(lbl, lbl.get_rect(center=(mx, my + 14)))

    # Compteurs de pioches
    labels = [
        ("Infra",       len(game.infrastructure_deck), C_INFRA),
        ("Bonus/Malus", len(game.bonus_malus_deck),    C_BONUS),
        ("Événements",  len(game.event_deck),           C_EVENT),
    ]
    dx = screen_w - 340
    for name, count, color in labels:
        pygame.draw.rect(surf, color, (dx, 8, 90, 26), border_radius=5)
        pygame.draw.rect(surf, (0, 0, 0), (dx, 8, 90, 26), width=1, border_radius=5)
        t = sf.render(f"{name} {count}", True, (10, 10, 20))
        surf.blit(t, (dx + 5, 15))
        dx += 98

    # Message dernier événement
    if game.last_message:
        msg = sf.render(game.last_message, True, C_HIGHLIGHT)
        surf.blit(msg, msg.get_rect(midright=(screen_w - 350, HUD_H // 2)))
