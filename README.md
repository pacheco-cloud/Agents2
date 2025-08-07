# 🤖 ChatBot Modular com PydanticAI

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
    """O que a ferramenta faz"""
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
