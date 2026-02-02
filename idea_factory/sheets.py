"""Google Sheets integration for storing ideas."""

import json
import os
from datetime import datetime
from typing import List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build


class SheetsClient:
    """Client for interacting with Google Sheets."""
    
    def __init__(self):
        """Initialize the Sheets client with service account credentials."""
        # Parse credentials from environment variable (JSON string)
        creds_json = os.getenv('GOOGLE_SHEETS_CREDS')
        if not creds_json:
            raise ValueError("GOOGLE_SHEETS_CREDS environment variable not set")
        
        try:
            creds_dict = json.loads(creds_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in GOOGLE_SHEETS_CREDS: {e}")
        
        # Create credentials from the parsed JSON
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        self.sheet_name = os.getenv('GOOGLE_SHEETS_SHEET_NAME', 'Ideas')
        
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID environment variable not set")
    
    def append_row(self, row_values: List[str]) -> bool:
        """
        Append a row to the Ideas sheet.
        
        Args:
            row_values: List of values to append (should match column order)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            range_name = f"{self.sheet_name}!A:J"  # Columns A through J (10 columns)
            body = {
                'values': [row_values]
            }
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error appending row to sheet: {e}")
            return False
    
    def read_recent_rows(self, limit: int = 50) -> Optional[List[List[str]]]:
        """
        Read recent rows from the Ideas sheet.
        
        Args:
            limit: Maximum number of rows to return
        
        Returns:
            List of rows (each row is a list of values), or None on error
        """
        try:
            range_name = f"{self.sheet_name}!A:J"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Return the last 'limit' rows (excluding header if present)
            if len(values) > 1:
                # Assume first row is header
                data_rows = values[1:]
                return data_rows[-limit:] if len(data_rows) > limit else data_rows
            
            return []
        except Exception as e:
            print(f"Error reading rows from sheet: {e}")
            return None
    
    def ensure_headers(self):
        """Ensure the sheet has the correct headers."""
        headers = [
            'timestamp_utc',
            'session_id',
            'prompt_initial',
            'idea_selected_title',
            'idea_selected_description',
            'user_edit_notes',
            'final_title',
            'final_description',
            'user_agent',
            'ip'
        ]
        
        try:
            # Check if first row exists
            range_name = f"{self.sheet_name}!A1:J1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # If no values or doesn't match headers, write headers
            if not values or values[0] != headers:
                body = {'values': [headers]}
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                print("Headers initialized in Google Sheet")
        except Exception as e:
            print(f"Error ensuring headers: {e}")

