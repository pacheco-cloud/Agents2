# ========================
# 📁 models/context.py
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime

class UserPreferences(BaseModel):
    """Preferências do usuário"""
    language: str = Field(default="pt-BR")
    timezone: str = Field(default="America/Sao_Paulo")
    notification_enabled: bool = Field(default=True)
    preferred_units: Dict[str, str] = Field(default_factory=lambda: {
        "temperature": "celsius",
        "distance": "km",
        "weight": "kg"
    })

class SessionData(BaseModel):
    """Dados da sessão"""
    session_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    start_time: datetime = Field(default_factory=datetime.now)
    message_count: int = Field(default=0)
    last_activity: datetime = Field(default_factory=datetime.now)

class ConversationContext(BaseModel):
    """Contexto completo da conversa"""
    user_id: str = Field(default="anonymous")
    user_preferences: UserPreferences = Field(default_factory=UserPreferences)
    session_data: SessionData = Field(default_factory=SessionData)
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    
    def update_activity(self):
        """Atualiza última atividade e incrementa contador"""
        self.session_data.last_activity = datetime.now()
        self.session_data.message_count += 1
    
    def get_user_data(self, key: str, default: Any = None) -> Any:
        """Recupera dados customizados do usuário"""
        return self.custom_data.get(key, default)
    
    def set_user_data(self, key: str, value: Any):
        """Salva dados customizados do usuário"""
        self.custom_data[key] = value

# ========================
