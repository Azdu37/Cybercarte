"""Test de la logique réseau (sans Pygame). Lancer : python3 test_network.py"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from src.models.card import load_cards
from src.models.network import Network

CHEMIN = os.path.join(os.path.dirname(__file__), "data", "infrastructure_cards.json")

def trouver_et_poser(net, cartes, pos, excl=frozenset()):
    for id_, c in cartes.items():
        if id_ in excl: continue
        if pos in net.positions_valides(c):
            net.poser_carte(c, pos); return id_
    return None

def main():
    cartes = load_cards(CHEMIN)
    print(f"{len(cartes)} cartes chargées.\n")
    net = Network()
    net.poser_carte(cartes["site_0"], (0,0))
    utilisees = {"site_0"}
    for pos in [(1,0),(0,1),(-1,0),(0,-1)]:
        id_ = trouver_et_poser(net, cartes, pos, utilisees)
        if id_: utilisees.add(id_); print(f"-> {cartes[id_].nom} posé en {pos}")
        else: print(f"-> Aucune carte pour {pos}")
    print(f"\nActifs: {net.nombre_cartes_actives()} | Trous: {net.nombre_trous()}")
    if (1,0) in net.grille:
        coupee = net.deconnecter((1,0))
        print(f"\nDéconnexion de '{coupee.nom}'")
        print(f"Actifs: {net.nombre_cartes_actives()} | Trous: {net.nombre_trous()}")
        id_ = trouver_et_poser(net, cartes, (1,0), utilisees)
        if id_: print(f"Trou comblé par '{cartes[id_].nom}'")
        print(f"Actifs: {net.nombre_cartes_actives()} | Trous: {net.nombre_trous()}")

if __name__ == "__main__":
    main()
