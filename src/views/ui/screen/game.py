"""
Écran de jeu principal.

Layout :
  ┌─────────────────────────────────────────────────────────────────┐
  │  HUD (manche, joueur, actions, pioches)                [44px]  │
  ├───────────────────────┬────────────┬───────────────────────────┤
  │  Réseau adversaires   │  Journal   │  Réseau joueur courant    │
  │  (small, lecture)     │  + boutons │  (plein, interactif)      │
  ├───────────────────────┴────────────┴───────────────────────────┤
  │  Barre de main  ◀ [cartes visibles] ▶              [scroll]   │
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
from src.views.ui.components.event_modal import EventModal
from src.views.ui.components.card_selector import CardSelector
from src.views.ui.components.card_detail_view import CardDetailView


Position = tuple[int, int]


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
        self.selected_hand: int | None = None
        self.selected_pos: Position | None = None
        self.hover_card = None

        # Scroll de la main
        self._hand_scroll: int = 0
        self._btn_left:  pygame.Rect | None = None
        self._btn_right: pygame.Rect | None = None

        # Zones plateau
        self._hand_rects: list[tuple[int, pygame.Rect]] = []
        self._active_net_rects: dict[Position, pygame.Rect] = {}
        self._active_net_origin: tuple[int, int] = (0, 0)
        self._active_net_xmin = 0
        self._active_net_ymin = 0
        self._surlignees: tuple[Position, ...] = ()

        # Boutons (recalculés à chaque frame dans draw)
        mid_x = screen_w - 200
        self._btn_fin   = pygame.Rect(mid_x, 140, 160, 34)
        self._btn_infra = pygame.Rect(mid_x, 184, 160, 34)
        self._btn_bonus = pygame.Rect(mid_x, 228, 160, 34)
        
        # V3: Modals et sélecteurs
        self.event_modal: EventModal | None = None
        self.card_selector: CardSelector | None = None
        self.card_detail_view: CardDetailView | None = None


    # ── Scroll ───────────────────────────────────────────────────────
    def _scroll_hand(self, delta: int, hand_size: int) -> None:
        """Déplace l'offset de scroll de `delta` cartes (négatif = gauche)."""
        self._hand_scroll = hand_bar.clamp_offset(
            self._hand_scroll + delta, hand_size, self.sw
        )

    def _reset_scroll_for_player(self, hand_size: int) -> None:
        """Remet le scroll à 0 (appelé au changement de joueur)."""
        self._hand_scroll = 0
    
    def handle_scroll(self, delta: int, game: Game) -> None:
        """Gère la molette de souris pour le scroll de la main."""
        cp = game.current_player
        self._scroll_hand(-delta, len(cp.hand))

    # ── Positions valides ────────────────────────────────────────────
    def _update_surlignees(self, game: Game) -> None:
        if self.selected_hand is None:
            self._surlignees = ()
            return
        cp = game.current_player
        if not (0 <= self.selected_hand < len(cp.hand)):
            self._surlignees = ()
            return
        self._surlignees = tuple(cp.valid_positions(cp.hand[self.selected_hand]))

    # ── Rendu ────────────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface, game: Game) -> None:
        surf.fill(C_BG)
        mx, my = pygame.mouse.get_pos()
        self.hover_card = None
        cp = game.current_player

        # S'assurer que le scroll est dans les bornes (la main peut avoir changé)
        self._hand_scroll = hand_bar.clamp_offset(
            self._hand_scroll, len(cp.hand), self.sw
        )

        # HUD
        hud.draw(surf, game, self.sw)

        top    = hud.HUD_H + 10
        bottom = hand_bar.bar_top(self.sh) - 10

        # ── Zone droite : log + boutons ──────────────────────────────
        log_w = 280
        log_x = self.sw - log_w - 10
        log_h = 240
        draw_rounded_rect(surf, C_PANEL, (log_x, top, log_w, log_h),
                          radius=8, border=1, border_color=C_BORDER)
        self.log.draw(surf, log_x, top, log_w, log_h)

        btn_start_y = top + log_h + 10
        btn_w = log_w - 20
        btn_h = 32
        self._btn_fin   = pygame.Rect(log_x + 10, btn_start_y,               btn_w, btn_h)
        self._btn_infra = pygame.Rect(log_x + 10, btn_start_y + btn_h + 6,   btn_w, btn_h)
        self._btn_bonus = pygame.Rect(log_x + 10, btn_start_y + (btn_h+6)*2, btn_w, btn_h)

        _draw_button(surf, "Fin de tour",   self._btn_fin,   self._btn_fin.collidepoint(mx, my))
        _draw_button(surf, "Piocher Infra", self._btn_infra, self._btn_infra.collidepoint(mx, my))
        _draw_button(surf, "Piocher Bonus", self._btn_bonus, self._btn_bonus.collidepoint(mx, my))

        # ── Zone gauche : réseaux adversaires ────────────────────────
        others = [p for p in game.players if p is not cp]
        opp_x  = 10
        for opp in others:
            nw, nh = network_pixel_size(opp.network, card_w=60)
            if opp_x + nw > log_x - 10:
                break
            if nw > 0 and nh > 0:
                draw_rounded_rect(surf, C_PANEL,
                                  (opp_x - 4, top - 4, nw + 16, nh + 32),
                                  radius=8, border=1, border_color=C_BORDER)
                f = pygame.font.SysFont(None, 14)
                surf.blit(f.render(f"{opp.name} {opp.nombre_cartes_actives()}/9", True, C_TEXT_DIM),
                          (opp_x, top))
                draw_network(surf, opp.network, opp_x, top + 18,
                             card_w=60, card_h=84, current=False, label="")
                opp_x += nw + 20

        # ── Réseau joueur courant ────────────────────────────────────
        net_w, net_h = network_pixel_size(cp.network, self._surlignees)
        net_ox = 10 + (log_x - 20) // 2 - net_w // 2
        net_ox = max(10, min(net_ox, log_x - 20 - net_w))
        net_oy = top + max(0, (bottom - top - net_h) // 2)

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

        for pos, r in self._active_net_rects.items():
            if r.collidepoint(mx, my) and pos in cp.network.grille:
                self.hover_card = cp.network.grille[pos].carte

        # ── Barre de main avec scroll ────────────────────────────────
        self._hand_rects, self._btn_left, self._btn_right = hand_bar.draw(
            surf, cp.hand, self.sw, self.sh,
            selected=self.selected_hand,
            scroll_offset=self._hand_scroll,
        )
        for i, r in self._hand_rects:
            if r.collidepoint(mx, my):
                self.hover_card = cp.hand[i]

        # Tooltip
        if self.hover_card:
            draw_tooltip(surf, self.hover_card, mx, my, self.sw, self.sh)
        
        # V3: Affichage des modals
        if self.event_modal:
            self.event_modal.draw(surf, self.sw, self.sh)
        
        # V3: Créer le sélecteur si un effet est en attente
        if game.pending_effect and not self.card_selector:
            effect = game.pending_effect
            if effect["effect_type"] == "deconnecter":
                msg = f"Sélectionnez {effect['count']} carte(s) à désactiver"
                self.card_selector = CardSelector(
                    msg,
                    effect["count"],
                    effect["available_positions"],
                    effect["player"].network.grille,
                )
        
        if self.card_selector:
            self.card_selector.draw(surf, self.sw, self.sh,
                                   self._active_net_origin[0], self._active_net_origin[1])
        
        # V3: Afficher les détails d'une carte
        if self.card_detail_view:
            self.card_detail_view.draw(surf, self.sw, self.sh)


    # ── Clics ────────────────────────────────────────────────────────
    def handle_click(self, pos: tuple[int, int], game: Game) -> bool:
        mx, my = pos
        cp = game.current_player
        
        # V3: Gestion des detéails de cartes en priorité
        if self.card_detail_view and self.card_detail_view.visible:
            if self.card_detail_view.handle_click(pos):
                self.card_detail_view = None
            return False
        
        # V3: Gestion des modals en priorité
        if self.event_modal and self.event_modal.visible:
            if self.event_modal.handle_click(pos):
                return False
        
        if self.card_selector and self.card_selector.visible:
            result = self.card_selector.handle_click(pos)
            if result is True:
                # Sélection complète
                selected = self.card_selector.selected
                game.apply_pending_effect_selection(selected)
                self.log.add(f"Cartes désactivées : {len(selected)}")
                self.card_selector = None
            elif result is False:
                # Clic sur une carte
                pass
            return False

        # Fin de tour
        if self._btn_fin.collidepoint(mx, my):
            game.next_turn()
            self.selected_hand = None
            self._surlignees   = ()
            self._reset_scroll_for_player(len(game.current_player.hand))
            self.log.add(f"► Tour de {game.current_player.name}")
            return False

        # Piocher infra
        if self._btn_infra.collidepoint(mx, my):
            ok, msg = game.perform_action(ACTION_DRAW_INFRA)
            self.log.add(msg)
            return False

        # Piocher bonus
        if self._btn_bonus.collidepoint(mx, my):
            ok, msg = game.perform_action(ACTION_DRAW_BONUS)
            self.log.add(msg)
            
            # V3: Afficher un modal explicatif
            if ok and game.last_effect_card:
                card = game.last_effect_card
                # Construire la liste des impacts
                players_affected = {}
                if card.categorie.value == "malus":
                    # Malus : affecte un adversaire
                    opponents = [p for p in game.players if p is not cp]
                    for opp in opponents:
                        players_affected[opp.name] = [f"Perte possible d'une carte active"]
                elif card.categorie.value == "bonus":
                    # Bonus : affecte le joueur courant
                    players_affected[cp.name] = [f"Réparation possible"]
                
                self.event_modal = EventModal(card, players_affected)
            
            return False

        # Flèche gauche
        if self._btn_left and self._btn_left.collidepoint(mx, my):
            self._scroll_hand(-1, len(cp.hand))
            return False

        # Flèche droite
        if self._btn_right and self._btn_right.collidepoint(mx, my):
            self._scroll_hand(1, len(cp.hand))
            return False

        # Carte en main
        for i, r in self._hand_rects:
            if r.collidepoint(mx, my):
                if i == self.selected_hand:
                    # Double clic affiche les détails
                    self.card_detail_view = CardDetailView(cp.hand[i])
                    self.selected_hand = None
                else:
                    self.selected_hand = i
                    self.log.add(f"Sélectionné : {cp.hand[i].nom}")
                self._update_surlignees(game)
                return False

        # Réseau actif
        net_pos = pixel_to_pos(
            (mx, my),
            self._active_net_origin[0], self._active_net_origin[1],
            self._active_net_xmin, self._active_net_ymin,
        )
        if net_pos is not None:
            if self.selected_hand is not None and net_pos in self._surlignees:
                ok, msg = game.perform_action(
                    ACTION_PLAY_CARD,
                    card_index=self.selected_hand,
                    pos=net_pos,
                )
                self.log.add(msg)
                self.selected_hand = None
                self._surlignees   = ()
                if ok and game.check_victory():
                    return True
                return False
            elif self.selected_hand is None and net_pos in cp.network.grille:
                # V3: Afficher les détails de la carte du réseau
                cel = cp.network.grille[net_pos]
                self.card_detail_view = CardDetailView(cel.carte)
                return False

        # Désélection
        self.selected_hand = None
        self._update_surlignees(game)
        return False

    # ── Molette ──────────────────────────────────────────────────────
    def handle_scroll(self, dy: int, game: Game) -> None:
        """
        À appeler depuis game_controller sur l'événement MOUSEWHEEL.
        dy > 0 = molette vers le haut = scroll vers la gauche.
        """
        bar_top_y = hand_bar.bar_top(self.sh)
        mx, my = pygame.mouse.get_pos()
        if my >= bar_top_y:   # souris dans la zone de la barre
            self._scroll_hand(-dy, len(game.current_player.hand))