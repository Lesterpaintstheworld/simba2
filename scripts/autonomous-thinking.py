import requests
import json
import os
from dotenv import load_dotenv
import argparse

# Charger les variables d'environnement
load_dotenv()

def trigger_autonomous_thinking(blueprint_id, kin_id, iterations=3, wait_time=600):
    """
    Déclenche le processus de pensée autonome pour un Kin spécifique.
    
    Args:
        blueprint_id (str): L'ID du blueprint
        kin_id (str): L'ID du Kin
        iterations (int, optional): Nombre d'itérations de pensée. Par défaut à 3.
        wait_time (int, optional): Temps d'attente entre les itérations en secondes. Par défaut à 600 (10 minutes).
    
    Returns:
        dict: La réponse de l'API
    """
    # URL de l'API
    api_url = f"https://api.kinos-engine.ai/v2/blueprints/{blueprint_id}/kins/{kin_id}/autonomous_thinking"
    
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
        "iterations": iterations,
        "wait_time": wait_time
    }
    
    # Effectuer la requête POST
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Lever une exception si la requête a échoué
        
        # Analyser la réponse JSON
        result = response.json()
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails de l'erreur: {e.response.text}")
        return None

if __name__ == "__main__":
    # Configurer les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Déclencher la pensée autonome pour Simba")
    parser.add_argument("--iterations", type=int, default=3, help="Nombre d'itérations de pensée")
    parser.add_argument("--wait-time", type=int, default=600, help="Temps d'attente entre les itérations en secondes")
    args = parser.parse_args()
    
    # Paramètres pour Simba
    blueprint_id = "simba"
    kin_id = "simba"
    
    # Déclencher la pensée autonome
    result = trigger_autonomous_thinking(
        blueprint_id=blueprint_id,
        kin_id=kin_id,
        iterations=args.iterations,
        wait_time=args.wait_time
    )
    
    # Afficher le résultat
    if result:
        print(json.dumps(result, indent=2))
        print(f"Pensée autonome démarrée pour {blueprint_id}/{kin_id}")
        print(f"Nombre d'itérations: {result.get('iterations', args.iterations)}")
        print(f"Temps d'attente entre les itérations: {result.get('wait_time', args.wait_time)} secondes")
    else:
        print("Échec du démarrage de la pensée autonome")
