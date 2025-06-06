# main.py för Replit.com
import asyncio
import requests
from telethon import TelegramClient, events
import os
from datetime import datetime
from flask import Flask
from threading import Thread

# Flask app för att hålla Replit aktiv
app = Flask('')

@app.route('/')
def home():
    return "Telegram Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Telegram & Discord credentials (lägg i Replit Secrets)
API_ID = os.environ.get('TELEGRAM_API_ID')
API_HASH = os.environ.get('TELEGRAM_API_HASH') 
PHONE_NUMBER = os.environ.get('TELEGRAM_PHONE')

CRYPTO_NEWS_WEBHOOK = os.environ.get('CRYPTO_NEWS_WEBHOOK')
WATCHER_GURU_WEBHOOK = os.environ.get('WATCHER_GURU_WEBHOOK')

client = TelegramClient('session', API_ID, API_HASH)

def send_to_discord(webhook_url, content, username="📱 Telegram"):
    """Send message to Discord via webhook"""
    
    data = {
        "content": content,
        "username": username,
    }
    
    try:
        response = requests.post(webhook_url, json=data)
        print(f"✅ Sent to Discord: {response.status_code}")
        return response.status_code == 204
    except Exception as e:
        print(f"❌ Error sending to Discord: {e}")
        return False

def send_embed_to_discord(webhook_url, title, description, username="📱 Telegram"):
    """Send rich embed to Discord"""
    
    embed = {
        "title": title[:256] if title else None,
        "description": description[:4096] if description else None,
        "color": 0x1DA1F2,  # Twitter blue
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "Live from Telegram"}
    }
    
    data = {
        "username": username,
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=data)
        print(f"✅ Sent embed to Discord: {response.status_code}")
        return response.status_code == 204
    except Exception as e:
        print(f"❌ Error sending embed: {e}")
        return False

@client.on(events.NewMessage)
async def handler(event):
    """Handle new messages from Telegram channels"""
    
    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, 'title', '')
        channel_username = getattr(chat, 'username', '')
        
        # Smart channel detection
        webhook_url = None
        channel_name = ""
        
        # Crypto News detection
        crypto_keywords = ['crypto', 'bitcoin', 'btc', 'ethereum', 'trading']
        if (any(keyword in chat_title.lower() for keyword in crypto_keywords) or 
            any(keyword in channel_username.lower() for keyword in crypto_keywords)):
            webhook_url = CRYPTO_NEWS_WEBHOOK
            channel_name = "🔥 CRYPTO NEWS"
        
        # Watcher Guru detection  
        elif 'watcher' in chat_title.lower() or 'watcher' in channel_username.lower():
            webhook_url = WATCHER_GURU_WEBHOOK
            channel_name = "👁️ WATCHER GURU"
        
        if not webhook_url:
            print(f"🔍 Unknown channel: {chat_title} (@{channel_username})")
            return
        
        message = event.message
        text_content = message.text or ""
        
        if not text_content:
            print("📭 Empty message, skipping...")
            return
        
        # Clean and format message
        if len(text_content) > 1500:
            # Long message → Send as embed
            await send_embed_to_discord(
                webhook_url,
                title=f"{channel_name} Update",
                description=text_content,
                username=channel_name
            )
        else:
            # Short message → Regular format
            formatted_text = f"**{channel_name}**\n\n{text_content}"
            await send_to_discord(
                webhook_url,
                formatted_text,
                username=channel_name
            )
        
        print(f"✅ Forwarded: {channel_name} → Discord")
        
    except Exception as e:
        print(f"❌ Error in handler: {e}")

async def main():
    """Main bot function"""
    
    print("🚀 Starting Telegram→Discord Bot...")
    print("🔗 Connecting to Telegram...")
    
    # Start Telegram client
    await client.start(phone=PHONE_NUMBER)
    
    print("✅ Connected to Telegram!")
    print("👂 Listening for messages...")
    print("🌐 Bot is live and running!")
    
    # Keep running
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Keep Replit alive
    keep_alive()
    
    # Start the bot
    asyncio.run(main())

# pyproject.toml (för Replit dependencies)
"""
[tool.poetry]
name = "telegram-discord-bot"
version = "0.1.0"
description = "Forward messages from Telegram to Discord"

[tool.poetry.dependencies]
python = "^3.9"
telethon = "^1.24.0"
requests = "^2.31.0"
flask = "^2.3.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
