# 📁 core/tool_registry.py
from typing import Dict, Callable, List, Any
from pydantic_ai import Agent
import importlib
import os
import inspect
from pathlib import Path

class ToolRegistry:
    """Registry para gerenciar ferramentas dinamicamente"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, name: str, func: Callable, metadata: Dict[str, Any] = None):
        """Registra uma ferramenta manualmente"""
        self.tools[name] = func
        self.tool_metadata[name] = metadata or {}
        print(f"🔧 Ferramenta registrada: {name}")
    
    def auto_discover_tools(self, tools_directory: str = "tools") -> List[str]:
        """Descobre e carrega ferramentas automaticamente"""
        discovered = []
        tools_path = Path(tools_directory)
        
        if not tools_path.exists():
            print(f"⚠️  Diretório {tools_directory} não encontrado")
            return discovered
        
        # Buscar arquivos Python no diretório
        for file_path in tools_path.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
                
            module_name = f"{tools_directory}.{file_path.stem}"
            try:
                # Importar módulo
                module = importlib.import_module(module_name)
                
                # Buscar funções que são ferramentas
                for name, obj in inspect.getmembers(module):
                    if (inspect.isfunction(obj) and 
                        hasattr(obj, '__tool_metadata__')):
                        
                        self.register_tool(
                            name, 
                            obj, 
                            getattr(obj, '__tool_metadata__', {})
                        )
                        discovered.append(name)
                        
            except ImportError as e:
                print(f"❌ Erro ao carregar {module_name}: {e}")
        
        return discovered
    
    def attach_tools_to_agent(self, agent: Agent):
        """Anexa todas as ferramentas registradas ao agente"""
        for name, tool_func in self.tools.items():
            # O decorador @agent.tool é aplicado dinamicamente
            agent.tool(tool_func)
            print(f"✅ Ferramenta {name} anexada ao agente")
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """Lista todas as ferramentas disponíveis"""
        return {
            name: {
                "function": func.__name__,
                "doc": func.__doc__ or "Sem descrição",
                "metadata": self.tool_metadata.get(name, {})
            }
            for name, func in self.tools.items()
        }

# Instância global do registry
tool_registry = ToolRegistry()

# ========================
