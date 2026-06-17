# V3 - Système d'Information et de Sélection des Cartes

## 🎯 Objectifs V3 Réalisés

### 1. Maximum d'infos au clic sur une carte
- **Double clic** sur une carte en main → affichage complet avec :
  - Catégorie et type
  - Nom et image en grand
  - Description détaillée
  - Connecteurs (pour les infrastructures)
  - Tags associés
- **Clic** sur une carte du réseau → affichage des mêmes détails

### 2. Explication claire des événements / bonus / malus
- **Modal d'événement** s'affiche automatiquement après :
  - Tirage d'une carte bonus/malus
  - Application d'un événement global
- Le modal affiche :
  - Type de carte (🔧 BONUS / ⚠️ MALUS / ⚡ ÉVÉNEMENT)
  - Nom et description
  - **Impact précis** pour chaque joueur affecté

### 3. Affichage de l'impact dans le jeu
- Pour chaque événement/bonus/malus, le modal liste :
  - Quels joueurs sont affectés
  - Quel type d'action sera appliquée
  - Nombre de cartes impliquées
- Le journal affiche un résumé après l'application

### 4. Sélection manuelle par le joueur
- **Lors d'un événement global** : le joueur courant voit un sélecteur
  - Les cartes actives sont mises en surbrillance
  - L'utilisateur **clique** sur les cartes à désactiver
  - Le nombre requis s'affiche ("Sélectionnez X carte(s)")
  - Bouton "Confirmer" pour valider la sélection
- Cela remplace l'aléatoire par le **contrôle du joueur**

---

## 🎮 Guide d'Utilisation

### Voir les détails d'une carte
1. **Clic simple** : Sélectionne la carte pour la placer
2. **Double clic** : Ouvre la vue détaillée avec toutes les infos

### Comprendre un événement / bonus / malus
1. Une carte bonus/malus est piochée
2. Un **modal explicatif** s'affiche automatiquement
3. Lisez l'impact pour chaque joueur
4. Cliquez "Compris" pour fermer

### Choisir les cartes à désactiver
1. Lors d'un événement qui impacte **votre réseau**
2. Un **sélecteur** apparaît avec vos cartes actives en surbrillance
3. **Cliquez** sur les cartes à désactiver (le nombre requis s'affiche)
4. Cliquez "Confirmer" pour valider votre choix

---

## 📁 Fichiers Nouveaux / Modifiés

### Nouveaux fichiers
- `src/views/ui/components/event_modal.py` - Modal d'explication d'événements
- `src/views/ui/components/card_selector.py` - Interface de sélection de cartes
- `src/views/ui/components/card_detail_view.py` - Afficheur détaillé de cartes

### Fichiers modifiés
- `src/models/game.py` - Support de la sélection manuelle d'effets
- `src/views/ui/screen/game.py` - Intégration des nouveaux composants
- `src/controllers/game_controller.py` - Support du scroll molette

---

## 🔧 Détails Techniques

### Flux des événements
1. `trigger_event()` pioche une carte événement
2. Pour le joueur courant : crée un `pending_effect` (au lieu d'appliquer directement)
3. `game_screen.draw()` détecte `pending_effect` et crée un `CardSelector`
4. L'utilisateur sélectionne les cartes
5. `apply_pending_effect_selection()` applique vraiment l'effet
6. Pour les autres joueurs : application aléatoire comme avant

### États des composants
- `event_modal` : affiche l'explication
- `card_selector` : gère la sélection manuelle
- `card_detail_view` : affiche les détails complets

---

## ✅ Checklist V3

- [x] Max d'infos au clic sur une carte
- [x] Modal explicatif pour événements/bonus/malus
- [x] Affichage de l'impact dans le jeu
- [x] Sélection manuelle des cartes à désactiver
- [x] Guide d'utilisation intégré
- [x] Validation des changements Python

---

## 🚀 Prochaines étapes possibles

1. Améliorer le visuel des sélecteurs (animations, effets hover)
2. Ajouter des statistiques en temps réel (cartes perdues, réparées)
3. Support du son (feedback audio)
4. Système d'aide contextuel (tooltips explicatifs)
5. Replay / historique des actions
