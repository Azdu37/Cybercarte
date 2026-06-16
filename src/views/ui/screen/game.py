"""
Écran de jeu principal — branche le rendu des camarades sur notre vrai moteur.

Layout :
  ┌─────────────────────────────────────────────────────────────────┐
  │  HUD (tour, joueur, actions, pioches)                  [44px]  │
  ├───────────────────────┬────────────┬───────────────────────────┤
  │  Réseau adversaires   │  Journal   │  Réseau joueur courant    │
  │  (small, lecture)     │  + boutons │  (plein, interactif)      │
  ├───────────────────────┴────────────┴───────────────────────────┤
  │  Barre de main                                        [158px]  │
  └─────────────────────────────────────────────────────────────────┘
"""
from __future__ import annotations
import pygame
from src.models.game import Game
from src.models.network import EtatCellule
from src.utils.constants import ACTION_DRAW_INFRA, ACTION_DRAW_BONUS, ACTION_PLAY_CARD
from src.views.ui.components.card_render import (
    draw_tooltip, draw_rounded_rect,
    C_BG, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT, C_TEXT, C_TEXT_DIM,
    CARD_W, CARD_H, SLOT_PAD
)
from src.views.ui.components import hud, hand_bar
from src.views.ui.components.network_board import (
    draw_network, pixel_to_pos, network_pixel_size, _limites
)
from src.views.ui.components.log import Log

Position = tuple[int, int]

# ── Boutons ──────────────────────────────────────────────────────────
def _draw_button(surf, text, rect, hover=False):
    bc = C_HIGHLIGHT if hover else C_BORDER
    draw_rounded_rect(surf, C_PANEL_LIGHT, rect, radius=7, border=2, border_color=bc)
    f = pygame.font.SysFont(None, 18)
    t = f.render(text, True, C_HIGHLIGHT if hover else C_TEXT)
    surf.blit(t, t.get_rect(center=rect.center))
    return rect


