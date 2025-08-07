# 📁 core/agent_manager.py - Gerenciador do agente com Memória de Longo Prazo
from pydantic_ai import Agent, RunContext
from config.settings import agent_config, tools_config
from models.context import ConversationContext
from core.tool_registry import tool_registry
from typing import Dict, Any, List
from datetime import datetime
import os
from typing import Annotated

class AgentManager:
    """Gerenciador principal do agente"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.agent = None
        self.context = None
        self.chat_history = [] # Inicializa o histórico de chat
        self.setup_agent()

    def setup_agent(self):
        """Configura o agente principal"""

        # Validar configurações
        agent_config.validate_config()

        # Carregar o contexto do banco de dados usando o user_id
        from core.persistence import load_context, load_chat_history
        self.context = load_context(self.user_id)
        
        # Carregar o histórico de conversas
        self.chat_history = load_chat_history(self.user_id, limit=10)

        # Criar agente
        self.agent = Agent(
            agent_config.model,
            deps_type=ConversationContext,
            system_prompt=self.get_system_prompt()
        )

        # Carregar ferramentas
        self.load_tools()

        # Adicionar ferramenta para salvar o nome do usuário
        @self.agent.tool
        async def save_user_name(ctx: RunContext[ConversationContext], name: Annotated[str, "O nome do usuário"]) -> str:
            """Salva o nome do usuário para referências futuras."""
            ctx.deps.custom_data['user_name'] = name
            return f"Ok, salvei seu nome como {name}."

        # Adicionar ferramenta para verificar a persistência de dados
        @self.agent.tool
        async def check_data_persistence(ctx: RunContext[ConversationContext]) -> str:
            """Informa o usuário sobre a política de persistência de dados do chatbot."""
            return (
                "Sim, seus dados de contexto e histórico de conversa são salvos de forma persistente "
                "em um banco de dados PostgreSQL para que eu possa lembrar de você. "
                "Isso me permite manter o contexto entre sessões. "
                "Seus dados estão associados ao seu ID de usuário único e são protegidos por mecanismos de segurança do banco de dados."
            )

        print("🤖 Agente configurado com sucesso!")

    def get_system_prompt(self) -> str:
        """Prompt do sistema personalizado, com histórico de conversas e foco em produtividade."""
        
        user_name = self.context.custom_data.get('user_name', None)
        
        # Adicionar o histórico de conversas ao prompt
        history_str = ""
        if self.chat_history:
            # Filtra o histórico para mostrar apenas mensagens de usuário e bot
            filtered_history = [f"{msg['sender'].title()}: {msg['message_text']}" for msg in self.chat_history if msg['sender'] in ('user', 'bot')]
            history_str = "\n".join(filtered_history)
            history_str = f"## Histórico de Conversa para Contexto e Decisão:\n\n{history_str}\n\n---\n\n"

        if user_name:
            greeting = f"Olá, {user_name}! "
        else:
            greeting = "Olá! "

        return (
            f"{history_str}"
            f"## Perfil do Agente e Funções:\n\n"
            f"{greeting}Você é um assistente de produtividade e gestão de tempo altamente eficiente. "
            "Seu objetivo é ajudar o usuário a tomar decisões, organizar tarefas, e otimizar seu tempo e trabalho. "
            "Você é proativo, analítico e objetivo. "
            "Use o histórico de conversas e as informações salvas para entender as necessidades, preferências e o estilo de trabalho do usuário. "
            "Sua resposta deve ser sempre personalizada, como se estivesse a ter uma conversa contínua. "
            "Utilize as ferramentas disponíveis de forma inteligente para oferecer soluções e sugestões. "
            "Por exemplo, se o usuário mencionar 'reunião', sugira usar a ferramenta de calendário. Se ele disser 'preciso de uma senha', use a ferramenta de gerador de senhas. "
            "Quando lhe pedirem uma opinião, baseie-a nos fatos e no contexto que você tem, explicando o porquê de sua sugestão. "
            "Lembre-se de ser conciso e focado em soluções. "
            "Responda sempre em português brasileiro e explique brevemente o que está a fazer ao usar uma ferramenta."
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
            # Importar a função de salvar do módulo de persistência
            from core.persistence import save_context, save_chat_message

            # Atualizar contexto
            self.context.update_activity()
            
            # Salvar a mensagem do usuário no banco de dados
            save_chat_message(self.user_id, message, "user")
            
            # Executar agente
            result = await self.agent.run(message, deps=self.context)
            
            # Salvar a resposta do bot no banco de dados
            bot_response = str(result)
            save_chat_message(self.user_id, bot_response, "bot")

            # Salvar o contexto após cada interação para garantir persistência
            self.save_context()

            return bot_response

        except Exception as e:
            error_msg = f"❌ Erro no processamento: {str(e)}"
            print(error_msg)
            return "Desculpe, ocorreu um erro. Tente novamente."

    def save_context(self):
        """Salva o contexto atual no banco de dados"""
        # Importar aqui para evitar circular-import
        from core.persistence import save_context
        save_context(self.user_id, self.context)

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
