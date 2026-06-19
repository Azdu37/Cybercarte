"""Fonctions de rendu du réseau (plateau) d'un joueur."""
from __future__ import annotations
import pygame
from src.models.card import Card
from src.models.enums import Connecteur, Direction
from src.models.network import Network, EtatCellule
from src.utils import constants as c

Position = tuple[int, int]


def dessiner_connecteurs_carte(surface: pygame.Surface, rect: pygame.Rect, carte: Card, taille: int = c.TAILLE_CONNECTEUR) -> None:
    cx, cy = rect.centerx, rect.centery
    positions = {
        Direction.NORD:  (cx, rect.top),
        Direction.SUD:   (cx, rect.bottom),
        Direction.EST:   (rect.right, cy),
        Direction.OUEST: (rect.left, cy),
    }
    for direction, (px, py) in positions.items():
        conn = carte.connecteur(direction)
        if conn is Connecteur.VIDE:
            continue
        if conn is Connecteur.DONNEES:
            sq = pygame.Rect(0, 0, taille, taille)
            sq.center = (px, py)
            pygame.draw.rect(surface, c.COULEUR_DONNEES, sq, border_radius=3)
        elif conn is Connecteur.ELECTRIQUE:
            pygame.draw.circle(surface, c.COULEUR_ELECTRIQUE, (px, py), taille // 2)
        elif conn is Connecteur.RJ45:
            r = taille // 2
            points = [
                (px, py - r), (px + r, py),
                (px, py + r), (px - r, py)
            ]
            pygame.draw.polygon(surface, c.COULEUR_RJ45, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, width=1)


def dessiner_carte(surface: pygame.Surface, rect: pygame.Rect, carte: Card, police, *,
                   morte: bool = False, police_petite=None, selectionne: bool = False) -> None:
    if morte:
        couleur = c.COULEUR_MORTE
    elif carte.categorie.value == "protection":
        couleur = c.COULEUR_PROTECTION
    else:
        couleur = c.COULEUR_INFRA

    pygame.draw.rect(surface, couleur, rect, border_radius=c.RAYON_COIN)

    bord = c.COULEUR_SURBRILLANCE if selectionne else c.COULEUR_GRILLE
    epaisseur = c.EPAISSEUR_SURBRILLANCE + 1 if selectionne else c.EPAISSEUR_BORD
    pygame.draw.rect(surface, bord, rect, width=epaisseur, border_radius=c.RAYON_COIN)

    if not morte:
        dessiner_connecteurs_carte(surface, rect, carte)

    couleur_texte = c.COULEUR_TEXTE_MORTE if morte else c.COULEUR_TEXTE
    dy = -8 if (morte and police_petite) else 0
    texte = police.render(carte.nom, True, couleur_texte)
    surface.blit(texte, texte.get_rect(center=(rect.centerx, rect.centery + dy)))

    if morte and police_petite:
        sous = police_petite.render("déconnectée", True, couleur_texte)
        surface.blit(sous, sous.get_rect(center=(rect.centerx, rect.centery + 16)))


def dessiner_case_surbrillance(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, c.COULEUR_ZONE_MAIN, rect, border_radius=c.RAYON_COIN)
    pygame.draw.rect(surface, c.COULEUR_SURBRILLANCE, rect, width=c.EPAISSEUR_SURBRILLANCE, border_radius=c.RAYON_COIN)


def limites_combinees(network: Network, extras: tuple[Position, ...] = ()) -> tuple[int, int, int, int]:
    positions = list(network.grille.keys()) + list(extras)
    if not positions:
        return (0, 0, 0, 0)
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    return (min(xs), min(ys), max(xs), max(ys))


def draw_network(
    surface: pygame.Surface,
    network: Network,
    origine: tuple[int, int],
    taille_case: int,
    police,
    police_petite,
    positions_surlignees: tuple[Position, ...] = (),
) -> tuple[int, int, int, int, int]:
    x_min, y_min, x_max, y_max = limites_combinees(network, positions_surlignees)
    pas = taille_case + c.ESPACE_CASE
    ox, oy = origine

    def rect_pour(pos: Position) -> pygame.Rect:
        x, y = pos
        return pygame.Rect(ox + (x - x_min) * pas, oy + (y - y_min) * pas, taille_case, taille_case)

    for pos in positions_surlignees:
        if pos not in network.grille:
            dessiner_case_surbrillance(surface, rect_pour(pos))

    for pos, cel in network.grille.items():
        dessiner_carte(surface, rect_pour(pos), cel.carte, police,
                       morte=cel.etat is EtatCellule.MORTE, police_petite=police_petite)

    return (x_min, y_min, x_max, y_max, pas)


def pixel_to_grid(pixel: tuple[int, int], origine: tuple[int, int], x_min: int, y_min: int,
                  pas: int, taille_case: int) -> Position | None:
    px, py = pixel
    ox, oy = origine
    dx, dy = px - ox, py - oy
    if dx < 0 or dy < 0:
        return None
    gx, gy = dx // pas, dy // pas
    if dx - gx * pas >= taille_case or dy - gy * pas >= taille_case:
        return None
    return (x_min + gx, y_min + gy)
