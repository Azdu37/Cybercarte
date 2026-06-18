"""
Écran de saisie des noms des joueurs.
Apparaît après la sélection du nombre de joueurs, avant le lancement de la partie.
"""
from __future__ import annotations
import pygame
from src.views.ui.components.card_render import (
    C_BG, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT, C_TEXT, C_TEXT_DIM,
    draw_rounded_rect
)
from src.utils.constants import PLAYER_COLORS

MAX_LEN = 16   # longueur max d'un nom


class NamingScreen:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.sw = screen_w
        self.sh = screen_h
        self.names: list[str] = []        # noms saisis
        self.nb: int = 2                  # nombre de joueurs
        self.active: int = 0             # champ actif (index)
        self._btn_start = pygame.Rect(0, 0, 200, 50)
        self._field_rects: list[pygame.Rect] = []

    def setup(self, nb: int) -> None:
        """Initialise l'écran pour `nb` joueurs."""
        self.nb = nb
        self.active = 0
        self.names = [f"Joueur {i+1}" for i in range(nb)]
        self._pristine = [True] * nb   # True = nom par défaut, effacer au 1er caractère

    # ── Rendu ─────────────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface) -> None:
        surf.fill(C_BG)
        mx, my = pygame.mouse.get_pos()

        # Titre
        tf = pygame.font.SysFont(None, 48)
        t  = tf.render("Noms des joueurs", True, C_HIGHLIGHT)
        surf.blit(t, t.get_rect(center=(self.sw // 2, 120)))

        sf = pygame.font.SysFont(None, 22)
        s  = sf.render("Cliquez sur un champ pour le modifier, puis tapez le nom.", True, C_TEXT_DIM)
        surf.blit(s, s.get_rect(center=(self.sw // 2, 170)))

        # Champs de saisie
        field_w = 340
        field_h = 52
        gap     = 22
        total_h = self.nb * (field_h + gap) - gap
        start_y = self.sh // 2 - total_h // 2 - 20

        self._field_rects = []
        lf  = pygame.font.SysFont(None, 18)
        nf  = pygame.font.SysFont(None, 26)

        for i in range(self.nb):
            fx = self.sw // 2 - field_w // 2
            fy = start_y + i * (field_h + gap)
            r  = pygame.Rect(fx, fy, field_w, field_h)
            self._field_rects.append(r)

            active    = (i == self.active)
            col_bord  = PLAYER_COLORS[i] if active else C_BORDER
            col_bg    = C_PANEL_LIGHT    if active else C_PANEL

            draw_rounded_rect(surf, col_bg, r, radius=10,
                              border=2, border_color=col_bord)

            # Point coloré joueur
            pygame.draw.circle(surf, PLAYER_COLORS[i], (fx - 18, fy + field_h // 2), 8)

            # Texte saisi + curseur clignotant
            name = self.names[i]
            if active:
                cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
                display = name + cursor
            else:
                display = name

            nt = nf.render(display, True, C_TEXT)
            surf.blit(nt, nt.get_rect(midleft=(fx + 14, fy + field_h // 2)))

        # Bouton Lancer
        bx = self.sw // 2 - 100
        by = start_y + self.nb * (field_h + gap) + 30
        self._btn_start = pygame.Rect(bx, by, 200, 50)
        hover = self._btn_start.collidepoint(mx, my)
        draw_rounded_rect(surf, C_HIGHLIGHT if hover else C_PANEL_LIGHT,
                          self._btn_start, radius=10, border=2,
                          border_color=C_HIGHLIGHT)
        bt = pygame.font.SysFont(None, 28).render(
            "Lancer la partie", True, C_BG if hover else C_TEXT)
        surf.blit(bt, bt.get_rect(center=self._btn_start.center))

    # ── Clics ─────────────────────────────────────────────────────────
    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Retourne True si on lance la partie."""
        if self._btn_start.collidepoint(pos):
            # Nettoyer les noms vides
            for i in range(self.nb):
                if not self.names[i].strip():
                    self.names[i] = f"Joueur {i+1}"
            return True

        for i, r in enumerate(self._field_rects):
            if r.collidepoint(pos):
                self.active = i
                return False

        return False

    # ── Clavier ───────────────────────────────────────────────────────
    def handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_BACKSPACE:
            self.names[self.active] = self.names[self.active][:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_TAB):
            # Passer au champ suivant
            self.active = (self.active + 1) % self.nb
        elif event.key == pygame.K_UP:
            self.active = (self.active - 1) % self.nb
        elif event.key == pygame.K_DOWN:
            self.active = (self.active + 1) % self.nb
        elif event.unicode and len(self.names[self.active]) < MAX_LEN:
            if self._pristine[self.active]:
                self.names[self.active] = ""
                self._pristine[self.active] = False
            self.names[self.active] += event.unicode

    def get_names(self) -> list[str]:
        return [n.strip() or f"Joueur {i+1}" for i, n in enumerate(self.names)]