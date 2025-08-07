# 📁 tools/text_analyzer.py
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated
import re
from collections import Counter

def tool_metadata():
    return {
        "name": "text_analyzer",
        "description": "Analisador avançado de textos",
        "version": "1.5.0",
        "author": "NLP Team", 
        "category": "text"
    }

async def analyze_text(
    ctx: RunContext[ConversationContext],
    text: Annotated[str, "Texto para analisar"],
    analysis_type: Annotated[str, "Tipo: 'basic', 'detailed', 'sentiment', 'keywords'"] = "basic"
) -> str:
    """Analisa texto com diferentes níveis de profundidade"""
    
    if not text.strip():
        return "❌ Forneça um texto para analisar"
    
    if analysis_type == 'basic':
        return basic_analysis(text)
    elif analysis_type == 'detailed':
        return detailed_analysis(text)
    elif analysis_type == 'sentiment':
        return sentiment_analysis(text)
    elif analysis_type == 'keywords':
        return keyword_analysis(text)
    else:
        return "❌ Tipo de análise inválido. Use: basic, detailed, sentiment, keywords"

def basic_analysis(text: str) -> str:
    """Análise básica do texto"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    paragraphs = text.split('\n\n')
    
    chars_no_spaces = len(text.replace(' ', ''))
    
    return (
        f"📝 ANÁLISE BÁSICA:\n"
        f"   📊 Caracteres: {len(text)}\n"
        f"   🔤 Caracteres (sem espaços): {chars_no_spaces}\n"  
        f"   💬 Palavras: {len(words)}\n"
        f"   📄 Frases: {len([s for s in sentences if s.strip()])}\n"
        f"   📋 Parágrafos: {len([p for p in paragraphs if p.strip()])}\n"
        f"   ⏱️ Tempo de leitura: ~{max(1, len(words) // 200)} min"
    )

def detailed_analysis(text: str) -> str:
    """Análise detalhada do texto"""
    words = text.split()
    
    # Contagem de tipos de caracteres
    letters = sum(1 for c in text if c.isalpha())
    numbers = sum(1 for c in text if c.isdigit()) 
    spaces = sum(1 for c in text if c.isspace())
    punctuation = sum(1 for c in text if c in '.,!?;:"()[]{}')
    
    # Análise de palavras
    word_lengths = [len(w.strip('.,!?;:"()[]{}')) for w in words]
    avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
    
    # Palavras mais comuns
    word_freq = Counter(word.lower().strip('.,!?;:"()[]{}') for word in words)
    most_common = word_freq.most_common(5)
    
    return (
        f"📊 ANÁLISE DETALHADA:\n"
        f"   🔤 Letras: {letters}\n"
        f"   🔢 Números: {numbers}\n"
        f"   ⭐ Espaços: {spaces}\n"
        f"   📝 Pontuação: {punctuation}\n"
        f"   💬 Total de palavras: {len(words)}\n"
        f"   📏 Média de caracteres por palavra: {avg_word_length:.1f}\n"
        f"   📋 Palavra mais longa: {max(word_lengths) if word_lengths else 0} chars\n"
        f"   🏆 Palavras mais frequentes: {', '.join([f'{w}({c})' for w, c in most_common[:3]])}"
    )

def sentiment_analysis(text: str) -> str:
    """Análise de sentimento básica"""
    # Palavras positivas e negativas básicas em português
    positive_words = {
        'bom', 'boa', 'ótimo', 'ótima', 'excelente', 'maravilhoso', 'fantástico', 
        'incrível', 'perfeito', 'adorei', 'amei', 'feliz', 'alegre', 'satisfeito',
        'positivo', 'sucesso', 'vitória', 'conquistar', 'vencer', 'legal', 'massa'
    }
    
    negative_words = {
        'ruim', 'péssimo', 'péssima', 'horrível', 'terrível', 'odiei', 
        'detesto', 'triste', 'chateado', 'frustrado', 'negativo', 'fracasso',
        'derrota', 'perder', 'problema', 'erro', 'difícil', 'impossível'
    }
    
    words = [word.lower().strip('.,!?;:"()[]{}') for word in text.split()]
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    # Calcular sentimento
    if positive_count > negative_count:
        sentiment = "😊 Positivo"
        confidence = min(90, (positive_count / len(words)) * 100 + 60)
    elif negative_count > positive_count:
        sentiment = "😞 Negativo"  
        confidence = min(90, (negative_count / len(words)) * 100 + 60)
    else:
        sentiment = "😐 Neutro"
        confidence = 50
    
    return (
        f"💭 ANÁLISE DE SENTIMENTO:\n"
        f"   🎯 Sentimento: {sentiment}\n"
        f"   📊 Confiança: {confidence:.1f}%\n"
        f"   😊 Palavras positivas: {positive_count}\n"
        f"   😞 Palavras negativas: {negative_count}\n"
        f"   📝 Total analisado: {len(words)} palavras"
    )

def keyword_analysis(text: str) -> str:
    """Extrai palavras-chave do texto"""
    # Palavras irrelevantes (stop words) em português
    stop_words = {
        'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'com', 'por', 'para',
        'se', 'que', 'não', 'na', 'no', 'como', 'mas', 'ou', 'ao', 'até', 'dos',
        'das', 'seu', 'sua', 'seus', 'suas', 'ele', 'ela', 'eles', 'elas', 'isso',
        'isto', 'aquilo', 'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses',
        'essas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'ser', 'estar', 'ter',
        'haver', 'foi', 'são', 'está', 'tem', 'mais', 'muito', 'bem', 'já', 'só'
    }
    
    # Limpar e filtrar palavras
    words = [word.lower().strip('.,!?;:"()[]{}') for word in text.split()]
    filtered_words = [w for w in words if w and len(w) > 2 and w not in stop_words]
    
    # Contar frequências
    word_freq = Counter(filtered_words)
    
    # Palavras-chave (mais de 1 ocorrência)
    keywords = [(word, count) for word, count in word_freq.most_common() if count > 1]
    
    # Palavras únicas importantes (mais de 4 caracteres)
    unique_important = [word for word, count in word_freq.items() 
                       if count == 1 and len(word) > 4][:10]
    
    result = f"🔍 ANÁLISE DE PALAVRAS-CHAVE:\n"
    
    if keywords:
        result += f"   🏷️ Palavras-chave principais:\n"
        for word, count in keywords[:8]:
            result += f"      • {word} ({count}x)\n"
    
    if unique_important:
        result += f"   ✨ Termos únicos relevantes: {', '.join(unique_important[:5])}\n"
    
    result += f"   📊 Vocabulário único: {len(word_freq)} palavras distintas\n"
    result += f"   🎯 Densidade de palavras-chave: {len(keywords)}/{len(filtered_words)}"
    
    return result

analyze_text.__tool_metadata__ = tool_metadata()

# ========================
