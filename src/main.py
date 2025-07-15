import os
import re
import logging
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .google_sheets import GoogleSheetsManager
from .statistics import StatisticsGenerator

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinanceBotManager:
    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        
        self.expense_pattern = re.compile(
            r'^(\d+(?:[.,]\d{1,2})?)\s*-\s*([^-]+?)\s*-\s*([^-()]+?)\s*\(([^)]+)\)\s*-\s*(.+?)$',
            re.IGNORECASE
        )
        
        self.credit_pattern = re.compile(
            r'^(\d+(?:[.,]\d{1,2})?)\s*-\s*credito\s*$',
            re.IGNORECASE
        )
    
    def parse_expense(self, message_text):
        message_text = message_text.strip()
        
        credit_match = self.credit_pattern.match(message_text)
        if credit_match:
            valor_str = credit_match.group(1)
            valor_str = valor_str.replace(',', '.')
            try:
                valor = float(valor_str)
            except ValueError:
                return None
            
            return {
                'tipo': 'credito',
                'valor': valor
            }
        
        expense_match = self.expense_pattern.match(message_text)
        if expense_match:
            valor_str, meio_pagamento, categoria, descricao, usuario = expense_match.groups()
            
            valor_str = valor_str.replace(',', '.')
            try:
                valor = float(valor_str)
            except ValueError:
                return None
            
            return {
                'tipo': 'despesa',
                'valor': valor,
                'meio_pagamento': meio_pagamento.strip(),
                'categoria': categoria.strip(),
                'descricao': descricao.strip(),
                'usuario': usuario.strip()
            }
        
        return None

bot_manager = FinanceBotManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
🤖 **Bot de Controle Financeiro Familiar**

Olá! Eu sou seu assistente financeiro pessoal.

📝 **Como usar:**

**Para despesas:**
`valor - meio de pagamento - categoria (descrição) - usuário`

**Para créditos:**
`valor - credito`

**Exemplos:**
• `100.50 - Cartão Visa - Alimentação (supermercado) - Maria`
• `50.00 - Dinheiro - Transporte (uber) - João`
• `1500.00 - credito`

💡 **Tipos de transação:**
• **Débitos**: Gastos normais com todas as informações
• **Créditos**: Entradas de dinheiro (formato simplificado)

📊 **Comandos disponíveis:**
• /start - Mostra esta mensagem
• /statistics - Gera relatórios e gráficos completos
• /clearTable - Limpa todos os dados (cuidado!)

📈 **Relatórios incluem:**
• Resumo financeiro com saldo atual
• Gastos por pessoa (apenas débitos)
• Comparação créditos vs débitos
• Débitos acumulados ao longo do tempo
• Análise por categoria e meio de pagamento

💡 **Dicas:**
- O valor pode usar vírgula ou ponto
- Não é obrigatório incluir centavos
- Para despesas, mantenha sempre os hífens (-) separando os campos
- A descrição deve estar entre parênteses
- Para créditos, use apenas: `valor - credito`

Vamos começar a controlar suas finanças! 💰
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def clear_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        success = bot_manager.sheets_manager.clear_table()
        
        if success:
            message = "✅ Tabela limpa com sucesso! Todos os dados foram removidos."
        else:
            message = "❌ Erro ao limpar a tabela. Tente novamente."
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Erro no comando clear_table: {e}")
        await update.message.reply_text("❌ Erro interno. Tente novamente mais tarde.")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("📊 Gerando estatísticas... Por favor, aguarde.")
        
        data = bot_manager.sheets_manager.get_all_data()
        
        if not data:
            await update.message.reply_text("📈 Nenhum dado encontrado para gerar estatísticas. Adicione algumas despesas primeiro!")
            return
        
        stats_gen = StatisticsGenerator(data)
        
        summary = stats_gen.get_summary_text()
        await update.message.reply_text(summary, parse_mode='Markdown')
        
        charts = stats_gen.generate_all_statistics()
        
        chart_names = {
            'gastos_por_pessoa': '👥 Gastos por Pessoa',
            'meio_pagamento': '💳 Meios de Pagamento',
            'compras_por_categoria': '🏷️ Compras por Categoria',
            'total_gasto_mes': '📅 Total Gasto por Mês',
            'gastos_por_dia': '📈 Gastos por Dia',
            'credito_vs_debito': '⚖️ Créditos vs Débitos',
            'debitos_acumulados': '📊 Débitos Acumulados'
        }
        
        for chart_key, chart_buffer in charts.items():
            if chart_buffer:
                chart_buffer.seek(0)
                caption = chart_names.get(chart_key, chart_key)
                
                await update.message.reply_photo(
                    photo=InputFile(chart_buffer, filename=f'{chart_key}.png'),
                    caption=caption
                )
        
        await update.message.reply_text("✅ Relatório completo enviado!")
        
    except Exception as e:
        logger.error(f"Erro no comando statistics: {e}")
        await update.message.reply_text("❌ Erro ao gerar estatísticas. Tente novamente mais tarde.")

async def handle_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text
        
        expense_data = bot_manager.parse_expense(message_text)
        
        if not expense_data:
            await update.message.reply_text(
                "❌ Formato inválido! Use:\n\n"
                "**Para despesas:**\n"
                "`valor - meio de pagamento - categoria (descrição) - usuário`\n"
                "Exemplo: `50.00 - Dinheiro - Transporte (uber) - João`\n\n"
                "**Para créditos:**\n"
                "`valor - credito`\n"
                "Exemplo: `1500.00 - credito`",
                parse_mode='Markdown'
            )
            return
        
        if expense_data['tipo'] == 'credito':
            success = bot_manager.sheets_manager.add_credit(expense_data['valor'])
            if success:
                await update.message.reply_text(
                    f"✅ Crédito registrado com sucesso! ➕\n\n"
                    f"💰 Valor: R$ {expense_data['valor']:.2f}"
                )
            else:
                await update.message.reply_text("❌ Erro ao registrar crédito. Tente novamente.")
        else:
            success = bot_manager.sheets_manager.add_expense(
                expense_data['valor'],
                expense_data['meio_pagamento'],
                expense_data['categoria'],
                expense_data['descricao'],
                expense_data['usuario']
            )
            
            if success:
                await update.message.reply_text(
                    f"✅ Despesa registrada com sucesso! ➖\n\n"
                    f"💰 Valor: R$ {expense_data['valor']:.2f}\n"
                    f"💳 Meio: {expense_data['meio_pagamento']}\n"
                    f"🏷️ Categoria: {expense_data['categoria']}\n"
                    f"📝 Descrição: {expense_data['descricao']}\n"
                    f"👤 Usuário: {expense_data['usuario']}"
                )
            else:
                await update.message.reply_text("❌ Erro ao registrar despesa. Tente novamente.")
    
    except Exception as e:
        logger.error(f"Erro ao processar transação: {e}")
        await update.message.reply_text("❌ Erro interno. Tente novamente mais tarde.")

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Comando não reconhecido.\n\n"
        "Use /start para ver os comandos disponíveis ou envie uma despesa no formato:\n"
        "`valor - meio de pagamento - categoria (descrição) - usuário`",
        parse_mode='Markdown'
    )

def main():
    os.makedirs('logs', exist_ok=True)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN não encontrado no .env")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clearTable", clear_table))
    application.add_handler(CommandHandler("statistics", statistics))
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_expense
    ))
    
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown))
    
    logger.info("Bot iniciado!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 