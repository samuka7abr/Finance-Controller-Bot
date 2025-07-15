# 🤖 Bot de Controle Financeiro Familiar

Um bot do Telegram para controle financeiro familiar que registra gastos em Google Sheets e gera relatórios estatísticos com gráficos.

## 📋 Funcionalidades

- ✅ Registro de despesas via mensagens no Telegram
- ✅ Armazenamento automático em Google Sheets
- ✅ Geração de relatórios estatísticos
- ✅ 5 tipos de gráficos diferentes
- ✅ Normalização automática de dados
- ✅ Interface amigável com emojis

## 📊 Gráficos Gerados

1. **Gastos por Pessoa** - Gráfico de barras horizontais
2. **Meio de Pagamento Mais Usado** - Gráfico de pizza
3. **Número de Compras por Categoria** - Gráfico de barras horizontais
4. **Total Gasto por Mês** - Gráfico de barras verticais
5. **Gastos por Dia** - Gráfico de linha temporal

## 🚀 Como Usar

### Formato das Mensagens

Envie mensagens no formato:
```
valor - meio de pagamento - categoria (descrição) - usuário
```

**Exemplos:**
- `100.50 - Cartão Visa - Alimentação (supermercado) - Maria`
- `25 - Dinheiro - Transporte (uber) - João`
- `150,00 - Pix - Lazer (cinema) - Ana`

### Comandos Disponíveis

- `/start` - Mostra as instruções de uso
- `/statistics` - Gera relatório completo com gráficos
- `/clearTable` - Limpa todos os dados da planilha

## ⚙️ Configuração

### 1. Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Conta do Google com Google Sheets API habilitada
- Bot do Telegram criado via @BotFather

### 2. Configuração do Google Sheets

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Habilite a Google Sheets API
4. Crie uma conta de serviço:
   - Vá em "IAM & Admin" > "Service Accounts"
   - Clique em "Create Service Account"
   - Baixe o arquivo JSON das credenciais
5. Crie uma planilha no Google Sheets
6. Compartilhe a planilha com o email da conta de serviço (permissão de editor)

### 3. Configuração do Bot do Telegram

1. Acesse [@BotFather](https://t.me/botfather) no Telegram
2. Use o comando `/newbot`
3. Siga as instruções para criar seu bot
4. Anote o token do bot

### 4. Configuração do Ambiente

O arquivo `.env` já está configurado. Você pode precisar adicionar o email da conta de serviço:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
GOOGLE_SHEET_ID=id_da_sua_planilha
GOOGLE_SHEET_NAME=nome_da_aba
GOOGLE_API_PRIVATE_KEY="sua_chave_privada_aqui"
GOOGLE_API_CLIENT_EMAIL=email_da_conta_de_servico@projeto.iam.gserviceaccount.com
```

## 🐳 Execução com Docker

### Build e execução
```bash
# Construir e executar
docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Parar o serviço
docker-compose down
```

### Execução local (desenvolvimento)
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o bot
python main.py
```

## 📁 Estrutura do Projeto

```
Finance-Controller-Bot/
├── main.py                 # Bot principal
├── google_sheets.py        # Gerenciador do Google Sheets
├── statistics.py           # Gerador de estatísticas
├── requirements.txt        # Dependências Python
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração Docker
├── .env                   # Variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
├── logs/                 # Logs da aplicação
└── README.md             # Este arquivo
```

## 🔧 Estrutura da Planilha

| Data e Hora | Valor (R$) | Meio de Pagamento | Categoria | Descrição | Usuário |
|--------------|------------|-------------------|-----------|-----------|---------|
| 01/01/2024 10:30:00 | 50.00 | cartaovisa | alimentacao | supermercado | maria |

**Observação:** Os campos de texto são automaticamente normalizados (minúsculas, sem espaços).

## 🛠️ Tecnologias Utilizadas

- **Python 3.11** - Linguagem principal
- **python-telegram-bot** - API do Telegram
- **gspread** - Integração com Google Sheets
- **pandas** - Manipulação de dados
- **matplotlib/seaborn** - Geração de gráficos
- **Docker** - Containerização

## 📝 Logs

Os logs são salvos em:
- Console (stdout)
- Arquivo `logs/bot.log`

## 🔒 Segurança

- Todas as credenciais são carregadas via variáveis de ambiente
- Arquivo `.env` não é versionado no Git
- Chaves privadas são tratadas de forma segura

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `logs/bot.log`
2. Certifique-se de que todas as variáveis de ambiente estão configuradas
3. Verifique se a planilha está compartilhada com a conta de serviço
4. Teste a conectividade com a API do Telegram

---
Made with ❤️ for better family finance control 