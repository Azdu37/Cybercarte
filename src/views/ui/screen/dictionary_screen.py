"""
Écran Dictionnaire — consultable depuis le menu ET depuis la partie.

Layout :
  ┌──────────────────────────────────────────────────────────────┐
  │  Titre + bouton Retour                              [60px]  │
  ├────────────────┬─────────────────────────────────────────────┤
  │  Catégories    │  Cartes de la catégorie sélectionnée        │
  │  (liste)       │  (scrollable)                               │
  └────────────────┴─────────────────────────────────────────────┘
"""
from __future__ import annotations
import pygame
from src.data.dictionary import DICTIONARY
from src.views.ui.components.card_render import (
    C_BG, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT,
    C_TEXT, C_TEXT_DIM, draw_rounded_rect
)

# Layout
HEADER_H   = 60
CAT_W      = 210     # largeur du panneau catégories
CARD_H     = 110     # hauteur d'une fiche de carte
CARD_PAD   = 12
SCROLL_W   = 14


def _wrap(text: str, font, max_w: int) -> list[str]:
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


class DictionaryScreen:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.sw = screen_w
        self.sh = screen_h
        self.cat_index  = 0     # catégorie sélectionnée
        self.scroll_y   = 0     # offset scroll (pixels)
        self._btn_back  = pygame.Rect(screen_w - 160, (HEADER_H - 36) // 2, 140, 36)
        self._cat_rects: list[pygame.Rect] = []
        self._content_h = 0    # hauteur totale du contenu (pour scroll)

    def reset(self) -> None:
        """Remet le scroll à zéro (utile quand on change de catégorie)."""
        self.scroll_y = 0

    # ── Rendu ─────────────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface) -> None:
        surf.fill(C_BG)
        mx, my = pygame.mouse.get_pos()

        # ── En-tête ────────────────────────────────────────────────
        pygame.draw.rect(surf, C_PANEL, (0, 0, self.sw, HEADER_H))
        pygame.draw.line(surf, C_BORDER, (0, HEADER_H), (self.sw, HEADER_H), 1)

        tf = pygame.font.SysFont(None, 36)
        t  = tf.render("📖  Dictionnaire du jeu", True, C_HIGHLIGHT)
        surf.blit(t, (20, (HEADER_H - t.get_height()) // 2))

        # Bouton Retour
        hover_back = self._btn_back.collidepoint(mx, my)
        draw_rounded_rect(surf, C_HIGHLIGHT if hover_back else C_PANEL_LIGHT,
                          self._btn_back, radius=8, border=2,
                          border_color=C_HIGHLIGHT if hover_back else C_BORDER)
        bf = pygame.font.SysFont(None, 24)
        bt = bf.render("← Retour", True, C_BG if hover_back else C_TEXT)
        surf.blit(bt, bt.get_rect(center=self._btn_back.center))

        # ── Panneau catégories (gauche) ─────────────────────────────
        pygame.draw.rect(surf, C_PANEL, (0, HEADER_H, CAT_W, self.sh - HEADER_H))
        pygame.draw.line(surf, C_BORDER, (CAT_W, HEADER_H), (CAT_W, self.sh), 1)

        self._cat_rects = []
        cf = pygame.font.SysFont(None, 22)
        for i, section in enumerate(DICTIONARY):
            ry = HEADER_H + 10 + i * 52
            r  = pygame.Rect(8, ry, CAT_W - 16, 44)
            self._cat_rects.append(r)
            selected = (i == self.cat_index)
            hover    = r.collidepoint(mx, my)
            cat_col  = tuple(section["couleur"])
            if selected:
                draw_rounded_rect(surf, cat_col, r, radius=8)
            elif hover:
                draw_rounded_rect(surf, C_PANEL_LIGHT, r, radius=8,
                                  border=1, border_color=cat_col)
            else:
                draw_rounded_rect(surf, C_PANEL, r, radius=8,
                                  border=1, border_color=C_BORDER)
            label_col = C_BG if selected else (cat_col if not selected else C_TEXT)
            lt = cf.render(section["categorie"], True, C_BG if selected else C_TEXT)
            surf.blit(lt, lt.get_rect(center=r.center))

        # ── Zone de contenu (droite) ────────────────────────────────
        content_x  = CAT_W + 10
        content_w  = self.sw - CAT_W - SCROLL_W - 20
        content_y0 = HEADER_H + 10

        # Clip pour que le contenu ne déborde pas sur l'en-tête
        clip = pygame.Rect(content_x, content_y0,
                           content_w + SCROLL_W, self.sh - content_y0)
        surf.set_clip(clip)

        section  = DICTIONARY[self.cat_index]
        cat_col  = tuple(section["couleur"])
        cartes   = section["cartes"]

        nf  = pygame.font.SysFont(None, 24)
        df  = pygame.font.SysFont(None, 20)
        ef  = pygame.font.SysFont(None, 18)
        lbl = pygame.font.SysFont(None, 16)

        y = content_y0 - self.scroll_y
        total_h = 0

        for card in cartes:
            # Calcul de la hauteur réelle de la fiche
            def_lines    = _wrap(card["definition"], df, content_w - 24)
            effet_lines  = _wrap("⚡ " + card["effet"], ef, content_w - 24)
            fiche_h = 14 + 24 + 8 + len(def_lines)*18 + 6 + len(effet_lines)*16 + 14

            r = pygame.Rect(content_x, y, content_w, fiche_h)
            # Fond coloré atténué
            bg = (*cat_col, 30)
            fiche_surf = pygame.Surface((content_w, fiche_h), pygame.SRCALPHA)
            pygame.draw.rect(fiche_surf, (*cat_col, 25), (0, 0, content_w, fiche_h), border_radius=10)
            pygame.draw.rect(fiche_surf, (*cat_col, 160), (0, 0, content_w, fiche_h),
                             width=1, border_radius=10)
            surf.blit(fiche_surf, (content_x, y))

            # Bande couleur gauche
            pygame.draw.rect(surf, cat_col, (content_x, y + 10, 4, fiche_h - 20), border_radius=2)

            ty = y + 14
            # Nom
            nt = nf.render(card["nom"], True, C_HIGHLIGHT)
            surf.blit(nt, (content_x + 16, ty))
            ty += 26

            # Définition
            for line in def_lines:
                surf.blit(df.render(line, True, C_TEXT), (content_x + 16, ty))
                ty += 18
            ty += 6

            # Effet
            for line in effet_lines:
                surf.blit(ef.render(line, True, C_TEXT_DIM), (content_x + 16, ty))
                ty += 16

            y        += fiche_h + CARD_PAD
            total_h  += fiche_h + CARD_PAD

        self._content_h = total_h
        surf.set_clip(None)

        # ── Scrollbar ───────────────────────────────────────────────
        visible_h = self.sh - content_y0
        if total_h > visible_h:
            ratio    = visible_h / total_h
            bar_h    = max(30, int(visible_h * ratio))
            bar_y    = content_y0 + int(self.scroll_y / total_h * visible_h)
            bar_x    = self.sw - SCROLL_W - 4
            pygame.draw.rect(surf, C_PANEL, (bar_x, content_y0, SCROLL_W, visible_h), border_radius=4)
            pygame.draw.rect(surf, C_BORDER, (bar_x, bar_y, SCROLL_W, bar_h), border_radius=4)

    # ── Interactions ──────────────────────────────────────────────────
    def handle_click(self, pos: tuple[int, int]) -> str | None:
        """
        Retourne :
          "back"  si le joueur clique Retour
          None    sinon
        """
        if self._btn_back.collidepoint(pos):
            return "back"

        for i, r in enumerate(self._cat_rects):
            if r.collidepoint(pos):
                self.cat_index = i
                self.scroll_y  = 0
                return None

        return None

    def handle_scroll(self, dy: int) -> None:
        """Scroll molette (dy > 0 = haut)."""
        visible_h = self.sh - HEADER_H - 10
        max_scroll = max(0, self._content_h - visible_h)
        self.scroll_y = max(0, min(self.scroll_y - dy * 30, max_scroll))

    def handle_key(self, key: int) -> str | None:
        if key == pygame.K_ESCAPE:
            return "back"
        if key == pygame.K_DOWN:
            self.handle_scroll(-1)
        if key == pygame.K_UP:
            self.handle_scroll(1)
        return None