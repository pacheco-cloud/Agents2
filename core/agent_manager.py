# 📁 core/agent_manager.py
from pydantic_ai import Agent
from config.settings import agent_config, tools_config
from models.context import ConversationContext
from core.tool_registry import tool_registry
from typing import Dict, Any
from datetime import datetime  # Add this import
import os

class AgentManager:
    """Gerenciador principal do agente"""
    
    def __init__(self):
        self.agent = None
        self.context = ConversationContext()
        self.setup_agent()
    
    def setup_agent(self):
        """Configura o agente principal"""
        # Validar configurações
        agent_config.validate_config()
        
        # Criar agente
        self.agent = Agent(
            agent_config.model,
            deps_type=ConversationContext,
            system_prompt=self.get_system_prompt()
        )
        
        # Carregar ferramentas
        self.load_tools()
        
        print("🤖 Agente configurado com sucesso!")
    
    def get_system_prompt(self) -> str:
        """Prompt do sistema personalizado"""
        return (
            "Você é um assistente avançado com acesso a várias ferramentas úteis. "
            "Use as ferramentas disponíveis sempre que apropriado para ajudar o usuário. "
            "Seja proativo, amigável e eficiente. Responda em português brasileiro. "
            "Quando usar uma ferramenta, explique brevemente o que está fazendo."
        )
    
    def load_tools(self):
        """Carrega e anexa ferramentas ao agente"""
        if tools_config.auto_discovery:
            discovered = tool_registry.auto_discover_tools(tools_config.tools_directory)
            print(f"🔍 Descobertas {len(discovered)} ferramentas automaticamente")
        
        # Anexar ferramentas ao agente
        tool_registry.attach_tools_to_agent(self.agent)
        
        # Listar ferramentas carregadas
        tools_list = tool_registry.list_tools()
        print(f"🛠️  Total de {len(tools_list)} ferramentas disponíveis")
    
    async def chat(self, message: str) -> str:
        """Processa mensagem do usuário"""
        try:
            # Atualizar contexto
            self.context.update_activity()
            
            # Executar agente
            result = await self.agent.run(message, deps=self.context)
            
            return str(result)  # Convert result directly to string
            
        except Exception as e:
            error_msg = f"❌ Erro no processamento: {str(e)}"
            print(error_msg)
            return "Desculpe, ocorreu um erro. Tente novamente."
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da sessão"""
        return {
            "session_id": self.context.session_data.session_id,
            "messages": self.context.session_data.message_count,
            "duration_minutes": (
                datetime.now() - self.context.session_data.start_time
            ).total_seconds() / 60,
            "tools_loaded": len(tool_registry.tools),
            "user_data_keys": list(self.context.custom_data.keys())
        }

# ========================
# ========================
