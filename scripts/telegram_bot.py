import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import requests
import json

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Récupérer les tokens et IDs
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KINOS_API_KEY = os.getenv("KINOS_API_KEY")

# Configuration de Simba
BLUEPRINT_ID = "simba"
KIN_ID = "simba"

async def send_to_kinos(content, images=None):
    """
    Envoie un message à KinOS et retourne la réponse.
    
    Args:
        content (str): Le contenu du message
        images (list, optional): Liste des images encodées en base64
    
    Returns:
        str: La réponse de KinOS
    """
    api_url = f"https://api.kinos-engine.ai/v2/blueprints/{BLUEPRINT_ID}/kins/{KIN_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {KINOS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": content,
        "model": "claude-3-5-haiku-latest",
        "history_length": 25,
        "mode": "creative"
    }
    
    if images:
        payload["images"] = images
    
    try:
        logger.info(f"Envoi du message à KinOS: {content}")
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Réponse reçue de KinOS: {result}")
        
        # Extraire la réponse (peut être dans 'response' ou 'content')
        return result.get("response") or result.get("content")
    
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message à KinOS: {e}")
        return "Désolé, je n'ai pas pu communiquer avec Simba pour le moment."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestionnaire pour la commande /start."""
    await update.message.reply_text(
        "Bonjour ! Je suis le bot Simba. Envoyez-moi un message et je vous répondrai !"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestionnaire pour la commande /help."""
    await update.message.reply_text(
        "Vous pouvez m'envoyer des messages texte ou des images, et je vous répondrai en tant que Simba !"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestionnaire pour les messages texte."""
    # Vérifier si le message provient du chat autorisé
    if str(update.effective_chat.id) != TELEGRAM_CHAT_ID and TELEGRAM_CHAT_ID != "*":
        logger.warning(f"Message reçu d'un chat non autorisé: {update.effective_chat.id}")
        return
    
    # Récupérer le message
    message_text = update.message.text
    logger.info(f"Message reçu: {message_text}")
    
    # Indiquer que le bot est en train d'écrire
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Envoyer le message à KinOS et obtenir la réponse
    response = await send_to_kinos(message_text)
    
    # Envoyer la réponse
    await update.message.reply_text(response)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestionnaire pour les messages avec photos."""
    # Vérifier si le message provient du chat autorisé
    if str(update.effective_chat.id) != TELEGRAM_CHAT_ID and TELEGRAM_CHAT_ID != "*":
        return
    
    # Récupérer la photo (la plus grande résolution disponible)
    photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
    
    # Télécharger la photo
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Convertir en base64
    import base64
    photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
    
    # Créer l'URL data
    photo_data_url = f"data:image/jpeg;base64,{photo_base64}"
    
    # Récupérer la légende de la photo ou utiliser un texte par défaut
    caption = update.message.caption or "Regarde cette image !"
    
    # Indiquer que le bot est en train d'écrire
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Envoyer le message et l'image à KinOS
    response = await send_to_kinos(caption, images=[photo_data_url])
    
    # Envoyer la réponse
    await update.message.reply_text(response)

def main() -> None:
    """Fonction principale pour démarrer le bot."""
    # Vérifier que les variables d'environnement nécessaires sont définies
    if not TELEGRAM_BOT_TOKEN:
        logger.error("La variable d'environnement TELEGRAM_BOT_TOKEN n'est pas définie")
        return
    
    if not KINOS_API_KEY:
        logger.error("La variable d'environnement KINOS_API_KEY n'est pas définie")
        return
    
    # Créer l'application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Ajouter les gestionnaires
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Démarrer le bot
    logger.info("Bot Telegram démarré")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
