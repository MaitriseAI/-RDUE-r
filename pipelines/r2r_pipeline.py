"""
title: Hello World Pipeline
author: Gemini
date: 2025-06-18
version: 1.0
license: MIT
description: A very simple pipeline that ignores user input and always returns 'Hello world'. Perfect for testing the basic structure.
requirements:
"""

# On importe les types nécessaires pour la signature de la fonction `pipe`
# C'est une bonne pratique, même si on ne les utilise pas tous ici.
from typing import List, Union, Generator, Iterator

class Pipeline:
    def __init__(self):
        # Cette méthode est appelée une seule fois lors de l'initialisation du pipeline.
        # Pour ce pipeline, nous n'avons rien à préparer.
        # On ajoute un print pour voir dans les logs que le pipeline est bien chargé.
        print("Pipeline 'Hello World' a été initialisé.")
        pass

    async def on_startup(self):
        # Cette fonction est appelée au démarrage du serveur.
        # Utile pour des tâches de préparation plus longues. Ici, on n'en a pas besoin.
        pass
    
    async def on_shutdown(self):
        # Appelée à l'arrêt du serveur.
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> str:
        """
        C'est le cœur du pipeline. Cette méthode est appelée à chaque fois
        qu'un utilisateur envoie un message.
        """
        
        # On peut afficher le message de l'utilisateur dans les logs pour prouver qu'on le reçoit.
        print(f"Message reçu de l'utilisateur : '{user_message}'. Je vais l'ignorer.")
        
        # Peu importe les paramètres d'entrée, on retourne toujours la même chose.
        return "Hello world"
