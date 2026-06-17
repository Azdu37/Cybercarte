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
from src.models.card import Card
from src.models.game import Game
from src.models.network import EtatCellule
from src.utils.constants import ACTION_DRAW_INFRA, ACTION_DRAW_BONUS, ACTION_PLAY_CARD, ACTION_DECONNECT
from src.views.ui.components.card_render import (
    draw_tooltip, draw_rounded_rect, draw_card, wrap_text,
    C_BG, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT, C_TEXT, C_TEXT_DIM,
    CARD_W, CARD_H, SLOT_PAD
)
from src.views.ui.components import hud, hand_bar
from src.views.ui.components.network_board import (
    draw_network, pixel_to_pos, network_pixel_size, _limites
)
from src.views.ui.components.log import Log

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
        self.detail_card: Card | None = None
        self.overlay_active = False  # Écran noir entre les tours
        self._opp_net_rects: dict[int, dict[Position, pygame.Rect]] = {}

        # Double clic
        self.last_click_time = 0
        self.last_click_button = None
        self.last_click_pos = (0, 0)

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
        self._btn_dico  = pygame.Rect(mid_x, 272, 160, 34)

    # ── Scroll ───────────────────────────────────────────────────────
    def _scroll_hand(self, delta: int, hand_size: int) -> None:
        """Déplace l'offset de scroll de `delta` cartes (négatif = gauche)."""
        self._hand_scroll = hand_bar.clamp_offset(
            self._hand_scroll + delta, hand_size, self.sw
        )

    def _reset_scroll_for_player(self, hand_size: int) -> None:
        """Remet le scroll à 0 (appelé au changement de joueur)."""
        self._hand_scroll = 0

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
        if self.overlay_active:
            surf.fill((0, 0, 0))
            f = pygame.font.SysFont(None, 36)
            t = f.render("Appuyez sur une touche pour voir vos cartes", True, (255, 255, 255))
            surf.blit(t, t.get_rect(center=(self.sw // 2, self.sh // 2)))
            return

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

        self._btn_dico  = pygame.Rect(log_x + 10, btn_start_y + (btn_h+6)*3, btn_w, btn_h)
        _draw_button(surf, "Fin de tour",   self._btn_fin,   self._btn_fin.collidepoint(mx, my))
        _draw_button(surf, "Piocher Infra", self._btn_infra, self._btn_infra.collidepoint(mx, my))
        _draw_button(surf, "Piocher Bonus", self._btn_bonus, self._btn_bonus.collidepoint(mx, my))

        _draw_button(surf, "📖 Dico", self._btn_dico, self._btn_dico.collidepoint(mx, my))
        # ── Zone gauche : réseaux adversaires ────────────────────────
        others = [p for p in game.players if p is not cp]
        opp_x  = 10
        self._opp_net_rects = {}
        for opp in others:
            nw, nh = network_pixel_size(opp.network, card_w=60)
            if opp_x + nw > log_x - 10:
                break
            if nw > 0 and nh > 0:
                draw_rounded_rect(surf, C_PANEL,
                                  (opp_x - 4, top - 4, nw + 16, nh + 32),
                                  radius=8, border=1, border_color=C_BORDER)
                f = pygame.font.SysFont(None, 14)
                info_txt = f"{opp.name} {opp.nombre_cartes_actives()}/9 | Main: {len(opp.hand)}"
                surf.blit(f.render(info_txt, True, C_TEXT_DIM),
                          (opp_x, top))
                self._opp_net_rects[opp.player_id] = draw_network(
                    surf, opp.network, opp_x, top + 18,
                    card_w=60, card_h=84, current=False, label=""
                )
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

        for pid, rects in self._opp_net_rects.items():
            opp = next(p for p in game.players if p.player_id == pid)
            for pos, r in rects.items():
                if r.collidepoint(mx, my) and pos in opp.network.grille:
                    self.hover_card = opp.network.grille[pos].carte

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
        if self.hover_card and not self.detail_card:
            draw_tooltip(surf, self.hover_card, mx, my, self.sw, self.sh)

        # Message si une carte Malus est sélectionnée
        if self.selected_hand is not None:
            sel_card = cp.hand[self.selected_hand]
            if sel_card.categorie.value == "Malus":
                f_msg = pygame.font.SysFont(None, 24)
                msg_t = f_msg.render("Sélectionnez une carte adverse à déconnecter", True, (255, 100, 100))
                surf.blit(msg_t, (10, bottom - 30))

        # Fenêtre de détail (Popup)
        if self.detail_card:
            self._draw_detail_popup(surf, self.detail_card)

    def _draw_detail_popup(self, surf: pygame.Surface, card: Card) -> None:
        # Overlay sombre
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        # Fenêtre centrale
        pw, ph = 400, 500
        px = (self.sw - pw) // 2
        py = (self.sh - ph) // 2
        rect = pygame.Rect(px, py, pw, ph)
        draw_rounded_rect(surf, C_PANEL, rect, radius=12, border=2, border_color=C_HIGHLIGHT)

        # Petite croix en haut à droite
        self._btn_close_detail = pygame.Rect(px + pw - 30, py + 10, 20, 20)
        pygame.draw.line(surf, (255, 50, 50), (px + pw - 28, py + 12), (px + pw - 12, py + 28), 2)
        pygame.draw.line(surf, (255, 50, 50), (px + pw - 12, py + 12), (px + pw - 28, py + 28), 2)

        # Contenu
        f_title = pygame.font.SysFont(None, 32)
        f_cat = pygame.font.SysFont(None, 20)
        f_desc = pygame.font.SysFont(None, 22)
        f_tag = pygame.font.SysFont(None, 18)

        # Titre
        title_surf = f_title.render(card.nom, True, C_HIGHLIGHT)
        surf.blit(title_surf, (px + 20, py + 20))

        # Catégorie
        cat_surf = f_cat.render(f"Catégorie : {card.categorie.value}", True, C_TEXT_DIM)
        surf.blit(cat_surf, (px + 20, py + 55))

        # Image de la carte (agrandie)
        img_w, img_h = 180, 252
        # On calcule les coordonnées pour centrer l'image dans la popup
        img_x = px + (pw - img_w) // 2
        img_y = py + 85
        
        # Pour dessiner une carte plus grande, on peut utiliser une surface temporaire et la scaler
        temp_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        draw_card(temp_surf, card, 0, 0, selected=False)
        scaled_img = pygame.transform.smoothscale(temp_surf, (img_w, img_h))
        surf.blit(scaled_img, (img_x, img_y))
        
        # Bordure de l'image agrandie
        pygame.draw.rect(surf, C_BORDER, (img_x, img_y, img_w, img_h), width=2, border_radius=8)

        # Description
        desc_y = py + 350
        
        # On essaie de séparer définition et effet si on a notre séparateur \n\n
        parts = (card.description or "Aucune description supplémentaire.").split("\n\n")
        
        current_y = desc_y
        for i, part in enumerate(parts):
            color = C_TEXT if i == 0 else C_TEXT_DIM
            prefix = "" if i == 0 else "⚡ "
            lines = wrap_text(prefix + part, f_desc, pw - 40)
            for line in lines:
                surf.blit(f_desc.render(line, True, color), (px + 20, current_y))
                current_y += 24
            current_y += 8 # petit espace entre definition et effet

        # Tags
        if card.tags:
            tags_txt = "Tags : " + ", ".join(card.tags)
            tags_surf = f_tag.render(tags_txt, True, C_TEXT_DIM)
            surf.blit(tags_surf, (px + 20, py + ph - 40))

    # ── Clics ────────────────────────────────────────────────────────
    def handle_click(self, pos: tuple[int, int], game: Game) -> bool:
        now = pygame.time.get_ticks()
        is_double = (now - self.last_click_time < 300) and (self.last_click_pos == pos)
        self.last_click_time = now
        self.last_click_pos = pos

        if self.detail_card:
            mx, my = pos
            if self._btn_close_detail.collidepoint(mx, my) or not pygame.Rect((self.sw-400)//2, (self.sh-500)//2, 400, 500).collidepoint(mx, my):
                self.detail_card = None
            return False

        if self.overlay_active:
            self.overlay_active = False
            return False

        mx, my = pos
        cp = game.current_player

        # Fin de tour
        if self._btn_fin.collidepoint(mx, my):
            game.next_turn()
            self.selected_hand = None
            self._surlignees   = ()
            self._reset_scroll_for_player(len(game.current_player.hand))
            self.log.add(f"► Tour de {game.current_player.name}")
            self.overlay_active = True
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
            return False

        # Flèche gauche
        if self._btn_left and self._btn_left.collidepoint(mx, my):
            self._scroll_hand(-1, len(cp.hand))
            return False

        # Flèche droite
        if self._btn_right and self._btn_right.collidepoint(mx, my):
            self._scroll_hand(1, len(cp.hand))
            return False

        # Dictionnaire
        if self._btn_dico.collidepoint(mx, my):
            return "open_dico"

        # Carte en main
        for i, r in self._hand_rects:
            if r.collidepoint(mx, my):
                if is_double:
                    self.detail_card = cp.hand[i]
                    return False
                if i == self.selected_hand:
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
            if net_pos in cp.network.grille and is_double:
                self.detail_card = cp.network.grille[net_pos].carte
                return False

            if self.selected_hand is not None:
                if net_pos in self._surlignees:
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

        # Réseaux adverses (pour Malus ciblé)
        if self.selected_hand is not None:
            sel_card = cp.hand[self.selected_hand]
            if sel_card.categorie.value == "Malus":
                for pid, rects in self._opp_net_rects.items():
                    for pos, r in rects.items():
                        if r.collidepoint(mx, my):
                            # On a cliqué sur une carte adverse
                            opp = next(p for p in game.players if p.player_id == pid)
                            if pos in opp.network.grille:
                                ok, msg = game.perform_action(
                                    ACTION_DECONNECT,
                                    target_player_id=pid,
                                    pos=pos
                                )
                                self.log.add(msg)
                                if ok:
                                    # On défausse la carte Malus manuellement si l'action a réussi
                                    # car ACTION_DECONNECT dans Game ne gère pas la défausse de la main
                                    card = cp.hand.pop(self.selected_hand)
                                    game.discard_pile.append(card)
                                    self.selected_hand = None
                                    self._update_surlignees(game)
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
        if self.overlay_active:
            return

        bar_top_y = hand_bar.bar_top(self.sh)
        mx, my = pygame.mouse.get_pos()
        if my >= bar_top_y:   # souris dans la zone de la barre
            self._scroll_hand(-dy, len(game.current_player.hand))

    def handle_key(self, key: int) -> None:
        """Appelé sur un appui touche."""
        if self.overlay_active:
            self.overlay_active = False