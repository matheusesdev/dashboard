# app.py

from flask import Flask, jsonify, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# --- CONFIGURAÇÕES ---
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = '1QFospGr7d3KDggAz-dtjbjGhZDVb-ZxANpw6pzr3lcU'  # <-- SUBSTITUA PELO SEU ID REAL
# Lendo da coluna A até a F, que corresponde às 6 colunas da sua imagem
RANGE_NAME = 'BaseDeDados!A:F'  # <-- AJUSTE O NOME DA ABA SE NECESSÁRIO
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# --------------------

@app.route('/')
def dashboard():
    """Renderiza a página principal do dashboard."""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """Busca, processa e serve os dados da planilha."""
    logging.info("Recebida requisição para /api/data")
    try:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values or len(values) < 2:
            return jsonify({"error": "Nenhum dado encontrado na planilha."}), 404

        header = values[0]
        data_rows = values[1:]
        
        df = pd.DataFrame(data_rows, columns=header)
        df.columns = df.columns.str.strip()

        required_cols = ['Imobiliária', 'Quantidade de Corretores', 'Estado', 'Cidade', 'Ativa em sistema', 'Contrato assinado']
        if not all(col in df.columns for col in required_cols):
            return jsonify({"error": "Colunas necessárias não encontradas na planilha."}), 500
            
        df['Quantidade de Corretores'] = pd.to_numeric(df['Quantidade de Corretores'], errors='coerce').fillna(0)
        df['Quantidade de Corretores'] = df['Quantidade de Corretores'].astype(int)

        logging.info(f"Processados {len(df)} registros.")
        return jsonify(df.to_dict('records'))

    except Exception as e:
        logging.error(f"Erro inesperado: {e}", exc_info=True)
        return jsonify({"error": "Erro interno no servidor.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)