# 📁 tools/calculator.py
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated

def tool_metadata():
    """Metadados da ferramenta"""
    return {
        "name": "calculator",
        "description": "Calculadora matemática avançada",
        "version": "1.0.0",
        "author": "ChatBot Team",
        "category": "math"
    }

async def calculate(
    ctx: RunContext[ConversationContext],
    expression: Annotated[str, "Expressão matemática para calcular (ex: 2+2, sqrt(16), sin(30)"]
) -> str:
    """Calcula expressões matemáticas básicas e avançadas"""
    import math
    import re
    
    try:
        # Limpar expressão
        expression = expression.replace(" ", "").lower()
        
        # Substituir funções matemáticas
        replacements = {
            'sqrt': 'math.sqrt',
            'sin': 'math.sin', 'cos': 'math.cos', 'tan': 'math.tan',
            'log': 'math.log', 'ln': 'math.log',
            'pi': 'math.pi', 'e': 'math.e',
            '^': '**'  # Exponenciação
        }
        
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        
        # Validar caracteres permitidos
        allowed = set('0123456789+-*/().mathsqrtincoslogatnpe ')
        if not all(c in allowed for c in expression):
            return "❌ Operação não permitida. Use apenas números e funções matemáticas básicas."
        
        # Calcular
        result = eval(expression)
        
        # Salvar no histórico do usuário
        history = ctx.deps.get_user_data('calc_history', [])
        history.append({
            'expression': expression,
            'result': result,
            'timestamp': str(datetime.now())
        })
        ctx.deps.set_user_data('calc_history', history[-10:])  # Manter apenas 10
        
        return f"🧮 {expression} = {result}"
        
    except Exception as e:
        return f"❌ Erro no cálculo: {str(e)}"

# Marcar função como ferramenta
calculate.__tool_metadata__ = tool_metadata()

# ========================
