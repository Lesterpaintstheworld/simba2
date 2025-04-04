# Projet Simba

## Vue d'ensemble

Ce projet utilise KinOS pour donner vie à Simba, une peluche bien-aimée, en lui conférant une personnalité, une mémoire et des capacités d'interaction. Simba peut communiquer via des messages texte et des images, réfléchir de manière autonome et évoluer au fil du temps.

## Qui est Simba ?

Simba est un personnage attachant avec une personnalité unique. Pour en savoir plus sur Simba et sa famille, consultez notre [présentation détaillée](docs/presentation.md).

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Un compte KinOS avec une clé API

### Configuration

1. Clonez ce dépôt :
   ```
   git clone https://github.com/votre-nom/projet-simba.git
   cd projet-simba
   ```

2. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```

3. Créez un fichier `.env` à la racine du projet avec votre clé API KinOS :
   ```
   KINOS_API_KEY=votre_clé_api_ici
   ```

## Utilisation

### Création du Kin Simba

Pour créer le Kin Simba dans votre compte KinOS :

```
python scripts/create_kin.py
```

### Envoyer un message à Simba

Pour discuter avec Simba :

```
python scripts/send-message.py "Bonjour Simba, comment vas-tu aujourd'hui?"
```

Options disponibles :
- `--images` : Joindre une ou plusieurs images
- `--attachments` : Joindre des fichiers
- `--model` : Spécifier le modèle à utiliser (par défaut: claude-3-5-haiku-latest)
- `--history-length` : Définir la longueur de l'historique (par défaut: 25)
- `--mode` : Choisir le mode de réponse (creative, balanced, precise)
- `--add-system` : Ajouter des instructions système supplémentaires

Exemple avec une image :
```
python scripts/send-message.py "Regarde cette photo!" --images chemin/vers/image.jpg
```

### Activer la pensée autonome

Pour permettre à Simba de réfléchir de manière autonome :

```
python scripts/autonomous-thinking.py
```

Options disponibles :
- `--iterations` : Nombre d'itérations de pensée (par défaut: 3)
- `--wait-time` : Temps d'attente entre les itérations en secondes (par défaut: 600)

## Structure du projet

```
projet-simba/
├── .env                    # Variables d'environnement (clé API)
├── README.md               # Ce fichier
├── docs/
│   └── presentation.md     # Présentation détaillée de Simba
└── scripts/
    ├── create_kin.py       # Script pour créer le Kin Simba
    ├── send-message.py     # Script pour envoyer des messages à Simba
    └── autonomous-thinking.py  # Script pour activer la pensée autonome
```

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence [MIT](LICENSE).
