"""
Rendu d'une carte Pygame.

Si une image PNG existe dans assets/cards/ pour cette carte, elle est
affichée directement (mise à l'échelle). Sinon, fallback sur le rendu
coloré généré (rectangles + texte).

Les indicateurs de connecteur (carré bleu / rond orange) sont toujours
dessinés PAR-DESSUS l'image, sur les bords de la carte.
Les hachures rouges "DÉCONN." sont appliquées en surcouche si la carte
est morte.
"""
from __future__ import annotations
import pygame
from src.models.card import Card
from src.models.enums import Connecteur, Direction, CategorieCarte
from src.models.network import EtatCellule
from src.utils.card_assets import get_card_surface

# ── Palette ──────────────────────────────────────────────────────────
C_BG          = (18,  22,  35)
C_PANEL       = (28,  33,  50)
C_PANEL_LIGHT = (38,  45,  65)
C_BORDER      = (60,  70, 100)
C_HIGHLIGHT   = (255, 215,   0)
C_TEXT        = (230, 230, 240)
C_TEXT_DIM    = (130, 135, 155)

C_INFRA      = (195, 210, 220)
C_PROTECTION = ( 80, 195, 215)
C_BONUS      = ( 90, 185, 100)
C_ATTACK     = (195,  70,  70)
C_EVENT      = (160, 110, 210)
C_DISCONNECT = ( 90,  90, 100)

C_DONNEES = ( 60, 120, 230)   # carré bleu
C_ELEC    = (235, 175,  60)   # rond orange

CARD_W, CARD_H = 90, 126
SLOT_PAD       = 10

# Taille des indicateurs de connecteur (en px, sur la carte pleine)
_CONN_R_FULL  = 7
_CONN_R_SMALL = 5


# ── Helpers ──────────────────────────────────────────────────────────
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


def draw_rounded_rect(surf, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, width=border, border_radius=radius)


def _card_bg(card: Card) -> tuple:
    cat = card.categorie
    if cat == CategorieCarte.PROTECTION:  return C_PROTECTION
    if cat in (CategorieCarte.BONUS, CategorieCarte.CAPACITE): return C_BONUS
    if cat == CategorieCarte.MALUS:       return C_ATTACK
    if cat == CategorieCarte.EVENEMENT:   return C_EVENT
    return C_INFRA


def _card_stripe(card: Card) -> tuple:
    cat = card.categorie
    if cat == CategorieCarte.PROTECTION:                       return (20, 130, 160)
    if cat in (CategorieCarte.BONUS, CategorieCarte.CAPACITE): return (40, 130,  60)
    if cat == CategorieCarte.MALUS:                            return (140, 30,  30)
    if cat == CategorieCarte.EVENEMENT:                        return (100, 60, 160)
    return (80, 100, 130)


def _card_text_color(card: Card) -> tuple:
    if card.categorie in (CategorieCarte.PROTECTION, CategorieCarte.MALUS):
        return (255, 255, 255)
    return (20, 20, 30)


# ── Connecteurs ───────────────────────────────────────────────────────
def _draw_connectors(surf, card: Card, x: int, y: int, w: int, h: int,
                     small: bool = False) -> None:
    r = _CONN_R_SMALL if small else _CONN_R_FULL
    sq = r * 2
    cx, cy = x + w // 2, y + h // 2
    positions = {
        Direction.NORD:  (cx,    y),
        Direction.SUD:   (cx,    y + h),
        Direction.EST:   (x + w, cy),
        Direction.OUEST: (x,     cy),
    }
    for direction, (px, py) in positions.items():
        conn = card.connecteur(direction)
        if conn is Connecteur.VIDE:
            continue
        if conn is Connecteur.DONNEES:
            rect = pygame.Rect(px - r, py - r, sq, sq)
            pygame.draw.rect(surf, C_DONNEES, rect, border_radius=2)
            pygame.draw.rect(surf, (0, 0, 0), rect, width=1, border_radius=2)
        else:  # ELECTRIQUE
            pygame.draw.circle(surf, C_ELEC, (px, py), r)
            pygame.draw.circle(surf, (0, 0, 0), (px, py), r, 1)


