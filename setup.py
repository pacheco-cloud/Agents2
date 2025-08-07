# 📁 setup.py - Script de configuração inicial
import os
import sys
from pathlib import Path

def create_directory_structure():
    """Cria estrutura de diretórios do projeto"""
    
    directories = [
        "config",
        "core", 
        "models",
        "tools",
        "tests",
        "logs",
        "data"
    ]
    
    print("🏗️ Criando estrutura de diretórios...")
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"   📁 {dir_name}/")
        
        # Criar __init__.py para tornar diretórios em pacotes Python
        if dir_name not in ['logs', 'data']:
            init_file = Path(dir_name) / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# -*- coding: utf-8 -*-\n")
    
    print("✅ Estrutura criada com sucesso!")

def create_env_file():
    """Cria arquivo .env se não existir"""
    env_file = Path(".env")
    
    if not env_file.exists():
        env_content = """# Configuração do ChatBot Modular
OPENAI_API_KEY=your_openai_api_key_here

# Configurações opcionais
AGENT_MODEL=openai:gpt-3.5-turbo
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=300

# Logs
LOG_LEVEL=INFO
LOG_FILE=logs/chatbot.log

# Tools
TOOLS_AUTO_DISCOVERY=true
TOOLS_DIRECTORY=tools
"""
        env_file.write_text(env_content)
        print("📝 Arquivo .env criado - Configure sua OPENAI_API_KEY!")
    else:
        print("ℹ️ Arquivo .env já existe")

def create_requirements():
    """Cria requirements.txt atualizado"""
    requirements = """# Core dependencies
pydantic-ai>=0.0.14
openai>=1.0.0
python-dotenv>=1.0.0

# Optional dependencies for advanced features
requests>=2.31.0
asyncio-mqtt>=0.16.0
schedule>=1.2.0

# Development dependencies
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
flake8>=6.0.0

# Logging
colorlog>=6.7.0
"""
    
    Path("requirements.txt").write_text(requirements)
    print("📋 requirements.txt atualizado")

def create_gitignore():
    """Cria .gitignore se não existir"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Data
data/
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db

# ChatBot specific
user_data/
chat_history/
temp/
"""
    
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        gitignore_file.write_text(gitignore_content)
        print("🚫 .gitignore criado")
    else:
        print("ℹ️ .gitignore já existe")

def create_readme():
    """Cria README.md do projeto"""
    readme_content = """# 🤖 ChatBot Modular com PydanticAI

Um chatbot inteligente e modular construído com PydanticAI, seguindo arquitetura de microserviços.

## ✨ Características

- 🧩 **Arquitetura Modular**: Cada ferramenta em arquivo separado
- 🔧 **Auto-descoberta**: Carregamento automático de ferramentas
- 💾 **Contexto Persistente**: Memória durante a sessão
- 🎯 **Type Safety**: Validação completa com Pydantic
- 🔄 **Hot Reload**: Adicione ferramentas sem reiniciar

## 🚀 Instalação Rápida

```bash
# 1. Clonar e configurar
git clone <repo_url>
cd chatbot-modular

# 2. Executar setup
python setup.py

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar API Key
# Edite o arquivo .env e adicione sua OPENAI_API_KEY

# 5. Executar
python main.py
```

## 🛠️ Ferramentas Disponíveis

- 🧮 **Calculadora**: Operações matemáticas avançadas
- 🔐 **Gerador de Senhas**: Senhas seguras personalizáveis
- 📝 **Gerenciador de Tarefas**: TO-DO list com prioridades
- 📊 **Analisador de Texto**: Análise completa de textos
- 🔄 **Conversor de Unidades**: Conversões universais

## 🔧 Criando Nova Ferramenta

1. Crie arquivo em `tools/minha_ferramenta.py`
2. Implemente seguindo o padrão:

```python
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated

def tool_metadata():
    return {
        "name": "minha_ferramenta",
        "description": "Descrição da ferramenta", 
        "version": "1.0.0",
        "category": "categoria"
    }

async def minha_funcao(
    ctx: RunContext[ConversationContext],
    parametro: Annotated[str, "Descrição do parâmetro"]
) -> str:
    \"\"\"O que a ferramenta faz\"\"\"
    # Sua lógica aqui
    return "Resultado"

minha_funcao.__tool_metadata__ = tool_metadata()
```

3. Reinicie o bot - será carregada automaticamente!

## 📁 Estrutura do Projeto

```
chatbot-modular/
├── config/          # Configurações
├── core/            # Core do sistema
├── models/          # Modelos Pydantic
├── tools/           # Ferramentas (microserviços)
├── tests/           # Testes automatizados
├── logs/            # Arquivos de log
├── data/            # Dados persistentes
├── main.py          # Aplicação principal
├── setup.py         # Script de configuração
└── requirements.txt # Dependências
```

## 🎯 Comandos Disponíveis

- `sair` - Encerrar chatbot
- `stats` - Estatísticas da sessão
- `tools` - Listar ferramentas disponíveis
- `context` - Ver contexto atual

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes específicos
pytest tests/test_tools.py
```

## 📈 Roadmap

- [ ] Interface web com FastAPI
- [ ] Persistência em banco de dados
- [ ] Sistema de plugins
- [ ] API REST para ferramentas
- [ ] Dashboard de monitoramento
- [ ] Deploy com Docker

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch
3. Adicione testes para novas ferramentas
4. Commit suas mudanças
5. Abra um Pull Request

## 📄 Licença

MIT License - veja LICENSE file para detalhes.

---

**Feito com ❤️ e PydanticAI**
"""
    
    Path("README.md").write_text(readme_content)
    print("📖 README.md criado")

