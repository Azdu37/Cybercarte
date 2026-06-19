"""Constantes partagées (couleurs, dimensions, règles du jeu)."""
import pygame

# ---------------------------------------------------------------------------
# Couleurs de base
# ---------------------------------------------------------------------------
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0  )
GRAY   = (200, 200, 200)

# Couleurs de l'interface (thème sombre)
COULEUR_FOND        = (30,  33,  41 )
COULEUR_GRILLE      = (60,  64,  74 )
COULEUR_INFRA       = (210, 212, 218)
COULEUR_PROTECTION  = (150, 210, 235)
COULEUR_MORTE       = (110, 70,  70 )
COULEUR_TEXTE       = (25,  25,  30 )
COULEUR_TEXTE_MORTE = (235, 225, 225)
COULEUR_TITRE       = (235, 235, 240)
COULEUR_DONNEES     = (60,  120, 230)
COULEUR_ELECTRIQUE  = (235, 175, 60 )
COULEUR_RJ45        = (180,  50, 255)
COULEUR_SURBRILLANCE = (95, 220, 140)
COULEUR_BOUTON           = (70,  75,  90 )
COULEUR_BOUTON_SURVOL    = (95,  100, 120)
COULEUR_BOUTON_SELECTION = (95,  145, 230)
COULEUR_BOUTON_TEXTE     = (235, 235, 240)
COULEUR_ZONE_MAIN        = (24,  26,  33 )

# Couleurs des joueurs (repris du projet Cybercarte)
PLAYER_COLORS = [
    (220, 80,  80 ),   # Rouge
    (80,  200, 120),   # Vert
    (80,  120, 220),   # Bleu
    (220, 200, 60 ),   # Jaune
]

# ---------------------------------------------------------------------------
# Dimensions écran et cartes
# ---------------------------------------------------------------------------
SCREEN_WIDTH  = 1200
SCREEN_HEIGHT = 800
CARD_WIDTH    = 100
CARD_HEIGHT   = 150

TAILLE_CASE         = 140
TAILLE_CASE_PLATEAU = 90
ESPACE_CASE         = 6
MARGE               = 30
RAYON_COIN          = 10
EPAISSEUR_BORD      = 3
EPAISSEUR_SURBRILLANCE = 3
TAILLE_CONNECTEUR   = 20

HAUTEUR_ENTETE      = 60
HAUTEUR_ZONE_MAIN   = 185
TAILLE_CARTE_MAIN   = (110, 150)
ESPACE_MAIN         = 14

# ---------------------------------------------------------------------------
# Règles du jeu
# ---------------------------------------------------------------------------
MAX_PLAYERS  = 4
MIN_PLAYERS  = 2
INFRASTRUCTURE_VICTORY_COUNT = 9
INITIAL_HAND_SIZE   = 4
ACTIONS_PER_TURN    = 2
EVENT_FREQUENCY     = 2   # Tous les 2 tours complets (un tour = tous les joueurs ont joué)

# Types d'actions
ACTION_DRAW_INFRA  = "draw_infra"
ACTION_DRAW_BONUS  = "draw_bonus"
ACTION_PLAY_CARD   = "play_card"
ACTION_END_TURN    = "end_turn"
ACTION_DECONNECT   = "deconnect"