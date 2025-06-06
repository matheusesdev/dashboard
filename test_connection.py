# test_connection.py
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- Configure estas 3 variáveis ---
SERVICE_ACCOUNT_FILE = 'config/dashboard.json'  # Verifique se o nome do arquivo está correto
SPREADSHEET_ID = '1WNi5B8ujhPTcGZgS5j7oMnnF4G_MxEEhO9ANhywLcpM'
RANGE_NAME = 'BaseDeDados!A1:Z50'  # Tente ler apenas uma ou duas células para testar
# ------------------------------------

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

try:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    print("✅ Conexão bem-sucedida!")
    print("Dados encontrados:", values)

except Exception as e:
    print("❌ Falha na conexão.")
    print("Erro:", e)