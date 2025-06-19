# testar_conexao.py

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- DADOS PARA CONFIGURAR ---
# Nome do arquivo de credenciais que você colocou na pasta.
SERVICE_ACCOUNT_FILE = 'credentials.json'

# O ID da sua planilha (que você copiou no Passo 2.3).
SPREADSHEET_ID = '1QFospGr7d3KDggAz-dtjbjGhZDVb-ZxANpw6pzr3lcU'

# O nome da aba e o intervalo de colunas que você quer ler.
# Exemplo: 'Dados!A:F' lê as colunas de A até F da aba chamada "Dados".
RANGE_NAME = 'BaseDeDados!A:F' 
# -----------------------------

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

print("Tentando conectar...")

try:
    # 1. Autenticação
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    print("Autenticação com o arquivo de credenciais bem-sucedida.")

    # 2. Conexão com a API
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    print("Conexão com a API do Google Sheets estabelecida.")

    # 3. Busca dos dados
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    print(f"Busca de dados concluída. {len(values)} linhas encontradas.")

    if not values:
        print("❌ AVISO: Nenhum dado foi encontrado na planilha. Verifique o ID, nome da aba e intervalo.")
    else:
        # Usando Pandas para uma visualização bonita no terminal
        df = pd.DataFrame(values[1:], columns=values[0])
        print("\n✅ Conexão e leitura de dados bem-sucedidas!")
        print("Amostra dos dados encontrados:")
        print(df.head()) # Mostra as 5 primeiras linhas

except FileNotFoundError:
    print(f"❌ ERRO CRÍTICO: O arquivo de credenciais '{SERVICE_ACCOUNT_FILE}' não foi encontrado.")
    print("Verifique se o nome está correto e se o arquivo está na mesma pasta que este script.")
except Exception as e:
    print(f"❌ Ocorreu um erro: {e}")
    print("\nPossíveis causas:")
    print("- A API do Google Sheets não está habilitada no seu projeto do Google Cloud?")
    print("- Você compartilhou a planilha com o e-mail da Conta de Serviço?")
    print("- O ID da planilha ou o nome da aba no RANGE_NAME estão corretos?")