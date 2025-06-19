# app.py - VERSÃO FINAL PARA DEPLOY (LÊ VARIÁVEL DE AMBIENTE OU ARQUIVO LOCAL)

import os
import json
from flask import Flask, jsonify, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# --- CONFIGURAÇÕES GERAIS ---
# O ID da sua planilha e o intervalo de dados.
# Certifique-se de que estes valores estão corretos.
SPREADSHEET_ID = '1QFospGr7d3KDggAz-dtjbjGhZDVb-ZxANpw6pzr3lcU'
RANGE_NAME = 'BaseDeDados!A:F'  # Verifique o nome da sua aba!
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# -----------------------------

def get_google_creds():
    """
    Função inteligente para obter as credenciais.
    Verifica se a variável de ambiente GOOGLE_CREDENTIALS existe (no Render).
    Se não, carrega do arquivo local 'credentials.json' (para desenvolvimento).
    """
    if 'GOOGLE_CREDENTIALS' in os.environ:
        logging.info("Carregando credenciais da variável de ambiente (Render).")
        creds_json_str = os.environ.get('GOOGLE_CREDENTIALS')
        creds_info = json.loads(creds_json_str)
        return service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    else:
        logging.info("Carregando credenciais do arquivo local 'credentials.json'.")
        # Substitua pelo nome do seu arquivo de credenciais local se for diferente
        SERVICE_ACCOUNT_FILE = 'credentials.json' 
        return service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    logging.info("Recebida requisição para /api/data")
    try:
        # Obtém as credenciais usando nossa função inteligente
        creds = get_google_creds()
        
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        
        if not values or len(values) < 2:
            return jsonify([])

        df = pd.DataFrame(values[1:], columns=values[0])
        df.columns = df.columns.str.strip()
        df['Quantidade de Corretores'] = pd.to_numeric(df['Quantidade de Corretores'], errors='coerce').fillna(0).astype(int)
        
        return jsonify(df.to_dict('records'))

    except Exception as e:
        # Este log aparecerá no Render e nos dirá o que deu errado
        logging.error(f"ERRO INESPERADO NA ROTA /api/data: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # O Gunicorn (servidor do Render) não usa esta parte, mas é útil para testes locais
    app.run(debug=True, host='0.0.0.0', port=5001)