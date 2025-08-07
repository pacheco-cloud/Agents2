# 📁 tools/shared_calendar_auth.py
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Se modificar esses escopos, delete o arquivo token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Mostra como autenticar e retornar o serviço da Google Calendar API."""
    creds = None
    # O arquivo token.pickle armazena os tokens de acesso e atualização do usuário,
    # e é criado automaticamente quando o fluxo de autorização é concluído pela primeira vez.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Se não houver credenciais (válidas) disponíveis, permita que o usuário faça login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Baixe o arquivo credentials.json do Google Cloud Console
            # e coloque-o na mesma pasta que este script.
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Salve as credenciais para a próxima execução
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service