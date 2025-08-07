# 📁 tools/unit_converter.py
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated, Dict, Callable
import math

def tool_metadata():
    return {
        "name": "unit_converter",
        "description": "Conversor universal de unidades",
        "version": "2.1.0",
        "author": "Math Team",
        "category": "utilities"
    }

async def convert_units(
    ctx: RunContext[ConversationContext],
    value: Annotated[float, "Valor a converter"],
    from_unit: Annotated[str, "Unidade de origem"],
    to_unit: Annotated[str, "Unidade de destino"],
    precision: Annotated[int, "Casas decimais (0-10)"] = 4
) -> str:
    """Converte entre diferentes tipos de unidades"""
    
    if precision < 0 or precision > 10:
        precision = 4
    
    # Dicionário com todas as conversões
    conversions = get_conversion_table()
    
    # Normalizar nomes das unidades
    from_unit = normalize_unit_name(from_unit)
    to_unit = normalize_unit_name(to_unit)
    
    # Verificar se conversão existe
    conversion_key = (from_unit, to_unit)
    
    if conversion_key in conversions:
        # Conversão direta
        result = conversions[conversion_key](value)
        category = get_unit_category(from_unit)
    else:
        # Tentar conversão via unidade base
        base_conversions = find_base_conversion(from_unit, to_unit, conversions)
        if base_conversions:
            result = base_conversions(value)
            category = get_unit_category(from_unit)
        else:
            return (f"❌ Conversão não suportada: {from_unit} → {to_unit}\n"
                   f"💡 Use 'listar conversoes' para ver opções disponíveis")
    
    # Salvar no histórico
    history = ctx.deps.get_user_data('conversion_history', [])
    history.append({
        'from': f"{value} {from_unit}",
        'to': f"{result} {to_unit}",
        'category': category,
        'timestamp': str(datetime.now())
    })
    ctx.deps.set_user_data('conversion_history', history[-20:])  # Manter 20
    
    # Informações extras baseadas na categoria
    extra_info = get_category_info(category, result, to_unit)
    
    return (
        f"🔄 CONVERSÃO {category.upper()}:\n"
        f"   📊 {value} {from_unit} = {result:.{precision}f} {to_unit}\n"
        f"{extra_info}"
        f"   📈 Conversões realizadas: {len(history)}"
    )

def get_conversion_table() -> Dict[tuple, Callable]:
    """Retorna tabela completa de conversões"""
    return {
        # DISTÂNCIA
        ('km', 'milhas'): lambda x: x * 0.621371,
        ('milhas', 'km'): lambda x: x * 1.60934,
        ('m', 'ft'): lambda x: x * 3.28084,
        ('ft', 'm'): lambda x: x * 0.3048,
        ('cm', 'in'): lambda x: x * 0.393701,
        ('in', 'cm'): lambda x: x * 2.54,
        ('km', 'm'): lambda x: x * 1000,
        ('m', 'km'): lambda x: x / 1000,
        ('m', 'cm'): lambda x: x * 100,
        ('cm', 'm'): lambda x: x / 100,
        
        # TEMPERATURA
        ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
        ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
        ('celsius', 'kelvin'): lambda x: x + 273.15,
        ('kelvin', 'celsius'): lambda x: x - 273.15,
        ('fahrenheit', 'kelvin'): lambda x: (x - 32) * 5/9 + 273.15,
        ('kelvin', 'fahrenheit'): lambda x: (x - 273.15) * 9/5 + 32,
        
        # PESO
        ('kg', 'lb'): lambda x: x * 2.20462,
        ('lb', 'kg'): lambda x: x * 0.453592,
        ('g', 'oz'): lambda x: x * 0.035274,
        ('oz', 'g'): lambda x: x * 28.3495,
        ('kg', 'g'): lambda x: x * 1000,
        ('g', 'kg'): lambda x: x / 1000,
        ('ton', 'kg'): lambda x: x * 1000,
        ('kg', 'ton'): lambda x: x / 1000,
        
        # VOLUME
        ('l', 'gal'): lambda x: x * 0.264172,
        ('gal', 'l'): lambda x: x * 3.78541,
        ('ml', 'floz'): lambda x: x * 0.033814,
        ('floz', 'ml'): lambda x: x * 29.5735,
        ('l', 'ml'): lambda x: x * 1000,
        ('ml', 'l'): lambda x: x / 1000,
        
        # ÁREA
        ('m2', 'ft2'): lambda x: x * 10.7639,
        ('ft2', 'm2'): lambda x: x * 0.092903,
        ('km2', 'milha2'): lambda x: x * 0.386102,
        ('milha2', 'km2'): lambda x: x * 2.58999,
        
        # VELOCIDADE
        ('kmh', 'mph'): lambda x: x * 0.621371,
        ('mph', 'kmh'): lambda x: x * 1.60934,
        ('ms', 'kmh'): lambda x: x * 3.6,
        ('kmh', 'ms'): lambda x: x / 3.6,
        
        # PRESSÃO
        ('bar', 'psi'): lambda x: x * 14.5038,
        ('psi', 'bar'): lambda x: x * 0.0689476,
        ('atm', 'bar'): lambda x: x * 1.01325,
        ('bar', 'atm'): lambda x: x * 0.986923,
        
        # ENERGIA
        ('cal', 'j'): lambda x: x * 4.184,
        ('j', 'cal'): lambda x: x * 0.239006,
        ('kwh', 'j'): lambda x: x * 3600000,
        ('j', 'kwh'): lambda x: x / 3600000,
    }

