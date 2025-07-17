# Maitrise.ai – Agent RAG Avancé

**Maitrise.ai** est un système avancé de **Retrieval-Augmented Generation (RAG)** conçu pour interagir dynamiquement avec des documents PDF locaux. Grâce à une architecture conteneurisée robuste et à une interface intuitive via **Open WebUI**, il permet d’interroger intelligemment vos documents comme si vous dialoguiez avec un expert.

Ce projet se distingue par l’intégration de techniques de recherche sémantique avancées pour garantir la **pertinence**, la **précision** et la **richesse contextuelle** des réponses.

---

## ✨ Fonctionnalités Clés

🔍 **Retrieval multi-niveau** :
- **Parent Document Retriever** : segmentation fine des documents tout en conservant un contexte riche pour le modèle.
- **Cross-Encoder Re-Ranking** : re-classement des résultats pour ne retenir que les passages les plus pertinents.
- **Multi-Query Expansion** : reformulation intelligente des questions pour ne rien laisser passer.

🖥️ **Interface Web Moderne** :
- Interface via Open WebUI pour une expérience utilisateur fluide et personnalisable.

⚙️ **Architecture Modulaire** :
- Architecture conteneurisée avec Docker Compose, facilitant l’installation, la scalabilité et la maintenance.

---

## 🏗️ Architecture Technique

```text
[Utilisateur]
     ⬇️
[🌐 Open WebUI] <==> [🔗 Pipeline] <==> [🧠 Serveur RAG] <==> [🤖 API OpenAI]
```

- **openwebui** : Interface utilisateur graphique basée sur Open WebUI.  
- **pipelines** : Service pont qui connecte l’UI avec le serveur RAG.  
- **rag_server** : Serveur Flask contenant la logique RAG (prétraitement, recherche, communication avec OpenAI).  

---

## 🛠️ Prérequis

Avant de commencer, veuillez installer les éléments suivants :

- [Git](https://git-scm.com/)
- [Docker & Docker Compose](https://www.docker.com/)
- Un compte [OpenAI](https://platform.openai.com/) avec une **clé API valide**

---

## 💻 Installation Locale (Windows, macOS, Linux)

### 1. Cloner le dépôt

```bash
git clone https://github.com/MaitriseAI/-RDUE-r.git
cd -RDUE-r
```

### 2. Configurer les variables d’environnement

```bash
cp .env.example .env
```

- Ouvrez le fichier `.env` avec un éditeur de texte.
- Remplacez la valeur de `OPENAI_API_KEY` par votre clé API OpenAI.

### 3. Ajouter votre document PDF

- Placez votre fichier PDF dans le dossier `rag_server/`.
- Par défaut, le fichier attendu est `votre_document.pdf`.

Pour utiliser un autre nom de fichier, modifiez la ligne suivante dans `rag_server/app.py` :

```python
# Ligne 20
document_path = "./nouveau_nom_de_document.pdf"
```

### 4. Lancer l’application

```bash
docker compose up --build -d
```

- `--build` : reconstruit les images à partir du code local.
- `-d` : démarre les conteneurs en arrière-plan (mode "detached").

> ℹ️ Le premier lancement peut prendre quelques minutes pour télécharger les images et installer les dépendances.

---

## 🚀 Utilisation

1. Ouvrez votre navigateur à l’adresse : [http://localhost:8081](http://localhost:8081)
2. Créez un compte utilisateur local si c’est votre première visite.
3. Cliquez sur **"Select a Model"** en haut de l’interface.
4. Sélectionnez **"Agent RAG Avancé"**.
5. Interrogez votre document PDF librement !

---

## ☁️ Déploiement sur un Serveur (ex : Scaleway)

### 1. Préparer l’instance

- Créez une instance (ex. DEV1-S ou DEV1-M) sur [Scaleway](https://www.scaleway.com/) ou tout autre fournisseur cloud.
- Connectez-vous via SSH à votre serveur distant.

### 2. Installer Git & Docker

```bash
sudo apt-get update
sudo apt-get install -y git docker.io docker-compose-v2
```

### 3. Déployer l’application

```bash
git clone https://github.com/MaitriseAI/-RDUE-r.git
cd -RDUE-r

cp .env.example .env
nano .env  # ou utilisez vim

sudo docker compose up --build -d
```

### 4. Accéder à l’interface

- Accédez à : `http://<IP_DE_VOTRE_SERVEUR>:8080`

> ⚠️ **Sécurité recommandée** :  
> Pour un usage en production, utilisez un **reverse proxy** comme **Nginx** ou **Caddy**.  
> Cela vous permettra de :
> - Gérer les certificats SSL (HTTPS)
> - Sécuriser les accès avec authentification
> - Associer un **nom de domaine personnalisé**

---

## 🧰 Dépannage

### Vérifier les logs du serveur RAG

```bash
docker compose logs rag_server
```

### Reprendre après une modification du code Python

```bash
docker compose up --build -d
```

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.  
Vous êtes libre de l’utiliser, le modifier et le distribuer sous les termes de cette licence.  
Voir le fichier [`LICENSE`](LICENSE) pour plus d’informations.

---

## 🤝 Contribuer

Les contributions sont les bienvenues !  
N’hésitez pas à :

- Ouvrir une **issue** pour signaler un bug ou proposer une amélioration.
- Créer une **pull request** pour soumettre des changements.

---

## 📬 Contact

Pour toute question, suggestion ou retour :

- **📧 Email** : contact@maitrise.ai  
- **🌐 Site Web** : [www.maitrise.ai](https://www.maitrise.ai)

---
