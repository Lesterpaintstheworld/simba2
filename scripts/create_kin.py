import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def create_kin(blueprint_id, kin_name, template_override=None):
    """
    Crée un nouveau kin pour un blueprint spécifique.
    
    Args:
        blueprint_id (str): L'ID du blueprint
        kin_name (str): Le nom du nouveau kin
        template_override (str, optional): Template à utiliser pour le kin
    
    Returns:
        dict: La réponse de l'API contenant les informations du kin créé
    """
    # URL de l'API
    api_url = f"https://api.kinos-engine.ai/v2/blueprints/{blueprint_id}/kins"
    
    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv("KINOS_API_KEY")
    
    if not api_key:
        raise ValueError("La clé API KINOS_API_KEY n'est pas définie dans les variables d'environnement")
    
    # Préparer les headers avec l'authentification
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Préparer le corps de la requête
    payload = {
        "name": kin_name
    }
    
    # Ajouter le template_override s'il est spécifié
    if template_override:
        payload["template_override"] = template_override
    
    # Effectuer la requête POST
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Lever une exception si la requête a échoué
        
        # Analyser la réponse JSON
        result = response.json()
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la création du kin: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails de l'erreur: {e.response.text}")
        return None

if __name__ == "__main__":
    # Paramètres pour Simba
    blueprint_id = "simba"
    kin_name = "simba"
    
    # Créer le kin Simba
    result = create_kin(blueprint_id, kin_name)
    
    # Afficher le résultat
    if result:
        print(json.dumps(result, indent=2))
        print(f"Kin '{kin_name}' créé avec succès!")
        print(f"ID du kin: {result.get('id')}")
        print(f"Blueprint: {result.get('blueprint_id')}")
        print(f"Créé le: {result.get('created_at')}")
        print(f"Statut: {result.get('status')}")
    else:
        print("Échec de la création du kin")
