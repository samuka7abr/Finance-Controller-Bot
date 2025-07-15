import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

class GoogleSheetsManager:
    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        credentials = Credentials.from_service_account_file(credentials_path, scopes=scope)
        self.client = gspread.authorize(credentials)

        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.sheet_name = os.getenv('GOOGLE_SHEET_NAME')
        self.spreadsheet = self.client.open_by_key(self.sheet_id)
        self.worksheet = self.spreadsheet.worksheet(self.sheet_name)

        self.tz = pytz.timezone('America/Sao_Paulo')
        self._initialize_headers()

    def _initialize_headers(self):
        try:
            headers = self.worksheet.row_values(1)
            if not headers:
                self.worksheet.append_row([
                    'Data e Hora', 'Valor (R$)', 'Meio de Pagamento', 
                    'Categoria', 'Descrição', 'Usuário', 'Créditos'
                ])
            elif len(headers) < 7:
                try:
                    self.worksheet.update_cell(1, 7, 'Créditos')
                except Exception as e:
                    print(f"Aviso: Não foi possível adicionar coluna de créditos automaticamente: {e}")
                    print("Por favor, adicione manualmente a coluna 'Créditos' na planilha.")
        except Exception as e:
            print(f"Erro ao inicializar cabeçalhos: {e}")

    def _normalize_text(self, text):
        return text.lower().replace(' ', '')

    def add_expense(self, valor, meio_pagamento, categoria, descricao, usuario):
        try:
            now = datetime.now(self.tz)
            data_hora = now.strftime('%d/%m/%Y %H:%M:%S')
            meio_pagamento = self._normalize_text(meio_pagamento)
            categoria = self._normalize_text(categoria)
            usuario = self._normalize_text(usuario)
            row = [data_hora, valor, meio_pagamento, categoria, descricao, usuario, '']
            self.worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Erro ao adicionar despesa: {e}")
            return False

    def add_credit(self, valor):
        try:
            now = datetime.now(self.tz)
            data_hora = now.strftime('%d/%m/%Y %H:%M:%S')
            row = [data_hora, '', '', '', '', '', valor]
            self.worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Erro ao adicionar crédito: {e}")
            return False

    def clear_table(self):
        try:
            all_values = self.worksheet.get_all_values()
            if len(all_values) > 1:
                self.worksheet.delete_rows(2, len(all_values))
            return True
        except Exception as e:
            print(f"Erro ao limpar tabela: {e}")
            return False

    def get_all_data(self):
        try:
            records = self.worksheet.get_all_records()
            return records
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return []
