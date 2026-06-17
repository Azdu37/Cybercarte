"""
Sélecteur de cartes : permet au joueur de choisir quelles cartes désactiver
lors d'un malus ou événement, au lieu d'être aléatoire.
"""
from __future__ import annotations
import pygame
from src.models.card import Card
from src.models.network import EtatCellule, Cellule
from src.views.ui.components.card_render import (
    draw_rounded_rect, draw_card, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT,
    C_TEXT, C_TEXT_DIM, C_ATTACK, CARD_W, CARD_H
)

Position = tuple[int, int]


class CardSelector:
    """
    Interface de sélection de cartes.
    Le joueur peut cliquer sur les cartes valides du réseau pour les sélectionner.
    """
    
    def __init__(self, message: str, count_to_select: int,
                 available_positions: list[Position],
                 network_grille: dict[Position, Cellule]) -> None:
        """
        message: texte d'explication (ex: "Choisissez 2 cartes à désactiver")
        count_to_select: nombre de cartes à sélectionner
        available_positions: positions des cartes disponibles pour sélection
        network_grille: le grille du réseau (Position -> Cellule)
        """
        self.message = message
        self.count_to_select = count_to_select
        self.available_positions = set(available_positions)
        self.network_grille = network_grille
        self.selected: list[Position] = []
        self.visible = True
        self.btn_confirm: pygame.Rect | None = None
        self.card_rects: dict[Position, pygame.Rect] = {}
    
    def draw(self, surf: pygame.Surface, screen_w: int, screen_h: int,
             network_ox: int, network_oy: int, card_scale: int = 90) -> None:
        """
        Dessine le sélecteur de cartes.
        
        network_ox, network_oy: position d'origine du réseau à l'écran
        card_scale: taille des cartes du réseau (ex: 90 pixels)
        """
        if not self.visible:
            return
        
        # Fond semi-transparent
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(150)
        overlay.fill((10, 10, 20))
        surf.blit(overlay, (0, 0))
        
        # Titre du sélecteur
        tf = pygame.font.SysFont(None, 26, bold=True)
        title = tf.render("Sélection de cartes", True, C_ATTACK)
        title_rect = title.get_rect(midtop=(screen_w // 2, 30))
        surf.blit(title, title_rect)
        
        # Message d'instruction
        mf = pygame.font.SysFont(None, 18)
        msg = mf.render(
            f"{self.message} ({len(self.selected)}/{self.count_to_select})",
            True, C_TEXT_DIM
        )
        msg_rect = msg.get_rect(midtop=(screen_w // 2, 70))
        surf.blit(msg, msg_rect)
        
        # Surbrillance des cartes sélectionnables
        self.card_rects = {}
        for pos in self.available_positions:
            if pos in self.network_grille:
                cel = self.network_grille[pos]
                x, y = network_ox + pos[0] * (card_scale + 8), network_oy + pos[1] * (card_scale + 8)
                
                rect = pygame.Rect(x, y, card_scale, card_scale + 20)
                self.card_rects[pos] = rect
                
                # Couleur selon l'état de sélection
                if pos in self.selected:
                    color = C_HIGHLIGHT
                    border_w = 3
                else:
                    color = C_PANEL_LIGHT
                    border_w = 1
                
                draw_rounded_rect(surf, C_PANEL, rect, radius=6,
                                 border=border_w, border_color=color)
                
                # Dessine la carte
                draw_card(surf, cel.carte, x + 5, y + 5,
                         morte=(cel.etat == EtatCellule.MORTE),
                         small=True)
                
                # Si sélectionnée, ajoute une checkmark
                if pos in self.selected:
                    ckf = pygame.font.SysFont(None, 32, bold=True)
                    ck = ckf.render("✓", True, C_HIGHLIGHT)
                    surf.blit(ck, (x + card_scale - 20, y + 5))
        
        # Bouton Confirmer (désactivé si pas assez de cartes sélectionnées)
        can_confirm = len(self.selected) == self.count_to_select
        
        btn_w, btn_h = 160, 40
        btn_x = (screen_w - btn_w) // 2
        btn_y = screen_h - 80
        self.btn_confirm = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        
        btn_color = C_HIGHLIGHT if can_confirm else C_BORDER
        draw_rounded_rect(surf, C_PANEL_LIGHT, self.btn_confirm,
                         radius=8, border=2, border_color=btn_color)
        
        bf = pygame.font.SysFont(None, 18, bold=True)
        btn_txt = bf.render("Confirmer", True, btn_color if can_confirm else C_TEXT_DIM)
        surf.blit(btn_txt, btn_txt.get_rect(center=self.btn_confirm.center))
    
    def handle_click(self, pos: tuple[int, int]) -> bool | None:
        """
        Gère le clic du joueur.
        Retourne :
          - None : pas d'action
          - False : clic sur une carte (sélection/déselection)
          - True : clic sur confirmer (sélection complète et validée)
        """
        if not self.visible:
            return None
        
        # Clic sur cartes
        for card_pos, rect in self.card_rects.items():
            if rect.collidepoint(pos):
                if card_pos in self.selected:
                    self.selected.remove(card_pos)
                else:
                    if len(self.selected) < self.count_to_select:
                        self.selected.append(card_pos)
                return False
        
        # Clic sur confirmer
        if self.btn_confirm and self.btn_confirm.collidepoint(pos):
            if len(self.selected) == self.count_to_select:
                self.visible = False
                return True
        
        return None
    
    def is_complete(self) -> bool:
        """Retourne True si le joueur a sélectionné le nombre de cartes requis."""
        return len(self.selected) == self.count_to_select
