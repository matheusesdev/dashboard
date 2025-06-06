import os
import json
# A função correta, 'send_from_directory', é importada aqui
from flask import Flask, send_from_directory, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import traceback

# O Flask é instruído a procurar arquivos estáticos na pasta 'static'
app = Flask(__name__, static_folder='static')

# --- Rota da API ---
@app.route('/api/data')
def get_data():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    creds = None

    try:
        creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if creds_json_str:
            creds_info = json.loads(creds_json_str)
            creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        else:
            creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        SPREADSHEET_ID = '1WNi5B8ujhPTcGZgS5j7oMnnF4G_MxEEhO9ANhywLcpM'
        RANGE_NAME = 'BaseDeDados!A:F'

        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values or len(values) < 2:
            return jsonify({"error": "Nenhum dado ou apenas cabeçalho encontrado na planilha."}), 404
        else:
            headers = values[0]
            json_data = [dict(zip(headers, row)) for row in values[1:]]
            for item in json_data:
                if 'Quantidade de Corretores' in item:
                    try:
                        item['Quantidade de Corretores'] = int(item['Quantidade de Corretores'])
                    except (ValueError, TypeError):
                        item['Quantidade de Corretores'] = 0
            return jsonify(json_data)

    except FileNotFoundError:
        return jsonify({"error": "Arquivo 'credentials.json' não encontrado."}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Erro interno do servidor: {e}"}), 500

# --- Rota para servir o Frontend (CORRIGIDA) ---
# Substituímos a função 'dashboard' pela 'serve_dashboard' que usa a função correta
@app.route('/')
def serve_dashboard():
    # send_from_directory é a função ideal para servir arquivos estáticos.
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)