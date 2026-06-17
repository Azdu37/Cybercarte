"""
Chargement des images de cartes depuis assets/cards/canonical/.

Le dossier canonical/ contient 64 fichiers nommés {type_id}_{0..3}.png.
"""
from __future__ import annotations
import os
import pygame

# Chemin absolu garanti, indépendant du répertoire de lancement
_THIS_FILE = os.path.abspath(__file__)
_SRC_UTILS  = os.path.dirname(_THIS_FILE)          # .../src/utils
_SRC        = os.path.dirname(_SRC_UTILS)           # .../src
_ROOT       = os.path.dirname(_SRC)                 # racine du projet
CANONICAL_DIR = os.path.join(_ROOT, "assets", "cards", "canonical")

# Cache (card_id, w, h) → Surface
_cache: dict[tuple, pygame.Surface] = {}


def get_card_surface(nom: str, card_id: str, width: int, height: int) -> pygame.Surface | None:
    """
    Charge et retourne une Surface redimensionnée pour la carte `card_id`.
    card_id est de la forme '{type_id}_{variante}', ex: 'vpn_2', 'pare_feu_0'.
    """
    key = (card_id, width, height)
    if key in _cache:
        return _cache[key]

    path = os.path.join(CANONICAL_DIR, f"{card_id}.png")
    if not os.path.exists(path):
        return None

    try:
        surf = pygame.image.load(path).convert_alpha()
        scaled = pygame.transform.smoothscale(surf, (width, height))
        _cache[key] = scaled
        return scaled
    except Exception:
        return None


def preload_all(width: int, height: int) -> None:
    """Précharge toutes les images au démarrage."""
    if not os.path.isdir(CANONICAL_DIR):
        return
    for fname in os.listdir(CANONICAL_DIR):
        if fname.endswith('.png'):
            get_card_surface("", fname[:-4], width, height)