class GameScreen:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.sw = screen_w
        self.sh = screen_h
        self.log = Log()

        # État UI
        self.selected_hand: int | None = None   # index carte en main
        self.selected_pos: Position | None = None  # position réseau sélectionnée (pour futur)
        self.hover_card = None

        # Zones (calculées dans _layout)
        self._hand_rects: list[tuple[int, pygame.Rect]] = []
        self._active_net_rects: dict[Position, pygame.Rect] = {}
        self._active_net_origin: tuple[int, int] = (0, 0)
        self._active_net_xmin = 0
        self._active_net_ymin = 0
        self._surlignees: tuple[Position, ...] = ()

        # Boutons (zone centrale)
        mid_x = screen_w - 200
        self._btn_fin   = pygame.Rect(mid_x, 300, 160, 34)
        self._btn_infra = pygame.Rect(mid_x, 344, 160, 34)
        self._btn_bonus = pygame.Rect(mid_x, 388, 160, 34)

    # ── Calcul des positions valides ─────────────────────────────────
    def _update_surlignees(self, game: Game) -> None:
        if self.selected_hand is None:
            self._surlignees = ()
            return
        cp = game.current_player
        if not (0 <= self.selected_hand < len(cp.hand)):
            self._surlignees = ()
            return
        self._surlignees = tuple(cp.valid_positions(cp.hand[self.selected_hand]))

    # ── Rendu complet ────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface, game: Game) -> None:
        surf.fill(C_BG)
        mx, my = pygame.mouse.get_pos()
        self.hover_card = None
        cp = game.current_player

        # HUD
        hud.draw(surf, game, self.sw)

        top = hud.HUD_H + 10
        bottom = hand_bar.bar_top(self.sh) - 10

        # ── Zone centrale : log + boutons ────────────────────────────
        cx = self.sw - 230
        # On sépare le log (haut) et les boutons (bas)
        log_h = 240
        draw_rounded_rect(surf, C_PANEL, (cx, top, 220, log_h), radius=8,
                          border=1, border_color=C_BORDER)
        self.log.draw(surf, cx, top, 220, log_h)

        # Mise à jour de la position des boutons pour qu'ils soient sous le log
        btn_start_y = top + log_h + 10
        self._btn_fin.x = cx + 10
        self._btn_infra.x = cx + 10
        self._btn_bonus.x = cx + 10
        self._btn_fin.w = 200
        self._btn_infra.w = 200
        self._btn_bonus.w = 200
        self._btn_fin.y = btn_start_y
        self._btn_infra.y = btn_start_y + 44
        self._btn_bonus.y = btn_start_y + 88

        hover_fin   = self._btn_fin.collidepoint(mx, my)
        hover_infra = self._btn_infra.collidepoint(mx, my)
        hover_bonus = self._btn_bonus.collidepoint(mx, my)
        _draw_button(surf, "Fin de tour",   self._btn_fin,   hover_fin)
        _draw_button(surf, "Piocher Infra", self._btn_infra, hover_infra)
        _draw_button(surf, "Piocher Bonus", self._btn_bonus, hover_bonus)

        # Réseaux adversaires (gauche, en petit) ───────────────────
        others = [p for p in game.players if p is not cp]
        opp_x = 10
        opp_w = CARD_W * 2 // 3   # cartes réduites
        
        # Limite droite pour les réseaux (ne pas empiéter sur le log/boutons)
        max_net_x = cx - 20
        for opp in others:
            # cadre
            nw, nh = network_pixel_size(opp.network, card_w=60)
            draw_rounded_rect(surf, C_PANEL, (opp_x - 4, top - 4, nw + 16, nh + 32),
                              radius=8, border=1, border_color=C_BORDER)
            f = pygame.font.SysFont(None, 16)
            nb = opp.nombre_cartes_actives()
            t = f.render(f"{opp.name}  {nb}/9", True, C_TEXT_DIM)
            surf.blit(t, (opp_x, top))
            draw_network(surf, opp.network, opp_x, top + 18, card_w=60, card_h=84,
                         current=False, label="")
            opp_x += nw + 20

        # ── Réseau du joueur courant (centre-droite) ─────────────────
        net_w, net_h = network_pixel_size(cp.network, self._surlignees)
        avail_w = cx - 10 - opp_x - 10
        net_ox = opp_x + 10 + max(0, (avail_w - net_w) // 2)
        avail_h = bottom - top
        net_oy = top + max(0, (avail_h - net_h) // 2)

        self._active_net_origin = (net_ox, net_oy)
        x_min, y_min, *_ = _limites(cp.network, self._surlignees)
        self._active_net_xmin = x_min
        self._active_net_ymin = y_min

        self._active_net_rects = draw_network(
            surf, cp.network, net_ox, net_oy,
            current=True,
            positions_surlignees=self._surlignees,
            selected_pos=self.selected_pos,
            label=f"{cp.name}  —  {cp.nombre_cartes_actives()}/9",
        )

        # hover tooltip réseau actif
        for pos, r in self._active_net_rects.items():
            if r.collidepoint(mx, my) and pos in cp.network.grille:
                self.hover_card = cp.network.grille[pos].carte

        # ── Barre de main ─────────────────────────────────────────────
        self._hand_rects = hand_bar.draw(surf, cp.hand, self.sw, self.sh,
                                          selected=self.selected_hand)
        for i, r in self._hand_rects:
            if r.collidepoint(mx, my):
                self.hover_card = cp.hand[i]

        # Tooltip
        if self.hover_card:
            draw_tooltip(surf, self.hover_card, mx, my, self.sw, self.sh)

    # ── Gestion des clics ─────────────────────────────────────────────
    def handle_click(self, pos: tuple[int, int], game: Game) -> bool:
        """
        Traite un clic. Renvoie True si la partie est terminée (victoire).
        """
        mx, my = pos
        cp = game.current_player

        # Bouton Fin de tour
        if self._btn_fin.collidepoint(mx, my):
            game.next_turn()
            self.selected_hand = None
            self._surlignees = ()
            self.log.add(f"► Tour de {game.current_player.name}")
            return False

        # Bouton Piocher Infra
        if self._btn_infra.collidepoint(mx, my):
            ok, msg = game.perform_action(ACTION_DRAW_INFRA)
            self.log.add(msg)
            return False

        # Bouton Piocher Bonus
        if self._btn_bonus.collidepoint(mx, my):
            ok, msg = game.perform_action(ACTION_DRAW_BONUS)
            self.log.add(msg)
            return False

        # Clic sur une carte en main → sélection / désélection
        for i, r in self._hand_rects:
            if r.collidepoint(mx, my):
                if i == self.selected_hand:
                    self.selected_hand = None
                else:
                    self.selected_hand = i
                    self.log.add(f"Sélectionné : {cp.hand[i].nom}")
                self._update_surlignees(game)
                return False

        # Clic sur le réseau actif
        net_pos = pixel_to_pos(
            (mx, my),
            self._active_net_origin[0],
            self._active_net_origin[1],
            self._active_net_xmin,
            self._active_net_ymin,
        )
        if net_pos is not None and self.selected_hand is not None:
            if net_pos in self._surlignees:
                ok, msg = game.perform_action(
                    ACTION_PLAY_CARD,
                    card_index=self.selected_hand,
                    pos=net_pos,
                )
                self.log.add(msg)
                self.selected_hand = None
                self._surlignees = ()
                if ok:
                    winner = game.check_victory()
                    if winner:
                        return True
                return False

        # Clic ailleurs → désélection
        self.selected_hand = None
        self._update_surlignees(game)
        return False
