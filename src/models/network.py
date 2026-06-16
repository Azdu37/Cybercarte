"""Réseau tentaculaire d'un joueur."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .card import Card
from .enums import Connecteur, Direction, OPPOSE, DELTA

Position = tuple[int, int]


class EtatCellule(Enum):
    VIVANTE = "vivante"
    MORTE   = "morte"


@dataclass
class Cellule:
    carte: Card
    etat: EtatCellule = EtatCellule.VIVANTE
    protection: Optional[Card] = None


class Network:
    def __init__(self) -> None:
        self.grille: dict[Position, Cellule] = {}

    def __contains__(self, pos: Position) -> bool:
        return pos in self.grille

    def __getitem__(self, pos: Position) -> Cellule:
        return self.grille[pos]

    def est_vide(self) -> bool:
        return not self.grille

    def voisins(self, pos: Position) -> dict[Direction, Optional[Cellule]]:
        x, y = pos
        return {d: self.grille.get((x + dx, y + dy)) for d, (dx, dy) in DELTA.items()}

    def peut_poser(self, carte: Card, pos: Position) -> bool:
        if not carte.est_placable():
            return False
        cel = self.grille.get(pos)
        if cel is not None and cel.etat == EtatCellule.VIVANTE:
            return False
        if not self.grille:
            return True

        vivants = [
            (d, c) for d, c in self.voisins(pos).items()
            if c is not None and c.etat == EtatCellule.VIVANTE
        ]
        if cel is None and not vivants:
            return False
        for d, cv in vivants:
            if not carte.connecteur(d).correspond_a(cv.carte.connecteur(OPPOSE[d])):
                return False
        return True

    def positions_candidates(self) -> set[Position]:
        if not self.grille:
            return {(0, 0)}
        cands: set[Position] = set()
        for pos, cel in self.grille.items():
            if cel.etat == EtatCellule.MORTE:
                cands.add(pos)
            else:
                for dx, dy in DELTA.values():
                    v = (pos[0] + dx, pos[1] + dy)
                    if v not in self.grille:
                        cands.add(v)
        return cands

    def positions_valides(self, carte: Card) -> list[Position]:
        return [p for p in self.positions_candidates() if self.peut_poser(carte, p)]

    def positions_libres_adjacentes(self) -> list[Position]:
        if not self.grille:
            return [(0, 0)]
        libres: set[Position] = set()
        for pos, cel in self.grille.items():
            if cel.etat == EtatCellule.VIVANTE:
                for dx, dy in DELTA.values():
                    v = (pos[0] + dx, pos[1] + dy)
                    if v not in self.grille:
                        libres.add(v)
        return list(libres)

    def poser_carte(self, carte: Card, pos: Position) -> None:
        if not self.peut_poser(carte, pos):
            raise ValueError(f"Placement invalide : {carte.nom} en {pos}")
        self.grille[pos] = Cellule(carte=carte, etat=EtatCellule.VIVANTE)

    def placer_force(self, carte: Card, pos: Position) -> None:
        self.grille[pos] = Cellule(carte=carte, etat=EtatCellule.VIVANTE)

    def deconnecter(self, pos: Position) -> Card:
        cel = self.grille.get(pos)
        if cel is None or cel.etat == EtatCellule.MORTE:
            raise ValueError(f"Pas de carte vivante en {pos}")
        cel.etat = EtatCellule.MORTE
        return cel.carte

    def reconnecter(self, pos: Position) -> None:
        cel = self.grille.get(pos)
        if cel is None or cel.etat != EtatCellule.MORTE:
            raise ValueError(f"Pas de trou en {pos}")
        cel.etat = EtatCellule.VIVANTE

    def permuter(self, a: Position, b: Position) -> None:
        ca, cb = self.grille.get(a), self.grille.get(b)
        if ca is None or cb is None:
            raise ValueError("Les deux cases doivent être occupées")
        ca.carte, cb.carte = cb.carte, ca.carte
        ca.protection, cb.protection = cb.protection, ca.protection

    def cartes_actives(self) -> list[Card]:
        return [c.carte for c in self.grille.values() if c.etat == EtatCellule.VIVANTE]

    def nombre_cartes_actives(self) -> int:
        return len(self.cartes_actives())

    def positions_trous(self) -> list[Position]:
        return [p for p, c in self.grille.items() if c.etat == EtatCellule.MORTE]

    def nombre_trous(self) -> int:
        return len(self.positions_trous())

    def limites(self) -> tuple[int, int, int, int]:
        if not self.grille:
            return (0, 0, 0, 0)
        xs = [p[0] for p in self.grille]
        ys = [p[1] for p in self.grille]
        return (min(xs), min(ys), max(xs), max(ys))

    # Alias anglais (compat Cybercarte)
    @property
    def grid(self) -> dict[Position, Cellule]:
        return self.grille
