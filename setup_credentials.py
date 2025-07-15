#!/usr/bin/env python3
import os
import json
import base64

def setup_google_credentials():
    """
    Configura as credenciais do Google a partir da variável de ambiente
    """
    # Cria a pasta config se não existir
    os.makedirs('config', exist_ok=True)
    
    # Pega as credenciais da variável de ambiente
    credentials_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
    
    if not credentials_base64:
        print("❌ GOOGLE_CREDENTIALS_BASE64 não encontrada")
        print("Configure a variável de ambiente no Render")
        return False
    
    try:
        # Decodifica de base64
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        
        # Valida se é um JSON válido
        json.loads(credentials_json)
        
        # Salva o arquivo
        with open('config/credentials.json', 'w') as f:
            f.write(credentials_json)
        
        print("✅ Credenciais do Google configuradas com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar credenciais: {e}")
        return False

if __name__ == '__main__':
    setup_google_credentials() 