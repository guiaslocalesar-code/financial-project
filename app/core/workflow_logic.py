import logging
from datetime import datetime
import pytz
from typing import List, Dict, Any, Optional
from app.config import config
from app.services.google_sheets_service import sheets_service
from app.services.metricool_service import metricool_service
from app.services.notification_service import notification_service

logger = logging.getLogger("workflow_logic")

class WorkflowLogic:
    NETWORKS = [
        'Facebook', 'Twitter/X', 'LinkedIn', 'GBP', 'Instagram',
        'Pinterest', 'TikTok', 'Youtube', 'Threads', 'Bluesky'
    ]
    
    NETWORK_MAP = {
        'Facebook': 'FACEBOOK', 'Twitter/X': 'TWITTER', 'LinkedIn': 'LINKEDIN', 
        'GBP': 'GMB', 'Instagram': 'INSTAGRAM', 'Pinterest': 'PINTEREST', 
        'TikTok': 'TIKTOK', 'Youtube': 'YOUTUBE', 'Threads': 'THREADS', 'Bluesky': 'BLUESKY'
    }

    async def run_workflow(self, sheet_name: str = "planificacion_data", publication_type: str = "POST"):
        """Execute the full workflow for a specific sheet and publication type."""
        logger.info(f"Starting migration run for {publication_type} on sheet {sheet_name}...")
        
        # 1. Fetch planning data
        planning_id = config.PLANNING_SHEET_ID
        planning_range = f"'{sheet_name}'!A:Z" # Broad range to get all columns
        
        raw_rows = sheets_service.read_sheet(planning_id, planning_range)
        if not raw_rows:
            logger.info(f"No rows found in planning sheet ({sheet_name}).")
            return []

        # 2. Filter pending rows
        pending_items = self._filter_pending_rows(raw_rows)
        if not pending_items:
            logger.info(f"No pending rows to process for {publication_type}.")
            return []

        logger.info(f"Processing {len(pending_items)} pending items for {publication_type}.")
        
        # 3. Load brands lookup
        brands_id = config.BRANDS_SHEET_ID
        brands_range = "'MM_Manual_de_Marca'!A:Z"
        brands_data = sheets_service.read_sheet(brands_id, brands_range)
        
        results = []
        for item in pending_items:
            result = await self._process_single_item(item, brands_data, planning_id, sheet_name, publication_type)
            results.append(result)
            
        return results

    def _filter_pending_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter rows where at least one network is TRUE and it hasn't been published yet.
        Also checks for future dates.
        """
        arg_tz = pytz.timezone("America/Argentina/Buenos_Aires")
        now = datetime.now(arg_tz)
        
        pending = []
        for row in rows:
            # Check for existing publication status (avoiding double publication)
            already_published = any(
                "PUBLICADO" in str(row.get(net, "")).upper() or "METRICOOL" in str(row.get(net, "")).upper() 
                for net in self.NETWORKS
            )
            if already_published:
                continue
                
            # Check if any network is set to TRUE
            active_networks = [net for net in self.NETWORKS if str(row.get(net, "")).upper() == "TRUE"]
            if not active_networks:
                continue
                
            # Check future date (n8n filter logic)
            date_str = row.get("Date", "").strip()
            time_str = row.get("Time", "").strip() or "00:00"
            if not date_str:
                continue
                
            try:
                # Merge date and time. Assuming YYYY-MM-DD
                dt = datetime.strptime(f"{date_str} {time_str[:5]}", "%Y-%m-%d %H:%M")
                dt = arg_tz.localize(dt)
                if dt < now:
                    logger.debug(f"Row {row.get('ID')} date {dt} is in the past. Skipping.")
                    continue
            except ValueError:
                logger.warning(f"Invalid date format for row {row.get('ID')}: {date_str} {time_str}")
                continue

            pending.append(row)
        return pending

    async def _process_single_item(self, row: Dict[str, Any], brands_data: List[Dict[str, Any]], planning_id: str, sheet_name: str, publication_type: str) -> Dict[str, Any]:
        """Process a single row from the spreadsheet."""
        client_name = row.get("Cliente", "")
        row_id = row.get("ID")
        
        logger.info(f"Processing row ID {row_id} for client '{client_name}' ({publication_type})")

        # 1. Look up brand data
        brand_info = next((b for b in brands_data if b.get("Empresa", "").strip() == client_name.strip()), None)
        if not brand_info:
            err_msg = f"Brand data not found for client: {client_name}"
            await notification_service.notify_error({"ID": row_id, "Cliente": client_name, "error": err_msg})
            return {"ID": row_id, "success": False, "error": err_msg}

        # 2. Extract brandId
        blog_id = brand_info.get("id_metricool") or brand_info.get("ID_Empresa")
        if not blog_id:
            err_msg = f"Metricool ID (id_metricool) missing in brand data for: {client_name}"
            return {"ID": row_id, "success": False, "error": err_msg}

        # 3. Construct payload
        active_nets = [net for net in self.NETWORKS if str(row.get(net, "")).upper() == "TRUE"]
        providers = [{"network": self.NETWORK_MAP[net]} for net in active_nets]
        
        # 4. Media normalization
        # n8n looked for Picture Url 1-10 or common patterns
        media_urls = []
        for i in range(1, 11):
            url_key = f"Picture Url {i}"
            val = row.get(url_key)
            if val and str(val).startswith("http"):
                normalized = await metricool_service.normalize_media_url(val, blog_id)
                media_urls.append(normalized)
        
        payload = {
            "text": row.get("Text") or row.get("Texto") or "",
            "publicationDate": {
                "dateTime": f"{row.get('Date')}T{row.get('Time', '00:00')[:5]}:00",
                "timezone": "America/Argentina/Buenos_Aires"
            },
            "providers": providers,
            "media": media_urls,
            "autoPublish": not (str(row.get("Draft", "")).upper() == "TRUE"),
            "draft": str(row.get("Draft", "")).upper() == "TRUE"
        }

        # 5. Call Metricool API
        api_result = await metricool_service.create_post(payload, blog_id, publication_type)
        
        # 6. Update spreadsheet
        update_row_idx = sheets_service.find_row_by_id(planning_id, sheet_name, "ID", row_id)
        if update_row_idx:
            status_val = "Publicado en Metricool" if api_result["success"] else "Error en Publicación"
            for net in active_nets:
                sheets_service.update_cell(planning_id, sheet_name, update_row_idx, net, status_val)
            
            if api_result["success"] and api_result.get("id"):
                sheets_service.update_cell(planning_id, sheet_name, update_row_idx, "ID_Metricool_Post", api_result["id"])
        
        # 7. Notify if failure
        if not api_result["success"]:
            await notification_service.notify_error({
                "ID": row_id, 
                "Cliente": client_name, 
                "Text": payload["text"], 
                "error": api_result["error"]
            })
            
        return {"ID": row_id, "success": api_result["success"]}

workflow_logic = WorkflowLogic()
