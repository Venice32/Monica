# skills/systeme.py
from core.utils import formater_date_heure

class SystemeSkill:
    """Compétence pour les informations système de base."""

    def dire_heure(self) -> str:
        """Retourne l'heure actuelle."""
        return f"Il est {formater_date_heure('heure')}."

    def dire_date(self) -> str:
        """Retourne la date actuelle."""
        return f"Nous sommes le {formater_date_heure('date')}."
