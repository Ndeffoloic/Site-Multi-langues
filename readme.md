
#30 juin 2024 05:45 UTC+2 | Création du multilang_site
#Candidat: Loïc NEMBOT, étudiant en 4A IA2R à Polytech Nancy
#Ce fichier README contient les instructions pour lancer le projet après avoir cloné le dépôt.


## Prérequis
Tous les modules 

## Installation
1. Clonez le dépôt sur votre machine en utilisant la commande suivante :
    ```
    git clone https://github.com/Ndeffoloic/Site-Multi-langues
    ```

2. Accédez au répertoire du projet :
    ```
    cd votre-depot
    ```

3. créer un environnement virutel et activez le 

4. Installez les dépendances du projet en exécutant la commande suivante :
    ```
    pip install -r requirements.txt
    ```

## Lancement du projet
Pour lancer le projet, vous pouvez  : 
aller à l'adresse suivante : 
```
https://multilang-site-wguu.onrender.com

```

ou exécuter la commande suivante :
```
python manage.py runserver
```

## Etapes de réalisation : 

- Création de l'environnement virtuel multilang_site
- Activation de l'environnement virtuel
- Initialisation du répertoire git
- Création du projet Django
- Premier démarrage du serveur
- Remplissage du fichier .gitignore pour ignorer les fichiers de configuration de Django dans les commits
- Création de l'app main
- Premières migrations étant donné que je garde le SGBD SQLite3
- Premier commit et premier push vers le répertoire distant
- Création des modèles et Vue de Base
- Installation de Bootstrap dans le dossier "static"
- Création des templates "base.html" et "js.html"
- Modification de settings.py pour gérer l'internationalisation
- Téléchargement et installation de GNU gettext
- Redémarrage de l'ordinateur
- Ajout de gettext à ma variable d'environnement PATH
- Premier déploiement sur render.com
- Deuxième déploiement sur render.com en utilisant PostgreSQL
- Création d'un super utilisateur pour ajouter des articles dans la base de données
- Ajout de 5 articles dans la base de données grâce à BingAi
- Vérification de la possibilité d'ajouter les articles depuis la page admin et depuis la page dédiée à la création des articles
- Création d'un bot sur PoeChatgpt
- Tentative de connexion du bot à l'application, mais les retours sont indéfinis
- Utilisation de l'API de Chatgpt et création d'une clé d'API
- Difficultés pour obtenir la réponse de Chatgpt, implémentation des fonctions de login/logout et register  en attendant
- Essai d'implémentation du bot framework de Azure : Echec. 
-J'ai utilisé Bing AI tout le long pour corriger certains bugs et m'aider lorsque je voulais implémenter le bot / l'api d'Azure. 

Temps de réalisation : J'ai commencé le site le 29 juin, mais après avoir rencontré certaines erreurs, j'ai abandonné l'ancienne version pour reprendre celle que je vous soumets. Ainsi, j'ai réalisé le projet ci-joint en 8 heures et l'ancienne version en deux heures.


Petites précisions
J'avais fait mon emploi du temps de cette semaine en allouant le weekend à la réalisation de ce site, et ce, avant que vous ne précisiez que nous devons finir le test avant le 30 juin. De ce fait, j'ai fini le test le 30 juin.