# ── Surcouche "déconnectée" ───────────────────────────────────────────
def _draw_dead_overlay(card_surf: pygame.Surface, w: int, h: int) -> None:
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))          # assombrissement semi-transparent
    for i in range(0, w + h, 14):
        pygame.draw.line(overlay, (255, 60, 60, 100),
                         (max(0, i - h), min(h, i)),
                         (min(w, i),     max(0, i - w)), 1)
    card_surf.blit(overlay, (0, 0))
    lf = pygame.font.SysFont(None, 14)
    lbl = lf.render("DÉCONN.", True, (255, 100, 100))
    card_surf.blit(lbl, (w // 2 - lbl.get_width() // 2, h // 2 - 6))


# ── Fallback (rendu coloré sans image) ───────────────────────────────
def _draw_fallback(card_surf: pygame.Surface, card: Card, w: int, h: int,
                   morte: bool) -> None:
    bg = C_DISCONNECT if morte else _card_bg(card)
    pygame.draw.rect(card_surf, (*bg, 255), (0, 0, w, h), border_radius=8)
    if not morte:
        stripe = _card_stripe(card)
        pygame.draw.rect(card_surf, (*stripe, 255), (0, 0, w, 6), border_radius=8)
        pygame.draw.rect(card_surf, (0, 0, 0, 0), (0, 3, w, 3))
    nf = pygame.font.SysFont(None, 14)
    tc = _card_text_color(card)
    for i, line in enumerate(wrap_text(card.nom, nf, w - 8)[:3]):
        card_surf.blit(nf.render(line, True, tc), (4, 8 + i * 13))


# ── Rendu principal ───────────────────────────────────────────────────
def draw_card(surf, card: Card, x: int, y: int, *,
              selected: bool = False,
              morte: bool = False,
              small: bool = False,
              just_drawn: bool = False) -> pygame.Rect:
    """
    Dessine une carte à (x, y). Renvoie le Rect (détection de clics).
      selected : bordure dorée
      morte    : assombrissement + hachures rouges
      small    : taille réduite (réseau adverse)
    """
    w = CARD_W if not small else 60
    h = CARD_H if not small else 84

    card_surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # ── Image réelle ──────────────────────────────────────────────────
    img = get_card_surface(card.nom, card.id, w, h)
    if img is not None:
        card_surf.blit(img, (0, 0))
    else:
        _draw_fallback(card_surf, card, w, h, morte=False)

    # ── Surcouche mort ───────────────────────────────────────────────
    if morte:
        _draw_dead_overlay(card_surf, w, h)

    # ── Bordure (sélection ou normale) ───────────────────────────────
    if selected:
        pygame.draw.rect(card_surf, C_HIGHLIGHT, (0, 0, w, h), width=3, border_radius=8)
    elif just_drawn:
        pygame.draw.rect(card_surf, (80, 220, 130), (0, 0, w, h), width=2, border_radius=8)
    else:
        pygame.draw.rect(card_surf, (0, 0, 0, 160), (0, 0, w, h), width=1, border_radius=8)

    if just_drawn:
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        alpha = int(80 + 140 * pulse)
        halo = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
        pygame.draw.rect(halo, (80, 220, 130, alpha), (0, 0, w + 10, h + 10), border_radius=11)
        surf.blit(halo, (x - 5, y - 5))

    surf.blit(card_surf, (x, y))

    # ── Connecteurs (dessinés sur surf pour ne pas être coupés) ──────
    if not morte and card.est_placable():
        _draw_connectors(surf, card, x, y, w, h, small=small)

    return pygame.Rect(x, y, w, h)


# ── Tooltip ───────────────────────────────────────────────────────────
def draw_tooltip(surf, card: Card, mx: int, my: int,
                 screen_w: int, screen_h: int) -> None:
    tip_font  = pygame.font.SysFont(None, 18)
    name_font = pygame.font.SysFont(None, 20)
    
    # On prend la première partie de la description (la définition) pour le tooltip
    full_desc = card.description or "Carte infrastructure"
    desc = full_desc.split("\n\n")[0]
    
    lines = wrap_text(desc, tip_font, 210)
    tw, th = 240, 28 + len(lines) * 15
    tx = min(mx + 15, screen_w - tw - 5)
    ty = min(my + 15, screen_h - th - 5)
    draw_rounded_rect(surf, C_PANEL_LIGHT, (tx, ty, tw, th),
                      radius=6, border=1, border_color=C_HIGHLIGHT)
    surf.blit(name_font.render(card.nom, True, C_HIGHLIGHT), (tx + 8, ty + 5))
    for i, line in enumerate(lines):
        surf.blit(tip_font.render(line, True, C_TEXT_DIM), (tx + 8, ty + 22 + i * 14))