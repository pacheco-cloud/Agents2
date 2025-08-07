# 📁 config/settings.py
import os
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class AgentConfig(BaseModel):
    """Configurações globais do agente"""
    model: str = Field(default="openai:gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=300, ge=1, le=4000)
    openai_api_key: str = Field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    
    def validate_config(self) -> bool:
        """Valida se as configurações estão corretas"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não encontrada!")
        return True

class ToolsConfig(BaseModel):
    """Configurações das ferramentas"""
    enabled_tools: List[str] = Field(default_factory=lambda: [
        "calculator",
        "password_generator", 
        "unit_converter",
        "task_manager",
        "text_analyzer"
    ])
    tools_directory: str = Field(default="tools")
    auto_discovery: bool = Field(default=True)

# Instância global das configurações
agent_config = AgentConfig()
tools_config = ToolsConfig()

