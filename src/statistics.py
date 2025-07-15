import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pytz
import io
import os
from collections import Counter

plt.switch_backend('Agg')

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class StatisticsGenerator:
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self.tz = pytz.timezone('America/Sao_Paulo')
        
        if not self.df.empty:
            self.df['Data e Hora'] = pd.to_datetime(self.df['Data e Hora'], format='%d/%m/%Y %H:%M:%S')
            
            self.df['Valor (R$)'] = self.df['Valor (R$)'].astype(str).str.replace(',', '.')
            self.df['Valor (R$)'] = pd.to_numeric(self.df['Valor (R$)'], errors='coerce').fillna(0)
            
            if 'Créditos' in self.df.columns:
                self.df['Créditos'] = self.df['Créditos'].astype(str).str.replace(',', '.')
                self.df['Créditos'] = pd.to_numeric(self.df['Créditos'], errors='coerce').fillna(0)
            else:
                self.df['Créditos'] = 0
            
            self.df['Data'] = self.df['Data e Hora'].dt.date
            
            self.debitos = self.df[self.df['Valor (R$)'] > 0].copy()
            self.creditos = self.df[self.df['Créditos'] > 0].copy()
    
    def _save_plot(self, fig, filename):
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        return buffer
    
    def gastos_por_pessoa(self):
        if self.debitos.empty:
            return None
            
        gastos_usuario = self.debitos.groupby('Usuário')['Valor (R$)'].sum().sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        gastos_usuario.plot(kind='barh', ax=ax, color='skyblue')
        
        ax.set_title('Gastos por Pessoa (Débitos)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Valor (R$)', fontsize=12)
        ax.set_ylabel('Usuário', fontsize=12)
        
        for i, v in enumerate(gastos_usuario.values):
            ax.text(v + max(gastos_usuario.values) * 0.01, i, f'R$ {v:.2f}', 
                   verticalalignment='center', fontweight='bold')
        
        plt.tight_layout()
        return self._save_plot(fig, 'gastos_por_pessoa.png')
    
    def meio_pagamento_mais_usado(self):
        if self.debitos.empty:
            return None
            
        pagamentos = self.debitos['Meio de Pagamento'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(pagamentos)))
        
        wedges, texts, autotexts = ax.pie(pagamentos.values, labels=pagamentos.index, 
                                         autopct='%1.1f%%', startangle=90, colors=colors)
        
        ax.set_title('Meio de Pagamento Mais Usado', fontsize=16, fontweight='bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        return self._save_plot(fig, 'meio_pagamento.png')
    
    def compras_por_categoria(self):
        if self.debitos.empty:
            return None
            
        categorias = self.debitos['Categoria'].value_counts().sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        categorias.plot(kind='barh', ax=ax, color='lightcoral')
        
        ax.set_title('Número de Compras por Categoria', fontsize=16, fontweight='bold')
        ax.set_xlabel('Número de Compras', fontsize=12)
        ax.set_ylabel('Categoria', fontsize=12)
        
        for i, v in enumerate(categorias.values):
            ax.text(v + max(categorias.values) * 0.01, i, str(v), 
                   verticalalignment='center', fontweight='bold')
        
        plt.tight_layout()
        return self._save_plot(fig, 'compras_por_categoria.png')
    
    def total_gasto_mes(self):
        if self.debitos.empty:
            return None
            
        self.debitos['Mes_Ano'] = self.debitos['Data e Hora'].dt.to_period('M')
        gastos_mes = self.debitos.groupby('Mes_Ano')['Valor (R$)'].sum()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        gastos_mes.plot(kind='bar', ax=ax, color='lightgreen')
        
        ax.set_title('Total Gasto por Mês', fontsize=16, fontweight='bold')
        ax.set_xlabel('Mês/Ano', fontsize=12)
        ax.set_ylabel('Valor (R$)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        for i, v in enumerate(gastos_mes.values):
            ax.text(i, v + max(gastos_mes.values) * 0.01, f'R$ {v:.2f}', 
                   horizontalalignment='center', fontweight='bold')
        
        plt.tight_layout()
        return self._save_plot(fig, 'total_gasto_mes.png')
    
    def gastos_por_dia(self):
        if self.debitos.empty:
            return None
            
        gastos_dia = self.debitos.groupby('Data')['Valor (R$)'].sum().sort_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        gastos_dia.plot(kind='line', ax=ax, marker='o', linewidth=2, markersize=6, color='purple')
        
        ax.set_title('Gastos por Dia', fontsize=16, fontweight='bold')
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Valor (R$)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return self._save_plot(fig, 'gastos_por_dia.png')
    
    def credito_vs_debito(self):
        total_creditos = self.df['Créditos'].sum()
        total_debitos = self.df['Valor (R$)'].sum()
        
        if total_creditos == 0 and total_debitos == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = ['Créditos', 'Débitos']
        values = [total_creditos, total_debitos]
        colors = ['green', 'red']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        
        ax.set_title('Comparação: Créditos vs Débitos', fontsize=16, fontweight='bold')
        ax.set_ylabel('Valor (R$)', fontsize=12)
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                   f'R$ {value:.2f}', ha='center', va='bottom', fontweight='bold')
        
        saldo = total_creditos - total_debitos
        ax.axhline(y=saldo, color='blue', linestyle='--', alpha=0.7)
        ax.text(0.5, saldo + max(values) * 0.05, f'Saldo: R$ {saldo:.2f}', 
               ha='center', va='bottom', fontweight='bold', color='blue')
        
        plt.tight_layout()
        return self._save_plot(fig, 'credito_vs_debito.png')
    
    def debitos_acumulados(self):
        if self.debitos.empty:
            return None
        
        debitos_por_dia = self.debitos.groupby('Data')['Valor (R$)'].sum().sort_index()
        
        debitos_acumulados = debitos_por_dia.cumsum()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        debitos_acumulados.plot(kind='line', ax=ax, marker='o', linewidth=2, 
                               markersize=6, color='red', alpha=0.7)
        
        ax.set_title('Débitos Acumulados por Data', fontsize=16, fontweight='bold')
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Valor Acumulado (R$)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        ax.fill_between(debitos_acumulados.index, debitos_acumulados.values, 
                       alpha=0.3, color='red')
        
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return self._save_plot(fig, 'debitos_acumulados.png')
    
    def generate_all_statistics(self):
        stats = {}
        
        stats['gastos_por_pessoa'] = self.gastos_por_pessoa()
        stats['meio_pagamento'] = self.meio_pagamento_mais_usado()
        stats['compras_por_categoria'] = self.compras_por_categoria()
        stats['total_gasto_mes'] = self.total_gasto_mes()
        stats['gastos_por_dia'] = self.gastos_por_dia()
        stats['credito_vs_debito'] = self.credito_vs_debito()
        stats['debitos_acumulados'] = self.debitos_acumulados()
        
        return {k: v for k, v in stats.items() if v is not None}
    
    def get_summary_text(self):
        if self.df.empty:
            return "Nenhum dado encontrado para gerar estatísticas."
        
        total_creditos = self.df['Créditos'].sum()
        total_debitos = self.df['Valor (R$)'].sum()
        saldo = total_creditos - total_debitos
        
        total_transacoes = len(self.df)
        num_creditos = len(self.creditos)
        num_debitos = len(self.debitos)
        
        data_inicio = self.df['Data e Hora'].min().strftime('%d/%m/%Y')
        data_fim = self.df['Data e Hora'].max().strftime('%d/%m/%Y')
        
        if not self.debitos.empty:
            gastos_usuario = self.debitos.groupby('Usuário')['Valor (R$)'].sum()
            maior_gastador = gastos_usuario.idxmax()
            valor_maior_gastador = gastos_usuario.max()
        else:
            maior_gastador = "N/A"
            valor_maior_gastador = 0
        
        if not self.debitos.empty:
            categoria_freq = self.debitos['Categoria'].mode()[0]
        else:
            categoria_freq = "N/A"
        
        summary = f"""📊 **RESUMO FINANCEIRO**
        
💰 **Total de créditos**: R$ {total_creditos:.2f} ({num_creditos} transações)
💸 **Total de débitos**: R$ {total_debitos:.2f} ({num_debitos} transações)
💳 **Saldo atual**: R$ {saldo:.2f}
📊 **Total de transações**: {total_transacoes}
📅 **Período**: {data_inicio} a {data_fim}

👤 **Maior gastador**: {maior_gastador} (R$ {valor_maior_gastador:.2f})
🏷️ **Categoria mais frequente**: {categoria_freq}
"""
        
        return summary 