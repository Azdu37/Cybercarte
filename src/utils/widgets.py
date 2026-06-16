"""Petits éléments d'interface réutilisables (boutons...)."""
from __future__ import annotations
import pygame
from . import constants as c


def dessiner_bouton(surface: pygame.Surface, rect: pygame.Rect, texte: str, police,
                    *, survol: bool = False, selectionne: bool = False) -> None:
    if selectionne:
        couleur = c.COULEUR_BOUTON_SELECTION
    elif survol:
        couleur = c.COULEUR_BOUTON_SURVOL
    else:
        couleur = c.COULEUR_BOUTON
    pygame.draw.rect(surface, couleur, rect, border_radius=c.RAYON_COIN)
    rendu = police.render(texte, True, c.COULEUR_BOUTON_TEXTE)
    surface.blit(rendu, rendu.get_rect(center=rect.center))
