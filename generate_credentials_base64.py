#!/usr/bin/env python3
import base64
import json

def generate_credentials_base64():
    """
    Gera a string base64 das credenciais para usar no Render
    """
    try:
        # Lê o arquivo de credenciais
        with open('config/credentials.json', 'r') as f:
            credentials_json = f.read()
        
        # Valida se é um JSON válido
        json.loads(credentials_json)
        
        # Converte para base64
        credentials_base64 = base64.b64encode(credentials_json.encode('utf-8')).decode('utf-8')
        
        print("✅ Base64 das credenciais gerado com sucesso!")
        print("\n" + "="*50)
        print("COPIE O TEXTO ABAIXO PARA O RENDER:")
        print("="*50)
        print(credentials_base64)
        print("="*50)
        print("\nUse esta string na variável de ambiente GOOGLE_CREDENTIALS_BASE64 no Render")
        
    except FileNotFoundError:
        print("❌ Arquivo config/credentials.json não encontrado")
        print("Certifique-se de que o arquivo existe")
    except json.JSONDecodeError:
        print("❌ Arquivo credentials.json não é um JSON válido")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    generate_credentials_base64() 