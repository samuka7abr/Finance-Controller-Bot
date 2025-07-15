#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura as credenciais do Google se estivermos em produção
if os.getenv('RENDER'):
    from setup_credentials import setup_google_credentials
    if not setup_google_credentials():
        print("❌ Falha ao configurar credenciais. Abortando...")
        sys.exit(1)

from src.main import main

if __name__ == '__main__':
    main() 