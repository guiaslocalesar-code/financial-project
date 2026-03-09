import logging
import httpx
import re
from typing import List, Dict, Any, Optional
from app.config import config

logger = logging.getLogger("metricool_service")

class MetricoolService:
    BASE_URL = "https://app.metricool.com/api/v2/scheduler/posts"
    NORMALIZE_URL = "https://app.metricool.com/api/actions/normalize/image/url"

    def __init__(self):
        self._auth_key = config.METRICOOL_API_KEY
        self._user_id = config.METRICOOL_USER_ID

    async def normalize_media_url(self, url: str, blog_id: str) -> str:
        """
        Normalize media URLs.
        First converts Google Drive links, then calls Metricool's normalization if needed.
        """
        # Convert Google Drive links locally first if possible
        drive_match = re.search(r'(?:[?&]id=|\/d\/)([a-zA-Z0-9_-]+)', url)
        if drive_match:
            file_id = drive_match.group(1)
            url = f"https://lh3.googleusercontent.com/d/{file_id}"
            return url  # Direct link is usually enough

        # Optional: call Metricool normalization endpoint
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "url": url,
                    "userId": self._user_id,
                    "blogId": blog_id
                }
                headers = {"X-Mc-Auth": self._auth_key}
                response = await client.get(self.NORMALIZE_URL, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("url", url)
                return url
        except Exception as e:
            logger.warning(f"Error normalizing url {url}: {e}")
            return url

    async def create_post(self, payload: Dict[str, Any], blog_id: str, publication_type: str = "POST") -> Dict[str, Any]:
        """
        Create a scheduler post in Metricool.
        publication_type can be 'POST' or 'STORY'.
        """
        url = self.BASE_URL
        params = {
            "userId": self._user_id,
            "blogId": blog_id
        }
        headers = {
            "X-Mc-Auth": self._auth_key,
            "Content-Type": "application/json"
        }
        
        # Prepare body based on the original n8n payload structure
        body = {
            "text": payload.get("text", ""),
            "publicationDate": payload.get("publicationDate", {}),
            "providers": payload.get("providers", []),
            "media": payload.get("media", []),
            "autoPublish": payload.get("autoPublish", True),
            "draft": payload.get("draft", False),
            "saveExternalMediaFiles": True,
        }
        
        # Inject network specific configurations based on publication type
        if publication_type.upper() == "STORY":
            body["instagramData"] = {"type": "STORY", "autoPublish": True}
            body["facebookData"] = {"type": "STORY"}
            # Fallback for others if needed, though usually omitted for stories
        else:
            # Default POST behavior
            body["instagramData"] = {"type": "POST", "autoPublish": True}
            body["facebookData"] = {"type": "POST"}
            body["twitterData"] = {"type": "POST"}

        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Sending post to Metricool for brand {blog_id}")
                response = await client.post(url, params=params, headers=headers, json=body, timeout=60.0)
                response_data = response.json()
                
                if response.status_code >= 400:
                    logger.error(f"Metricool API error: {response.text}")
                    return {"success": False, "error": response.text, "id": None}
                
                # Check for success in response body
                # n8n logic used smaller than 400 as success
                post_id = response_data.get("data", {}).get("id") or response_data.get("id")
                return {"success": True, "id": post_id, "data": response_data}
                
            except Exception as e:
                logger.error(f"Failed to post to Metricool: {e}")
                return {"success": False, "error": str(e), "id": None}

metricool_service = MetricoolService()
