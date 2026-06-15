import pygame

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Couleurs des joueurs
PLAYER_COLORS = [
    (255, 50, 50),   # Rouge
    (50, 255, 50),   # Vert
    (50, 50, 255),   # Bleu
    (255, 255, 50)   # Jaune
]

# Dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CARD_WIDTH = 100
CARD_HEIGHT = 150

# Jeu
MAX_PLAYERS = 4
MIN_PLAYERS = 2
INFRASTRUCTURE_VICTORY_COUNT = 9
INITIAL_HAND_SIZE = 4
ACTIONS_PER_TURN = 2
EVENT_FREQUENCY = 2  # Toutes les 2 manches

# Types d'actions
ACTION_DRAW_INFRA = "draw_infra"
ACTION_DRAW_BONUS = "draw_bonus"
ACTION_PLAY_CARD = "play_card"

# Directions pour le placement
TOP = "top"
BOTTOM = "bottom"
LEFT = "left"
RIGHT = "right"
DIRECTIONS = [TOP, BOTTOM, LEFT, RIGHT]
