import logging
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from google.oauth2 import service_account
from app.config import config

logger = logging.getLogger("google_sheets_service")

class GoogleSheetsService:
    def __init__(self):
        self._creds = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self._creds)
        self.sheet = self.service.spreadsheets()

    def _get_credentials(self):
        """Fetch credentials from Secrets Manager if available, or fall back to default logic."""
        # Check if SA JSON is in Secret Manager (more recommended than files)
        sa_json = config.get_secret("GOOGLE_SHEETS_SA_JSON")
        if sa_json:
            import json
            import io
            return service_account.Credentials.from_service_account_info(json.loads(sa_json))
        
        # Else, if GOOGLE_APPLICATION_CREDENTIALS points to a file, this happens internally
        # But we'll use default Google credentials for Cloud Run environments
        import google.auth
        credentials, _ = google.auth.default()
        return credentials

    def read_sheet(self, sheet_id: str, range_name: str) -> List[Dict[str, Any]]:
        """Read data from a spreadsheet and return it as a list of dicts (with headers)."""
        try:
            result = self.sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
            values = result.get('values', [])
            
            if not values:
                return []
                
            headers = values[0]
            data = []
            for row in values[1:]:
                # Handle rows shorter than headers
                padded_row = row + [''] * (len(headers) - len(row))
                data.append(dict(zip(headers, padded_row)))
            
            return data
        except Exception as e:
            logger.error(f"Error reading sheet {sheet_id} [{range_name}]: {e}")
            raise

    def find_row_by_id(self, sheet_id: str, range_name: str, id_column: str, target_id: str) -> Optional[int]:
        """Find the row number (1-based) where the ID matches."""
        # Read the entire identified sheet and range
        result = self.sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])
        
        if not values:
            return None
            
        headers = values[0]
        try:
            col_idx = headers.index(id_column)
            for i, row in enumerate(values[1:], start=2): # Headers are row 1
                if len(row) > col_idx and str(row[col_idx]).strip() == str(target_id).strip():
                    return i
            return None
        except ValueError:
            logger.error(f"Column '{id_column}' not found in headers: {headers}")
            return None

    def update_cell(self, sheet_id: str, sheet_name: str, row: int, column_name: str, value: str):
        """Update a specific cell value based on the column name and row number."""
        # First find the column index
        result = self.sheet.values().get(
            spreadsheetId=sheet_id, range=f"'{sheet_name}'!1:1"
        ).execute()
        headers = result.get('values', [[]])[0]
        
        try:
            col_idx = headers.index(column_name)
            # Sheet cells are e.g. 'Sheet1!A2'
            # Convert col_idx to letter
            col_letter = self._get_column_letter(col_idx + 1)
            cell_range = f"'{sheet_name}'!{col_letter}{row}"
            
            body = {'values': [[value]]}
            self.sheet.values().update(
                spreadsheetId=sheet_id, range=cell_range,
                valueInputOption='RAW', body=body
            ).execute()
            logger.info(f"Updated {cell_range} to '{value}'")
        except (ValueError, IndexError):
            logger.error(f"Could not find column {column_name} in spreadsheet {sheet_id}")

    def _get_column_letter(self, n: int) -> str:
        """Helper to convert column index (1-based) to letter (A, B, C...)"""
        result = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            result = chr(65 + remainder) + result
        return result

sheets_service = GoogleSheetsService()
