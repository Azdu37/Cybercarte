"""
Chargement et cache des images de cartes depuis assets/cards/.

Chaque type de carte (Card.nom) peut avoir plusieurs variantes d'image
(ex: PC_1, PC_2, PC_3...). Le choix d'une variante est fait une fois
par instance de carte (via son id) et reste stable pendant la partie.
"""

from __future__ import annotations
import os
import unicodedata
import pygame

# Chemin vers le dossier des PNG
ASSETS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "assets", "cards"
)

# Cache : nom normalisé → liste de surfaces pygame chargées
_cache: dict[str, list[pygame.Surface]] = {}
# Cache redimensionné : (nom, w, h) → liste de surfaces
_scaled_cache: dict[tuple, list[pygame.Surface]] = {}


def _normalise(nom: str) -> str:
    """
    Transforme un nom de carte en clé de recherche robuste :
    retire les accents, remplace espaces et tirets par '_', met en minuscule.
    Ex: 'Boîte Mail' → 'boite_mail'
        'Pare-Feu'   → 'pare_feu'
        'Base de donnée' → 'base_de_donnee'
    """
    # NFD décompose les caractères accentués en base + diacritique
    nfd = unicodedata.normalize("NFD", nom)
    # Garder seulement les caractères de base (catégorie 'L' ou chiffres)
    sans_accents = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    # Remplacer espaces, tirets, apostrophes par _
    cle = sans_accents.lower()
    for ch in (" ", "-", "'", "œ"):
        cle = cle.replace(ch, "_")
    return cle


def _build_index() -> dict[str, list[str]]:
    """
    Construit un index { clé_normalisée → [chemin_png, ...] }
    en listant tous les fichiers du dossier assets/cards/.
    """
    index: dict[str, list[str]] = {}
    if not os.path.isdir(ASSETS_DIR):
        return index

    for fname in sorted(os.listdir(ASSETS_DIR)):
        if not fname.endswith(".png"):
            continue
        # Retirer le préfixe numérique "NN_" et l'extension
        base = fname[3:] if fname[2] == "_" and fname[:2].isdigit() else fname
        base = base[:-4]  # enlever .png
        # Retirer le suffixe de variante "_2", "_3"... s'il existe
        parts = base.rsplit("_", 1)
        cle_raw = parts[0] if (len(parts) == 2 and parts[1].isdigit()) else base
        cle = _normalise(cle_raw)
        index.setdefault(cle, []).append(os.path.join(ASSETS_DIR, fname))

    return index


_INDEX: dict[str, list[str]] | None = None


def _get_index() -> dict[str, list[str]]:
    global _INDEX
    if _INDEX is None:
        _INDEX = _build_index()
    return _INDEX


def _pick_variant(nom: str, card_id: str) -> list[str] | None:
    """
    Renvoie la liste de chemins PNG correspondant à `nom`, ou None si
    aucun fichier ne correspond.
    """
    index = _get_index()
    cle = _normalise(nom)
    if cle in index:
        return index[cle]
    # Essai partiel : cherche une clé qui contient notre clé
    for k, paths in index.items():
        if cle in k or k in cle:
            return paths
    return None


def get_card_surface(nom: str, card_id: str, width: int, height: int) -> pygame.Surface | None:
    """
    Renvoie une Surface Pygame redimensionnée à (width, height) pour la
    carte de nom `nom`. Utilise `card_id` pour choisir de façon
    déterministe (mais variée) parmi les variantes disponibles.
    Renvoie None si aucune image n'est trouvée.
    """
    cache_key = (nom, width, height, card_id)
    if cache_key in _scaled_cache:
        return _scaled_cache[cache_key][0]

    paths = _pick_variant(nom, card_id)
    if not paths:
        return None

    # Choisir une variante de façon déterministe via le suffixe numérique de l'id
    # ex: "pc_2" → variante index 2 % len(paths)
    try:
        variant_idx = int(card_id.rsplit("_", 1)[-1]) % len(paths)
    except (ValueError, IndexError):
        variant_idx = 0

    path = paths[variant_idx]

    try:
        surf = pygame.image.load(path).convert_alpha()
        scaled = pygame.transform.smoothscale(surf, (width, height))
        _scaled_cache[cache_key] = [scaled]
        return scaled
    except Exception:
        return None


def preload_all(width: int, height: int) -> None:
    """
    Précharge toutes les images à la taille (width, height) au démarrage
    pour éviter les freezes pendant la partie.
    """
    index = _get_index()
    for paths in index.values():
        for path in paths:
            try:
                surf = pygame.image.load(path).convert_alpha()
                pygame.transform.smoothscale(surf, (width, height))
            except Exception:
                pass