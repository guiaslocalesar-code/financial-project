import logging
import httpx
from typing import Optional
from app.config import config

logger = logging.getLogger("notification_service")

class NotificationService:
    def __init__(self):
        self._token = config.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self._token}/sendMessage"

    async def send_telegram(self, chat_id: str, message: str):
        """Send a message to a telegram chat."""
        if not self._token or not chat_id:
            logger.warning("Telegram configuration missing. Skipping message.")
            return

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload, timeout=10.0)
                if response.status_code >= 400:
                    logger.error(f"Telegram API error ({response.status_code}): {response.text}")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    async def notify_error(self, details: dict):
        """Standard notification for errors."""
        msg = f"<b>⚠️ ERROR al publicar en Metricool</b>\n\n" \
              f"📋 <b>Detalles del post:</b>\n" \
              f"- ID: {details.get('ID', 'N/A')}\n" \
              f"- Cliente: {details.get('Cliente', 'N/A')}\n" \
              f"- Texto: {details.get('Text', 'N/A')[:100]}...\n\n" \
              f"🔴 <b>Error técnico:</b>\n{details.get('error', 'Error desconocido')}"
        
        # Notify Matias
        chat_id = config.TELEGRAM_CHAT_ID_MATIAS
        if chat_id:
            await self.send_telegram(chat_id, msg)

    async def notify_success(self, details: dict):
        """Standard notification for success."""
        # Optional success channel
        pass

notification_service = NotificationService()