def main():
    """Executa setup completo do projeto"""
    print("🚀 SETUP DO CHATBOT MODULAR")
    print("="*50)
    
    try:
        create_directory_structure()
        create_env_file()
        create_requirements()
        create_gitignore() 
        create_readme()
        
        print("\n" + "="*50)
        print("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("="*50)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Configure sua OPENAI_API_KEY no arquivo .env")
        print("2. Execute: pip install -r requirements.txt")
        print("3. Execute: python main.py")
        print("\n🎯 Para criar nova ferramenta:")
        print("   - Adicione arquivo em tools/")
        print("   - Siga o padrão dos exemplos")
        print("   - Reinicie o bot")
        
    except Exception as e:
        print(f"❌ Erro durante setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# ========================
# 📁 tools/__init__.py
"""
Módulo de ferramentas do ChatBot Modular

Este módulo contém todas as ferramentas disponíveis para o agente.
Novas ferramentas são automaticamente descobertas e carregadas.
"""

# Lista de ferramentas disponíveis (atualizada automaticamente)
AVAILABLE_TOOLS = [
    "calculator",
    "password_generator", 
    "task_manager",
    "text_analyzer",
    "unit_converter"
]

# Metadados das categorias
TOOL_CATEGORIES = {
    "math": "🧮 Ferramentas Matemáticas",
    "security": "🔐 Ferramentas de Segurança", 
    "productivity": "📋 Ferramentas de Produtividade",
    "text": "📝 Ferramentas de Texto",
    "utilities": "🔧 Utilitários Gerais"
}

def get_tools_by_category():
    """Retorna ferramentas agrupadas por categoria"""
    # Esta função seria implementada para organizar ferramentas
    return TOOL_CATEGORIES

# ========================
# 📁 tests/test_tools.py
import pytest
import asyncio
from unittest.mock import Mock
from models.context import ConversationContext

# Importar ferramentas para teste
from tools.calculator import calculate
from tools.password_generator import generate_password
from tools.task_manager import manage_task

class TestCalculator:
    """Testes para a calculadora"""
    
    @pytest.fixture
    def mock_context(self):
        """Contexto mock para testes"""
        ctx = Mock()
        ctx.deps = ConversationContext()
        return ctx
    
    @pytest.mark.asyncio
    async def test_basic_calculation(self, mock_context):
        """Testa cálculo básico"""
        result = await calculate(mock_context, "2 + 2")
        assert "4" in result
        assert "🧮" in result
    
    @pytest.mark.asyncio
    async def test_invalid_expression(self, mock_context):
        """Testa expressão inválida"""
        result = await calculate(mock_context, "invalid")
        assert "❌" in result

class TestPasswordGenerator:
    """Testes para gerador de senhas"""
    
    @pytest.fixture
    def mock_context(self):
        ctx = Mock()
        ctx.deps = ConversationContext()
        return ctx
    
    @pytest.mark.asyncio
    async def test_password_generation(self, mock_context):
        """Testa geração de senha"""
        result = await generate_password(mock_context, 12, True, True, True)
        assert "🔐" in result
        assert "12 caracteres" in result
    
    @pytest.mark.asyncio
    async def test_invalid_length(self, mock_context):
        """Testa tamanho inválido"""
        result = await generate_password(mock_context, 200, True, True, True)
        assert "❌" in result

class TestTaskManager:
    """Testes para gerenciador de tarefas"""
    
    @pytest.fixture
    def mock_context(self):
        ctx = Mock()
        ctx.deps = ConversationContext()
        return ctx
    
    @pytest.mark.asyncio
    async def test_add_task(self, mock_context):
        """Testa adição de tarefa"""
        result = await manage_task(mock_context, "add", "Tarefa teste", 0, "high")
        assert "✅" in result
        assert "Tarefa teste" in result
    
    @pytest.mark.asyncio
    async def test_list_empty_tasks(self, mock_context):
        """Testa listagem quando vazia"""
        result = await manage_task(mock_context, "list")
        assert "📝 Nenhuma tarefa" in result

# Para executar: pytest tests/test_tools.py -v

# ========================
# 📁 run_tests.py - Script para executar testes
import subprocess
import sys
from pathlib import Path