import pygame
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK

# Couleurs inspirées de la maquette
C_BG          = (18,  22,  35)
C_PANEL       = (28,  33,  50)
C_PANEL_LIGHT = (38,  45,  65)
C_BORDER      = (60,  70, 100)
C_HIGHLIGHT   = (255, 215,   0)
C_TEXT        = (230, 230, 240)
C_TEXT_DIM    = (130, 135, 155)
C_INFRA       = (195, 210, 220)
C_PROTECTION  = ( 80, 195, 215)
C_BONUS       = ( 90, 185, 100)
C_ATTACK      = (195,  70,  70)
C_EVENT       = (160, 110, 210)
C_DISCONNECT  = ( 90,  90, 100)

CARD_W, CARD_H   = 90, 126
SLOT_PAD         = 10
GRID_COLS        = 3

class GameView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Network Codex")
        self.font_main = pygame.font.SysFont("Arial", 24)
        self.font_title = pygame.font.SysFont("Arial", 13, bold=True)
        self.font_card_name = pygame.font.SysFont("Arial", 10, bold=True)
        self.font_card_eff = pygame.font.SysFont("Arial", 8)
        self.font_slot = pygame.font.SysFont("Arial", 9)
        self.message = ""
        self.message_timer = 0

    def set_message(self, text):
        self.message = text
        self.message_timer = 120 # 2 secondes à 60fps

    def draw_game(self, game, selected_card_index=None):
        self.screen.fill(C_BG)
        
        # 1. Dessiner les grilles des joueurs
        for i, player in enumerate(game.players):
            is_current = (i == game.current_player_index)
            ox = 20 + i * (GRID_COLS * (CARD_W + SLOT_PAD) + SLOT_PAD + 40)
            oy = 40
            self.draw_network_grid(player, ox, oy, is_current)

        # 2. Dessiner le HUD (Manche, Actions restantes)
        self.draw_hud(game)

        # 3. Dessiner la main du joueur actuel
        current_player = game.get_current_player()
        self.draw_hand_bar(current_player, selected_card_index)

        # 4. Dessiner le message d'info
        if self.message_timer > 0:
            txt = self.font_main.render(self.message, True, C_HIGHLIGHT)
            self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT - 200))
            self.message_timer -= 1

        pygame.display.flip()

    def draw_rounded_rect(self, surf, color, rect, radius=8, border=0, border_color=None):
        rect = pygame.Rect(rect)
        pygame.draw.rect(surf, color, rect, border_radius=radius)
        if border > 0 and border_color:
            pygame.draw.rect(surf, border_color, rect, width=border, border_radius=radius)

    def get_card_color(self, card):
        if card.is_flipped:
            return C_DISCONNECT
        cat = card.category.name
        if cat == "MACHINE": return C_INFRA
        if cat == "PROTECTION": return C_PROTECTION
        if cat == "ATTACK": return C_ATTACK
        if cat == "UTILITY": return C_BONUS
        return C_INFRA

    def draw_card(self, surf, card, x, y, selected=False, alpha=255):
        bg = self.get_card_color(card)
        card_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        
        # Fond
        pygame.draw.rect(card_surf, (*bg, alpha), (0, 0, CARD_W, CARD_H), border_radius=8)

        # Bande couleur
        stripe_color = {
            "MACHINE":    ( 80, 100, 130),
            "PROTECTION": ( 20, 130, 160),
            "ATTACK":     (140,  30,  30),
            "UTILITY":    ( 40, 130,  60),
        }.get(card.category.name, (80, 80, 80))
        pygame.draw.rect(card_surf, (*stripe_color, alpha), (0, 0, CARD_W, 6), border_radius=8)
        pygame.draw.rect(card_surf, (0, 0, 0, 0), (0, 3, CARD_W, 3))

        # Bordure
        if selected:
            pygame.draw.rect(card_surf, C_HIGHLIGHT, (0, 0, CARD_W, CARD_H), width=2, border_radius=8)
        else:
            pygame.draw.rect(card_surf, (0, 0, 0, 100), (0, 0, CARD_W, CARD_H), width=1, border_radius=8)

        # Nom
        tc = (255, 255, 255) if card.category.name in ["ATTACK", "PROTECTION"] else (20, 20, 30)
        name_txt = self.font_card_name.render(card.name, True, tc)
        card_surf.blit(name_txt, (5, 10))

        # Déconnecté ?
        if card.is_flipped:
            lbl = self.font_slot.render("HORS LIGNE", True, (255, 100, 100))
            card_surf.blit(lbl, (CARD_W//2 - lbl.get_width()//2, CARD_H//2))

        surf.blit(card_surf, (x, y))
        return pygame.Rect(x, y, CARD_W, CARD_H)

    def draw_network_grid(self, player, ox, oy, is_current):
        grid_w = GRID_COLS * (CARD_W + SLOT_PAD) + SLOT_PAD
        grid_h = 3 * (CARD_H + SLOT_PAD) + SLOT_PAD + 24
        panel_color = C_PANEL_LIGHT if is_current else C_PANEL
        border_color = C_HIGHLIGHT if is_current else C_BORDER
        
        self.draw_rounded_rect(self.screen, panel_color, (ox, oy, grid_w, grid_h), radius=10, border=2, border_color=border_color)
        
        name_txt = self.font_title.render(f"{player.name} - Score: {player.score}", True, C_HIGHLIGHT if is_current else C_TEXT)
        self.screen.blit(name_txt, (ox + 10, oy + 6))

        # La grille est 3x3. On mappe les positions (x,y)
        for row in range(3):
            for col in range(3):
                cx = ox + SLOT_PAD + col * (CARD_W + SLOT_PAD)
                cy = oy + 24 + SLOT_PAD + row * (CARD_H + SLOT_PAD)
                
                card = player.grid.get((col, row))
                if card:
                    self.draw_card(self.screen, card, cx, cy)
                else:
                    slot_r = pygame.Rect(cx, cy, CARD_W, CARD_H)
                    self.draw_rounded_rect(self.screen, C_BG, slot_r, radius=8, border=1, border_color=C_BORDER)
                    n = self.font_slot.render(f"{col},{row}", True, C_BORDER)
                    self.screen.blit(n, (cx + CARD_W//2 - n.get_width()//2, cy + CARD_H//2 - n.get_height()//2))

    def draw_hand_bar(self, player, selected_card_index):
        bar_h = CARD_H + 30
        bar_y = SCREEN_HEIGHT - bar_h - 10
        pygame.draw.rect(self.screen, C_PANEL, (0, bar_y, SCREEN_WIDTH, bar_h))
        pygame.draw.line(self.screen, C_BORDER, (0, bar_y), (SCREEN_WIDTH, bar_y), 1)
        
        txt = self.font_title.render("MAIN", True, C_TEXT_DIM)
        self.screen.blit(txt, (10, bar_y + 4))
        
        for i, card in enumerate(player.hand):
            cx = 20 + i * (CARD_W + 15)
            cy = bar_y + 20
            is_selected = (i == selected_card_index)
            self.draw_card(self.screen, card, cx, cy, selected=is_selected)

    def draw_hud(self, game):
        hud_y = 10
        round_txt = self.font_title.render(f"MANCHE {game.round_count}", True, C_TEXT)
        self.screen.blit(round_txt, (SCREEN_WIDTH // 2 - 250, hud_y))
        
        cp = game.get_current_player()
        act_txt = self.font_title.render(f"ACTIONS: {cp.actions_left}", True, C_HIGHLIGHT)
        self.screen.blit(act_txt, (SCREEN_WIDTH // 2 - 100, hud_y))

        if cp.objective:
            obj_txt = self.font_title.render(f"OBJECTIF: {cp.objective['name']} ({cp.objective['desc']})", True, C_BONUS)
            self.screen.blit(obj_txt, (SCREEN_WIDTH // 2 + 50, hud_y))
            if cp.personal_objective_accomplished:
                check_txt = self.font_title.render("✓ ACCOMPLI", True, C_BONUS)
                self.screen.blit(check_txt, (SCREEN_WIDTH // 2 + 400, hud_y))

    def show_menu(self):
        pass
