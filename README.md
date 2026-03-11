# Email Lookup API & Phishing Email Generator

This repository contains two main components:
1. **Email Lookup API**: A FastAPI-based service that retrieves email information from a Google Sheet by ID.
2. **Phishing Email Generator**: A Jupyter Notebook that generates simulated phishing emails for defensive training using LLMs.

## Components

### 1. Email Lookup API (`main.py`)
This API allows users to look up records in a Google Sheet by a numeric ID. It is designed to be deployed on Railway but can also run locally.

#### Features:
- **FastAPI**: Provides a high-performance, easy-to-use API framework.
- **Google Sheets Integration**: Uses the Google Sheets API to read data.
- **Swagger Documentation**: Automatically generated API docs at `/docs`.
- **Health Check & Connection Testing**: Endpoints to verify the API status and Google Sheets connection.

#### API Endpoints:
- `GET /`: Health check and list of endpoints.
- `GET /email/{id}`: Look up a record by ID.
- `GET /test-sheet`: Test the Google Sheets API connection.

### 2. Phishing Email Generator (`Generated_Phishing_Emails.ipynb`)
A Jupyter notebook that uses large language models (like IBM Granite or Microsoft Phi-4) to generate tailored phishing emails for security awareness training.

## Setup Instructions

### Prerequisites
- Python 3.10+
- A Google Cloud Project with the Google Sheets API enabled.
- Service Account credentials (JSON format).

### Local Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory:
   ```env
   SHEET_ID=your_google_sheet_id
   GOOGLE_CREDS_JSON_PATH=path/to/your/credentials.json
   ```
   *Alternatively, you can set `GOOGLE_CREDS_JSON` with the content of your JSON credentials file.*

4. Run the API:
   ```bash
   uvicorn main:app --reload
   ```

## Deployment (Railway)
The repository includes a `railway.json` file for easy deployment on [Railway](https://railway.app/).

### Configuration:
Set the following environment variables in your Railway project:
- `SHEET_ID`: Your Google Sheet ID.
- `GOOGLE_CREDS_JSON`: The full JSON content of your Google Service Account key.

The deployment uses `NIXPACKS` as the builder and runs the FastAPI app on the specified port.
