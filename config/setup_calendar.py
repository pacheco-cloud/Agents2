# 📁 config/setup_calendar.py
"""

Script de configuração para integração com Google Calendar
Integrado ao sistema de ChatBot Modular
"""

import os
import sys
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Adicionar diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def print_header():
    """Cabeçalho do script"""
    print("🗓️  CONFIGURAÇÃO GOOGLE CALENDAR")
    print("="*50)

def check_requirements():
    """Verifica dependências necessárias"""
    print("\n🔍 Verificando dependências...")
    
    required_packages = {
        'google-api-python-client': 'google.api_core',
        'google-auth-httplib2': 'google.auth.transport.requests', 
        'google-auth-oauthlib': 'google_auth_oauthlib.flow'
    }
    
    missing = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Dependências faltando: {', '.join(missing)}")
        print("\n📋 Para instalar, execute:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    print("   ✅ Todas as dependências estão instaladas")
    return True

def check_credentials():
    """Verifica arquivo credentials.json"""
    print("\n🔐 Verificando credenciais...")
    
    if not os.path.exists('credentials.json'):
        print("   ❌ Arquivo credentials.json não encontrado!")
        print("\n📋 PASSOS PARA OBTER CREDENCIAIS:")
        print("1. Acesse: https://console.cloud.google.com/")
        print("2. Crie um projeto ou selecione existente")
        print("3. Ative a 'Google Calendar API'")
        print("4. Vá em 'Credenciais' → 'Criar credenciais' → 'ID do cliente OAuth 2.0'")
        print("5. Escolha 'Aplicativo para computador'")
        print("6. Baixe o arquivo JSON")
        print("7. Renomeie para 'credentials.json'")
        print("8. Coloque na raiz do seu projeto")
        return False
    
    print("   ✅ credentials.json encontrado")
    
    # Verificar estrutura do arquivo
    try:
        import json
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
            
        if 'installed' in creds_data:
            client_id = creds_data['installed'].get('client_id', '')
            if client_id:
                print(f"   ℹ️  Client ID: {client_id[:20]}...")
                return True
        
        print("   ⚠️  Formato do credentials.json pode estar incorreto")
        return True  # Continuar mesmo assim
        
    except Exception as e:
        print(f"   ⚠️  Erro ao ler credentials.json: {e}")
        return True  # Continuar mesmo assim

def setup_authentication():
    """Configura autenticação OAuth"""
    print("\n🔑 Configurando autenticação...")
    
    # Criar diretório data se não existir
    os.makedirs('data', exist_ok=True)
    
    token_file = 'data/calendar_token.pickle'
    creds = None
    
    # Verificar token existente
    if os.path.exists(token_file):
        print("   📄 Token existente encontrado")
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
            
            if creds and creds.valid:
                print("   ✅ Token válido - autenticação OK!")
                return creds
            
            print("   ⚠️  Token expirado - renovando...")
            
        except Exception as e:
            print(f"   ❌ Erro ao ler token: {e}")
            creds = None
    
    # Renovar ou criar novo token
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            print("   ✅ Token renovado com sucesso!")
        except Exception as e:
            print(f"   ❌ Erro ao renovar token: {e}")
            creds = None
    
    if not creds:
        print("   🌐 Iniciando fluxo de autenticação...")
        print("   ℹ️  Seu navegador será aberto para autorização")
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("   ✅ Autenticação concluída!")
            
        except Exception as e:
            print(f"   ❌ Erro na autenticação: {e}")
            return None
    
    # Salvar token
    try:
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        print(f"   💾 Token salvo em: {token_file}")
        
    except Exception as e:
        print(f"   ⚠️  Erro ao salvar token: {e}")
    
    return creds

def test_calendar_access(creds):
    """Testa acesso ao calendário"""
    print("\n🧪 Testando acesso ao calendário...")
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Listar calendários
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        print(f"   ✅ {len(calendars)} calendário(s) encontrado(s):")
        
        for calendar in calendars[:3]:  # Mostrar apenas os 3 primeiros
            name = calendar['summary']
            is_primary = calendar.get('primary', False)
            marker = "⭐" if is_primary else "📋"
            print(f"      {marker} {name}")
        
        if len(calendars) > 3:
            print(f"      ... e mais {len(calendars) - 3} calendário(s)")
        
        # Testar busca de eventos
        print("\n   🔍 Testando busca de eventos...")
        
        from datetime import datetime, timedelta
        import pytz
        
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(sao_paulo_tz)
        week_later = now + timedelta(days=7)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat(),
            timeMax=week_later.isoformat(),
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"   ✅ {len(events)} evento(s) encontrado(s) nos próximos 7 dias")
        
        return True
        
    except HttpError as e:
        print(f"   ❌ Erro da API do Google: {e}")
        return False
        
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False

def update_requirements():
    """Atualiza requirements.txt com dependências do Google"""
    print("\n📋 Atualizando requirements.txt...")
    
    requirements_file = Path('../requirements.txt')  # Voltar um diretório
    if not requirements_file.exists():
        requirements_file = Path('requirements.txt')  # Tentar no diretório atual
    
    if requirements_file.exists():
        # Ler requirements atuais
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Verificar se já tem as dependências do Google
        google_deps = [
            'google-api-python-client',
            'google-auth-oauthlib', 
            'google-auth-httplib2'
        ]
        
        missing_deps = []
        for dep in google_deps:
            if dep not in content:
                missing_deps.append(dep)
        
        if missing_deps:
            # Adicionar seção do Google Calendar
            google_section = "\n# Google Calendar API\n" + "\n".join(missing_deps) + "\n"
            
            with open(requirements_file, 'a') as f:
                f.write(google_section)
            
            print(f"   ✅ Adicionadas {len(missing_deps)} dependências")
            print("   💡 Execute: pip install -r requirements.txt")
        else:
            print("   ✅ Dependências já estão no requirements.txt")
    else:
        print("   ⚠️  requirements.txt não encontrado")

def main():
    """Função principal do setup"""
    print_header()
    
    # Verificações
    if not check_requirements():
        print("\n❌ Setup cancelado - instale as dependências primeiro")
        return False
    
    if not check_credentials():
        print("\n❌ Setup cancelado - configure as credenciais primeiro")
        return False
    
    # Autenticação
    creds = setup_authentication()
    if not creds:
        print("\n❌ Setup cancelado - falha na autenticação")
        return False
    
    # Teste
    if not test_calendar_access(creds):
        print("\n❌ Setup cancelado - falha no teste de acesso")
        return False
    
    # Atualizar requirements
    update_requirements()
    
    # Sucesso!
    print("\n" + "="*50)
    print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*50)
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. A ferramenta calendar_reader está disponível")
    print("2. Execute: python main.py")
    print("3. Teste com: 'Quais meus próximos compromissos?'")
    print("\n💡 COMANDOS ÚTEIS:")
    print("• 'Compromissos de hoje'")
    print("• 'Agenda da próxima semana'") 
    print("• 'Listar meus calendários'")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)