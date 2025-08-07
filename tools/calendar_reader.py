# 📁 tools/calendar_reader.py
"""
Ferramenta de leitura do Google Calendar
Permite listar compromissos e calendários disponíveis
"""

from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated
from datetime import datetime, timedelta
import pytz
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopos necessários para ler o calendário
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def tool_metadata():
    """Metadados da ferramenta para listar compromissos."""
    return {
        "name": "calendar_reader",
        "description": "Lista compromissos e calendários do Google Calendar",
        "version": "1.1.0",
        "author": "ChatBot Team",
        "category": "productivity"
    }

def get_calendar_service():
    """Obtém o serviço do Google Calendar autenticado."""
    creds = None
    token_file = 'data/calendar_token.pickle'
    credentials_file = 'credentials.json'
    
    # Criar diretório data se não existir
    os.makedirs('data', exist_ok=True)
    
    # Verificar se o token existe
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # Se não há credenciais válidas, fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # Remove token inválido
                if os.path.exists(token_file):
                    os.remove(token_file)
                creds = None
        
        if not creds:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    "Arquivo credentials.json não encontrado. "
                    "Configure no Google Cloud Console e coloque na raiz do projeto."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salvar credenciais
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def parse_date_string(date_str: str, default_tz=None) -> datetime:
    """Analisa string de data em vários formatos."""
    if default_tz is None:
        default_tz = pytz.timezone('America/Sao_Paulo')
    
    # Tentar ISO format primeiro
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    
    # Formatos comuns
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = default_tz.localize(dt)
            return dt
        except ValueError:
            continue
    
    raise ValueError(f"Não foi possível analisar a data: {date_str}")

def format_event_time(start_str: str, end_str: str) -> tuple:
    """Formata as datas de início e fim do evento."""
    try:
        # Verificar se é evento de dia inteiro
        if 'T' not in start_str:
            start_date = datetime.fromisoformat(start_str).date()
            end_date = datetime.fromisoformat(end_str).date()
            
            if start_date == end_date:
                return start_date.strftime('%d/%m/%Y'), "", True
            else:
                return (f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}", 
                       "", True)
        else:
            # Evento com horário específico
            start_dt = datetime.fromisoformat(start_str)
            end_dt = datetime.fromisoformat(end_str)
            
            start_formatted = start_dt.strftime('%d/%m/%Y às %H:%M')
            
            if start_dt.date() == end_dt.date():
                end_formatted = end_dt.strftime('%H:%M')
            else:
                end_formatted = end_dt.strftime('%d/%m/%Y às %H:%M')
            
            return start_formatted, end_formatted, False
            
    except Exception:
        return start_str, end_str, False

async def list_events(
    ctx: RunContext[ConversationContext],
    max_results: Annotated[int, "Número máximo de compromissos (padrão: 10)"] = 10,
    time_min: Annotated[str, "Data de início (formato: dd/mm/yyyy ou ISO). Padrão: agora"] = None,
    time_max: Annotated[str, "Data de término (formato: dd/mm/yyyy ou ISO). Padrão: +7 dias"] = None,
    calendar_id: Annotated[str, "ID do calendário específico (padrão: principal)"] = 'primary'
) -> str:
    """Lista os próximos compromissos do Google Calendar."""
    
    try:
        service = get_calendar_service()
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

        # Definir período de busca
        if time_min:
            start_time_obj = parse_date_string(time_min, sao_paulo_tz)
        else:
            start_time_obj = datetime.now(sao_paulo_tz)

        if time_max:
            end_time_obj = parse_date_string(time_max, sao_paulo_tz)
        else:
            end_time_obj = start_time_obj + timedelta(days=7)

        # Buscar eventos
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time_obj.isoformat(),
            timeMax=end_time_obj.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            period_str = f"de {start_time_obj.strftime('%d/%m/%Y')} até {end_time_obj.strftime('%d/%m/%Y')}"
            return f"🗓️ Nenhum compromisso encontrado para o período {period_str}."
        
        # Formatar resposta
        period_str = f"de {start_time_obj.strftime('%d/%m/%Y')} até {end_time_obj.strftime('%d/%m/%Y')}"
        response = f"🗓️ **Seus próximos compromissos ({period_str}):**\n\n"
        
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'Sem título')
            location = event.get('location', '')
            description = event.get('description', '')
            
            # Formatar horário
            start_formatted, end_formatted, is_all_day = format_event_time(start, end)
            
            response += f"**{i}. {summary}**\n"
            
            if is_all_day:
                response += f"📅 Data: {start_formatted}\n"
            else:
                response += f"⏰ Início: {start_formatted}\n"
                if end_formatted:
                    response += f"⏱️ Término: {end_formatted}\n"
            
            if location:
                response += f"📍 Local: {location}\n"
            
            if description and len(description) < 100:
                response += f"📝 Descrição: {description[:97]}{'...' if len(description) > 97 else ''}\n"
            
            response += "\n"

        return response.strip()

    except FileNotFoundError as e:
        return f"❌ {str(e)}\n\n💡 Execute 'python config/setup_calendar.py' para configurar."
    
    except HttpError as e:
        if "credentials" in str(e).lower():
            return ("❌ Erro de autenticação. Execute 'python config/setup_calendar.py' para reconfigurar.")
        else:
            return f"❌ Erro da API do Google: {str(e)}"
    
    except Exception as e:
        return f"❌ Erro ao listar compromissos: {str(e)}"

async def list_calendars(ctx: RunContext[ConversationContext]) -> str:
    """Lista todos os calendários disponíveis na conta do Google."""
    
    try:
        service = get_calendar_service()
        
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        if not calendars:
            return "📅 Nenhum calendário encontrado."
        
        response = "📅 **Seus calendários disponíveis:**\n\n"
        
        for calendar in calendars:
            name = calendar['summary']
            calendar_id = calendar['id']
            
            # Marcar calendário principal
            if calendar.get('primary', False) or 'gmail.com' in calendar_id:
                response += f"⭐ **{name}** (Principal)\n"
            else:
                response += f"📋 **{name}**\n"
            
            response += f"   ID: `{calendar_id}`\n"
            
            if 'description' in calendar:
                response += f"   Descrição: {calendar['description']}\n"
            
            response += "\n"
        
        response += "\n💡 **Dica:** Use o ID do calendário no parâmetro `calendar_id` para consultar um calendário específico."
        
        return response.strip()
        
    except Exception as e:
        return f"❌ Erro ao listar calendários: {str(e)}"

# Registrar metadados das ferramentas
list_events.__tool_metadata__ = tool_metadata()
list_calendars.__tool_metadata__ = {
    "name": "list_calendars", 
    "description": "Lista calendários disponíveis no Google",
    "version": "1.0.0",
    "author": "ChatBot Team",
    "category": "productivity"
}