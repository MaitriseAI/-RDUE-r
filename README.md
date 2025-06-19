# Projet RAG avec Open WebUI et Serveur Dédié

Ce projet met en place une solution de Retrieval-Augmented Generation (RAG) utilisant Open WebUI comme interface utilisateur et un serveur Python dédié pour la logique RAG avec LangChain et OpenAI.

## Architecture

Le projet utilise Docker Compose pour orchestrer 3 services :
* `openwebui`: L'interface web pour interagir avec l'agent.
* `pipelines`: Un service léger qui reçoit les requêtes de l'UI et les transmet au serveur RAG.
* `rag_server`: Un serveur Flask qui contient la logique RAG, charge un document local, et communique avec l'API d'OpenAI.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :
* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)
* [Git](https://git-scm.com/downloads)

## Installation et Lancement

1.  **Clonez le dépôt :**
    ```bash
    git clone [https://github.com/MaitriseAI/Test1.git](https://github.com/MaitriseAI/Test1.git)
    cd Test1
    ```

2.  **Configurez les variables d'environnement :**
    Copiez le fichier d'exemple `.env.example` pour créer votre propre fichier de configuration `.env`.
    ```bash
    cp .env.example .env
    ```
    Ouvrez ensuite le fichier `.env` et insérez votre clé API OpenAI.

3.  **Ajoutez votre document :**
    Placez le document PDF que vous souhaitez utiliser dans le dossier `rag_server/`. Assurez-vous que le nom du fichier correspond à celui spécifié dans `rag_server/app.py` (actuellement `mon_document.pdf`).

4.  **Lancez l'application :**
    Utilisez Docker Compose pour construire les images et démarrer les conteneurs.
    ```bash
    docker compose up --build -d
    ```
    Le premier lancement peut prendre plusieurs minutes, le temps de télécharger les images et d'installer les dépendances.

## Utilisation

1.  Ouvrez votre navigateur et allez sur `http://localhost:8080`.
2.  Créez un compte administrateur lors de la première visite.
3.  Dans l'interface, sélectionnez le pipeline **"RAG API Caller Pipeline"**.
4.  Commencez à poser des questions sur votre document !

# Projet RAG avec Open WebUI et Serveur Dédié

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-b546f2?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

Ce projet met en place une solution de **R**etrieval-**A**ugmented **G**eneration (RAG) utilisant Open WebUI comme interface et un serveur Python dédié pour la logique RAG. Il permet de "discuter" avec un document local en utilisant la puissance des modèles OpenAI.

## Architecture

Le projet est entièrement conteneurisé avec Docker Compose et s'articule autour de 3 services principaux :

```
[Utilisateur] <--> [Open WebUI] <--> [Pipeline Intermédiaire] <--> [Serveur RAG] <--> [API OpenAI]
```

* **`openwebui`**: L'interface web pour interagir avec l'agent.
* **`pipelines`**: Un service Open WebUI qui agit comme un simple client HTTP. Il reçoit la question de l'utilisateur et la transmet au `rag_server`.
* **`rag_server`**: Un serveur API (basé sur Flask) qui contient toute la logique RAG. Au démarrage, il charge un document local, le traite avec LangChain et OpenAI, et expose une API pour répondre aux questions.

# PLUS DE DETAILS ICI

## Prérequis

Avant de commencer, assurez-vous d'avoir installé sur votre machine :
* [Docker](https://www.docker.com/get-started) & Docker Compose
* [Git](https://git-scm.com/downloads)
* Un compte OpenAI et une clé API valide.

## Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone [https://github.com/MaitriseAI/Test1.git](https://github.com/MaitriseAI/Test1.git)
    cd Test1
    ```

2.  **Créez votre fichier de configuration :**
    Copiez le modèle `.env.example` pour créer votre propre fichier `.env`. C'est ce fichier qui contiendra vos secrets.
    ```bash
    cp .env.example .env
    ```

3.  **Lancez l'application :**
    Utilisez Docker Compose pour construire les images et démarrer les conteneurs.
    ```bash
    docker compose up --build -d
    ```
    Le premier lancement peut prendre plusieurs minutes, le temps de télécharger les images de base et d'installer toutes les dépendances Python.

## Configuration

Pour que l'application fonctionne, deux configurations sont nécessaires après l'installation.

#### 1. Configuration de la Clé API

* Ouvrez le fichier `.env` que vous venez de créer.
* Remplacez `VOTRE_CLE_API_OPENAI_ICI` par votre véritable clé API OpenAI.
* Ce fichier est ignoré par Git et restera privé sur votre machine.

#### 2. Configuration du Document Source

* Placez le document PDF que vous souhaitez utiliser dans le dossier `rag_server/`.
* Par défaut, le serveur est configuré pour charger un fichier nommé `mon_document.pdf`.
* Si votre fichier a un nom différent, ouvrez `rag_server/app.py` et modifiez la ligne suivante :
    ```python
    # Ligne à modifier si votre document a un autre nom
    document_path = "./votre_autre_document.pdf"
    ```
* Après avoir modifié la configuration, n'oubliez pas de relancer les services : `docker compose up -d --build`.

## Utilisation

Une fois les conteneurs démarrés, suivez ces étapes pour interagir avec votre RAG.

#### 1. Accès et Configuration d'Open WebUI

1.  Ouvrez votre navigateur et allez sur `http://localhost:8080`.
2.  Lors de votre première visite, Open WebUI vous demandera de créer un compte administrateur. Créez ce compte.
3.  Une fois connecté, vous arrivez sur l'interface de chat principale.

#### 2. Sélection du Pipeline RAG

Pour que vos questions soient envoyées à votre serveur RAG, vous devez sélectionner le bon pipeline.

1.  En haut de l'écran de chat, cliquez sur le menu déroulant qui affiche le modèle (par défaut, il peut afficher "Ollama").
2.  Dans la liste qui apparaît, cherchez et sélectionnez le pipeline nommé **"RAG API Caller Pipeline"**. Le nom affiché correspond au `title` défini dans le fichier `pipelines/pipeline_rag_api_call.py`.
3.  Une fois sélectionné, le nom du modèle en haut de l'écran doit indiquer "RAG API Caller Pipeline".

Vous êtes maintenant prêt ! Chaque message que vous enverrez sera traité par votre système RAG complet.

## Dépannage (Troubleshooting)

* **Erreur : "Impossible de contacter le serveur RAG"**
    Cela signifie que le conteneur `pipelines` ne peut pas joindre le `rag_server`. La première chose à faire est de vérifier les logs du serveur RAG pour voir s'il a démarré correctement :
    ```bash
    docker compose logs rag_server
    ```
    Cherchez des messages d'erreur (problème de clé API, document non trouvé, etc.).

* **Mettre à jour après une modification du code**
    * Si vous modifiez le code du `rag_server` ou ses dépendances, reconstruisez l'image : `docker compose up --build -d`.
    * Si vous ne modifiez que le code du `pipelines` (qui est dans un volume monté), un simple redémarrage suffit : `docker compose restart pipelines`.
