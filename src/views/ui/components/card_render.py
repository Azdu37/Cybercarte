"""
Rendu d'une carte Pygame — reprend le style visuel de tes camarades
(bande couleur, effet wrappé, hachures si déconnectée) et l'adapte
à notre vrai modèle Card + les connecteurs Données/Électrique.
"""
from __future__ import annotations
import pygame
from src.models.card import Card
from src.models.enums import Connecteur, Direction, CategorieCarte
from src.models.network import EtatCellule

# ── Palette (identique à game.py des camarades) ──────────────────────
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
C_CANARD     = (230, 175,  40)

C_DONNEES    = ( 60, 120, 230)   # carré bleu
C_ELEC       = (235, 175,  60)   # rond orange

CARD_W, CARD_H = 90, 126
SLOT_PAD       = 10

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
    if cat == CategorieCarte.PROTECTION:
        return C_PROTECTION
    if cat in (CategorieCarte.BONUS, CategorieCarte.CAPACITE):
        return C_BONUS
    if cat == CategorieCarte.MALUS:
        return C_ATTACK
    if cat == CategorieCarte.EVENEMENT:
        return C_EVENT
    return C_INFRA


def _card_stripe(card: Card) -> tuple:
    cat = card.categorie
    if cat == CategorieCarte.PROTECTION: return (20, 130, 160)
    if cat in (CategorieCarte.BONUS, CategorieCarte.CAPACITE): return (40, 130, 60)
    if cat == CategorieCarte.MALUS:      return (140, 30, 30)
    if cat == CategorieCarte.EVENEMENT:  return (100, 60, 160)
    return (80, 100, 130)


def _card_text_color(card: Card) -> tuple:
    if card.categorie in (CategorieCarte.PROTECTION, CategorieCarte.MALUS):
        return (255, 255, 255)
    return (20, 20, 30)


# ── Connecteurs sur les bords ─────────────────────────────────────────
def _draw_connectors(surf, card: Card, x: int, y: int, w: int, h: int) -> None:
    """Dessine les indicateurs de connecteur sur les 4 bords de la carte."""
    cx, cy = x + w // 2, y + h // 2
    positions = {
        Direction.NORD:  (cx,     y),
        Direction.SUD:   (cx,     y + h),
        Direction.EST:   (x + w,  cy),
        Direction.OUEST: (x,      cy),
    }
    for direction, (px, py) in positions.items():
        conn = card.connecteur(direction)
        if conn is Connecteur.VIDE:
            continue
        if conn is Connecteur.DONNEES:
            sq = pygame.Rect(px - 6, py - 6, 12, 12)
            pygame.draw.rect(surf, C_DONNEES, sq, border_radius=2)
        else:  # ELECTRIQUE
            pygame.draw.circle(surf, C_ELEC, (px, py), 6)


# ── Rendu principal ───────────────────────────────────────────────────
def draw_card(surf, card: Card, x: int, y: int, *,
              selected: bool = False,
              morte: bool = False,
              small: bool = False) -> pygame.Rect:
    """
    Dessine une carte à (x, y). Renvoie le Rect pour la détection de clics.
    - selected : bordure dorée
    - morte    : grisée + hachures rouges (carte déconnectée)
    - small    : taille réduite (aperçu réseau adverse)
    """
    w = CARD_W if not small else 70
    h = CARD_H if not small else 98

    card_surf = pygame.Surface((w, h), pygame.SRCALPHA)

    bg = C_DISCONNECT if morte else _card_bg(card)
    pygame.draw.rect(card_surf, (*bg, 255), (0, 0, w, h), border_radius=8)

    # Bande couleur en haut
    if not morte:
        stripe = _card_stripe(card)
        pygame.draw.rect(card_surf, (*stripe, 255), (0, 0, w, 6), border_radius=8)
        pygame.draw.rect(card_surf, (0, 0, 0, 0), (0, 3, w, 3))

    # Bordure
    if selected:
        pygame.draw.rect(card_surf, C_HIGHLIGHT, (0, 0, w, h), width=2, border_radius=8)
    else:
        pygame.draw.rect(card_surf, (0, 0, 0, 120), (0, 0, w, h), width=1, border_radius=8)

    # Hachures si déconnectée
    if morte:
        for i in range(0, w + h, 14):
            pygame.draw.line(card_surf, (255, 80, 80, 70),
                             (max(0, i - h), min(h, i)),
                             (min(w, i),     max(0, i - w)), 1)
        lf = pygame.font.SysFont(None, 14)
        lbl = lf.render("DÉCONN.", True, (255, 100, 100))
        card_surf.blit(lbl, (w // 2 - lbl.get_width() // 2, h // 2 - 6))

    # Nom
    nf = pygame.font.SysFont(None, 16 if not small else 13)
    tc = _card_text_color(card)
    for i, line in enumerate(wrap_text(card.nom, nf, w - 10)[:3]):
        card_surf.blit(nf.render(line, True, tc), (5, 10 + i * 13))

    # Effet / description (petit texte)
    if not small and card.description and not morte:
        ef = pygame.font.SysFont(None, 12)
        for i, line in enumerate(wrap_text(card.description, ef, w - 8)[:4]):
            card_surf.blit(ef.render(line, True, (*tc, 180)), (4, h - 42 + i * 10))

    surf.blit(card_surf, (x, y))

    # Connecteurs dessinés directement sur surf (pas sur card_surf pour éviter le clipping)
    if not morte:
        _draw_connectors(surf, card, x, y, w, h)

    return pygame.Rect(x, y, w, h)


def draw_tooltip(surf, card: Card, mx: int, my: int, screen_w: int, screen_h: int) -> None:
    tip_font  = pygame.font.SysFont(None, 18)
    name_font = pygame.font.SysFont(None, 20)
    lines = [card.nom] + wrap_text(card.description or "Carte infrastructure", tip_font, 200)
    tw, th = 230, 20 + len(lines) * 16
    tx = min(mx + 15, screen_w - tw - 5)
    ty = min(my + 15, screen_h - th - 5)
    draw_rounded_rect(surf, C_PANEL_LIGHT, (tx, ty, tw, th), radius=6,
                      border=1, border_color=C_HIGHLIGHT)
    surf.blit(name_font.render(card.nom, True, _card_bg(card)), (tx + 8, ty + 4))
    for i, line in enumerate(lines[1:]):
        surf.blit(tip_font.render(line, True, C_TEXT_DIM), (tx + 8, ty + 20 + i * 14))
