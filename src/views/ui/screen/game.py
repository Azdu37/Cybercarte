"""
Écran de jeu principal.

Layout :
  ┌─────────────────────────────────────────────────────────────────┐
  │  HUD (manche, joueur, actions, pioches)                [44px]  │
  ├───────────────────────┬────────────────────────────────────────┤
  │  Réseau adversaires   │  Journal (scrollable) ▲▼              │
  │  (small, lecture)     │  Zone objectif (dorée)                 │
  │                       │  Boutons                               │
  ├───────────────────────┴────────────────────────────────────────┤
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

# Couleurs zone objectif
C_OBJ_BG     = (40, 36, 20)
C_OBJ_BORDER = (180, 150, 40)
C_OBJ_TEXT   = (230, 200, 80)

# Couleurs bouton/popup capitulation
C_CAP_BTN    = (120, 30, 30)
C_CAP_HOVER  = (180, 50, 50)
C_CAP_POPUP  = (28, 22, 22)


def _draw_button(surf, text, rect, hover=False):
    bc = C_HIGHLIGHT if hover else C_BORDER
    draw_rounded_rect(surf, C_PANEL_LIGHT, rect, radius=7, border=2, border_color=bc)
    f = pygame.font.SysFont(None, 18)
    t = f.render(text, True, C_HIGHLIGHT if hover else C_TEXT)
    surf.blit(t, t.get_rect(center=rect.center))
    return rect


def _draw_objectif(surf: pygame.Surface, player, x: int, y: int, w: int) -> int:
    """Dessine la zone objectif. Retourne la hauteur occupée."""
    f_lbl  = pygame.font.SysFont(None, 16)
    f_nom  = pygame.font.SysFont(None, 18)
    f_desc = pygame.font.SysFont(None, 16)

    if player.objectif is None:
        h = 34
        draw_rounded_rect(surf, C_OBJ_BG, (x, y, w, h),
                          radius=6, border=1, border_color=C_OBJ_BORDER)
        t = f_lbl.render("Pas d'objectif assigné", True, C_TEXT_DIM)
        surf.blit(t, t.get_rect(center=(x + w // 2, y + h // 2)))
        return h

    obj   = player.objectif
    desc  = obj.description or obj.nom
    lines = wrap_text(desc, f_desc, w - 20)
    h     = 12 + 16 + 18 + len(lines) * 15 + 10

    draw_rounded_rect(surf, C_OBJ_BG, (x, y, w, h),
                      radius=6, border=1, border_color=C_OBJ_BORDER)
    pygame.draw.rect(surf, C_OBJ_BORDER, (x, y + 8, 3, h - 16), border_radius=2)

    ty = y + 8
    surf.blit(f_lbl.render("🎯  Votre objectif secret", True, C_OBJ_BORDER), (x + 10, ty))
    ty += 16
    surf.blit(f_nom.render(obj.nom, True, C_OBJ_TEXT), (x + 10, ty))
    ty += 18
    for line in lines:
        surf.blit(f_desc.render(line, True, C_TEXT_DIM), (x + 10, ty))
        ty += 15

    if player.personal_objective_accomplished:
        ok = f_lbl.render("✓ Accompli  (+5 pts)", True, (100, 220, 100))
        surf.blit(ok, (x + 10, ty))

    return h


class GameScreen:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.sw = screen_w
        self.sh = screen_h
        self.log = Log()

        # État UI
        self.selected_hand: int | None = None
        self.just_drawn: int | None = None 
        self.selected_pos:  Position | None = None
        self.hover_card = None
        self.detail_card: Card | None = None
        self.overlay_active = False
        self._opp_net_rects: dict[int, dict[Position, pygame.Rect]] = {}

        # Double clic
        self.last_click_time  = 0
        self.last_click_pos   = (0, 0)

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

        # Boutons
        mid_x = screen_w - 200
        self._btn_fin   = pygame.Rect(mid_x, 140, 160, 34)
        self._btn_infra = pygame.Rect(mid_x, 184, 160, 34)
        self._btn_bonus = pygame.Rect(mid_x, 228, 160, 34)
        self._btn_dico  = pygame.Rect(mid_x, 272, 160, 34)
        self._btn_close_detail = pygame.Rect(0, 0, 20, 20)

        # Capitulation
        self._btn_cap = pygame.Rect(10, 10, 120, 34)   # repositionné dans draw()
        self.show_confirm_cap = False   # True = popup de confirmation affiché

    # ── Scroll main ───────────────────────────────────────────────────
    def _scroll_hand(self, delta: int, hand_size: int) -> None:
        self._hand_scroll = hand_bar.clamp_offset(
            self._hand_scroll + delta, hand_size, self.sw
        )

    def _reset_scroll_for_player(self, hand_size: int) -> None:
        self._hand_scroll = 0

    # ── Positions valides ─────────────────────────────────────────────
    def _update_surlignees(self, game: Game) -> None:
        if self.selected_hand is None:
            self._surlignees = ()
            return
        cp = game.current_player
        if not (0 <= self.selected_hand < len(cp.hand)):
            self._surlignees = ()
            return
        self._surlignees = tuple(cp.valid_positions(cp.hand[self.selected_hand]))

    # ── Rendu ─────────────────────────────────────────────────────────
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

        self._hand_scroll = hand_bar.clamp_offset(
            self._hand_scroll, len(cp.hand), self.sw
        )

        hud.draw(surf, game, self.sw)

        top    = hud.HUD_H + 10
        bottom = hand_bar.bar_top(self.sh) - 10

        # ── Panneau droit ─────────────────────────────────────────────
        log_w = 280
        log_x = self.sw - log_w - 10

        btn_h      = 32
        btn_gap    = 6
        nb_btn     = 4
        btns_h     = nb_btn * (btn_h + btn_gap)
        obj_h_est  = 85
        log_h      = max(80, (bottom - top) - btns_h - obj_h_est - 24)

        # Journal scrollable
        self.log.draw(surf, log_x, top, log_w, log_h)

        # Zone objectif
        obj_y = top + log_h + 6
        obj_h = _draw_objectif(surf, cp, log_x, obj_y, log_w)

        # Boutons
        btn_start_y = obj_y + obj_h + 6
        btn_w = log_w - 20
        self._btn_fin   = pygame.Rect(log_x + 10, btn_start_y,                     btn_w, btn_h)
        self._btn_infra = pygame.Rect(log_x + 10, btn_start_y + (btn_h+btn_gap),   btn_w, btn_h)
        self._btn_bonus = pygame.Rect(log_x + 10, btn_start_y + (btn_h+btn_gap)*2, btn_w, btn_h)
        self._btn_dico  = pygame.Rect(log_x + 10, btn_start_y + (btn_h+btn_gap)*3, btn_w, btn_h)

        _draw_button(surf, "Fin de tour",   self._btn_fin,   self._btn_fin.collidepoint(mx, my))
        _draw_button(surf, "Piocher Infra", self._btn_infra, self._btn_infra.collidepoint(mx, my))
        _draw_button(surf, "Piocher Bonus", self._btn_bonus, self._btn_bonus.collidepoint(mx, my))
        _draw_button(surf, "📖 Dico",       self._btn_dico,  self._btn_dico.collidepoint(mx, my))

        # ── Réseaux adversaires ────────────────────────────────────────
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
                surf.blit(f.render(info_txt, True, C_TEXT_DIM), (opp_x, top))
                self._opp_net_rects[opp.player_id] = draw_network(
                    surf, opp.network, opp_x, top + 18,
                    card_w=60, card_h=84, current=False, label=""
                )
                opp_x += nw + 20

        # ── Réseau joueur courant ──────────────────────────────────────
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

        # ── Barre de main ──────────────────────────────────────────────
        self._hand_rects, self._btn_left, self._btn_right = hand_bar.draw(
            surf, cp.hand, self.sw, self.sh,
            selected=self.selected_hand,
            scroll_offset=self._hand_scroll,
        )
        for i, r in self._hand_rects:
            if r.collidepoint(mx, my):
                self.hover_card = cp.hand[i]

        if self.hover_card and not self.detail_card:
            draw_tooltip(surf, self.hover_card, mx, my, self.sw, self.sh)

        if self.selected_hand is not None:
            sel_card = cp.hand[self.selected_hand]
            if sel_card.categorie.value == "Malus":
                f_msg = pygame.font.SysFont(None, 24)
                msg_t = f_msg.render("Sélectionnez une carte adverse à déconnecter", True, (255, 100, 100))
                surf.blit(msg_t, (10, bottom - 30))

        # ── Bouton Capitulation (bas gauche) ─────────────────────────
        bar_top_y = hand_bar.bar_top(self.sh)
        self._btn_cap = pygame.Rect(10, bar_top_y - 44, 120, 34)
        mx_c, my_c = pygame.mouse.get_pos()
        hover_cap = self._btn_cap.collidepoint(mx_c, my_c)
        cap_col = C_CAP_HOVER if hover_cap else C_CAP_BTN
        pygame.draw.rect(surf, cap_col, self._btn_cap, border_radius=8)
        pygame.draw.rect(surf, (255, 80, 80), self._btn_cap, width=1, border_radius=8)
        cf = pygame.font.SysFont(None, 18)
        ct = cf.render("⚑  Capituler", True, (255, 200, 200))
        surf.blit(ct, ct.get_rect(center=self._btn_cap.center))

        # ── Popup confirmation capitulation ───────────────────────────
        if self.show_confirm_cap:
            self._draw_confirm_cap(surf)

        if self.detail_card:
            self._draw_detail_popup(surf, self.detail_card)

    def _draw_confirm_cap(self, surf: pygame.Surface) -> None:
        """Popup de confirmation de capitulation."""
        # Overlay sombre
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        pw, ph = 420, 200
        px = (self.sw - pw) // 2
        py = (self.sh - ph) // 2
        draw_rounded_rect(surf, C_CAP_POPUP, (px, py, pw, ph),
                          radius=12, border=2, border_color=(200, 50, 50))

        f_title = pygame.font.SysFont(None, 28)
        f_sub   = pygame.font.SysFont(None, 20)
        f_btn   = pygame.font.SysFont(None, 22)

        title = f_title.render("Voulez-vous vraiment abandonner ?", True, (255, 180, 180))
        surf.blit(title, title.get_rect(center=(px + pw // 2, py + 38)))

        sub = f_sub.render("Cette action est irréversible.", True, C_TEXT_DIM)
        surf.blit(sub, sub.get_rect(center=(px + pw // 2, py + 68)))

        # Boutons Oui / Non
        self._btn_cap_oui = pygame.Rect(px + 60,  py + 120, 120, 40)
        self._btn_cap_non = pygame.Rect(px + 240, py + 120, 120, 40)

        mx, my = pygame.mouse.get_pos()
        for rect, label, col_base, col_hover in (
            (self._btn_cap_oui, "Oui, abandonner", (150, 30, 30), (200, 50, 50)),
            (self._btn_cap_non, "Non, continuer",  (30, 90, 30),  (50, 140, 50)),
        ):
            col = col_hover if rect.collidepoint(mx, my) else col_base
            pygame.draw.rect(surf, col, rect, border_radius=8)
            pygame.draw.rect(surf, (200, 200, 200), rect, width=1, border_radius=8)
            t = f_btn.render(label, True, (240, 240, 240))
            surf.blit(t, t.get_rect(center=rect.center))

    def _draw_detail_popup(self, surf: pygame.Surface, card: Card) -> None:
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        pw, ph = 400, 500
        px = (self.sw - pw) // 2
        py = (self.sh - ph) // 2
        rect = pygame.Rect(px, py, pw, ph)
        draw_rounded_rect(surf, C_PANEL, rect, radius=12, border=2, border_color=C_HIGHLIGHT)

        self._btn_close_detail = pygame.Rect(px + pw - 30, py + 10, 20, 20)
        pygame.draw.line(surf, (255, 50, 50), (px + pw - 28, py + 12), (px + pw - 12, py + 28), 2)
        pygame.draw.line(surf, (255, 50, 50), (px + pw - 12, py + 12), (px + pw - 28, py + 28), 2)

        f_title = pygame.font.SysFont(None, 32)
        f_cat   = pygame.font.SysFont(None, 20)
        f_desc  = pygame.font.SysFont(None, 22)
        f_tag   = pygame.font.SysFont(None, 18)

        surf.blit(f_title.render(card.nom, True, C_HIGHLIGHT), (px + 20, py + 20))
        surf.blit(f_cat.render(f"Catégorie : {card.categorie.value}", True, C_TEXT_DIM), (px + 20, py + 55))

        img_w, img_h = 180, 252
        img_x = px + (pw - img_w) // 2
        img_y = py + 85
        temp_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        draw_card(temp_surf, card, 0, 0, selected=False)
        scaled_img = pygame.transform.smoothscale(temp_surf, (img_w, img_h))
        surf.blit(scaled_img, (img_x, img_y))
        pygame.draw.rect(surf, C_BORDER, (img_x, img_y, img_w, img_h), width=2, border_radius=8)

        desc_y = py + 350
        parts  = (card.description or "Aucune description supplémentaire.").split("\n\n")
        current_y = desc_y
        for i, part in enumerate(parts):
            color  = C_TEXT if i == 0 else C_TEXT_DIM
            prefix = "" if i == 0 else "⚡ "
            for line in wrap_text(prefix + part, f_desc, pw - 40):
                surf.blit(f_desc.render(line, True, color), (px + 20, current_y))
                current_y += 24
            current_y += 8

        if card.tags:
            surf.blit(f_tag.render("Tags : " + ", ".join(card.tags), True, C_TEXT_DIM),
                      (px + 20, py + ph - 40))

    # ── Clics ─────────────────────────────────────────────────────────
    def handle_click(self, pos: tuple[int, int], game: Game):
        now       = pygame.time.get_ticks()
        is_double = (now - self.last_click_time < 300) and (self.last_click_pos == pos)
        self.last_click_time = now
        self.last_click_pos  = pos

        # ── Popup capitulation (priorité maximale) ──────────────────
        if self.show_confirm_cap:
            mx, my = pos
            if hasattr(self, '_btn_cap_oui') and self._btn_cap_oui.collidepoint(mx, my):
                self.show_confirm_cap = False
                return "capitulation"
            elif hasattr(self, '_btn_cap_non') and self._btn_cap_non.collidepoint(mx, my):
                self.show_confirm_cap = False
            return False

        if self.detail_card:
            mx, my = pos
            popup  = pygame.Rect((self.sw-400)//2, (self.sh-500)//2, 400, 500)
            if self._btn_close_detail.collidepoint(mx, my) or not popup.collidepoint(mx, my):
                self.detail_card = None
            return False

        if self.overlay_active:
            self.overlay_active = False
            return False

        mx, my = pos
        cp = game.current_player

        # ── Bouton Capitulation ──────────────────────────────────────
        if self._btn_cap.collidepoint(mx, my):
            self.show_confirm_cap = True
            return False

        # Journal — flèches ▲▼
        if self.log.handle_click(pos):
            return False

        if self._btn_fin.collidepoint(mx, my):
            game.next_turn()
            self.selected_hand = None
            self._surlignees   = ()
            self._reset_scroll_for_player(len(game.current_player.hand))
            self.log.add(f"► Tour de {game.current_player.name}")
            self.overlay_active = True
            return False

        if self._btn_infra.collidepoint(mx, my):
            ok, msg = game.perform_action(ACTION_DRAW_INFRA)
            self.log.add(msg)
            if ok:
                self.just_drawn = len(game.current_player.hand) - 1
            return False

        if self._btn_bonus.collidepoint(mx, my):
            ok, msg = game.perform_action(ACTION_DRAW_BONUS)
            self.log.add(msg)
            if ok:
                self.just_drawn = len(game.current_player.hand) - 1
            return False

        if self._btn_left and self._btn_left.collidepoint(mx, my):
            self._scroll_hand(-1, len(cp.hand))
            return False

        if self._btn_right and self._btn_right.collidepoint(mx, my):
            self._scroll_hand(1, len(cp.hand))
            return False

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

        # Réseaux adverses (Malus ciblé)
        if self.selected_hand is not None:
            sel_card = cp.hand[self.selected_hand]
            if sel_card.categorie.value == "Malus":
                for pid, rects in self._opp_net_rects.items():
                    for pos, r in rects.items():
                        if r.collidepoint(mx, my):
                            opp = next(p for p in game.players if p.player_id == pid)
                            if pos in opp.network.grille:
                                ok, msg = game.perform_action(
                                    ACTION_DECONNECT,
                                    target_player_id=pid,
                                    pos=pos
                                )
                                self.log.add(msg)
                                if ok:
                                    card = cp.hand.pop(self.selected_hand)
                                    game.discard_pile.append(card)
                                    self.selected_hand = None
                                    self._update_surlignees(game)
                                return False

        self.selected_hand = None
        self._update_surlignees(game)
        return False

    # ── Molette ───────────────────────────────────────────────────────
    def handle_scroll(self, dy: int, game: Game) -> None:
        if self.overlay_active:
            return
        mx, my = pygame.mouse.get_pos()
        # Molette sur le journal
        if self.log.is_hovered((mx, my)):
            self.log.scroll(-dy)
            return
        # Molette sur la barre de main
        if my >= hand_bar.bar_top(self.sh):
            self._scroll_hand(-dy, len(game.current_player.hand))

    def handle_key(self, key: int) -> None:
        if self.overlay_active:
            self.overlay_active = False