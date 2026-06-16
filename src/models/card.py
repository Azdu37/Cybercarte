"""Représentation d'une carte du jeu."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from .enums import Connecteur, Direction, CategorieCarte


@dataclass(frozen=True)
class Card:
    id: str
    nom: str
    categorie: CategorieCarte
    connecteurs: dict[Direction, Connecteur] = field(default_factory=dict)
    description: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    protege_de: tuple[str, ...] = field(default_factory=tuple)

    def connecteur(self, direction: Direction) -> Connecteur:
        return self.connecteurs.get(direction, Connecteur.VIDE)

    def est_placable(self) -> bool:
        return self.categorie in (CategorieCarte.INFRASTRUCTURE, CategorieCarte.PROTECTION)

    def __str__(self) -> str:
        return self.nom

    # Alias anglais pour compat avec le code Cybercarte
    @property
    def name(self) -> str:
        return self.nom

    @property
    def card_type(self) -> str:
        return self.categorie.value


def card_from_dict(data: dict) -> Card:
    connecteurs = {
        Direction(d): Connecteur(v) for d, v in data.get("connecteurs", {}).items()
    }
    return Card(
        id=data["id"],
        nom=data["nom"],
        categorie=CategorieCarte(data["categorie"]),
        connecteurs=connecteurs,
        description=data.get("description", ""),
        tags=tuple(data.get("tags", [])),
        protege_de=tuple(data.get("protege_de", [])),
    )


def load_cards(chemin: str) -> dict[str, Card]:
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)
    return {d["id"]: card_from_dict(d) for d in data}
