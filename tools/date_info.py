# 📁 tools/date_info.py
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated
from datetime import datetime, date

def tool_metadata():
    """Metadados da ferramenta para obter informações de data e hora."""
    return {
        "name": "informacoes_data", # Mantenha o nome que o agente já conhece
        "description": "Fornece a data, o dia da semana e a hora atual no Brasil.",
        "version": "1.0.0",
        "author": "ChatBot Team",
        "category": "time"
    }

async def informacoes_data(
    ctx: RunContext[ConversationContext]
) -> str:
    """Fornece informações sobre data e hora atual (dia, mês, ano, dia da semana, hora)."""
    now = datetime.now() # O datetime.now() por padrão pega a hora local do servidor
    hoje = date.today()
    
    dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    dia_semana = dias_semana[hoje.weekday()]
    mes = meses[hoje.month - 1]
    
    return (f"📅 Hoje é {dia_semana}, {hoje.day} de {mes} de {hoje.year}\n"
            f"🕐 Horário atual: {now.strftime('%H:%M:%S')}")

# Marcar função como ferramenta
informacoes_data.__tool_metadata__ = tool_metadata()