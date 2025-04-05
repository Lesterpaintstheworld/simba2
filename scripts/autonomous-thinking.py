import requests
import json
import os
import asyncio
import telegram
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

def compose_message_for_mom(thoughts_result):
    """
    Utilise Claude pour composer un message personnalisé pour maman basé sur les réflexions.
    """
    api_url = f"https://api.kinos-engine.ai/v2/blueprints/simba/kins/simba/analysis"
    
    api_key = os.getenv("KINOS_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = f"""En tant que Simba, compose un message affectueux pour maman.
    Voici mes réflexions récentes: {json.dumps(thoughts_result, indent=2)}
    Le message doit être personnel, chaleureux et refléter mes pensées actuelles.
    Utilise un ton doux et affectueux, avec quelques emojis appropriés."""

    payload = {
        "message": "Compose un message pour maman qui exprime mes sentiments actuels",
        "model": "claude-3-5-haiku-latest",
        "addSystem": system_prompt
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response") or result.get("content")
    except Exception as e:
        print(f"Erreur lors de la composition du message: {e}")
        return None

async def send_telegram_notification(message, chat_id, token):
    """
    Envoie une notification Telegram.
    
    Args:
        message (str): Le message à envoyer
        chat_id (str): L'ID du chat Telegram
        token (str): Le token du bot Telegram
    """
    try:
        bot = telegram.Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        print("Notification Telegram envoyée avec succès")
    except Exception as e:
        print(f"Erreur lors de l'envoi de la notification Telegram: {e}")

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

        # Composer le message via Claude
        message = compose_message_for_mom(result)
        
        if message:
            # Envoyer via Telegram
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
            
            if telegram_token and telegram_chat_id:
                asyncio.run(send_telegram_notification(message, telegram_chat_id, telegram_token))
            else:
                print("Variables d'environnement Telegram non définies")
    else:
        print("Échec du démarrage de la pensée autonome")
