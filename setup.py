# 📁 setup.py - Script de configuração inicial
import os
import sys
from pathlib import Path
import json
import subprocess # Importar para executar comandos externos
from dotenv import load_dotenv, set_key

# Adicionar diretório raiz ao sys.path para importações relativas
sys.path.append(str(Path(__file__).parent))

# Importar create_tables_if_not_exists do core/persistence.py
# Fazer um import condicional para não quebrar se o arquivo não existir ainda
try:
    from core.persistence import create_tables_if_not_exists
except ImportError:
    print("⚠️ Módulo persistence não encontrado, a criação de tabelas não será executada.")
    create_tables_if_not_exists = None

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
    """Cria arquivo .env se não existir e adiciona variáveis padrão."""
    env_file = Path(".env")
    
    # Carrega o .env existente para não apagar variáveis já configuradas
    load_dotenv(dotenv_path=env_file)

    initial_env_content = {
        "OPENAI_API_KEY": "your_openai_api_key_here",
        "AGENT_MODEL": "openai:gpt-3.5-turbo",
        "AGENT_TEMPERATURE": "0.7",
        "AGENT_MAX_TOKENS": "300",
        "LOG_LEVEL": "INFO",
        "LOG_FILE": "logs/chatbot.log",
        "TOOLS_AUTO_DISCOVERY": "true",
        "TOOLS_DIRECTORY": "tools",
        # Novas variáveis para o PostgreSQL
        "DB_HOST": "localhost",
        "DB_NAME": "chatbot_db",
        "DB_USER": "chatbot_user",
        "DB_PASSWORD": "password",
        "DB_PORT": "5432"
    }

    # Adiciona variáveis ao .env se não existirem
    updated = False
    for key, value in initial_env_content.items():
        if os.getenv(key) is None:
            set_key(env_file, key, value)
            updated = True
            print(f"   📝 Adicionando ao .env: {key}={value}")
    
    if not env_file.exists():
        env_file.touch()
        print("📝 Arquivo .env criado - Configure sua OPENAI_API_KEY!")
    elif updated:
        print("📝 Arquivo .env atualizado com novas variáveis!")
    else:
        print("ℹ️ Arquivo .env já existe e está atualizado com as variáveis padrão.")


def create_requirements():
    """Cria requirements.txt atualizado"""
    requirements = """# Core dependencies
pydantic-ai>=0.0.14
openai>=1.0.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.0

# Google Calendar API
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.2.0

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

# Timezone support
pytz>=2023.3
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
parts/sdist/
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

def install_dependencies():
    """
    Instala as dependências listadas no requirements.txt.
    """
    print("\n📦 Instalando dependências do requirements.txt...")
    try:
        # Usamos sys.executable para garantir que o pip do ambiente virtual seja usado
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True, capture_output=True, text=True)
        print("   ✅ Dependências instaladas com sucesso!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 'pip' não encontrado. Certifique-se de que o Python e o pip estão no PATH.")
        sys.exit(1)

def setup_database():
    """
    Configura o banco de dados PostgreSQL: cria o usuário e o banco de dados,
    e então cria as tabelas definidas no módulo de persistência.
    """
    # Importações movidas para dentro da função para serem executadas após a instalação
    import psycopg2
    from psycopg2 import sql

    print("\n📦 Configurando banco de dados PostgreSQL...")
    load_dotenv() # Garante que as variáveis de ambiente do .env sejam carregadas
    
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'chatbot_db')
    db_user = os.getenv('DB_USER', 'chatbot_user')
    db_password = os.getenv('DB_PASSWORD', 'password')

    conn_admin = None
    try:
        conn_admin = psycopg2.connect(
            host=db_host,
            database='postgres',
            user='postgres',
            password=os.getenv('POSTGRES_SUPERUSER_PASSWORD', 'your_postgres_superuser_password'),
            port=db_port
        )
        conn_admin.autocommit = True
        cur_admin = conn_admin.cursor()

        # 1. Criar o usuário para a aplicação se não existir
        cur_admin.execute(f"SELECT 1 FROM pg_user WHERE usename = '{db_user}';")
        if not cur_admin.fetchone():
            cur_admin.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s;").format(sql.Identifier(db_user)), (db_password,))
            print(f"   ✅ Usuário '{db_user}' criado.")
        else:
            print(f"   ℹ️ Usuário '{db_user}' já existe.")
        
        # 2. Criar o banco de dados se não existir
        cur_admin.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        if not cur_admin.fetchone():
            cur_admin.execute(sql.SQL("CREATE DATABASE {} OWNER {};").format(sql.Identifier(db_name), sql.Identifier(db_user)))
            print(f"   ✅ Banco de dados '{db_name}' criado e atribuído a '{db_user}'.")
        else:
            print(f"   ℹ️ Banco de dados '{db_name}' já existe.")

        print("   🔗 Testando conexão com o novo banco de dados...")
        if conn_admin:
            conn_admin.close()
        
        if create_tables_if_not_exists:
            create_tables_if_not_exists()

        print("✅ Configuração do banco de dados concluída!")

    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão ao PostgreSQL. Certifique-se de que o servidor está rodando e o usuário 'postgres' tem a senha correta configurada no .env (POSTGRES_SUPERUSER_PASSWORD).\nDetalhes: {e}")
        print("   💡 Para sistemas baseados em Linux, pode ser necessário configurar a senha do usuário 'postgres':")
        print("      1. sudo -u postgres psql")
        print("      2. ALTER USER postgres WITH PASSWORD 'your_postgres_superuser_password';")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado durante a configuração do banco de dados: {e}")
        sys.exit(1)
    finally:
        if conn_admin:
            conn_admin.close()


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
        
        install_dependencies() # AQUI INSTALAMOS AS DEPENDENCIAS PRIMEIRO

        setup_database() # E SÓ DEPOIS CONFIGURAMOS O BANCO DE DADOS
        
        print("\n" + "="*50)
        print("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("="*50)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Configure sua OPENAI_API_KEY no arquivo .env (se ainda não o fez).")
        print("2. Verifique e, se necessário, configure a 'POSTGRES_SUPERUSER_PASSWORD' no .env.")
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
