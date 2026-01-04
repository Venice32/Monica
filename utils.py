# core/utils.py
import datetime
import pytz

def formater_date_heure(formatage: str = "complet") -> str:
    """Retourne la date et l'heure actuelles formatées."""
    fuseau_paris = pytz.timezone('Europe/Paris')
    maintenant = datetime.datetime.now(fuseau_paris)

    if formatage == "heure":
        return maintenant.strftime("%H:%M")
    elif formatage == "date":
        return maintenant.strftime("%d %B %Y")
    else:  # formatage == "complet"
        return maintenant.strftime("%A %d %B %Y, %H:%M")
