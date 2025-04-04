import requests
import json
import os
import argparse
import time
import telegram
import asyncio
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def generate_image(blueprint_id, kin_id, prompt, aspect_ratio="ASPECT_1_1", model="V_2", magic_prompt_option="AUTO"):
    """
    Génère une image basée sur un prompt en utilisant l'API Ideogram via KinOS.
    
    Args:
        blueprint_id (str): L'ID du blueprint
        kin_id (str): L'ID du Kin
        prompt (str): Le prompt pour générer l'image
        aspect_ratio (str, optional): Ratio d'aspect de l'image. Par défaut "ASPECT_1_1"
        model (str, optional): Modèle à utiliser. Par défaut "V_2"
        magic_prompt_option (str, optional): Option de prompt magique. Par défaut "AUTO"
    
    Returns:
        dict: La réponse de l'API
    """
    # URL de l'API
    api_url = f"https://api.kinos-engine.ai/v2/blueprints/{blueprint_id}/kins/{kin_id}/images"
    
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
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "model": model,
        "magic_prompt_option": magic_prompt_option
    }
    
    # Effectuer la requête POST
    try:
        print(f"Envoi de la requête à {api_url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(api_url, headers=headers, json=payload)
        
        print(f"Code de statut HTTP: {response.status_code}")
        print(f"Réponse brute: {response.text}")
        
        response.raise_for_status()  # Lever une exception si la requête a échoué
        
        # Analyser la réponse JSON
        result = response.json()
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la génération de l'image: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails de l'erreur: {e.response.text}")
        return None

def send_message_with_image(blueprint_id, kin_id, content, image_url, model="claude-3-5-haiku-latest"):
    """
    Envoie un message avec une image à un Kin.
    
    Args:
        blueprint_id (str): L'ID du blueprint
        kin_id (str): L'ID du Kin
        content (str): Le contenu du message
        image_url (str): L'URL de l'image à envoyer
        model (str, optional): Le modèle à utiliser. Par défaut "claude-3-5-haiku-latest"
    
    Returns:
        dict: La réponse de l'API
    """
    # URL de l'API
    api_url = f"https://api.kinos-engine.ai/v2/blueprints/{blueprint_id}/kins/{kin_id}/messages"
    
    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv("KINOS_API_KEY")
    
    # Préparer les headers avec l'authentification
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Télécharger l'image depuis l'URL
    try:
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Encoder l'image en base64
        import base64
        image_data = base64.b64encode(image_response.content).decode('utf-8')
        
        # Créer l'URL data
        image_data_url = f"data:image/jpeg;base64,{image_data}"
        
        # Préparer le corps de la requête
        payload = {
            "content": content,
            "model": model,
            "images": [image_data_url]
        }
        
        # Effectuer la requête POST
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Analyser la réponse JSON
        result = response.json()
        return result
        
    except Exception as e:
        print(f"Erreur lors de l'envoi du message avec image: {e}")
        return None

async def send_telegram_notification(message, image_url, chat_id, token):
    """
    Envoie une notification Telegram avec une image.
    
    Args:
        message (str): Le message à envoyer
        image_url (str): L'URL de l'image à envoyer
        chat_id (str): L'ID du chat Telegram
        token (str): Le token du bot Telegram
    """
    try:
        bot = telegram.Bot(token=token)
        
        # Envoyer l'image avec la légende
        await bot.send_photo(chat_id=chat_id, photo=image_url, caption=message)
        print("Notification Telegram avec image envoyée avec succès")
    except Exception as e:
        print(f"Erreur lors de l'envoi de la notification Telegram: {e}")
        
        # Essayer d'envoyer juste le message et l'URL de l'image en cas d'échec
        try:
            message_with_url = f"{message}\n\nImage: {image_url}"
            await bot.send_message(chat_id=chat_id, text=message_with_url)
            print("Message Telegram avec URL de l'image envoyé avec succès")
        except Exception as e2:
            print(f"Erreur lors de l'envoi du message Telegram: {e2}")

if __name__ == "__main__":
    # Configurer les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Générer une image avec Simba")
    parser.add_argument("prompt", help="Le prompt pour générer l'image")
    parser.add_argument("--aspect-ratio", default="ASPECT_1_1", 
                        choices=["ASPECT_1_1", "ASPECT_16_9", "ASPECT_9_16", "ASPECT_4_3", "ASPECT_3_4"],
                        help="Ratio d'aspect de l'image")
    parser.add_argument("--model", default="V_2", choices=["V_1", "V_2"], help="Modèle à utiliser")
    parser.add_argument("--magic-prompt", default="AUTO", 
                        choices=["AUTO", "NONE", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"],
                        help="Option de prompt magique")
    parser.add_argument("--message", default="Voici l'image que j'ai dessinée pour toi!", 
                        help="Message à envoyer avec l'image")
    parser.add_argument("--no-telegram", action="store_true", help="Désactiver la notification Telegram")
    parser.add_argument("--no-send-to-kin", action="store_true", help="Ne pas envoyer l'image au Kin")
    args = parser.parse_args()
    
    # Paramètres pour Simba
    blueprint_id = "simba"
    kin_id = "simba"
    
    # Générer l'image
    print(f"Génération de l'image avec le prompt: {args.prompt}")
    result = generate_image(
        blueprint_id=blueprint_id,
        kin_id=kin_id,
        prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        model=args.model,
        magic_prompt_option=args.magic_prompt
    )
    
    # Traiter le résultat
    if result:
        print("\nImage générée avec succès:")
        print("-" * 50)
        print(f"ID: {result.get('id')}")
        print(f"Statut: {result.get('status')}")
        print(f"Prompt: {result.get('prompt')}")
        print(f"Créée le: {result.get('created_at')}")
        
        # Récupérer l'URL de l'image
        image_url = result.get('data', {}).get('url')
        local_path = result.get('local_path')
        
        if image_url:
            print(f"URL de l'image: {image_url}")
            print(f"Chemin local: {local_path}")
            
            # Envoyer l'image à Simba si demandé
            if not args.no_send_to_kin:
                print("\nEnvoi de l'image à Simba...")
                message_result = send_message_with_image(
                    blueprint_id=blueprint_id,
                    kin_id=kin_id,
                    content=args.message,
                    image_url=image_url
                )
                
                if message_result:
                    # Vérifier si la réponse contient du contenu
                    content = message_result.get("response") or message_result.get("content")
                    if content:
                        print("\nRéponse de Simba:")
                        print("-" * 50)
                        print(content)
                        print("-" * 50)
                    else:
                        print("Pas de réponse de Simba")
                else:
                    print("Échec de l'envoi du message avec image à Simba")
            
            # Envoyer la notification Telegram si activée
            if not args.no_telegram:
                # Récupérer les informations Telegram depuis les variables d'environnement
                telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
                telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
                
                if telegram_token and telegram_chat_id:
                    # Préparer le message pour Telegram
                    telegram_message = f"Simba a dessiné: {args.prompt}"
                    
                    # Envoyer la notification Telegram de manière asynchrone
                    asyncio.run(send_telegram_notification(telegram_message, image_url, telegram_chat_id, telegram_token))
                else:
                    print("Variables d'environnement TELEGRAM_BOT_TOKEN et/ou TELEGRAM_CHAT_ID non définies")
        else:
            print("URL de l'image non trouvée dans la réponse")
    else:
        print("Échec de la génération de l'image")
