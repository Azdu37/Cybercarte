"""
Afficheur détaillé de carte : affiche toutes les infos quand on clique sur une carte.
"""
from __future__ import annotations
import pygame
from src.models.card import Card
from src.views.ui.components.card_render import (
    draw_rounded_rect, draw_card, C_PANEL, C_PANEL_LIGHT, C_BORDER, C_HIGHLIGHT,
    C_TEXT, C_TEXT_DIM, C_INFRA, C_BONUS, C_ATTACK, C_EVENT, C_PROTECTION,
    CARD_W, CARD_H
)


class CardDetailView:
    """
    Affiche une carte en grand avec tous les détails.
    """
    
    def __init__(self, card: Card) -> None:
        self.card = card
        self.visible = True
        self.btn_close: pygame.Rect | None = None
    
    def draw(self, surf: pygame.Surface, screen_w: int, screen_h: int) -> None:
        if not self.visible:
            return
        
        # Fond semi-transparent
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(200)
        overlay.fill((10, 10, 20))
        surf.blit(overlay, (0, 0))
        
        # Cadre du détail
        detail_w, detail_h = 500, 600
        detail_x = (screen_w - detail_w) // 2
        detail_y = (screen_h - detail_h) // 2
        
        draw_rounded_rect(surf, C_PANEL, (detail_x, detail_y, detail_w, detail_h),
                         radius=12, border=2, border_color=C_BORDER)
        
        # Couleur selon catégorie
        if self.card.categorie.value == "infrastructure":
            cat_color = C_INFRA
            cat_txt = "🔗 INFRASTRUCTURE"
        elif self.card.categorie.value == "bonus":
            cat_color = C_BONUS
            cat_txt = "✨ BONUS"
        elif self.card.categorie.value == "malus":
            cat_color = C_ATTACK
            cat_txt = "⚠️ MALUS"
        elif self.card.categorie.value == "protection":
            cat_color = C_PROTECTION
            cat_txt = "🛡️ PROTECTION"
        elif self.card.categorie.value == "evenement":
            cat_color = C_EVENT
            cat_txt = "⚡ ÉVÉNEMENT"
        elif self.card.categorie.value == "objectif":
            cat_color = C_TEXT_DIM
            cat_txt = "🎯 OBJECTIF"
        else:
            cat_color = C_TEXT_DIM
            cat_txt = "CARTE"
        
        # Titre
        tf = pygame.font.SysFont(None, 20, bold=True)
        t = tf.render(cat_txt, True, cat_color)
        surf.blit(t, (detail_x + 20, detail_y + 16))
        
        # Nom en gros
        nf = pygame.font.SysFont(None, 28, bold=True)
        n = nf.render(self.card.nom, True, C_HIGHLIGHT)
        n_rect = n.get_rect(midtop=(detail_x + detail_w // 2, detail_y + 50))
        surf.blit(n, n_rect)
        
        # Image de la carte
        draw_card(surf, self.card, detail_x + detail_w // 2 - 50, detail_y + 90)
        
        # Séparateur
        pygame.draw.line(surf, C_BORDER, (detail_x + 20, detail_y + 245),
                        (detail_x + detail_w - 20, detail_y + 245), 1)
        
        # Description
        y_desc = detail_y + 265
        df = pygame.font.SysFont(None, 16)
        desc_label = df.render("Description :", True, C_TEXT_DIM)
        surf.blit(desc_label, (detail_x + 20, y_desc))
        
        y_desc += 24
        for line in self._wrap(self.card.description, df, detail_w - 40):
            t = df.render(line, True, C_TEXT)
            surf.blit(t, (detail_x + 20, y_desc))
            y_desc += 18
        
        # Connecteurs (si c'est une infrastructure)
        if hasattr(self.card, 'connecteurs') and self.card.connecteurs:
            y_conn = y_desc + 10
            conn_label = df.render("Connecteurs :", True, C_TEXT_DIM)
            surf.blit(conn_label, (detail_x + 20, y_conn))
            
            y_conn += 24
            for dir_name, conn in self.card.connecteurs.items():
                conn_txt = f"  • {dir_name}: {conn.nom if hasattr(conn, 'nom') else conn}"
                t = df.render(conn_txt, True, C_TEXT)
                surf.blit(t, (detail_x + 20, y_conn))
                y_conn += 18
        
        # Tags
        if self.card.tags:
            y_tags = y_conn + 10
            tags_label = df.render("Tags :", True, C_TEXT_DIM)
            surf.blit(tags_label, (detail_x + 20, y_tags))
            
            tags_str = ", ".join(self.card.tags)
            tags_txt = self._wrap(tags_str, df, detail_w - 40)
            y_tags += 24
            for line in tags_txt:
                t = df.render(line, True, C_TEXT)
                surf.blit(t, (detail_x + 20, y_tags))
                y_tags += 18
        
        # Bouton Fermer
        btn_w, btn_h = 120, 32
        btn_x = detail_x + (detail_w - btn_w) // 2
        btn_y = detail_y + detail_h - 50
        
        self.btn_close = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        draw_rounded_rect(surf, C_PANEL_LIGHT, self.btn_close,
                         radius=6, border=1, border_color=C_BORDER)
        
        bf = pygame.font.SysFont(None, 18)
        b = bf.render("Fermer", True, C_HIGHLIGHT)
        surf.blit(b, b.get_rect(center=self.btn_close.center))
    
    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Retourne True si le modal doit se fermer."""
        if self.btn_close and self.btn_close.collidepoint(pos):
            self.visible = False
            return True
        # Clic ailleurs ferme aussi le modal
        if self.visible:
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
