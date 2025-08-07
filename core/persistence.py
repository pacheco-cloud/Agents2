# 📁 core/persistence.py
import json
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json
from models.context import ConversationContext, SessionData, UserPreferences

# Classe customizada para serializar objetos datetime para JSON
class DateTimeEncoder(json.JSONEncoder):
    """
    JSON Encoder que lida com objetos datetime.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def get_db_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados PostgreSQL.
    As credenciais são lidas de variáveis de ambiente.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'chatbot_db'),
            user=os.getenv('DB_USER', 'user'),
            password=os.getenv('DB_PASSWORD', 'password'),
            port=os.getenv('DB_PORT', '5432')
        )
        print("🔗 Conexão com o banco de dados estabelecida com sucesso!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        raise

def create_tables_if_not_exists():
    """
    Cria as tabelas necessárias no banco de dados se elas ainda não existirem.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Tabela para armazenar o contexto do usuário
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_contexts (
                user_id VARCHAR(255) PRIMARY KEY,
                user_preferences JSONB,
                session_data JSONB,
                custom_data JSONB,
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        
        # Tabela para histórico de conversas
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) REFERENCES user_contexts(user_id) ON DELETE CASCADE,
                message_text TEXT NOT NULL,
                sender VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        
        conn.commit()
        print("✅ Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def save_context(user_id: str, context: ConversationContext):
    """
    Salva o estado atual do ConversationContext para um user_id específico no PostgreSQL.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        user_preferences_json = json.dumps(context.user_preferences.model_dump(), cls=DateTimeEncoder)
        session_data_json = json.dumps(context.session_data.model_dump(), cls=DateTimeEncoder)
        custom_data_json = json.dumps(context.custom_data, cls=DateTimeEncoder)
        
        cur.execute(
            """
            INSERT INTO user_contexts (user_id, user_preferences, session_data, custom_data)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET user_preferences = EXCLUDED.user_preferences,
                session_data = EXCLUDED.session_data,
                custom_data = EXCLUDED.custom_data,
                last_updated = CURRENT_TIMESTAMP;
            """,
            (user_id, Json(user_preferences_json), Json(session_data_json), Json(custom_data_json))
        )
        conn.commit()
        print(f"💾 Contexto do usuário '{user_id}' salvo com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao salvar contexto do usuário '{user_id}': {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def load_context(user_id: str) -> ConversationContext:
    """
    Carrega o ConversationContext para um user_id específico do PostgreSQL.
    Retorna um novo ConversationContext se não encontrar dados.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT user_preferences, session_data, custom_data FROM user_contexts WHERE user_id = %s;",
            (user_id,)
        )
        record = cur.fetchone()
        
        if record:
            user_preferences_data, session_data_data, custom_data = record
            print(f"🔄 Contexto do usuário '{user_id}' carregado com sucesso.")

            if isinstance(user_preferences_data, str):
                user_preferences_data = json.loads(user_preferences_data)
            if isinstance(session_data_data, str):
                session_data_data = json.loads(session_data_data)
            if isinstance(custom_data, str):
                custom_data = json.loads(custom_data)

            user_preferences = UserPreferences(**user_preferences_data)
            session_data = SessionData(**session_data_data)
            
            context = ConversationContext(
                user_id=user_id,
                user_preferences=user_preferences,
                session_data=session_data,
                custom_data=custom_data
            )
            return context
        else:
            print(f"🆕 Nenhum contexto encontrado para o usuário '{user_id}'. Criando novo.")
            return ConversationContext(user_id=user_id)
    except Exception as e:
        print(f"❌ Erro ao carregar contexto do usuário '{user_id}': {e}")
        return ConversationContext(user_id=user_id) 
    finally:
        if conn:
            conn.close()

def save_chat_message(user_id: str, message: str, sender: str):
    """
    Salva uma mensagem de conversa no histórico do banco de dados.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_history (user_id, message_text, sender) VALUES (%s, %s, %s);",
            (user_id, message, sender)
        )
        conn.commit()
    except Exception as e:
        print(f"❌ Erro ao salvar mensagem no histórico: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def load_chat_history(user_id: str, limit: int = 10) -> list:
    """
    Carrega as últimas N mensagens de conversa do banco de dados para um usuário.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT message_text, sender FROM chat_history WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s;",
            (user_id, limit)
        )
        messages = cur.fetchall()
        
        # O resultado vem em ordem decrescente, então inverta para que a conversa seja cronológica
        history = [{"sender": row[1], "message_text": row[0]} for row in reversed(messages)]
        return history
    except Exception as e:
        print(f"❌ Erro ao carregar histórico de conversa: {e}")
        return []
    finally:
        if conn:
            conn.close()
