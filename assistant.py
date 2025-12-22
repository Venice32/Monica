# core/assistant.py
import json
from skills.meteo import MeteoSkill
from skills.systeme import SystemeSkill
from config import FICHIER_RAPPELS

class Assistant:
    """Classe principale de l'assistant Monica."""

    def __init__(self):
        print("Initialisation de Monica, votre assistant personnel...")
        self.meteo_skill = MeteoSkill()
        self.systeme_skill = SystemeSkill()
        self.rappels = self._charger_rappels()

    def _charger_rappels(self):
        """Charge les rappels depuis un fichier JSON."""
        try:
            with open(FICHIER_RAPPELS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def traiter_commande(self, commande: str) -> str:
        """Analyse la commande de l'utilisateur et exécute l'action appropriée."""
        commande = commande.lower().strip()

        if "quel temps" in commande or "météo" in commande:
            # Extraction simple du nom de la ville
            if "à" in commande:
                ville = commande.split("à")[-1].strip()
                return self.meteo_skill.obtenir_meteo(ville)
            else:
                return self.meteo_skill.obtenir_meteo()

        elif "heure" in commande:
            return self.systeme_skill.dire_heure()

        elif "date" in commande:
            return self.systeme_skill.dire_date()
            
        elif "rappel" in commande:
            # Logique de rappel simplifiée
            return "La gestion des rappels est une fonctionnalité en cours de développement."

        elif "aide" in commande or "help" in commande:
            return self.afficher_aide()

        else:
            return "Désolé, je n'ai pas compris. Dites 'aide' pour voir les commandes disponibles."

    def afficher_aide(self) -> str:
        """Affiche une liste des commandes disponibles."""
        aide = (
            "Voici les commandes que je peux exécuter :\n"
            "- 'Quelle heure est-il ?' ou 'Donne-moi l'heure'\n"
            "- "Quelle date sommes-nous ?' ou 'Donne-moi la date'\n"
            "- 'Quel temps fait-il à [ville] ?' ou 'Météo à [ville]'\n"
            "- 'Aide' pour afficher ce message."
        )
        return aide
