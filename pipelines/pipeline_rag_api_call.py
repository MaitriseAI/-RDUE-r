"""
title: Agent RAG Avancé (avec Sources)
author: VotreNom
date: 2025-07-17
version: 2.0
license: MIT
description: Un pipeline qui appelle notre serveur RAG avancé et formate la réponse avec ses sources.
requirements: requests
"""

import requests
import os

class Pipeline:
    def __init__(self):
        # L'URL de notre serveur RAG. On utilise le nom du service docker-compose.
        self.rag_server_url = "http://rag_server:5000/ask_rag"
        print(f"Pipeline '{self.__class__.__name__}' initialisé. Il appellera {self.rag_server_url}")

    def pipe(self, user_message: str, **kwargs) -> str:
        print(f"Pipeline a reçu '{user_message}'. Transfert au serveur RAG.")

        try:
            # On envoie une requête POST avec la question en JSON
            response = requests.post(self.rag_server_url, json={"question": user_message})
            response.raise_for_status() # Lève une erreur si le statut n'est pas 200

            # On extrait les données complètes du JSON retourné par le serveur
            data = response.json()
            answer = data.get("answer", "Le serveur n'a pas renvoyé de réponse.")
            sources = data.get("sources", [])

            # --- FORMATAGE DE LA RÉPONSE POUR L'AFFICHAGE ---
            
            # On commence par la réponse textuelle du LLM
            final_response = answer

            # S'il y a des sources, on les ajoute dans une section dédiée en Markdown
            if sources:
                # On s'assure de ne pas avoir de doublons dans les sources
                unique_sources = []
                seen = set()
                for source in sources:
                    # Crée un identifiant unique pour chaque source (nom du fichier + page)
                    identifier = (source.get('source'), source.get('page'))
                    if identifier not in seen:
                        unique_sources.append(source)
                        seen.add(identifier)

                # On ajoute un séparateur et un titre pour la section des sources
                final_response += "\n\n---\n**Sources :**\n"
                # On crée une liste à puces pour chaque source
                for src in unique_sources:
                    source_name = src.get("source", "Inconnue")
                    page_number = src.get("page", "N/A")
                    final_response += f"- {source_name} (Page {page_number})\n"
            
            return final_response

        except requests.exceptions.RequestException as e:
            print(f"Erreur de communication avec le serveur RAG : {e}")
            return "Erreur : Impossible de contacter le serveur RAG."
        except Exception as e:
            print(f"Une erreur inattendue est survenue dans le pipeline : {e}")
            return "Une erreur inattendue est survenue."

