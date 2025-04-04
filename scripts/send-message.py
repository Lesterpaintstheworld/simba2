import requests
import json
import os
import argparse
import base64
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def send_message(blueprint_id, kin_id, content, images=None, attachments=None, 
                model="claude-3-5-haiku-latest", history_length=25, 
                mode="creative", add_system=None):
    """
    Envoie un message à un Kin spécifique.
    
    Args:
        blueprint_id (str): L'ID du blueprint
        kin_id (str): L'ID du Kin
        content (str): Le contenu du message
        images (list, optional): Liste des chemins d'images à envoyer
        attachments (list, optional): Liste des fichiers à joindre
        model (str, optional): Le modèle à utiliser. Par défaut "claude-3-5-haiku-latest"
        history_length (int, optional): Longueur de l'historique à considérer. Par défaut 25
        mode (str, optional): Mode de réponse ("creative", "balanced", "precise"). Par défaut "creative"
        add_system (str, optional): Instructions système supplémentaires
    
    Returns:
        dict: La réponse de l'API
    """
    # URL de l'API
    api_url = f"https://api.kinos-engine.ai/v2/blueprints/{blueprint_id}/kins/{kin_id}/messages"
    
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
        "content": content,
        "model": model,
        "history_length": history_length,
        "mode": mode
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
    
    # Ajouter les pièces jointes si spécifiées
    if attachments:
        payload["attachments"] = attachments
    
    # Effectuer la requête POST
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Lever une exception si la requête a échoué
        
        # Analyser la réponse JSON
        result = response.json()
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi du message: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails de l'erreur: {e.response.text}")
        return None

if __name__ == "__main__":
    # Configurer les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Envoyer un message à Simba")
    parser.add_argument("message", help="Le message à envoyer à Simba")
    parser.add_argument("--images", nargs="+", help="Chemins des images à envoyer")
    parser.add_argument("--attachments", nargs="+", help="Fichiers à joindre")
    parser.add_argument("--model", default="claude-3-5-haiku-latest", help="Modèle à utiliser")
    parser.add_argument("--history-length", type=int, default=25, help="Longueur de l'historique")
    parser.add_argument("--mode", default="creative", choices=["creative", "balanced", "precise"], 
                        help="Mode de réponse")
    parser.add_argument("--add-system", help="Instructions système supplémentaires")
    args = parser.parse_args()
    
    # Paramètres pour Simba
    blueprint_id = "simba"
    kin_id = "simba"
    
    # Envoyer le message
    result = send_message(
        blueprint_id=blueprint_id,
        kin_id=kin_id,
        content=args.message,
        images=args.images,
        attachments=args.attachments,
        model=args.model,
        history_length=args.history_length,
        mode=args.mode,
        add_system=args.add_system
    )
    
    # Afficher le résultat
    if result:
        print("\nRéponse de Simba:")
        print("-" * 50)
        print(result.get("content", "Pas de contenu dans la réponse"))
        print("-" * 50)
        print(f"ID du message: {result.get('id')}")
        print(f"Statut: {result.get('status')}")
        print(f"Rôle: {result.get('role')}")
        print(f"Horodatage: {result.get('timestamp')}")
    else:
        print("Échec de l'envoi du message")
