# 📁 tools/calendar_deleter.py
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated
from tools.shared_calendar_auth import get_calendar_service # Importar o serviço

def tool_metadata():
    """Metadados da ferramenta para deletar compromissos."""
    return {
        "name": "calendar_deleter",
        "description": "Deleta um compromisso específico do Google Calendar usando seu ID.",
        "version": "1.0.0",
        "author": "ChatBot Team",
        "category": "calendar"
    }

async def delete_event(
    ctx: RunContext[ConversationContext],
    event_id: Annotated[str, "O ID do compromisso a ser deletado. Este ID pode ser obtido listando os compromissos."]
) -> str:
    """
    Deleta um compromisso do Google Calendar dado o seu ID.
    """
    try:
        service = get_calendar_service()
        
        # O Google Calendar API retorna 204 No Content para deleção bem-sucedida.
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        return f"✅ Compromisso com ID '{event_id}' deletado com sucesso."

    except Exception as e:
        return f"❌ Erro ao deletar compromisso: {str(e)}. Verifique se o ID está correto e se você tem permissão."

# Marcar função como ferramenta
delete_event.__tool_metadata__ = tool_metadata()