def normalize_unit_name(unit: str) -> str:
    """Normaliza nome da unidade"""
    unit = unit.lower().strip()
    
    # Aliases comuns
    aliases = {
        'quilometros': 'km', 'kilometros': 'km', 'quilômetros': 'km',
        'metros': 'm', 'centimetros': 'cm', 'centímetros': 'cm',
        'milhas': 'milhas', 'pes': 'ft', 'pés': 'ft', 'polegadas': 'in',
        'graus': 'celsius', '°c': 'celsius', '°f': 'fahrenheit', '°k': 'kelvin',
        'quilos': 'kg', 'kilos': 'kg', 'gramas': 'g', 'libras': 'lb',
        'litros': 'l', 'mililitros': 'ml', 'galoes': 'gal', 'galões': 'gal',
        'metro quadrado': 'm2', 'quilometro quadrado': 'km2',
        'quilômetro por hora': 'kmh', 'metros por segundo': 'ms',
        'calorias': 'cal', 'joules': 'j', 'quilowatt hora': 'kwh'
    }
    
    return aliases.get(unit, unit)

def get_unit_category(unit: str) -> str:
    """Retorna categoria da unidade"""
    categories = {
        'distância': ['km', 'milhas', 'm', 'ft', 'cm', 'in'],
        'temperatura': ['celsius', 'fahrenheit', 'kelvin'],
        'peso': ['kg', 'lb', 'g', 'oz', 'ton'],
        'volume': ['l', 'gal', 'ml', 'floz'],
        'área': ['m2', 'ft2', 'km2', 'milha2'],
        'velocidade': ['kmh', 'mph', 'ms'],
        'pressão': ['bar', 'psi', 'atm'],
        'energia': ['cal', 'j', 'kwh']
    }
    
    for category, units in categories.items():
        if unit in units:
            return category
    return 'geral'

def find_base_conversion(from_unit: str, to_unit: str, conversions: Dict) -> Callable:
    """Encontra conversão via unidade base"""
    # Implementação simplificada - poderia ser mais robusta
    return None

def get_category_info(category: str, value: float, unit: str) -> str:
    """Retorna informações extras baseadas na categoria"""
    if category == 'temperatura':
        if unit == 'celsius':
            if value < 0: info = "❄️ Abaixo do congelamento"
            elif value > 100: info = "🔥 Acima da fervura"
            elif 20 <= value <= 25: info = "🌡️ Temperatura ambiente ideal"
            else: info = ""
        else: info = ""
    elif category == 'distância' and unit == 'km':
        if value > 40000: info = "🌍 Mais que uma volta na Terra"
        elif value > 1000: info = "✈️ Distância de viagem longa"
        else: info = ""
    elif category == 'peso' and unit == 'kg':
        if value > 1000: info = "🚛 Peso de veículo"
        elif value < 0.001: info = "⚖️ Peso microscópico"
        else: info = ""
    else:
        info = ""
    
    return f"   💡 {info}\n" if info else ""

convert_units.__tool_metadata__ = tool_metadata()

# Lista todas as ferramentas para facilitar importação
__all__ = ['calculate', 'generate_password', 'manage_task', 'analyze_text', 'convert_units']