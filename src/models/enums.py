"""Énumérations de base partagées par tout le moteur de jeu."""
from __future__ import annotations
from enum import Enum


class Connecteur(Enum):
    VIDE      = "vide"
    DONNEES   = "donnees"
    ELECTRIQUE = "electrique"
    RJ45      = "rj45"

    def correspond_a(self, autre: "Connecteur") -> bool:
        return self is not Connecteur.VIDE and self is autre


class Direction(Enum):
    NORD  = "N"
    EST   = "E"
    SUD   = "S"
    OUEST = "O"


OPPOSE: dict[Direction, Direction] = {
    Direction.NORD: Direction.SUD,
    Direction.SUD:  Direction.NORD,
    Direction.EST:  Direction.OUEST,
    Direction.OUEST: Direction.EST,
}

DELTA: dict[Direction, tuple[int, int]] = {
    Direction.NORD:  (0, -1),
    Direction.SUD:   (0,  1),
    Direction.EST:   (1,  0),
    Direction.OUEST: (-1, 0),
}

ROTATION_HORAIRE: dict[Direction, Direction] = {
    Direction.NORD:  Direction.OUEST,
    Direction.EST:   Direction.NORD,
    Direction.SUD:   Direction.EST,
    Direction.OUEST: Direction.SUD,
}


class CategorieCarte(Enum):
    INFRASTRUCTURE = "infrastructure"
    PROTECTION     = "protection"
    BONUS          = "bonus"
    MALUS          = "malus"
    CAPACITE       = "capacite"
    EVENEMENT      = "evenement"
    OBJECTIF       = "objectif"
