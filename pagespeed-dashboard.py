import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from scipy import stats
import matplotlib.dates as mdates
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

# Configurar estilo visual
plt.style.use('ggplot')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

# Benchmarks atualizados conforme especificado
BENCHMARKS = {
    'First Contentful Paint (FCP)': {'bom': 1.8, 'ruim': 3.0, 'unidade': 's'},
    'Largest Contentful Paint (LCP)': {'bom': 2.5, 'ruim': 4.0, 'unidade': 's'},
    'Cumulative Layout Shift (CLS)': {'bom': 0.1, 'ruim': 0.25, 'unidade': ''},
    'Interaction to Next Paint (INP)': {'bom': 200, 'ruim': 500, 'unidade': 'ms'},
    'Time to First Byte (TTFB)': {'bom': 0.8, 'ruim': 1.8, 'unidade': 's'}
}

# Dicionário de métricas com informações
METRICAS_INFO = {
    'Largest Contentful Paint (LCP)': {
        'sigla': 'LCP',
        'titulo': 'Maior Elemento de Conteúdo Visível',
        'descricao': 'Mede o tempo para o maior elemento de conteúdo ficar visível. Crucial para percepção de velocidade.',
        'impacto': 'Usuários abandonam sites que demoram mais que 3s para carregar conteúdo principal.'
    },
    'Interaction to Next Paint (INP)': {
        'sigla': 'INP',
        'titulo': 'Tempo de Resposta a Interações',
        'descricao': 'Mede o tempo entre uma interação do usuário e a resposta visual. Essencial para experiência fluída.',
        'impacto': 'Valores acima de 500ms fazem o site parecer lento e não responsivo.'
    },
    'Cumulative Layout Shift (CLS)': {
        'sigla': 'CLS',
        'titulo': 'Mudanças Inesperadas de Layout',
        'descricao': 'Mede a instabilidade visual durante o carregamento. Elementos que "pulam" na tela.',
        'impacto': 'Alto CLS causa frustração e erros de clique, prejudicando conversões.'
    },
    'First Contentful Paint (FCP)': {
        'sigla': 'FCP',
        'titulo': 'Primeiro Conteúdo Visível',
        'descricao': 'Tempo para qualquer conteúdo aparecer na tela. Primeira impressão do usuário.',
        'impacto': 'Usuários percebem sites com FCP < 2s como mais rápidos e confiáveis.'
    },
    'Time to First Byte (TTFB)': {
        'sigla': 'TTFB',
        'titulo': 'Tempo de Resposta do Servidor',
        'descricao': 'Tempo entre a requisição do navegador e o primeiro byte do servidor.',
        'impacto': 'Valores altos indicam problemas no servidor ou rede, afetando todas as outras métricas.'
    }
}

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()
    caminho = filedialog.askopenfilename(
        title="Selecione o arquivo de dados",
        filetypes=(
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        )
    )
    return caminho if caminho else None

def selecionar_pasta_saida():
    root = tk.Tk()
    root.withdraw()
    pasta = filedialog.askdirectory(title="Selecione a pasta para salvar o relatório")
    return pasta if pasta else None

def processar_arquivo(caminho_arquivo):
    if caminho_arquivo.endswith('.csv'):
        return pd.read_csv(caminho_arquivo)
    else:
        return pd.read_excel(caminho_arquivo, sheet_name="Sheet1", engine='openpyxl')

