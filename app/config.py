import os
import logging
from typing import Optional
from google.cloud import secretmanager
from google.api_core import exceptions
from dotenv import load_dotenv

# Optional local env loading
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("metricool_publisher_config")

class Config:
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "reemplazador-n8n")
    
    # Sheets configuration
    PLANNING_SHEET_ID = os.getenv("PLANNING_SHEET_ID", "1PMvDlydPAJFb_NJo0TgLlHePH0vIZtfS4RK2GVP6bYY")
    BRANDS_SHEET_ID = os.getenv("BRANDS_SHEET_ID", "1Yt0gJ-BxldHTcgSWXLdY7XPPxs0lmDf5lchJWmMprgA")
    STORIES_SHEET_NAME = os.getenv("STORIES_SHEET_NAME", "planificacion_historia")
    
    # Secrets management
    _client: Optional[secretmanager.SecretManagerServiceClient] = None

    @classmethod
    def get_secret(cls, secret_id: str, default: Optional[str] = None) -> Optional[str]:
        """Fetch secret from SM or falling back to environment variable."""
        # Try env first for local development convenience
        env_val = os.getenv(secret_id.upper())
        if env_val:
            return env_val
            
        if not cls._client:
            try:
                cls._client = secretmanager.SecretManagerServiceClient()
            except Exception as e:
                logger.debug(f"Could not initialize Secret Manager: {e}")
                return default

        try:
            name = f"projects/{cls.PROJECT_ID}/secrets/{secret_id}/versions/latest"
            response = cls._client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except exceptions.GoogleAPICallError as e:
            logger.warning(f"Error fetching secret '{secret_id}' from SM: {e}")
            return default
        except Exception:
            return default

    @property
    def METRICOOL_API_KEY(self):
        return self.get_secret("METRICOOL_API_KEY")

    @property
    def METRICOOL_USER_ID(self):
        return self.get_secret("METRICOOL_USER_ID")

    @property
    def TELEGRAM_BOT_TOKEN(self):
        return self.get_secret("TELEGRAM_BOT_TOKEN")

    @property
    def TELEGRAM_CHAT_ID_MATIAS(self):
        return self.get_secret("TELEGRAM_CHAT_ID_MATIAS")

config = Config()
