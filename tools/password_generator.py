# 📁 tools/password_generator.py
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated
import string
import random
import secrets

def tool_metadata():
    return {
        "name": "password_generator", 
        "description": "Gerador de senhas seguras",
        "version": "1.2.0",
        "author": "Security Team",
        "category": "security"
    }

async def generate_password(
    ctx: RunContext[ConversationContext],
    length: Annotated[int, "Tamanho da senha (4-128)"] = 12,
    include_symbols: Annotated[bool, "Incluir símbolos especiais"] = True,
    include_numbers: Annotated[bool, "Incluir números"] = True,
    exclude_ambiguous: Annotated[bool, "Excluir caracteres ambíguos (0,O,l,1)"] = True
) -> str:
    """Gera senhas seguras com opções personalizáveis"""
    
    if length < 4 or length > 128:
        return "❌ Tamanho deve ser entre 4 e 128 caracteres"
    
    # Base de caracteres
    chars = string.ascii_letters
    
    if include_numbers:
        chars += string.digits
    
    if include_symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    # Remover caracteres ambíguos se solicitado
    if exclude_ambiguous:
        ambiguous = "0O1lI"
        chars = ''.join(c for c in chars if c not in ambiguous)
    
    # Gerar senha usando secrets (mais seguro)
    password = ''.join(secrets.choice(chars) for _ in range(length))
    
    # Calcular força da senha
    strength = calculate_strength(password, length, include_numbers, include_symbols)
    
    # Salvar estatística
    stats = ctx.deps.get_user_data('password_stats', {'generated': 0, 'total_length': 0})
    stats['generated'] += 1
    stats['total_length'] += length
    ctx.deps.set_user_data('password_stats', stats)
    
    return (
        f"🔐 Senha gerada: `{password}`\n"
        f"💪 Força: {strength}\n"
        f"📏 Comprimento: {length} caracteres\n"
        f"📊 Total gerado nesta sessão: {stats['generated']}"
    )

def calculate_strength(password: str, length: int, has_numbers: bool, has_symbols: bool) -> str:
    """Calcula força da senha"""
    score = 0
    
    if length >= 12: score += 2
    elif length >= 8: score += 1
    
    if has_numbers: score += 1
    if has_symbols: score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.islower() for c in password): score += 1
    
    if score >= 6: return "🔴 Muito Forte"
    elif score >= 4: return "🟡 Forte"  
    elif score >= 2: return "🟠 Média"
    else: return "🔴 Fraca"

generate_password.__tool_metadata__ = tool_metadata()

# ========================