def gerar_grafico(metrica_nome, df_agrupado, pasta_saida):
    info = METRICAS_INFO.get(metrica_nome)
    bench = BENCHMARKS.get(metrica_nome)
    
    if not info or not bench:
        return None
        
    df_metrica = df_agrupado[df_agrupado['Métrica'] == metrica_nome]
    
    if df_metrica.empty:
        return None
        
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Paleta de cores melhorada
    cores = {
        'Mobile - URL Atual': '#1f77b4',
        'Mobile - Origem': '#aec7e8',
        'Desktop - URL Atual': '#ff7f0e',
        'Desktop - Origem': '#ffbb78'
    }
    
    # Plotar cada combinação
    for (dispositivo, tipo), grupo in df_metrica.groupby(['Dispositivo', 'Tipo']):
        chave = f"{dispositivo} - {tipo}"
        grupo = grupo.sort_values('Dia')
        
        ax.plot(
            grupo['Dia'], 
            grupo['Valor'], 
            label=chave,
            marker='o' if dispositivo == 'Mobile' else 's',
            markersize=8,
            linewidth=2.5,
            color=cores[chave],
            alpha=0.9
        )
    
    # Adicionar áreas de benchmark
    y_min, y_max = ax.get_ylim()
    ax.fill_between(ax.get_xlim(), bench['bom'], color='green', alpha=0.1, label='Bom')
    ax.fill_between(ax.get_xlim(), bench['bom'], bench['ruim'], color='yellow', alpha=0.1, label='Precisa Melhorar')
    ax.fill_between(ax.get_xlim(), bench['ruim'], y_max, color='red', alpha=0.1, label='Ruim')
    
    # Linhas de referência
    ax.axhline(y=bench['bom'], color='green', linestyle='--', alpha=0.7, linewidth=1.5)
    ax.axhline(y=bench['ruim'], color='red', linestyle='--', alpha=0.7, linewidth=1.5)
    
    # Configurações do gráfico
    ax.set_title(f"{info['titulo']} ({info['sigla']})", fontsize=16, pad=20)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel(f"Tempo ({bench['unidade']})" if bench['unidade'] else 'Pontuação', fontsize=12)
    
    # Formatar datas no eixo X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    
    # Corrigir problema de muitos ticks
    if len(df_metrica['Dia'].unique()) > 30:  # Muitos dias - agrupar por semana
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    elif len(df_metrica['Dia'].unique()) > 10:  # Muitos dias - agrupar por 3 dias
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    else:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    
    plt.xticks(rotation=45, ha='right')
    
    # Melhorar legenda
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
    
    # Adicionar texto de benchmarks
    ax.text(0.01, 0.95, f"Bom: < {bench['bom']}{bench['unidade']}", 
            transform=ax.transAxes, color='green', fontsize=10,
            bbox=dict(facecolor='white', alpha=0.8))
    
    ax.text(0.01, 0.85, f"Precisa melhorar: {bench['bom']}-{bench['ruim']}{bench['unidade']}", 
            transform=ax.transAxes, color='orange', fontsize=10,
            bbox=dict(facecolor='white', alpha=0.8))
    
    ax.text(0.01, 0.75, f"Ruim: > {bench['ruim']}{bench['unidade']}", 
            transform=ax.transAxes, color='red', fontsize=10,
            bbox=dict(facecolor='white', alpha=0.8))
    
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    
    # Salvar gráfico
    nome_arquivo = f"{info['sigla']}_grafico.png"
    caminho = os.path.join(pasta_saida, nome_arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    
    return nome_arquivo

def gerar_relatorio(caminho_arquivo, pasta_saida):
    try:
        # Processar arquivo
        df = processar_arquivo(caminho_arquivo)
        
        # Verificar estrutura do DataFrame
        if len(df.columns) < 4:
            messagebox.showerror("Erro", "O arquivo precisa ter pelo menos 4 colunas: Data, Métrica, Valor, Contexto")
            return False

        # Renomear colunas
        df.columns = ['Data', 'Métrica', 'Valor', 'Contexto'][:len(df.columns)]
        
        # Processar datas e valores
        # Converter a coluna 'Data' para string, caso não seja
        df['Data'] = df['Data'].astype(str)
        # Substituir underscores por espaços e converter para datetime
        df['Data'] = pd.to_datetime(df['Data'].str.replace('_', ' '), 
                                    format='%Y-%m-%d %H-%M', 
                                    errors='coerce')
        df['Dia'] = df['Data'].dt.date
        
        # Converter valores para numéricos
        def convert_value(val):
            if isinstance(val, str):
                # Remove unidades (s, ms) e substitui vírgulas por pontos
                val = val.replace(',', '.').replace('ms', '').replace('s', '').strip()
                # Tenta converter para float, se falhar retorna NaN
                try:
                    return float(val)
                except ValueError:
                    return np.nan
            return float(val)
        
        df['Valor'] = df['Valor'].apply(convert_value)
        
        # Extrair categorias
        df['Dispositivo'] = df['Contexto'].apply(lambda x: 'Mobile' if 'Mobile' in str(x) else 'Desktop')
        df['Tipo'] = df['Contexto'].apply(lambda x: 'URL Atual' if 'URL atual' in str(x) else 'Origem')
        
        # Agrupar por dia, dispositivo e tipo
        df_agrupado = df.groupby(['Dia', 'Dispositivo', 'Tipo', 'Métrica'], as_index=False)['Valor'].mean()
        
        # Gerar todos os gráficos
        graficos = {}
        for metrica in BENCHMARKS.keys():
            arquivo_grafico = gerar_grafico(metrica, df_agrupado, pasta_saida)
            if arquivo_grafico:
                graficos[metrica] = arquivo_grafico
        
        # Gerar relatório HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Performance Web</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{ 
                    text-align: center; 
                    padding: 20px 0;
                    background: linear-gradient(135deg, #1a2a6c, #b21f1f, #1a2a6c);
                    color: white;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .section {{ 
                    background-color: white;
                    border-radius: 10px;
                    padding: 25px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .metric-card {{ 
                    border-left: 5px solid #1a2a6c;
                    padding: 15px;
                    margin-bottom: 20px;
                    background-color: #f8f9fa;
                    border-radius: 0 8px 8px 0;
                }}
                .metric-title {{ 
                    color: #1a2a6c;
                    margin-top: 0;
                }}
                .graph-container {{ 
                    text-align: center;
                    margin: 25px 0;
                }}
                .graph-container img {{
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    border: 1px solid #ddd;
                }}
                .benchmarks {{ 
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    margin: 20px 0;
                }}
                .benchmark-card {{
                    background-color: #e9ecef;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px;
                    flex: 1;
                    min-width: 200px;
                    text-align: center;
                }}
                .good {{ color: #28a745; font-weight: bold; }}
                .medium {{ color: #ffc107; font-weight: bold; }}
                .bad {{ color: #dc3545; font-weight: bold; }}
                .insights {{ 
                    background-color: #e7f3ff;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                }}
                .recommendations ul {{
                    padding-left: 20px;
                }}
                .recommendations li {{
                    margin-bottom: 10px;
                }}
                footer {{ 
                    text-align: center;
                    margin-top: 40px;
                    color: #6c757d;
                    font-size: 0.9em;
                }}
                .legend {{
                    display: flex;
                    justify-content: center;
                    margin: 15px 0;
                    flex-wrap: wrap;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    margin: 0 15px;
                }}
                .legend-color {{
                    width: 20px;
                    height: 20px;
                    margin-right: 8px;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Relatório de Performance Web</h1>
                <p>Análise de Core Web Vitals | {datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
            
            <div class="section">
                <h2>Introdução</h2>
                <p>Este relatório analisa as principais métricas de performance (Core Web Vitals) que impactam diretamente a experiência do usuário e o SEO. Os dados mostram a evolução diária das métricas em dispositivos Mobile e Desktop.</p>
                
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #1f77b4;"></div>
                        <span>Mobile - URL Atual</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #aec7e8;"></div>
                        <span>Mobile - Origem</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #ff7f0e;"></div>
                        <span>Desktop - URL Atual</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #ffbb78;"></div>
                        <span>Desktop - Origem</span>
                    </div>
                </div>
            </div>
        """
        
        # Adicionar seção para cada métrica
        for metrica, info in METRICAS_INFO.items():
            # Se o gráfico não foi gerado, pular esta métrica
            if metrica not in graficos:
                continue
                
            # Análise estatística
            df_metrica = df_agrupado[df_agrupado['Métrica'] == metrica]
            stats_text = ""
            
            for (dispositivo, tipo), grupo in df_metrica.groupby(['Dispositivo', 'Tipo']):
                media = grupo['Valor'].mean()
                maximo = grupo['Valor'].max()
                minimo = grupo['Valor'].min()
                
                # Tendência (regressão linear)
                if len(grupo) > 1:
                    x = np.arange(len(grupo))
                    slope, _, _, _, _ = stats.linregress(x, grupo['Valor'])
                    if slope < 0:
                        tendencia = "melhorando"
                        classe_tendencia = 'good'
                    elif slope > 0:
                        tendencia = "piorando"
                        classe_tendencia = 'bad'
                    else:
                        tendencia = "estável"
                        classe_tendencia = ''
                else:
                    tendencia = "indeterminada"
                    classe_tendencia = ''
                    
                stats_text += f"""
                <p><strong>{dispositivo} - {tipo}:</strong> 
                Média: {media:.2f}{BENCHMARKS[metrica]['unidade']} | 
                Máximo: {maximo:.2f}{BENCHMARKS[metrica]['unidade']} | 
                Mínimo: {minimo:.2f}{BENCHMARKS[metrica]['unidade']} |
                Tendência: <span class="{classe_tendencia}">{tendencia}</span>
                </p>
                """
            
            html += f"""
            <div class="section">
                <div class="metric-card">
                    <h3 class="metric-title">{info['titulo']} ({info['sigla']})</h3>
                    <p><strong>O que mede:</strong> {info['descricao']}</p>
                    <p><strong>Impacto no usuário:</strong> {info['impacto']}</p>
                </div>
                
                <div class="graph-container">
                    <img src="{graficos[metrica]}" alt="Gráfico {info['sigla']}">
                </div>
                
                <div class="benchmarks">
                    <div class="benchmark-card">
                        <h4>Benchmarks</h4>
                        <p><span class="good">Bom:</span> &lt; {BENCHMARKS[metrica]['bom']}{BENCHMARKS[metrica]['unidade']}</p>
                        <p><span class="medium">Precisa melhorar:</span> {BENCHMARKS[metrica]['bom']}-{BENCHMARKS[metrica]['ruim']}{BENCHMARKS[metrica]['unidade']}</p>
                        <p><span class="bad">Ruim:</span> &gt; {BENCHMARKS[metrica]['ruim']}{BENCHMARKS[metrica]['unidade']}</p>
                    </div>
                    
                    <div class="benchmark-card">
                        <h4>Estatísticas</h4>
                        {stats_text}
                    </div>
                </div>
                
                <div class="insights">
                    <h4>Análise e Insights</h4>
            """
            
            # Insights específicos para cada métrica
            if info['sigla'] == 'LCP':
                html += """
                    <p>O LCP mostra o tempo de carregamento do conteúdo principal. Valores altos indicam:</p>
                    <ul>
                        <li>Imagens/vídeos grandes não otimizados</li>
                        <li>Fontes web bloqueando renderização</li>
                        <li>CSS/JS bloqueando o thread principal</li>
                        <li>Tempo de resposta do servidor lento (TTFB alto)</li>
                    </ul>
                """
            elif info['sigla'] == 'INP':
                html += """
                    <p>O INP mede a responsividade do site. Valores altos indicam:</p>
                    <ul>
                        <li>Código JavaScript pesado ou ineficiente</li>
                        <li>Event handlers de longa duração</li>
                        <li>Excesso de operações no thread principal</li>
                        <li>Falta de Web Workers para processamento pesado</li>
                    </ul>
                """
            elif info['sigla'] == 'CLS':
                html += """
                    <p>O CLS mede a estabilidade visual. Valores altos indicam:</p>
                    <ul>
                        <li>Imagens/vídeos sem dimensões definidas</li>
                        <li>Anúncios, embeds ou iframes sem espaço reservado</li>
                        <li>Conteúdo injetado dinamicamente sem reserva de espaço</li>
                        <li>Fontes com FOIT/FOUT (flash of invisible/text)</li>
                    </ul>
                """
            elif info['sigla'] == 'FCP':
                html += """
                    <p>O FCP mostra o tempo para o primeiro conteúdo aparecer. Valores altos indicam:</p>
                    <ul>
                        <li>Servidor lento ou sobrecarregado</li>
                        <li>DNS/TCP/TLS com alta latência</li>
                        <li>Redirecionamentos múltiplos</li>
                        <li>Recursos críticos bloqueando renderização</li>
                    </ul>
                """
            else:  # TTFB
                html += """
                    <p>O TTFB mede a resposta do servidor. Valores altos indicam:</p>
                    <ul>
                        <li>Otimização insuficiente no backend</li>
                        <li>Consultas de banco de dados lentas</li>
                        <li>Falta de cache em servidor ou CDN</li>
                        <li>Problemas de infraestrutura ou rede</li>
                    </ul>
                """
            
            html += """
                </div>
                
                <div class="recommendations">
                    <h4>Recomendações de Otimização</h4>
                    <ul>
            """
            
            # Recomendações gerais
            if info['sigla'] in ['LCP', 'FCP', 'TTFB']:
                html += """
                        <li>Otimize imagens (compressão, formato moderno, lazy loading)</li>
                        <li>Implemente CDN para entrega de conteúdo estático</li>
                        <li>Ative compressão Gzip/Brotli no servidor</li>
                """
            if info['sigla'] in ['INP', 'CLS']:
                html += """
                        <li>Minimize e adie carregamento de JavaScript</li>
                        <li>Use Web Workers para processamento pesado</li>
                        <li>Defina dimensões explícitas para mídia e elementos</li>
                """
            if info['sigla'] == 'CLS':
                html += """
                        <li>Reserve espaço para elementos dinâmicos com CSS aspect-ratio</li>
                        <li>Use font-display: swap para fontes web</li>
                """
            if info['sigla'] == 'TTFB':
                html += """
                        <li>Otimize consultas de banco de dados</li>
                        <li>Implemente cache em servidor</li>
                        <li>Considere soluções de edge computing</li>
                """
            
            html += """
                    </ul>
                </div>
            </div>
            """
        
        # Finalizar HTML
        html += f"""
            <div class="section">
                <h2>Conclusão Geral</h2>
                <p>Com base na análise dos Core Web Vitals, o site apresenta oportunidades de melhoria em várias áreas críticas para experiência do usuário e SEO. As principais recomendações são:</p>
                <ul>
                    <li><strong>Otimizar imagens e mídia</strong> para reduzir LCP e FCP</li>
                    <li><strong>Melhorar eficiência de JavaScript</strong> para reduzir INP</li>
                    <li><strong>Definir dimensões estáticas</strong> para elementos para reduzir CLS</li>
                    <li><strong>Otimizar tempo de resposta do servidor</strong> para reduzir TTFB</li>
                </ul>
                <p>Implementar essas melhorias pode aumentar significativamente a satisfação do usuário, taxas de conversão e posicionamento nos mecanismos de busca.</p>
            </div>
            
            <footer>
                <p>Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p>Fonte de dados: {os.path.basename(caminho_arquivo)}</p>
            </footer>
        </body>
        </html>
        """
        
        # Salvar relatório HTML
        caminho_html = os.path.join(pasta_saida, 'relatorio_performance.html')
        with open(caminho_html, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return caminho_html

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}\n\n{type(e).__name__}\n\nCertifique-se de que o arquivo tem o formato correto.")
        traceback.print_exc()
        return None

def main():
    # Criar interface
    root = tk.Tk()
    root.title("Gerador de Relatório de Performance")
    root.geometry("500x300")
    
    # Estilo
    root.configure(bg="#f0f0f0")
    font_title = ("Arial", 14, "bold")
    font_button = ("Arial", 10)
    
    # Frame principal
    frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
    frame.pack(expand=True, fill=tk.BOTH)
    
    # Título
    tk.Label(frame, text="Relatório de Performance Web", 
            bg="#f0f0f0", fg="#1a3c6c", font=font_title).pack(pady=(0, 20))
    
    # Botões
    def selecionar_arquivo_callback():
        caminho = selecionar_arquivo()
        if caminho:
            entry_arquivo.delete(0, tk.END)
            entry_arquivo.insert(0, caminho)
    
    def selecionar_pasta_callback():
        pasta = selecionar_pasta_saida()
        if pasta:
            entry_pasta.delete(0, tk.END)
            entry_pasta.insert(0, pasta)
    
    def gerar_callback():
        arquivo = entry_arquivo.get()
        pasta = entry_pasta.get()
        
        if not arquivo or not pasta:
            messagebox.showwarning("Aviso", "Selecione um arquivo e uma pasta de saída!")
            return
        
        caminho_html = gerar_relatorio(arquivo, pasta)
        if caminho_html:
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\n\nAcesse:\n{caminho_html}")
            root.destroy()
        else:
            messagebox.showerror("Erro", "Falha ao gerar relatório. Verifique os logs.")
    
    # Campos de entrada
    tk.Label(frame, text="Arquivo de dados:", bg="#f0f0f0", anchor='w').pack(fill=tk.X)
    frame_arquivo = tk.Frame(frame, bg="#f0f0f0")
    frame_arquivo.pack(fill=tk.X, pady=(0, 10))
    entry_arquivo = tk.Entry(frame_arquivo, width=40)
    entry_arquivo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(frame_arquivo, text="Procurar", command=selecionar_arquivo_callback).pack(side=tk.RIGHT)
    
    tk.Label(frame, text="Pasta de saída:", bg="#f0f0f0", anchor='w').pack(fill=tk.X)
    frame_pasta = tk.Frame(frame, bg="#f0f0f0")
    frame_pasta.pack(fill=tk.X, pady=(0, 20))
    entry_pasta = tk.Entry(frame_pasta, width=40)
    entry_pasta.pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(frame_pasta, text="Procurar", command=selecionar_pasta_callback).pack(side=tk.RIGHT)
    
    # Botão de gerar
    tk.Button(frame, text="Gerar Relatório", command=gerar_callback, 
             bg="#4CAF50", fg="white", font=font_button, padx=10, pady=5).pack()
    
    # Créditos
    tk.Label(frame, text="© 2025 - Gerador de Relatórios de Performance", 
            bg="#f0f0f0", fg="#666", font=("Arial", 8)).pack(side=tk.BOTTOM, pady=(10, 0))
    
    root.mainloop()

if __name__ == "__main__":
    main()