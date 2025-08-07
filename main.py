# 📁 main.py - Aplicação Principal com Memória de Longo Prazo
import asyncio
from core.agent_manager import AgentManager
from core.tool_registry import tool_registry
import os
from core.persistence import create_tables_if_not_exists # Importar a função de criação de tabelas

async def main():
    """Aplicação principal do chatbot modular"""
    
    print("🚀 ChatBot Modular com Memória de Longo Prazo")
    print("="*50)
    
    # === AQUI VEM A ALTERAÇÃO ===
    # Garante que as tabelas existem antes de tentar usar o banco de dados
    create_tables_if_not_exists()
    
    # Em uma aplicação real, você obteria o user_id de um sistema de autenticação.
    # Por agora, usaremos um ID de exemplo.
    user_id = os.getenv("CHATBOT_USER_ID", "default_user_123")
    print(f"🆔 A sessão será executada com o User ID: {user_id}")
    print("==================================================")
    
    try:
        # Inicializar gerenciador do agente
        manager = AgentManager(user_id=user_id)
        
        # Mostrar ferramentas disponíveis
        tools_list = tool_registry.list_tools()
        print("\n🛠️  Ferramentas Disponíveis:")
        for name, info in tools_list.items():
            print(f"   • {name}: {info['doc'][:50]}...")
        
        print("\n" + "="*50)
        print("Digite 'sair' para encerrar")
        print("Digite 'stats' para ver estatísticas")
        print("Digite 'tools' para listar ferramentas")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return
    
    # Loop principal
    while True:
        try:
            user_input = input("\n🧑 Você: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'sair':
                stats = manager.get_stats()
                print(f"\n📊 Estatísticas da sessão:")
                for key, value in stats.items():
                    print(f"   • {key}: {value}")
                
                # Salvar o contexto antes de sair
                manager.save_context() 
                print("👋 Obrigado por usar o ChatBot! Contexto salvo.")
                break
                
            elif user_input.lower() == 'stats':
                stats = manager.get_stats()
                print(f"\n📊 Estatísticas:")
                for key, value in stats.items():
                    print(f"   • {key}: {value}")
                continue
                
            elif user_input.lower() == 'tools':
                tools_list = tool_registry.list_tools()
                print(f"\n🔧 Ferramentas ({len(tools_list)}):")
                for name, info in tools_list.items():
                    print(f"   • {name}: {info['doc']}")
                continue
            
            # Processar mensagem
            print("🤖 Processando...")
            response = await manager.chat(user_input)
            print(f"🤖 Bot: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Encerrando...")
            # Salvar o contexto antes de sair
            manager.save_context() 
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

def run():
    """Ponto de entrada da aplicação"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 ChatBot encerrado!")

if __name__ == "__main__":
    run()
