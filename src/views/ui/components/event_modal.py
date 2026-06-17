"""
Modal d'événement / bonus / malus : explique ce qui se passe et affiche l'impact.

Structure :
  - Titre du type (Événement, Bonus, Malus)
  - Nom et description de la carte
  - Ce qui va se passer (effet expliqué)
  - Impact pour chaque joueur
  - Bouton "Compris" ou sélection manuelle si besoin
"""
from __future__ import annotations
import pygame
from src.models.card import Card
from src.models.game import Game
from src.models.enums import CategorieCarte
from src.views.ui.components.card_render import (
    draw_rounded_rect, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT, 
    C_TEXT, C_TEXT_DIM, C_BONUS, C_ATTACK, C_EVENT
)

Position = tuple[int, int]


class EventModal:
    """Affiche un modal explicatif pour un événement/bonus/malus."""
    
    def __init__(self, card: Card, players_affected: dict[str, list[str]]) -> None:
        """
        card: la carte bonus/malus/événement
        players_affected: {player_name: [cartes_affectées_nom_ou_description]}
        """
        self.card = card
        self.players_affected = players_affected
        self.visible = True
        self.btn_ok: pygame.Rect | None = None
    
    def draw(self, surf: pygame.Surface, screen_w: int, screen_h: int) -> None:
        if not self.visible:
            return
        
        # Fond semi-transparent
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(200)
        overlay.fill((10, 10, 20))
        surf.blit(overlay, (0, 0))
        
        # Cadre du modal
        modal_w, modal_h = 600, 450
        modal_x = (screen_w - modal_w) // 2
        modal_y = (screen_h - modal_h) // 2
        
        draw_rounded_rect(surf, C_PANEL, (modal_x, modal_y, modal_w, modal_h),
                         radius=12, border=2, border_color=C_BORDER)
        
        # Titre (type de carte)
        title_color = C_EVENT
        if self.card.categorie == CategorieCarte.BONUS:
            title_color = C_BONUS
            titre = "🔧 BONUS"
        elif self.card.categorie == CategorieCarte.MALUS:
            title_color = C_ATTACK
            titre = "⚠️ MALUS"
        elif self.card.categorie == CategorieCarte.EVENEMENT:
            titre = "⚡ ÉVÉNEMENT"
        else:
            titre = "CARTE"
        
        tf = pygame.font.SysFont(None, 28, bold=True)
        t = tf.render(titre, True, title_color)
        surf.blit(t, (modal_x + 24, modal_y + 16))
        
        # Nom de la carte
        nf = pygame.font.SysFont(None, 22, bold=True)
        n = nf.render(self.card.nom, True, C_TEXT)
        surf.blit(n, (modal_x + 24, modal_y + 50))
        
        # Description
        df = pygame.font.SysFont(None, 16)
        y_desc = modal_y + 85
        for line in self._wrap(self.card.description, df, modal_w - 48):
            t = df.render(line, True, C_TEXT_DIM)
            surf.blit(t, (modal_x + 24, y_desc))
            y_desc += 18
        
        # Séparateur
        pygame.draw.line(surf, C_BORDER, (modal_x + 24, y_desc + 8),
                        (modal_x + modal_w - 24, y_desc + 8), 1)
        
        # Impact pour chaque joueur
        y_impact = y_desc + 20
        sf = pygame.font.SysFont(None, 14)
        
        for player_name, affected_items in self.players_affected.items():
            if affected_items:
                label = f"→ {player_name}:"
                t = sf.render(label, True, C_HIGHLIGHT)
                surf.blit(t, (modal_x + 24, y_impact))
                y_impact += 18
                
                for item in affected_items[:2]:  # max 2 items par joueur
                    item_txt = f"  • {item}"
                    t = sf.render(item_txt, True, C_TEXT_DIM)
                    surf.blit(t, (modal_x + 32, y_impact))
                    y_impact += 16
                
                if len(affected_items) > 2:
                    more = f"  ... et {len(affected_items) - 2} de plus"
                    t = sf.render(more, True, C_TEXT_DIM)
                    surf.blit(t, (modal_x + 32, y_impact))
                    y_impact += 16
        
        # Bouton OK
        btn_w, btn_h = 140, 36
        btn_x = modal_x + (modal_w - btn_w) // 2
        btn_y = modal_y + modal_h - 50
        
        self.btn_ok = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        draw_rounded_rect(surf, C_PANEL_LIGHT, self.btn_ok,
                         radius=6, border=1, border_color=C_BORDER)
        
        bf = pygame.font.SysFont(None, 18)
        b = bf.render("Compris", True, C_HIGHLIGHT)
        surf.blit(b, b.get_rect(center=self.btn_ok.center))
    
    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Retourne True si le modal doit se fermer."""
        if self.btn_ok and self.btn_ok.collidepoint(pos):
            self.visible = False
            return True
        return False
    
    @staticmethod
    def _wrap(text: str, font, max_w: int) -> list[str]:
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines
