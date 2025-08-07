# 📁 tools/calendar_scheduler.py
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated, List
from datetime import datetime, timedelta
import pytz
from tools.shared_calendar_auth import get_calendar_service # Importar o serviço

def tool_metadata():
    """Metadados da ferramenta para agendar compromissos."""
    return {
        "name": "calendar_scheduler",
        "description": "Agenda um novo compromisso no Google Calendar.",
        "version": "1.0.0",
        "author": "ChatBot Team",
        "category": "calendar"
    }

async def create_event(
    ctx: RunContext[ConversationContext],
    summary: Annotated[str, "Título do compromisso."],
    start_time: Annotated[str, "Data e hora de início do compromisso (formato ISO 8601, ex: '2025-08-06T14:00:00-03:00')."],
    end_time: Annotated[str, "Data e hora de término do compromisso (formato ISO 8601, ex: '2025-08-06T15:00:00-03:00')."],
    description: Annotated[str, "Descrição detalhada do compromisso."] = None,
    location: Annotated[str, "Local do compromisso."] = None,
    attendees: Annotated[List[str], "Lista de e-mails dos participantes (ex: ['email1@example.com', 'email2@example.com'])."] = []
) -> str:
    """
    Agenda um novo compromisso no Google Calendar com os detalhes fornecidos.
    """
    try:
        service = get_calendar_service()
        
        # Definir fuso horário para São Paulo para garantir consistência
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

        # Converter strings de tempo para objetos datetime e adicionar fuso horário
        # Se as strings já vierem com offset, fromisoformat lida com isso.
        # Caso contrário, localize-as com o fuso horário de São Paulo.
        try:
            start_dt = datetime.fromisoformat(start_time)
            if start_dt.tzinfo is None:
                start_dt = sao_paulo_tz.localize(start_dt)
        except ValueError:
            return "❌ Formato de 'start_time' inválido. Use o formato ISO 8601 (ex: '2025-08-06T14:00:00-03:00')."
        
        try:
            end_dt = datetime.fromisoformat(end_time)
            if end_dt.tzinfo is None:
                end_dt = sao_paulo_tz.localize(end_dt)
        except ValueError:
            return "❌ Formato de 'end_time' inválido. Use o formato ISO 8601 (ex: '2025-08-06T15:00:00-03:00')."

        if start_dt >= end_dt:
            return "❌ A hora de início deve ser anterior à hora de término."

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'attendees': [{'email': email} for email in attendees],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60}, # 24 horas antes
                    {'method': 'popup', 'minutes': 10},    # 10 minutos antes
                ],
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        
        return (f"✅ Compromisso agendado com sucesso!\n"
                f"Título: {event.get('htmlLink', 'N/A')}\n"
                f"ID: {event.get('id', 'N/A')}\n"
                f"Início: {start_dt.strftime('%d/%m/%Y %H:%M')}\n"
                f"Término: {end_dt.strftime('%d/%m/%Y %H:%M')}")

    except Exception as e:
        return f"❌ Erro ao agendar compromisso: {str(e)}"

# Marcar função como ferramenta
create_event.__tool_metadata__ = tool_metadata()