"""
Network Codex — game_screen.py (standalone, données mockées)
Fonctionne sans les modules logique/cartes.
Remplace les classes MockCard / MockPlayer par les vraies quand prêt.
"""

import pygame
import sys
import textwrap

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

# Palette (correspond aux couleurs des vraies cartes)
C_BG          = (18,  22,  35)
C_PANEL       = (28,  33,  50)
C_PANEL_LIGHT = (38,  45,  65)
C_BORDER      = (60,  70, 100)
C_HIGHLIGHT   = (255, 215,   0)
C_TEXT        = (230, 230, 240)
C_TEXT_DIM    = (130, 135, 155)
C_INFRA       = (195, 210, 220)   # gris bleuté
C_PROTECTION  = ( 80, 195, 215)   # cyan
C_BONUS       = ( 90, 185, 100)   # vert
C_ATTACK      = (195,  70,  70)   # rouge
C_EVENT       = (160, 110, 210)   # violet
C_DISCONNECT  = ( 90,  90, 100)   # gris foncé (carte déconnectée)
C_CANARD      = (230, 175,  40)   # orange doré

CARD_W, CARD_H   = 90, 126
SLOT_PAD         = 10
GRID_COLS        = 3

# ─────────────────────────────────────────────
#  MOCK DATA  (remplacer par les vraies classes)
# ─────────────────────────────────────────────
class MockCard:
    def __init__(self, name, card_type, effect="", disconnected=False):
        self.name        = name
        self.card_type   = card_type   # "infra" | "protection" | "bonus" | "attack" | "canard"
        self.effect      = effect
        self.disconnected = disconnected  # carte retournée sur le côté

INFRA_CARDS = [
    MockCard("PC",              "infra"),
    MockCard("Serveur",         "infra"),
    MockCard("Routeur",         "infra"),
    MockCard("Cloud",           "infra"),
    MockCard("Base de donnée",  "infra"),
    MockCard("Site",            "infra"),
    MockCard("Smartphone",      "infra"),
    MockCard("Boîte Mail",      "infra"),
    MockCard("Périphérique",    "infra"),
    MockCard("Point Réseau",    "infra"),
    MockCard("Logiciel",        "infra"),
]

HAND_CARDS = [
    MockCard("Antivirus",         "protection", "Protège du Cheval de Troie et des ransomwares"),
    MockCard("VPN",               "protection", "Protège des ransomwares"),
    MockCard("Cheval de Troie",   "attack",     "Volez une carte dans une infrastructure ennemie"),
    MockCard("Ransomware",        "attack",     "Une carte est déconnectée, il faudra la remplacer"),
    MockCard("Bonne organisation","bonus",      "Réorganisez votre système immédiatement"),
    MockCard("Canard en plastique","canard",    "Aucun joueur ne peut finir avec cette carte sauf Le Fou"),
]

class MockPlayer:
    def __init__(self, name, network_cards, hand, actions_left=2):
        self.name         = name
        self.network      = network_cards   # liste de MockCard|None, max 9
        self.hand         = hand
        self.actions_left = actions_left

PLAYERS = [
    MockPlayer("Alice", [
        INFRA_CARDS[0], INFRA_CARDS[1],
        MockCard("Pare-Feu", "protection", "Protège Cheval de Troie et spywares"),
        INFRA_CARDS[3],
        MockCard("Routeur", "infra", "", disconnected=True),   # déconnectée !
        INFRA_CARDS[5], None, None, None
    ], HAND_CARDS[:]),
    MockPlayer("Bob", [
        INFRA_CARDS[2], INFRA_CARDS[6], INFRA_CARDS[7],
        INFRA_CARDS[4], INFRA_CARDS[8], None,
        None, None, None
    ], [
        MockCard("Mise à Jour",   "protection", "Protège spyware et obsolescence"),
        MockCard("Cable sectionné","attack",    "Défaussez une carte dans un réseau adverse"),
        MockCard("Coup de chance","bonus",      "Tirez 3 cartes, choisissez-en 2"),
    ]),
]

# ─────────────────────────────────────────────
#  HELPERS DESSIN
# ─────────────────────────────────────────────
def wrap_text(text, font, max_w):
    """Découpe un texte en lignes qui tiennent dans max_w pixels."""
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

