"""
Génère `infrastructure_cards.json` : les 64 cartes "infrastructure"
(16 types distincts x 4 exemplaires).

Comme les cartes ne peuvent jamais être pivotées en jeu, chaque type a 4
"variantes" qui correspondent aux 4 rotations possibles à 90° de son motif
de connecteurs de référence (déterminé en observant les visuels du jeu).
Pour les motifs ayant une symétrie (ex: tous les côtés identiques, ou
symétrie à 180°), certaines des 4 variantes seront identiques entre elles
- c'est normal et reflète simplement le fait que la rotation n'a alors pas
d'effet sur la connectivité.

Si après vérification sur les visuels du jeu un pattern de référence est
incorrect, il suffit de corriger l'entrée correspondante dans
BASE_PATTERNS ci-dessous et de relancer ce script :

    python3 data/generate_infrastructure.py
"""

from __future__ import annotations
import json
import os
import sys

# Permet d'importer `game` même en lançant ce script directement.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game.enums import Connecteur, Direction, ROTATION_HORAIRE  # noqa: E402

D = Connecteur.DONNEES
P = Connecteur.ELECTRIQUE
V = Connecteur.VIDE
N, E, S, O = Direction.NORD, Direction.EST, Direction.SUD, Direction.OUEST


# ---------------------------------------------------------------------------
# Motifs de référence (orientation 0), déterminés à partir des visuels.
# ---------------------------------------------------------------------------
BASE_PATTERNS: dict[str, dict[Direction, Connecteur]] = {
    # --- Cartes grises ---
    "pc":               {N: P, E: D, S: P, O: P},
    "smartphone":       {N: D, E: P, S: D, O: P},
    "serveur":          {N: P, E: P, S: D, O: D},
    "routeur":          {N: P, E: P, S: P, O: D},
    "boite_mail":       {N: D, E: D, S: D, O: D},
    "peripherique":     {N: P, E: D, S: P, O: P},
    "site":             {N: D, E: D, S: D, O: D},
    "logiciel":         {N: D, E: D, S: D, O: D},
    "point_reseau":     {N: D, E: P, S: P, O: D},
    "cloud":            {N: D, E: D, S: D, O: D},
    "base_de_donnee":   {N: P, E: D, S: D, O: P},
    # --- Cartes bleues (protection) ---
    "pare_feu":         {N: V, E: V, S: D, O: D},
    "mise_a_jour":      {N: P, E: D, S: P, O: V},
    "hygiene_numerique": {N: D, E: V, S: V, O: D},
    "vpn":              {N: P, E: D, S: V, O: V},
    "antivirus":        {N: P, E: V, S: V, O: D},
}

NOMS_AFFICHES: dict[str, str] = {
    "pc": "PC",
    "smartphone": "Smartphone",
    "serveur": "Serveur",
    "routeur": "Routeur",
    "boite_mail": "Boîte Mail",
    "peripherique": "Périphérique",
    "site": "Site",
    "logiciel": "Logiciel",
    "point_reseau": "Point Réseau",
    "cloud": "Cloud",
    "base_de_donnee": "Base de donnée",
    "pare_feu": "Pare-Feu",
    "mise_a_jour": "Mise à Jour",
    "hygiene_numerique": "Hygiène Numérique",
    "vpn": "VPN",
    "antivirus": "Antivirus",
}

# Catégorie : "infrastructure" (grise) ou "protection" (bleue)
CATEGORIES: dict[str, str] = {k: "infrastructure" for k in BASE_PATTERNS}
for k in ("pare_feu", "mise_a_jour", "hygiene_numerique", "vpn", "antivirus"):
    CATEGORIES[k] = "protection"

# Étiquettes utilisées plus tard par les objectifs / effets.
TAGS: dict[str, tuple[str, ...]] = {
    "pc": ("appareil_physique",),
    "smartphone": ("appareil_physique",),
    "serveur": ("serveur",),
    "routeur": ("routeur",),
    "boite_mail": ("interface_en_ligne",),
    "peripherique": ("peripherique",),
    "site": ("interface_en_ligne",),
    "logiciel": ("interface_en_ligne",),
    "point_reseau": ("point_reseau",),
    "cloud": ("interface_en_ligne",),
    "base_de_donnee": ("base_de_donnee",),
    "pare_feu": ("protection",),
    "mise_a_jour": ("protection",),
    "hygiene_numerique": ("protection",),
    "vpn": ("protection",),
    "antivirus": ("protection",),
}

# Pour les cartes protection : description + liste des malus dont elles protègent.
PROTECTIONS: dict[str, tuple[str, tuple[str, ...]]] = {
    "pare_feu": (
        "Vous protège du Cheval de Troie et des spywares",
        ("Cheval de Troie", "Spyware"),
    ),
    "mise_a_jour": (
        "Vous protège des spyware et de l'obsolescence programmée",
        ("Spyware", "Obsolescence programmée"),
    ),
    "hygiene_numerique": (
        "Vous protège de l'obsolescence programmée et des fichiers corrompus",
        ("Obsolescence programmée", "Fichier corrompu"),
    ),
    "vpn": (
        "Vous protège des ransomwares",
        ("Ransomware",),
    ),
    "antivirus": (
        "Vous protège du Cheval de Troie et des ransomwares",
        ("Cheval de Troie", "Ransomware"),
    ),
}


def tourner(pattern: dict[Direction, Connecteur]) -> dict[Direction, Connecteur]:
    """Renvoie le motif obtenu après une rotation de 90° dans le sens
    horaire (new[d] = old[ROTATION_HORAIRE[d]])."""
    return {d: pattern[ROTATION_HORAIRE[d]] for d in Direction}


def generer() -> list[dict]:
    cartes: list[dict] = []
    for type_id, motif0 in BASE_PATTERNS.items():
        description, protege_de = "", ()
        if type_id in PROTECTIONS:
            description, protege_de = PROTECTIONS[type_id]

        # Les cartes PROTECTION ont une orientation fixe sur le jeu physique :
        # leurs 4 exemplaires sont identiques, pas des rotations.
        # Les cartes INFRASTRUCTURE ont 4 variantes = 4 rotations a 90 degres.
        est_protection = CATEGORIES[type_id] == "protection"

        motif = motif0
        for variante in range(4):
            cartes.append(
                {
                    "id": f"{type_id}_{variante}",
                    "type": type_id,
                    "nom": NOMS_AFFICHES[type_id],
                    "categorie": CATEGORIES[type_id],
                    "connecteurs": {d.value: c.value for d, c in motif.items()},
                    "description": description,
                    "tags": list(TAGS.get(type_id, ())),
                    "protege_de": list(protege_de),
                }
            )
            if not est_protection:
                motif = tourner(motif)
    return cartes


def main() -> None:
    cartes = generer()
    out_path = os.path.join(os.path.dirname(__file__), "infrastructure_cards.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cartes, f, ensure_ascii=False, indent=2)
    print(f"{len(cartes)} cartes écrites dans {out_path}")


if __name__ == "__main__":
    main()