import pygame

CARD_W, CARD_H = 100, 140

COLOR_MAP = {
    "infra":       (220, 220, 220),  # gris clair
    "bonus_malus": (120, 200, 120),  # vert
    "attack":      (200, 80,  80),   # rouge
    "event":       (180, 140, 220),  # violet
    "protection":  (100, 200, 220),  # bleu clair
}

def draw_card(surface, card, x, y, selected=False):
    color = COLOR_MAP.get(card.card_type, (200, 200, 200))
    rect = pygame.Rect(x, y, CARD_W, CARD_H)

    # fond de carte
    pygame.draw.rect(surface, color, rect, border_radius=8)

    # bordure (jaune si sélectionnée)
    border_color = (255, 220, 0) if selected else (50, 50, 50)
    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=8)

    # nom de la carte
    font = pygame.font.SysFont("Arial", 11, bold=True)
    text = font.render(card.name, True, (30, 30, 30))
    surface.blit(text, (x + 6, y + 8))

    return rect  # important : retourner le rect pour détecter les clics