import requests
import json
import os
import argparse
import base64
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def analyze_kin(blueprint_id, kin_id, message, images=None, model="claude-3-5-haiku-latest", add_system=None):
    """
    Analyse un message avec Claude sans l'enregistrer dans l'historique de conversation.
    
    Args:
        blueprint_id (str): L'ID du blueprint
        kin_id (str): L'ID du Kin
        message (str): Le message à analyser
        images (list, optional): Liste des chemins d'images à envoyer
        model (str, optional): Le modèle à utiliser. Par défaut "claude-3-5-haiku-latest"
        add_system (str, optional): Instructions système supplémentaires
    
    Returns:
        dict: La réponse de l'API
    """
    # URL de l'API
    api_url = f"https://api.kinos-engine.ai/v2/blueprints/{blueprint_id}/kins/{kin_id}/analysis"
    
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
        "message": message,
        "model": model
    }
    
    # Ajouter les instructions système si spécifiées
    if add_system:
        payload["addSystem"] = add_system
    
    # Traiter les images si spécifiées
    if images:
        processed_images = []
        for image_path in images:
            try:
                with open(image_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    # Déterminer le type MIME en fonction de l'extension
                    ext = os.path.splitext(image_path)[1].lower()
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp'
                    }.get(ext, 'image/jpeg')
                    processed_images.append(f"data:{mime_type};base64,{img_data}")
            except Exception as e:
                print(f"Erreur lors du traitement de l'image {image_path}: {e}")
        
        if processed_images:
            payload["images"] = processed_images
    
    # Effectuer la requête POST
    try:
        print(f"Envoi de la requête d'analyse à {api_url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(api_url, headers=headers, json=payload)
        
        print(f"Code de statut HTTP: {response.status_code}")
        print(f"Réponse brute: {response.text}")
        
        response.raise_for_status()  # Lever une exception si la requête a échoué
        
        # Analyser la réponse JSON
        result = response.json()
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'analyse: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails de l'erreur: {e.response.text}")
        return None

if __name__ == "__main__":
    # Configurer les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Analyser l'état émotionnel de Simba")
    parser.add_argument("--message", default="Analyse l'état émotionnel actuel de Simba. Comment se sent-il? Quelles sont ses préoccupations actuelles? Quels sont ses désirs et ses besoins?", 
                        help="Le message d'analyse à envoyer")
    parser.add_argument("--images", nargs="+", help="Chemins des images à envoyer")
    parser.add_argument("--model", default="claude-3-5-haiku-latest", help="Modèle à utiliser")
    parser.add_argument("--add-system", default="Analyse en profondeur l'état émotionnel actuel de Simba en te basant sur ses conversations récentes, ses souvenirs et sa personnalité. Identifie ses émotions dominantes, ses préoccupations, ses désirs et ses besoins. Fournis une analyse psychologique détaillée mais accessible.", 
                        help="Instructions système supplémentaires")
    args = parser.parse_args()
    
    # Paramètres pour Simba
    blueprint_id = "simba"
    kin_id = "simba"
    
    # Analyser l'état émotionnel de Simba
    result = analyze_kin(
        blueprint_id=blueprint_id,
        kin_id=kin_id,
        message=args.message,
        images=args.images,
        model=args.model,
        add_system=args.add_system
    )
    
    # Afficher le résultat
    if result:
        print("\nAnalyse de l'état émotionnel de Simba:")
        print("=" * 60)
        
        # Vérifier si la réponse contient une analyse
        response = result.get("response")
        if response:
            print(response)
        else:
            print("Pas d'analyse dans la réponse. Réponse complète:")
            print(json.dumps(result, indent=2))
        
        print("=" * 60)
        print(f"Statut: {result.get('status')}")
        print(f"Mode: {result.get('mode')}")
    else:
        print("Échec de l'analyse")
