"""
Contenu du dictionnaire du jeu : définitions et effets de toutes les cartes,
classées par catégorie.
"""

DICTIONARY = [
    # ── INFRASTRUCTURE (grises) ─────────────────────────────────────────
    {
        "categorie": "Infrastructure",
        "couleur": (195, 210, 220),
        "cartes": [
            {
                "nom": "PC",
                "definition": "Ordinateur personnel. Élément de base de tout réseau.",
                "effet": "Carte infrastructure standard. Se connecte via des ports Données et Électrique.",
            },
            {
                "nom": "Smartphone",
                "definition": "Terminal mobile connecté au réseau de l'entreprise.",
                "effet": "Carte infrastructure. Connecteurs Données (N/S) et Électrique (E/O).",
            },
            {
                "nom": "Serveur",
                "definition": "Machine centrale qui héberge les services et données de l'infrastructure.",
                "effet": "Carte infrastructure. Connecteurs mixtes Données et Électrique.",
            },
            {
                "nom": "Routeur",
                "definition": "Équipement réseau qui dirige le trafic entre les différents segments.",
                "effet": "Carte infrastructure. Trois connecteurs Électrique, un Données.",
            },
            {
                "nom": "Boîte Mail",
                "definition": "Service de messagerie électronique de l'organisation.",
                "effet": "Carte infrastructure. Quatre connecteurs Données (tous côtés).",
            },
            {
                "nom": "Périphérique",
                "definition": "Équipement externe : imprimante, scanner, disque dur...",
                "effet": "Carte infrastructure. Connecteurs mixtes.",
            },
            {
                "nom": "Site",
                "definition": "Site web ou portail intranet de l'organisation.",
                "effet": "Carte infrastructure. Quatre connecteurs Données (tous côtés).",
            },
            {
                "nom": "Logiciel",
                "definition": "Application métier installée sur le réseau.",
                "effet": "Carte infrastructure. Quatre connecteurs Données (tous côtés).",
            },
            {
                "nom": "Point Réseau",
                "definition": "Prise ou borne d'accès physique au réseau local.",
                "effet": "Carte infrastructure. Connecteurs Données (N/O) et Électrique (E/S).",
            },
            {
                "nom": "Cloud",
                "definition": "Service hébergé en ligne, accessible depuis n'importe où.",
                "effet": "Carte infrastructure. Quatre connecteurs Données (tous côtés).",
            },
            {
                "nom": "Base de donnée",
                "definition": "Système de stockage et d'organisation des données.",
                "effet": "Carte infrastructure. Connecteurs Données (E/S/O) et Électrique (N).",
            },
        ],
    },
    # ── PROTECTION (bleues) ─────────────────────────────────────────────
    {
        "categorie": "Protection",
        "couleur": (80, 195, 215),
        "cartes": [
            {
                "nom": "Pare-Feu",
                "definition": "Barrière logicielle ou matérielle qui filtre le trafic réseau entrant et sortant.",
                "effet": "Protège contre le Cheval de Troie et les Spywares. Connecteurs Données (S/O) uniquement.",
            },
            {
                "nom": "Antivirus",
                "definition": "Logiciel de détection et suppression des programmes malveillants.",
                "effet": "Protège contre le Cheval de Troie et les Ransomwares. Connecteurs Électrique (N) et Données (O).",
            },
            {
                "nom": "VPN",
                "definition": "Réseau privé virtuel qui chiffre les communications.",
                "effet": "Protège contre les Ransomwares. Connecteurs Électrique (N) et Données (E).",
            },
            {
                "nom": "Mise à Jour",
                "definition": "Correctif logiciel qui comble les failles de sécurité connues.",
                "effet": "Protège contre les Spywares et l'Obsolescence programmée. Connecteurs Électrique (N/S) et Données (E).",
            },
            {
                "nom": "Hygiène Numérique",
                "definition": "Ensemble de bonnes pratiques pour maintenir la sécurité au quotidien.",
                "effet": "Protège contre l'Obsolescence programmée et les Fichiers corrompus. Connecteurs Données (N/O).",
            },
        ],
    },
    # ── MALUS (rouges) ──────────────────────────────────────────────────
    {
        "categorie": "Malus",
        "couleur": (195, 70, 70),
        "cartes": [
            {
                "nom": "Cheval de Troie",
                "definition": "Programme malveillant dissimulé dans un logiciel légitime.",
                "effet": "Déconnecte une carte de l'infrastructure d'un adversaire. Bloqué par Pare-Feu et Antivirus.",
            },
            {
                "nom": "Ransomware",
                "definition": "Logiciel qui chiffre vos données et exige une rançon.",
                "effet": "Déconnecte deux cartes d'un adversaire. Bloqué par VPN et Antivirus.",
            },
            {
                "nom": "Phishing",
                "definition": "Tentative d'hameçonnage par e-mail pour voler des identifiants.",
                "effet": "Déconnecte une carte d'un adversaire.",
            },
            {
                "nom": "DDOS",
                "definition": "Attaque par déni de service distribué qui sature un système.",
                "effet": "Chaque joueur doit défausser une carte infrastructure ou passer son prochain tour.",
            },
            {
                "nom": "Spyware",
                "definition": "Logiciel espion qui collecte vos données à votre insu.",
                "effet": "Déconnecte une carte d'un adversaire. Bloqué par Pare-Feu et Mise à Jour.",
            },
            {
                "nom": "Keylogger",
                "definition": "Programme qui enregistre toutes les frappes clavier.",
                "effet": "Remplacez une carte infrastructure de votre réseau avec la première carte de la pioche.",
            },
            {
                "nom": "Ingénierie Sociale",
                "definition": "Manipulation psychologique pour obtenir des informations confidentielles.",
                "effet": "Vous devez permuter deux cartes adjacentes de votre réseau.",
            },
            {
                "nom": "Obsolescence programmée",
                "definition": "Fin de vie planifiée d'un équipement, le rendant vulnérable.",
                "effet": "Déconnecte une carte d'un adversaire. Bloqué par Mise à Jour et Hygiène Numérique.",
            },
            {
                "nom": "Fichier corrompu",
                "definition": "Fichier endommagé pouvant rendre un système instable.",
                "effet": "Déconnecte une carte. Bloqué par Hygiène Numérique.",
            },
        ],
    },
    # ── BONUS / CAPACITÉS (verts) ───────────────────────────────────────
    {
        "categorie": "Bonus & Capacités",
        "couleur": (90, 185, 100),
        "cartes": [
            {
                "nom": "Sauvegarde locale",
                "definition": "Copie de sécurité stockée sur site.",
                "effet": "Placez cette carte sous une carte de votre réseau. Si cette carte est déconnectée, c'est la Sauvegarde qui est détruite à sa place.",
            },
            {
                "nom": "Sauvegarde système",
                "definition": "Instantané complet du système pour une restauration rapide.",
                "effet": "Sauvegardez une photo de votre réseau. Il sera restauré à son état actuel à la fin de votre prochain tour.",
            },
            {
                "nom": "Mise en Ligne",
                "definition": "Reconnexion d'un équipement tombé hors réseau.",
                "effet": "Une carte déconnectée de votre infrastructure est reconnectée immédiatement.",
            },
            {
                "nom": "Nettoyage de Disque",
                "definition": "Suppression des fichiers inutiles pour optimiser les performances.",
                "effet": "Piochez une carte infrastructure supplémentaire à la fin de votre tour.",
            },
            {
                "nom": "Extension du réseau",
                "definition": "Ajout de nouveaux équipements pour étendre la couverture.",
                "effet": "Vous pouvez jouer une carte infrastructure supplémentaire pendant ce tour.",
            },
            {
                "nom": "Assistant IA",
                "definition": "Intelligence artificielle qui optimise la gestion du réseau.",
                "effet": "Placez cette carte dans votre réseau. À chaque tour, piochez une carte supplémentaire.",
            },
            {
                "nom": "Compression des données",
                "definition": "Réduction de la taille des données pour optimiser le stockage.",
                "effet": "Regardez les 3 premières cartes de n'importe quelle pioche. Remettez les 3 cartes dans l'ordre que vous souhaitez.",
            },
            {
                "nom": "Overclocking",
                "definition": "Augmentation des performances d'un composant au-delà de ses limites.",
                "effet": "Si vous jouez une carte production, son effet est doublé.",
            },
            {
                "nom": "Restauration du système",
                "definition": "Retour à un état antérieur stable du système.",
                "effet": "Vous pouvez permuter deux cartes de votre réseau avec la première carte de la pioche.",
            },
            {
                "nom": "Bonne organisation",
                "definition": "Gestion rigoureuse des ressources informatiques.",
                "effet": "Trois cartes sont choisies au hasard en deux à jouer. Il est possible de choisir en deux à jouer. Diffusez les autres.",
            },
            {
                "nom": "Coup de chance",
                "definition": "Une opportunité inattendue tombe à pic.",
                "effet": "Trois cartes sont choisies au hasard en deux à jouer. Diffusez les autres.",
            },
            {
                "nom": "Protection des données",
                "definition": "Mise en conformité avec les réglementations de protection des données.",
                "effet": "Toutes les cartes de votre réseau sont immunisées contre les attaques jusqu'à votre prochain tour.",
            },
            {
                "nom": "RSSI",
                "definition": "Responsable de la Sécurité des Systèmes d'Information.",
                "effet": "Sort de mêlée : peut être joué pour parer à la prochaine attaque contre votre infrastructure.",
            },
            {
                "nom": "Correctif rapide",
                "definition": "Patch d'urgence appliqué pour colmater une faille critique.",
                "effet": "Répare immédiatement une carte déconnectée de votre réseau.",
            },
            {
                "nom": "Hotfix opérateur",
                "definition": "Correction déployée en urgence par l'opérateur réseau.",
                "effet": "Reconnecte une carte déconnectée et pioche une carte infrastructure.",
            },
        ],
    },
    # ── ÉVÉNEMENTS (violets) ────────────────────────────────────────────
    {
        "categorie": "Événements",
        "couleur": (160, 110, 210),
        "cartes": [
            {
                "nom": "Panne électrique",
                "definition": "Coupure de courant affectant l'ensemble du réseau.",
                "effet": "Tous les joueurs perdent une carte active de leur infrastructure.",
            },
            {
                "nom": "Fuite de données",
                "definition": "Divulgation non autorisée d'informations sensibles.",
                "effet": "Chaque joueur doit déconnecter une carte de son réseau.",
            },
            {
                "nom": "Maintenance critique",
                "definition": "Intervention d'urgence sur l'infrastructure.",
                "effet": "Aucun joueur ne peut poser de carte infrastructure pendant ce tour.",
            },
            {
                "nom": "Connexion",
                "definition": "Établissement soudain d'une nouvelle liaison réseau.",
                "effet": "Si vous possédez une carte 'Site' reliée à une carte 'Serveur', vous pouvez jouer une carte infrastructure immédiatement.",
            },
            {
                "nom": "Surcharge Courante",
                "definition": "Le réseau électrique est saturé par une consommation excessive.",
                "effet": "Le branchement n'a pas été vite : si votre carte 'Routeur' est reliée à une 'Base de données', elle est déconnectée.",
            },
            {
                "nom": "Attaque par phishing",
                "definition": "Campagne d'hameçonnage massive visant toute l'organisation.",
                "effet": "Vous cliquez sur un lien dans un e-mail qui vous propulse sur un site frauduleux. Vos cartes 'Serveur' sont perdues, puis 'Périphérique' est déconnectée.",
            },
            {
                "nom": "Attaque DDOS",
                "definition": "Saturation coordonnée du réseau par des milliers de requêtes.",
                "effet": "Toutes les cartes sont attaquées par un hacker. Tout contact avec elles déconnecte vos cartes 'Base de données'.",
            },
            {
                "nom": "Toujours à jour",
                "definition": "Une mise à jour automatique se déclenche au pire moment.",
                "effet": "Si vous possédez une carte 'Smartphone' sans 'Mise à Jour', elle est déconnectée.",
            },
            {
                "nom": "Café renversé",
                "definition": "Accident domestique aux conséquences désastreuses.",
                "effet": "Votre clavier est perdu, dans le lavabo. Vos cartes 'PC' sont déconnectées.",
            },
            {
                "nom": "Politique",
                "definition": "Décision administrative impactant le système d'information.",
                "effet": "Les DSI revoient le budget du département. Vous ne pouvez pas piocher de carte infrastructure ce tour.",
            },
            {
                "nom": "Réchauffement climatique",
                "definition": "La chaleur excessive surchauffe les équipements.",
                "effet": "Vous avez laissé votre ordi 'en veille'. Si vous avez au moins 3 cartes 'PC', deux d'entre elles sont déconnectées.",
            },
            {
                "nom": "Canard en plastique",
                "definition": "Célèbre technique de débogage par explication à voix haute... ou intrus indésirable.",
                "effet": "Se place à un endroit libre du réseau d'un joueur. Aucun joueur ne peut finir la partie avec le canard, sauf s'il possède l'objectif 'Le Fou'.",
            },
        ],
    },
    # ── OBJECTIFS ───────────────────────────────────────────────────────
    {
        "categorie": "Objectifs",
        "couleur": (220, 200, 120),
        "cartes": [
            {
                "nom": "Le Fou",
                "definition": "Objectif secret permettant une victoire alternative.",
                "effet": "+5 pts. Vous pouvez terminer la partie avec une infrastructure de 8 cartes si vous possédez le Canard en plastique dans votre réseau.",
            },
            {
                "nom": "Online",
                "definition": "Spécialisation dans les services en ligne.",
                "effet": "+5 pts. Ayez 4 interfaces en ligne (Site, Boîte Mail, Logiciel, Cloud) actives dans votre réseau.",
            },
            {
                "nom": "Un bon réseau",
                "definition": "Infrastructure équilibrée et robuste.",
                "effet": "+5 pts. Ayez au moins un Serveur et un Routeur actifs dans votre réseau.",
            },
            {
                "nom": "Ingénieur informaticien",
                "definition": "Maîtrise technique complète de l'infrastructure.",
                "effet": "+5 pts. Ayez un PC, une Base de données et un Point Réseau actifs dans votre réseau.",
            },
            {
                "nom": "Protection avant tout",
                "definition": "Priorité absolue donnée à la cybersécurité.",
                "effet": "+5 pts. Ayez les 5 types de cartes protection (Pare-Feu, Antivirus, VPN, Mise à Jour, Hygiène Numérique) actives.",
            },
            {
                "nom": "Sécuriser deux routeurs",
                "definition": "Redondance réseau pour une disponibilité maximale.",
                "effet": "+5 pts. Ayez 2 cartes Routeur actives dans votre réseau.",
            },
            {
                "nom": "Déployer une protection",
                "definition": "Mise en place d'un premier rempart de sécurité.",
                "effet": "+5 pts. Ayez au moins une carte de protection active dans votre réseau.",
            },
            {
                "nom": "Réseau robuste",
                "definition": "Infrastructure solide capable de résister aux attaques.",
                "effet": "+5 pts. Maintenez au moins 6 cartes actives dans votre réseau.",
            },
            {
                "nom": "Sécuriser une base de données",
                "definition": "Protection des données critiques de l'organisation.",
                "effet": "+5 pts. Ayez au moins une carte Base de donnée active dans votre réseau.",
            },
        ],
    },
]