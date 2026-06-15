# Network Codex - Architecture

## Structure du Projet

```text
Cybercarte/
├── assets/             # Ressources multimédia
│   ├── images/         # Cartes, icônes, arrière-plans
│   └── sounds/         # Effets sonores et musique
├── src/                # Code source
│   ├── controllers/    # Gestion de la logique d'entrée et coordination
│   ├── models/         # Objets métier (Cartes, Joueurs, Plateau)
│   ├── views/          # Rendu graphique (Pygame)
│   └── utils/          # Constantes et fonctions utilitaires
├── main.py             # Point d'entrée du jeu
└── .gitignore          # Exclusion des fichiers PyCharm/Python
```

## Description des Composants

### Models (`src/models/`)
- `card.py`: Définit la classe `Card` avec ses types (Infrastructure, Bonus/Malus, Événement), ses connexions (Haut, Bas, Gauche, Droite) et ses états (connectée ou non).
- `player.py`: Gère l'état d'un joueur, sa main, son infrastructure personnelle et son score.
- `game.py`: Contient la logique globale du jeu, la gestion des tours, les pioches et la vérification des conditions de victoire.

### Views (`src/views/`)
- `game_view.py`: Utilise Pygame pour dessiner l'interface utilisateur, les cartes et les informations de jeu.

### Controllers (`src/controllers/`)
- `game_controller.py`: Fait le lien entre la vue et le modèle. Intercepte les événements utilisateur (clics, touches) et met à jour le modèle de jeu.

### Utils (`src/utils/`)
- `constants.py`: Centralise les couleurs, dimensions des cartes et paramètres du jeu (nombre de cartes pour gagner, etc.).

## Fonctionnalités Implémentées (Squelette)
- Initialisation des joueurs (2 à 4 joueurs).
- Gestion des tours de jeu.
- Système de score (cartes connectées + objectif personnel).
- Structure pour les différentes pioches.
- Détection de fin de partie (9 cartes).

## Installation
Assurez-vous d'avoir Pygame installé :
```bash
pip install pygame
```

Lancer le jeu :
```bash
python main.py
```
