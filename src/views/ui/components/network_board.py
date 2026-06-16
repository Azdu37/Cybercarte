"""
Rendu du réseau tentaculaire d'un joueur.

Contrairement à la grille 3×3 fixe des camarades, notre réseau
est dynamique : les cartes s'étendent dans toutes les directions.
On calcule les limites à chaque frame et on centre le tout.
"""
from __future__ import annotations
import pygame
from src.models.network import Network, EtatCellule
from src.models.card import Card
from src.models.enums import Direction, DELTA
from src.views.ui.components.card_render import (
    draw_card, draw_rounded_rect,
    C_BG, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT, C_TEXT,
    CARD_W, CARD_H, SLOT_PAD
)

Position = tuple[int, int]


def _limites(network: Network, extras: tuple[Position, ...] = ()) -> tuple[int, int, int, int]:
    positions = list(network.grille.keys()) + list(extras)
    if not positions:
        return (0, 0, 0, 0)
    xs = [p[0] for p in positions]; ys = [p[1] for p in positions]
    return (min(xs), min(ys), max(xs), max(ys))


def draw_network(
    surf: pygame.Surface,
    network: Network,
    ox: int, oy: int,
    card_w: int = CARD_W, card_h: int = CARD_H,
    *,
    current: bool = True,
    positions_surlignees: tuple[Position, ...] = (),
    selected_pos: Position | None = None,
    label: str = "",
) -> dict[Position, pygame.Rect]:
    """
    Dessine le réseau à partir de (ox, oy).
    Renvoie un dict {position_grille: Rect_ecran} pour la détection de clics.
    """
    pas = card_w + SLOT_PAD
    x_min, y_min, x_max, y_max = _limites(network, positions_surlignees)

    if label:
        f = pygame.font.SysFont(None, 18)
        t = f.render(label, True, C_HIGHLIGHT if current else C_TEXT)
        surf.blit(t, (ox, oy - 18))

    rects: dict[Position, pygame.Rect] = {}

    # Cases en surbrillance (placement possible)
    for pos in positions_surlignees:
        if pos not in network.grille:
            x, y = ox + (pos[0] - x_min) * pas, oy + (pos[1] - y_min) * pas
            r = pygame.Rect(x, y, card_w, card_h)
            draw_rounded_rect(surf, C_BG, r, radius=8, border=2,
                              border_color=C_HIGHLIGHT)
            rects[pos] = r

    # Cartes posées
    for pos, cel in network.grille.items():
        x = ox + (pos[0] - x_min) * pas
        y = oy + (pos[1] - y_min) * pas
        if cel.dessous is not None:
            offset = 12 if current else 8
            draw_card(surf, cel.dessous, x + offset, y + offset,
                      selected=False,
                      morte=(cel.dessous_etat is EtatCellule.MORTE),
                      small=not current)
        r = draw_card(surf, cel.carte, x, y,
                      selected=(pos == selected_pos),
                      morte=(cel.etat is EtatCellule.MORTE),
                      small=not current)
        rects[pos] = r

    return rects


def pixel_to_pos(
    pixel: tuple[int, int],
    ox: int, oy: int,
    x_min: int, y_min: int,
    card_w: int = CARD_W,
) -> Position | None:
    pas = card_w + SLOT_PAD
    dx, dy = pixel[0] - ox, pixel[1] - oy
    if dx < 0 or dy < 0:
        return None
    gx, gy = dx // pas, dy // pas
    if dx - gx * pas >= card_w or dy - gy * pas >= CARD_H:
        return None
    return (x_min + gx, y_min + gy)


def network_pixel_size(
    network: Network,
    extras: tuple[Position, ...] = (),
    card_w: int = CARD_W,
) -> tuple[int, int]:
    """Taille en pixels (largeur, hauteur) du rendu du réseau."""
    x_min, y_min, x_max, y_max = _limites(network, extras)
    pas = card_w + SLOT_PAD
    w = (x_max - x_min + 1) * pas - SLOT_PAD
    h = (y_max - y_min + 1) * (CARD_H + SLOT_PAD) - SLOT_PAD
    return (max(w, card_w), max(h, CARD_H))
