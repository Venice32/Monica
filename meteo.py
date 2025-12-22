# skills/meteo.py
import requests
from core.utils import formater_date_heure
from config import CLE_API_METEO, VILLE_PAR_DEFAUT, LANGUE_PAR_DEFAUT

class MeteoSkill:
    """Compétence pour obtenir les informations météorologiques."""

    def __init__(self):
        self.api_key = CLE_API_METEO
        self.ville = VILLE_PAR_DEFAUT
        self.langue = LANGUE_PAR_DEFAUT
        self.url_base = "http://api.openweathermap.org/data/2.5/weather"

    def obtenir_meteo(self, ville: str = None) -> str:
        """Récupère et formate les informations météo pour une ville donnée."""
        ville_cible = ville or self.ville
        if not self.api_key or self.api_key == "VOTRE_CLÉ_API_OPENWEATHERMAP":
            return "La clé API pour la météo n'est pas configurée. Veuillez vérifier le fichier config.py."

        params = {
            'q': ville_cible,
            'appid': self.api_key,
            'lang': self.langue,
            'units': 'metric'  # Pour obtenir les températures en Celsius
        }

        try:
            reponse = requests.get(self.url_base, params=params)
            reponse.raise_for_status()  # Lève une exception si la requête échoue
            donnees = reponse.json()

            description = donnees['weather'][0]['description'].capitalize()
            temperature = donnees['main']['temp']
            ressenti = donnees['main']['feels_like']
            humidite = donnees['main']['humidity']
            ville_nom = donnees['name']
            pays = donnees['sys']['country']

            message = (
                f"À {ville_nom} ({pays}), le temps est {description}.\n"
                f"Température : {temperature}°C (ressenti {ressenti}°C).\n"
                f"Humidité : {humidite}%."
            )
            return message

        except requests.exceptions.RequestException as e:
            return f"Erreur de connexion à l'API météo : {e}"
        except KeyError:
            return f"Impossible de trouver les informations météo pour '{ville_cible}'. Vérifiez le nom de la ville."
