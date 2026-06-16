# Network Codex (prototype Python / Pygame)

Implémentation en cours du jeu de cartes français **Network Codex** (2 à 4
joueurs, bâtir une infrastructure réseau "sécurisée" de 9 cartes reliées par
leurs connecteurs).

## Installation

```bash
pip install pygame
```

## Lancer le prototype

```bash
python3 main.py
```

- **Écran d'accueil** : choisis le nombre de joueurs (2 à 4), puis clique
  "Commencer".
- **Écran de partie** : jeu local "chacun son tour" sur le même écran.
  Le joueur dont c'est le tour voit son réseau et sa main en bas. Clique
  une carte de la main pour la sélectionner : les cases où elle peut être
  posées s'illuminent en vert sur le plateau. Clique une case en
  surbrillance pour poser la carte, ou re-clique la carte (ou ailleurs)
  pour annuler la sélection. Le bouton **"Fin de tour"** passe au joueur
  suivant (son réseau et sa main remplacent ceux affichés).

Fermez la fenêtre ou appuyez sur **Échap** pour quitter.

## Lancer les tests de logique (sans Pygame)

```bash
python3 test_network.py
```

Affiche en texte la construction d'un réseau, son extension tentaculaire,
puis le cycle déconnexion -> trou -> réparation.

## Architecture actuelle

```
network_codex/
├── main.py                     # point d'entrée (lance la fenêtre Pygame)
├── test_network.py             # test texte de la logique réseau
├── data/
│   ├── infrastructure_cards.json   # les 64 cartes infrastructure (16 types x 4 rotations)
│   └── generate_infrastructure.py  # script générateur (voir ci-dessous)
├── game/                        # logique de jeu, indépendante de l'affichage
│   ├── enums.py                 # Connecteur, Direction, CategorieCarte, rotations
│   ├── card.py                  # classe Carte + chargement JSON
│   ├── network.py               # classe Reseau : grille, placement, trous/réparation
│   ├── player.py                # classe Joueur : main, réseau, score, objectif
│   └── partie.py                # classe Partie : joueurs + tour courant, nouvelle_partie()
└── ui/                           # interface Pygame
    ├── constants.py              # couleurs, tailles
    ├── widgets.py                # petits éléments réutilisables (boutons)
    ├── rendu_reseau.py           # dessin d'un Reseau (cases, connecteurs, surbrillance)
    ├── ecran_accueil.py          # écran de choix du nombre de joueurs (2-4)
    ├── ecran_partie.py           # écran de partie (plateau + main + interactions)
    └── app.py                    # boucle principale / machine à états
```

### Système de connecteurs

Chaque carte infrastructure a, sur chacun de ses 4 côtés (N/E/S/O), soit un
connecteur **Données**, soit un connecteur **Électrique**, soit rien (vide).
Deux cartes adjacentes ne sont reliées que si leurs côtés en contact portent
le **même type** de connecteur, et aucun des deux n'est vide (logique de
domino). Les cartes ne sont **jamais pivotées** en jeu.

### Réseau "tentaculaire"

`game.network.Reseau` stocke les cartes posées dans un dictionnaire
`{(x, y): Cellule}` (pas de grille de taille fixe), ce qui permet au réseau
de s'étendre dans n'importe quelle direction. Une carte ne peut être posée
que sur une case vide adjacente à au moins une carte vivante du réseau (ou
n'importe où si le réseau est encore vide), et tous les côtés en contact
avec des cartes vivantes voisines doivent correspondre.

### Déconnexion / trous / réparation

- `reseau.deconnecter(position)` transforme une carte vivante en carte
  **morte** : elle ne compte plus dans les cartes actives et laisse un
  "trou".
- Poser une nouvelle carte sur ce trou (`reseau.poser_carte`) utilise la
  **même validation** que pour étendre le réseau : la nouvelle carte doit
  donc, au minimum, recréer les connexions qui existaient avec les voisins
  encore vivants - exactement la règle décrite dans les règles du jeu.
- `reseau.reconnecter(position)` réactive directement une carte morte sans
  poser de nouvelle carte (pour l'effet "Mise en Ligne").

### Joueur, Partie et déroulé local

- `game.player.Joueur` regroupe la main (`main: list[Carte]`), le réseau
  (`reseau: Reseau`) et le score d'un joueur. `jouer_carte(carte, position)`
  retire la carte de la main et la pose dans le réseau (en réutilisant la
  validation de `Reseau.poser_carte`).
- `game.partie.Partie` contient la liste des `Joueur` et l'index du joueur
  courant (`joueur_courant`, `joueur_suivant()`).
- `nouvelle_partie(nombre_joueurs, cartes_infrastructure)` crée la partie et
  distribue à chaque joueur une main de départ de 4 cartes. **Distribution
  temporaire** : tirage aléatoire sans remise dans les 64 cartes
  infrastructure, en attendant le vrai système des 3 piles
  (`game/deck.py`).
- Côté interface, `ui/app.py` implémente une machine à états `"accueil"` ->
  `"partie"` : l'écran de partie n'affiche que le réseau et la main du
  joueur courant (jeu "chacun son tour" en local, écran partagé).

### Données des cartes infrastructure (`infrastructure_cards.json`)

Les 16 types de cartes infrastructure (11 grises + 5 bleues "protection")
ont chacun **4 exemplaires**, qui sont implémentés ici comme les **4
rotations à 90°** d'un motif de connecteurs de référence (déterminé à
partir des visuels du jeu). C'est l'hypothèse la plus cohérente avec la
règle "pas de rotation en jeu" + "4 exemplaires par type" : chaque
exemplaire physique correspond à une orientation différente du même motif.

Si en comparant avec le jeu physique un motif de référence s'avère
incorrect, il suffit de corriger l'entrée correspondante dans
`BASE_PATTERNS` (fichier `data/generate_infrastructure.py`) puis de relancer :

```bash
python3 data/generate_infrastructure.py
```

## Prochaines étapes

- [ ] `game/deck.py` : vraie gestion des 3 piles (Infrastructure, Capacité/Bonus-Malus, Événements) pour remplacer la distribution aléatoire actuelle
- [ ] Données JSON pour les cartes bonus/malus, événements (+ Canard en plastique) et objectifs
- [ ] `game/effects.py` : implémentation des effets (vol de carte, déconnexion, Sauvegarde locale, Mise en Ligne, etc.)
- [ ] Suivi des 2 actions par tour, déclenchement des événements tous les 2 tours, condition de victoire (9 cartes actives), score final (objectif rempli = +5)
- [ ] Interface : indication des autres joueurs (noms/scores) pendant le tour, écran de fin de partie / classement
- [ ] Pioche / défausse visibles et cliquables dans `ecran_partie.py`
