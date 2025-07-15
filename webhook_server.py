#!/usr/bin/env python3
"""
Servidor Webhook para o Finance Controller Bot
Mantém toda a funcionalidade do bot original, apenas muda a forma de receber mensagens
"""

import os
import sys
import json
import logging
import asyncio
from threading import Thread
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if os.getenv('RENDER') == 'true' and os.getenv('RENDER_EXTERNAL_URL'):
    from setup_credentials import setup_google_credentials
    if not setup_google_credentials():
        print("❌ Falha ao configurar credenciais. Abortando...")
        sys.exit(1)

from src.main import (
    start, clear_table, statistics, handle_expense, handle_unknown,
    bot_manager
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

telegram_app = None
loop = None

def create_telegram_app():
    """Cria a aplicação do Telegram com os mesmos handlers do bot original"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN não encontrado")
        return None
    
    application = Application.builder().token(token).build()
    
    from telegram.ext import CommandHandler, MessageHandler, filters
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clearTable", clear_table))
    application.add_handler(CommandHandler("statistics", statistics))
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_expense
    ))
    
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown))
    
    return application

def run_async_task(coro):
    """Executa uma corrotina no loop asyncio"""
    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, loop)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para o Render saber que o serviço está ativo"""
    return jsonify({
        'status': 'healthy',
        'service': 'Finance Controller Bot',
        'mode': 'webhook'
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint que recebe mensagens do Telegram via webhook"""
    try:
        update_data = request.get_json()
        
        if not update_data:
            logger.warning("Webhook chamado sem dados")
            return jsonify({'status': 'no_data'}), 400
        
        update = Update.de_json(update_data, telegram_app.bot)
        
        run_async_task(telegram_app.process_update(update))
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Endpoint para configurar o webhook do Telegram (apenas para setup)"""
    try:
        webhook_url = request.json.get('webhook_url')
        if not webhook_url:
            return jsonify({'error': 'webhook_url é obrigatório'}), 400
        
        run_async_task(telegram_app.bot.set_webhook(webhook_url))
        
        return jsonify({
            'status': 'webhook_set',
            'url': webhook_url
        })
    
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Página inicial informativa"""
    return """
    <h1>🤖 Finance Controller Bot</h1>
    <p><strong>Status:</strong> ✅ Online (Webhook Mode)</p>
    <p><strong>Endpoints:</strong></p>
    <ul>
        <li><code>/health</code> - Health check</li>
        <li><code>/webhook</code> - Webhook do Telegram</li>
    </ul>
    <p><em>Bot funcionando em modo webhook para deploy no Render.</em></p>
    """

def setup_webhook():
    """Configura o webhook automaticamente no startup"""
    try:
        render_external_url = os.getenv('RENDER_EXTERNAL_URL')
        if render_external_url:
            webhook_url = f"{render_external_url}/webhook"
            logger.info(f"Configurando webhook para: {webhook_url}")
            
            async def set_webhook_async():
                await telegram_app.bot.set_webhook(webhook_url)
                logger.info("✅ Webhook configurado com sucesso!")
            
            run_async_task(set_webhook_async())
        else:
            logger.warning("RENDER_EXTERNAL_URL não encontrada - webhook não configurado")
    
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {e}")

def run_async_loop():
    """Executa o loop asyncio em uma thread separada"""
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def init_app():
        await telegram_app.initialize()
        await telegram_app.start()
    
    loop.run_until_complete(init_app())
    
    if os.getenv('RENDER'):
        setup_webhook()
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

def main():
    """Função principal que inicializa o servidor webhook"""
    global telegram_app
    
    os.makedirs('logs', exist_ok=True)
    
    telegram_app = create_telegram_app()
    if not telegram_app:
        logger.error("Falha ao criar aplicação do Telegram")
        return
    
    async_thread = Thread(target=run_async_loop, daemon=True)
    async_thread.start()
    
    import time
    time.sleep(2)
    
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"🚀 Servidor webhook iniciado na porta {port}")
    logger.info("🤖 Bot funcionando em modo webhook")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 