def card_color(card):
    if card.disconnected:
        return C_DISCONNECT
    return {
        "infra":      C_INFRA,
        "protection": C_PROTECTION,
        "bonus":      C_BONUS,
        "attack":     C_ATTACK,
        "canard":     C_CANARD,
    }.get(card.card_type, C_INFRA)

def card_text_color(card):
    if card.card_type in ("attack", "protection"):
        return (255, 255, 255)
    if card.card_type == "canard":
        return (60, 40, 10)
    return (20, 20, 30)

# ─────────────────────────────────────────────
#  RENDU D'UNE CARTE
# ─────────────────────────────────────────────
def draw_card(surf, card, x, y, selected=False, small=False, alpha=255):
    w = CARD_W if not small else 70
    h = CARD_H if not small else 98

    card_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    bg = card_color(card)
    border = C_HIGHLIGHT if selected else (0, 0, 0, 180)

    # fond
    pygame.draw.rect(card_surf, (*bg, alpha), (0, 0, w, h), border_radius=8)

    # bande couleur en haut
    stripe_color = {
        "infra":      ( 80, 100, 130),
        "protection": ( 20, 130, 160),
        "bonus":      ( 40, 130,  60),
        "attack":     (140,  30,  30),
        "canard":     (180, 120,  10),
    }.get(card.card_type, (80, 80, 80))
    pygame.draw.rect(card_surf, (*stripe_color, alpha), (0, 0, w, 6), border_radius=8)
    pygame.draw.rect(card_surf, (0, 0, 0, 0), (0, 3, w, 3))  # bord bas plat

    # bordure sélection
    if selected:
        pygame.draw.rect(card_surf, C_HIGHLIGHT, (0, 0, w, h), width=2, border_radius=8)
    else:
        pygame.draw.rect(card_surf, (0, 0, 0, 100), (0, 0, w, h), width=1, border_radius=8)

    # si déconnectée : hachures
    if card.disconnected:
        for i in range(0, w + h, 14):
            pygame.draw.line(card_surf, (255, 80, 80, 60),
                             (max(0, i - h), min(h, i)),
                             (min(w, i),     max(0, i - w)), 1)
        label_font = pygame.font.SysFont("Arial", 9, bold=True)
        lbl = label_font.render("DÉCONNECTÉ", True, (255, 100, 100))
        card_surf.blit(lbl, (w//2 - lbl.get_width()//2, h//2 - 6))

    # nom
    name_font = pygame.font.SysFont("Arial", 10 if not small else 9, bold=True)
    tc = card_text_color(card)
    lines = wrap_text(card.name, name_font, w - 10)
    for i, line in enumerate(lines[:3]):
        txt = name_font.render(line, True, tc)
        card_surf.blit(txt, (5, 10 + i * 13))

    # effet (petit texte, seulement si assez grand)
    if not small and card.effect and not card.disconnected:
        eff_font = pygame.font.SysFont("Arial", 8)
        eff_lines = wrap_text(card.effect, eff_font, w - 8)
        for i, line in enumerate(eff_lines[:4]):
            etxt = eff_font.render(line, True, (*tc[:3], 180) if len(tc) == 3 else tc)
            card_surf.blit(etxt, (4, h - 40 + i * 10))

    surf.blit(card_surf, (x, y))
    return pygame.Rect(x, y, w, h)

# ─────────────────────────────────────────────
#  GRILLE RÉSEAU (3x3)
# ─────────────────────────────────────────────
def draw_network_grid(surf, player, ox, oy, current=False, selected_slot=None):
    """Dessine la grille 3×3 du réseau d'un joueur."""
    title_font = pygame.font.SysFont("Arial", 13, bold=True)
    slot_font  = pygame.font.SysFont("Arial", 9)

    # Cadre du réseau
    grid_w = GRID_COLS * (CARD_W + SLOT_PAD) + SLOT_PAD
    grid_h = 3        * (CARD_H + SLOT_PAD) + SLOT_PAD + 24
    panel_color = C_PANEL_LIGHT if current else C_PANEL
    border_color = C_HIGHLIGHT if current else C_BORDER
    draw_rounded_rect(surf, panel_color, (ox, oy, grid_w, grid_h), radius=10,
                      border=2, border_color=border_color)

    # Nom du joueur + compte
    nb = sum(1 for c in player.network if c is not None)
    name_txt = title_font.render(f"{player.name}  —  {nb}/9", True,
                                  C_HIGHLIGHT if current else C_TEXT)
    surf.blit(name_txt, (ox + 10, oy + 6))

    rects = []
    for idx in range(9):
        col = idx % GRID_COLS
        row = idx // GRID_COLS
        cx = ox + SLOT_PAD + col * (CARD_W + SLOT_PAD)
        cy = oy + 24 + SLOT_PAD + row * (CARD_H + SLOT_PAD)

        card = player.network[idx] if idx < len(player.network) else None
        if card:
            sel = (selected_slot == idx) and current
            r = draw_card(surf, card, cx, cy, selected=sel)
        else:
            # slot vide
            slot_r = pygame.Rect(cx, cy, CARD_W, CARD_H)
            draw_rounded_rect(surf, C_BG, slot_r, radius=8,
                              border=1, border_color=C_BORDER)
            n = slot_font.render(f"#{idx+1}", True, C_BORDER)
            surf.blit(n, (cx + CARD_W//2 - n.get_width()//2,
                          cy + CARD_H//2 - n.get_height()//2))
            r = slot_r
        rects.append((idx, r))
    return rects

# ─────────────────────────────────────────────
#  BARRE DE MAIN
# ─────────────────────────────────────────────
def draw_hand_bar(surf, player, selected_hand=None):
    """Affiche les cartes en main du joueur actif en bas d'écran."""
    bar_h = CARD_H + 24
    bar_y = SCREEN_H - bar_h - 8
    pygame.draw.rect(surf, C_PANEL, (0, bar_y - 4, SCREEN_W, bar_h + 12))
    pygame.draw.line(surf, C_BORDER, (0, bar_y - 4), (SCREEN_W, bar_y - 4), 1)

    label_font = pygame.font.SysFont("Arial", 11, bold=True)
    lbl = label_font.render("MAIN", True, C_TEXT_DIM)
    surf.blit(lbl, (10, bar_y + 4))

    rects = []
    n = len(player.hand)
    total_w = n * (CARD_W + 8) - 8
    start_x = max(80, SCREEN_W // 2 - total_w // 2)
    for i, card in enumerate(player.hand):
        cx = start_x + i * (CARD_W + 8)
        cy = bar_y + 4
        sel = (selected_hand == i)
        r = draw_card(surf, card, cx, cy, selected=sel)
        rects.append((i, r))
    return rects, bar_y

# ─────────────────────────────────────────────
#  HUD (actions, tour, pioche)
# ─────────────────────────────────────────────
def draw_hud(surf, current_player, turn_num, deck_counts):
    hud_font  = pygame.font.SysFont("Arial", 13, bold=True)
    info_font = pygame.font.SysFont("Arial", 11)

    pygame.draw.rect(surf, C_PANEL, (0, 0, SCREEN_W, 40))
    pygame.draw.line(surf, C_BORDER, (0, 40), (SCREEN_W, 40), 1)

    # Tour
    t = hud_font.render(f"Tour {turn_num}", True, C_TEXT)
    surf.blit(t, (14, 12))

    # Joueur actif
    p = hud_font.render(f"► {current_player.name}", True, C_HIGHLIGHT)
    surf.blit(p, (110, 12))

    # Actions restantes
    for i in range(2):
        color = C_HIGHLIGHT if i < current_player.actions_left else C_BORDER
        pygame.draw.circle(surf, color, (340 + i * 22, 20), 7)

    a = info_font.render("actions", True, C_TEXT_DIM)
    surf.blit(a, (370, 14))

    # Pioches
    labels = [("Infra", deck_counts[0], C_INFRA),
              ("Bonus/Malus", deck_counts[1], C_BONUS),
              ("Événements", deck_counts[2], C_EVENT)]
    dx = SCREEN_W - 340
    for name, count, color in labels:
        pygame.draw.rect(surf, color, (dx, 8, 80, 24), border_radius=5)
        pygame.draw.rect(surf, (0,0,0,80), (dx, 8, 80, 24), width=1, border_radius=5)
        txt = info_font.render(f"{name} {count}", True, (10, 10, 20))
        surf.blit(txt, (dx + 4, 14))
        dx += 92

# ─────────────────────────────────────────────
#  TOOLTIP CARTE
# ─────────────────────────────────────────────
def draw_tooltip(surf, card, mx, my):
    if not card:
        return
    tip_font = pygame.font.SysFont("Arial", 11)
    name_font = pygame.font.SysFont("Arial", 13, bold=True)
    lines = [card.name] + wrap_text(card.effect or "Carte infrastructure", tip_font, 200)
    tw = 220
    th = 20 + len(lines) * 16
    tx = min(mx + 15, SCREEN_W - tw - 5)
    ty = min(my + 15, SCREEN_H - th - 5)
    draw_rounded_rect(surf, C_PANEL_LIGHT, (tx, ty, tw, th), radius=6,
                      border=1, border_color=C_HIGHLIGHT)
    name_surf = name_font.render(card.name, True, card_color(card))
    surf.blit(name_surf, (tx + 8, ty + 4))
    for i, line in enumerate(lines[1:]):
        s = tip_font.render(line, True, C_TEXT_DIM)
        surf.blit(s, (tx + 8, ty + 20 + i * 14))

# ─────────────────────────────────────────────
#  ÉCRAN DE LOG / ÉVÉNEMENT
# ─────────────────────────────────────────────
def draw_log(surf, messages, x, y, w, h):
    draw_rounded_rect(surf, C_PANEL, (x, y, w, h), radius=8,
                      border=1, border_color=C_BORDER)
    log_font = pygame.font.SysFont("Arial", 10)
    title = pygame.font.SysFont("Arial", 11, bold=True).render("Journal", True, C_TEXT_DIM)
    surf.blit(title, (x + 8, y + 6))
    for i, msg in enumerate(messages[-8:]):
        color = C_HIGHLIGHT if msg.startswith("►") else C_TEXT_DIM
        s = log_font.render(msg[:40], True, color)
        surf.blit(s, (x + 8, y + 24 + i * 14))

# ─────────────────────────────────────────────
#  BOUTONS
# ─────────────────────────────────────────────
def draw_button(surf, text, x, y, w=140, h=34, color=C_PANEL_LIGHT, hover=False):
    bc = C_HIGHLIGHT if hover else C_BORDER
    draw_rounded_rect(surf, color, (x, y, w, h), radius=7, border=2, border_color=bc)
    f = pygame.font.SysFont("Arial", 12, bold=True)
    t = f.render(text, True, C_HIGHLIGHT if hover else C_TEXT)
    surf.blit(t, (x + w//2 - t.get_width()//2, y + h//2 - t.get_height()//2))
    return pygame.Rect(x, y, w, h)

# ─────────────────────────────────────────────
#  BOUCLE PRINCIPALE
# ─────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Network Codex")
    clock = pygame.time.Clock()

    # État UI local
    current_player_idx = 0
    turn_num           = 1
    selected_hand      = None   # index carte en main sélectionnée
    selected_slot      = None   # index slot réseau sélectionné
    hover_card         = None   # carte sous la souris pour le tooltip
    log_messages       = [
        "► Début de la partie !",
        "Alice commence.",
        "2 actions disponibles.",
    ]
    deck_counts = [28, 18, 12]

    # Positions des grilles réseau
    # Joueur 1 (actif) à gauche, Joueur 2 à droite
    GRID_W = GRID_COLS * (CARD_W + SLOT_PAD) + SLOT_PAD
    GRID_H = 3 * (CARD_H + SLOT_PAD) + SLOT_PAD + 24
    grid_positions = [
        (20,  55),
        (680, 55),
    ]

    # Zone log et boutons
    LOG_X, LOG_Y, LOG_W, LOG_H = 460, 55, 195, 180
    BTN_Y = 250

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        hover_card = None

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_TAB:
                    # Passer au joueur suivant (debug)
                    current_player_idx = (current_player_idx + 1) % len(PLAYERS)
                    selected_hand = None
                    selected_slot = None
                    log_messages.append(f"► Tour de {PLAYERS[current_player_idx].name}")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cp = PLAYERS[current_player_idx]

                # Clic sur une carte en main
                for i, r in hand_rects:
                    if r.collidepoint(mx, my):
                        selected_hand = i if selected_hand != i else None
                        selected_slot = None
                        log_messages.append(f"Carte sélectionnée : {cp.hand[i].name}")

                # Clic sur un slot du réseau actif → jouer la carte sélectionnée
                for idx, r in active_grid_rects:
                    if r.collidepoint(mx, my):
                        if selected_hand is not None:
                            card = cp.hand[selected_hand]
                            if cp.network[idx] is None:
                                cp.network[idx] = card
                                cp.hand.pop(selected_hand)
                                cp.actions_left = max(0, cp.actions_left - 1)
                                deck_counts[0] = max(0, deck_counts[0] - 0)
                                log_messages.append(f"► {card.name} posé en slot #{idx+1}")
                                selected_hand = None
                                selected_slot = None
                            else:
                                log_messages.append("Slot occupé !")
                        else:
                            selected_slot = idx

        # ── Draw ──
        screen.fill(C_BG)

        cp = PLAYERS[current_player_idx]

        # Grilles réseau
        active_grid_rects = []
        for pi, (gx, gy) in enumerate(grid_positions):
            if pi >= len(PLAYERS):
                break
            p = PLAYERS[pi]
            is_current = (pi == current_player_idx)
            rects = draw_network_grid(screen, p, gx, gy,
                                      current=is_current,
                                      selected_slot=selected_slot if is_current else None)
            if is_current:
                active_grid_rects = rects
            # hover tooltip
            for idx, r in rects:
                if r.collidepoint(mx, my):
                    card = p.network[idx] if idx < len(p.network) else None
                    if card:
                        hover_card = card

        # Barre de main
        hand_rects, bar_y = draw_hand_bar(screen, cp, selected_hand)
        for i, r in hand_rects:
            if r.collidepoint(mx, my):
                hover_card = cp.hand[i]

        # HUD
        draw_hud(screen, cp, turn_num, deck_counts)

        # Log
        draw_log(screen, log_messages, LOG_X, LOG_Y, LOG_W, LOG_H)

        # Boutons
        btn_end = draw_button(screen, "Fin de tour", LOG_X, BTN_Y, hover=(
            pygame.Rect(LOG_X, BTN_Y, 140, 34).collidepoint(mx, my)))
        btn_draw_infra = draw_button(screen, "Piocher Infra", LOG_X, BTN_Y + 44,
                                     hover=(pygame.Rect(LOG_X, BTN_Y+44, 140, 34).collidepoint(mx, my)))
        btn_draw_bonus = draw_button(screen, "Piocher Bonus", LOG_X, BTN_Y + 88,
                                     hover=(pygame.Rect(LOG_X, BTN_Y+88, 140, 34).collidepoint(mx, my)))

        # Actions boutons
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if btn_end.collidepoint(mx, my):
                cp.actions_left = 2
                current_player_idx = (current_player_idx + 1) % len(PLAYERS)
                if current_player_idx == 0:
                    turn_num += 1
                    log_messages.append(f"── Tour {turn_num} ──")
                log_messages.append(f"► Tour de {PLAYERS[current_player_idx].name}")
                selected_hand = selected_slot = None

            if btn_draw_infra.collidepoint(mx, my) and cp.actions_left > 0:
                import random
                new_card = random.choice(INFRA_CARDS)
                cp.hand.append(MockCard(new_card.name, new_card.card_type))
                cp.actions_left -= 1
                deck_counts[0] = max(0, deck_counts[0] - 1)
                log_messages.append(f"Pioché : {new_card.name}")

            if btn_draw_bonus.collidepoint(mx, my) and cp.actions_left > 0:
                cp.actions_left -= 1
                deck_counts[1] = max(0, deck_counts[1] - 1)
                log_messages.append("Carte bonus/malus piochée")

        # Tooltip
        if hover_card:
            draw_tooltip(screen, hover_card, mx, my)

        # Instruction bas d'écran si une carte est sélectionnée
        if selected_hand is not None:
            f = pygame.font.SysFont("Arial", 11)
            s = f.render("Cliquez sur un slot vide pour jouer la carte", True, C_HIGHLIGHT)
            screen.blit(s, (SCREEN_W//2 - s.get_width()//2, bar_y - 18))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()