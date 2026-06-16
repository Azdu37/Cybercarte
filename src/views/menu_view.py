"""Écran d'accueil : choix du nombre de joueurs (2 à 4)."""
from __future__ import annotations
import pygame
from src.utils import constants as c
from src.utils.widgets import dessiner_bouton

TAILLE_CASE_NB = 90
ESPACE_NB = 24


def calculer_disposition() -> dict:
    largeur = 3 * TAILLE_CASE_NB + 2 * ESPACE_NB
    x0 = (c.SCREEN_WIDTH - largeur) // 2
    y_cases = 320
    cases: dict[int, pygame.Rect] = {}
    for i, nb in enumerate((2, 3, 4)):
        cases[nb] = pygame.Rect(x0 + i * (TAILLE_CASE_NB + ESPACE_NB), y_cases, TAILLE_CASE_NB, TAILLE_CASE_NB)
    bouton = pygame.Rect((c.SCREEN_WIDTH - 240) // 2, 480, 240, 64)
    return {"cases": cases, "bouton": bouton}


def draw(surface: pygame.Surface, nb_sel: int, polices: dict, disp: dict) -> None:
    titre = polices["titre"].render("Network Codex", True, c.COULEUR_TITRE)
    surface.blit(titre, titre.get_rect(center=(c.SCREEN_WIDTH // 2, 140)))

    sous = polices["normale"].render("Partie locale · chacun joue à son tour", True, c.COULEUR_TITRE)
    surface.blit(sous, sous.get_rect(center=(c.SCREEN_WIDTH // 2, 200)))

    label = polices["normale"].render("Nombre de joueurs :", True, c.COULEUR_TITRE)
    surface.blit(label, label.get_rect(center=(c.SCREEN_WIDTH // 2, 270)))

    souris = pygame.mouse.get_pos()
    for nb, rect in disp["cases"].items():
        dessiner_bouton(surface, rect, str(nb), polices["grande"],
                        survol=rect.collidepoint(souris), selectionne=(nb == nb_sel))

    dessiner_bouton(surface, disp["bouton"], "Commencer", polices["normale"],
                    survol=disp["bouton"].collidepoint(souris))


def handle_click(pixel: tuple[int, int], nb_sel: int, disp: dict) -> tuple[int, bool]:
    for nb, rect in disp["cases"].items():
        if rect.collidepoint(pixel):
            return nb, False
    if disp["bouton"].collidepoint(pixel):
        return nb_sel, True
    return nb_sel, False
