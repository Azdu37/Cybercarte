"""
Vue de partie : plateau du joueur courant + main + en-tête avec
indicateurs de couleur des joueurs (repris de Cybercarte).
"""
from __future__ import annotations
import pygame
from src.models.game import Game
from src.utils import constants as c
from src.utils.widgets import dessiner_bouton
from src.views.board_renderer import (
    draw_network, dessiner_carte, pixel_to_grid, limites_combinees
)

Position = tuple[int, int]


def _positions_surlignees(game: Game, carte_sel: int | None) -> tuple[Position, ...]:
    if carte_sel is None:
        return ()
    joueur = game.current_player
    if not (0 <= carte_sel < len(joueur.hand)):
        return ()
    return tuple(joueur.valid_positions(joueur.hand[carte_sel]))


def calculer_disposition(game: Game, carte_sel: int | None) -> dict:
    joueur = game.current_player
    surlignees = _positions_surlignees(game, carte_sel)

    x_min, y_min, x_max, y_max = limites_combinees(joueur.network, surlignees)
    pas = c.TAILLE_CASE_PLATEAU + c.ESPACE_CASE
    larg_plateau = (x_max - x_min + 1) * pas - c.ESPACE_CASE
    haut_plateau = (y_max - y_min + 1) * pas - c.ESPACE_CASE

    zone_h = c.SCREEN_HEIGHT - c.HAUTEUR_ENTETE - c.HAUTEUR_ZONE_MAIN
    origine = (
        (c.SCREEN_WIDTH - larg_plateau) // 2,
        c.HAUTEUR_ENTETE + (zone_h - haut_plateau) // 2,
    )

    # Cartes en main
    lc, hc = c.TAILLE_CARTE_MAIN
    n = len(joueur.hand)
    largeur_totale = n * lc + max(0, n - 1) * c.ESPACE_MAIN
    x0 = (c.SCREEN_WIDTH - largeur_totale) // 2
    y_main = c.SCREEN_HEIGHT - c.HAUTEUR_ZONE_MAIN + (c.HAUTEUR_ZONE_MAIN - hc) // 2
    rects_main = [
        pygame.Rect(x0 + i * (lc + c.ESPACE_MAIN), y_main, lc, hc)
        for i in range(n)
    ]

    bouton_fin = pygame.Rect(c.SCREEN_WIDTH - 180 - c.MARGE, (c.HAUTEUR_ENTETE - 40) // 2, 180, 40)

    return {
        "surlignees": surlignees,
        "x_min": x_min, "y_min": y_min, "pas": pas,
        "origine": origine,
        "rects_main": rects_main,
        "bouton_fin": bouton_fin,
    }


def draw(surface: pygame.Surface, game: Game, carte_sel: int | None, polices: dict, disp: dict) -> None:
    joueur = game.current_player

    # --- En-tête -------------------------------------------------------
    # Point coloré + nom du joueur courant
    pygame.draw.circle(surface, joueur.color, (c.MARGE + 8, c.HAUTEUR_ENTETE // 2), 8)
    titre = polices["normale"].render(f"Tour de {joueur.name}", True, c.COULEUR_TITRE)
    surface.blit(titre, (c.MARGE + 24, (c.HAUTEUR_ENTETE - titre.get_height()) // 2))

    # Actions restantes
    actions_txt = f"Actions : {joueur.actions_left}/{c.ACTIONS_PER_TURN}"
    at = polices["petite"].render(actions_txt, True, c.COULEUR_TITRE)
    surface.blit(at, at.get_rect(midleft=(c.SCREEN_WIDTH // 2 - 120, c.HAUTEUR_ENTETE // 2)))

    # Cartes actives
    info = f"Réseau : {joueur.nombre_cartes_actives()}/9"
    it = polices["petite"].render(info, True, c.COULEUR_TITRE)
    surface.blit(it, it.get_rect(midleft=(c.SCREEN_WIDTH // 2 + 30, c.HAUTEUR_ENTETE // 2)))

    # Indicateurs couleurs de tous les joueurs (en haut à gauche, en ligne)
    for i, p in enumerate(game.players):
        marker_x = c.MARGE + 200 + i * 34
        marker_y = c.HAUTEUR_ENTETE // 2
        pygame.draw.circle(surface, p.color, (marker_x, marker_y), 7)
        if i == game.current_player_index:
            pygame.draw.circle(surface, c.COULEUR_TITRE, (marker_x, marker_y), 7, 2)
        lbl = polices["minuscule"].render(str(p.nombre_cartes_actives()), True, c.COULEUR_TITRE)
        surface.blit(lbl, lbl.get_rect(center=(marker_x, marker_y + 14)))

    souris = pygame.mouse.get_pos()
    dessiner_bouton(surface, disp["bouton_fin"], "Fin de tour", polices["petite"],
                    survol=disp["bouton_fin"].collidepoint(souris))

    # Message du dernier événement / action
    if game.last_message:
        msg = polices["petite"].render(game.last_message, True, c.COULEUR_ELECTRIQUE)
        surface.blit(msg, msg.get_rect(midbottom=(c.SCREEN_WIDTH // 2, c.HAUTEUR_ENTETE - 4)))

    # --- Plateau -------------------------------------------------------
    draw_network(surface, joueur.network, disp["origine"], c.TAILLE_CASE_PLATEAU,
                 polices["petite"], polices["minuscule"],
                 positions_surlignees=disp["surlignees"])

    # --- Zone de main --------------------------------------------------
    zone = pygame.Rect(0, c.SCREEN_HEIGHT - c.HAUTEUR_ZONE_MAIN, c.SCREEN_WIDTH, c.HAUTEUR_ZONE_MAIN)
    pygame.draw.rect(surface, c.COULEUR_ZONE_MAIN, zone)

    if not joueur.hand:
        t = polices["petite"].render("Main vide", True, c.COULEUR_TITRE)
        surface.blit(t, t.get_rect(center=zone.center))

    for i, (carte, rect) in enumerate(zip(joueur.hand, disp["rects_main"])):
        dessiner_carte(surface, rect, carte, polices["petite"], selectionne=(i == carte_sel))

    # Séparateur
    pygame.draw.line(surface, c.COULEUR_GRILLE, (0, c.SCREEN_HEIGHT - c.HAUTEUR_ZONE_MAIN),
                     (c.SCREEN_WIDTH, c.SCREEN_HEIGHT - c.HAUTEUR_ZONE_MAIN), 2)


def handle_click(game: Game, carte_sel: int | None, pixel: tuple[int, int], disp: dict) -> int | None:
    joueur = game.current_player

    if disp["bouton_fin"].collidepoint(pixel):
        game.next_turn()
        return None

    for i, rect in enumerate(disp["rects_main"]):
        if rect.collidepoint(pixel):
            return None if i == carte_sel else i

    pos = pixel_to_grid(pixel, disp["origine"], disp["x_min"], disp["y_min"],
                        disp["pas"], c.TAILLE_CASE_PLATEAU)
    if pos is not None and carte_sel is not None and 0 <= carte_sel < len(joueur.hand):
        if pos in disp["surlignees"]:
            success, _ = game.perform_action("play_card", card_index=carte_sel, pos=pos)
            return None

    return None
