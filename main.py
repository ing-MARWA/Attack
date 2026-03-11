import os
import json
from fastapi import FastAPI, HTTPException, Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

app = FastAPI(
    title="Email Lookup API",
    description="Read email info by ID from Google Sheet",
    version="1.0.0",
    docs_url="/docs",  # Enable Swagger UI at /docs
    redoc_url="/redoc"  # Enable ReDoc at /redoc
)

# Environment vars - Railway will set these
SPREADSHEET_ID = os.getenv("SHEET_ID", "YOUR_SPREADSHEET_ID_HERE")  # Replace with your actual spreadsheet ID
RANGE_NAME = "Sheet1"  # Adjust if needed

# Google Sheets API scopes
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheets_service():
    """
    Creates a Google Sheets API service using service account credentials.
    On Railway, credentials come from environment variable as JSON string.
    """
    # First try to get credentials from environment variable (Railway)
    creds_json_string = os.getenv("GOOGLE_CREDS_JSON")
    
    if creds_json_string:
        # Parse JSON string from environment variable
        service_account_info = json.loads(creds_json_string)
        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )
    else:
        # Fall back to file for local development
        service_account_file = os.getenv("GOOGLE_CREDS_JSON_PATH", "credentials.json")
        if os.path.exists(service_account_file):
            creds = Credentials.from_service_account_file(
                service_account_file,
                scopes=SCOPES
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="No Google credentials found. Set GOOGLE_CREDS_JSON environment variable."
            )
    
    return build("sheets", "v4", credentials=creds)

@app.get("/")
def health_check():
    return {
        "status": "API is running",
        "service": "Email Lookup API",
        "endpoints": {
            "docs": "/docs",
            "lookup_email": "/email/{id}"
        }
    }

@app.get("/email/{id}")
def get_email_by_id(id: int = Path(..., description="The ID to look up", ge=1)):
    """
    Returns email information for a specific ID from the Google Sheet.
    """
    try:
        service = get_sheets_service()
        
        # Try to get all sheets to find the correct one
        try:
            sheet = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, 
                range=RANGE_NAME
            ).execute()
        except HttpError as e:
            if "Unable to parse range" in str(e):
                # Try to get first sheet dynamically
                spreadsheet_metadata = service.spreadsheets().get(
                    spreadsheetId=SPREADSHEET_ID
                ).execute()
                sheets = spreadsheet_metadata.get('sheets', [])
                if sheets:
                    first_sheet_name = sheets[0]['properties']['title']
                    sheet = service.spreadsheets().values().get(
                        spreadsheetId=SPREADSHEET_ID,
                        range=first_sheet_name
                    ).execute()
                else:
                    raise HTTPException(status_code=404, detail="No sheets found in the spreadsheet")
            else:
                raise

        values = sheet.get("values", [])
        if not values:
            raise HTTPException(status_code=404, detail="No data found in the sheet")

        # First row is header
        header = values[0]
        rows = values[1:]

        # Look for matching ID
        for row in rows:
            try:
                if int(row[0]) == id:
                    # Construct dictionary with possible missing columns
                    result = {
                        header[i]: (row[i] if i < len(row) else None)
                        for i in range(len(header))
                    }
                    return result
            except (ValueError, IndexError):
                continue

        raise HTTPException(status_code=404, detail=f"No record found with ID {id}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-sheet")
def test_sheet_connection():
    """Test endpoint to verify Google Sheets connection"""
    try:
        service = get_sheets_service()
        spreadsheet_metadata = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID
        ).execute()
        
        sheets = spreadsheet_metadata.get('sheets', [])
        sheet_names = [sheet['properties']['title'] for sheet in sheets]
        
        return {
            "status": "connected",
            "spreadsheet_id": SPREADSHEET_ID,
            "sheets": sheet_names,
            "sheet_count": len(sheets)
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}