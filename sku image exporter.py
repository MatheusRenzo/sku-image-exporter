import requests
import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import threading
import pandas as pd
import openpyxl

class SkuImageExporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SKU Image Exporter")
        self.root.geometry("900x800")  # Aumentei um pouco a altura para o novo campo
        self.root.configure(bg="#f0f0f0")
        
        # Variáveis de controle
        self.selected_column = tk.StringVar(value="Selecione uma coluna")
        self.running = False
        self.results = []
        self.file_path = ""
        self.sku_list = []
        self.file_type = None
        
        # Configuração de credenciais (serão solicitadas ao usuário)
        self.API_KEY = ""
        self.API_TOKEN = ""
        self.ACCOUNT_NAME = ""  # Novo campo para o nome da conta
        
        # Configuração de saída
        self.DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop', 'sku_images.csv')
        
        self.create_widgets()

    def create_widgets(self):
        # Cabeçalho
        header_frame = tk.Frame(self.root, bg="#0c1e3e")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = tk.Label(
            header_frame,
            text="SKU IMAGE EXPORTER",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#0c1e3e"
        )
        title_label.pack(pady=10)
        
        # Frame de credenciais
        cred_frame = tk.LabelFrame(
            self.root,
            text=" CREDENCIAIS API ",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        cred_frame.pack(fill="x", padx=15, pady=10)
        
        # Account Name (Novo campo)
        tk.Label(cred_frame, text="Account Name:", bg="#f0f0f0", font=("Arial", 9)).grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.account_name_entry = tk.Entry(cred_frame, width=50, font=("Arial", 9))
        self.account_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # API Key
        tk.Label(cred_frame, text="API Key:", bg="#f0f0f0", font=("Arial", 9)).grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.api_key_entry = tk.Entry(cred_frame, width=50, font=("Arial", 9))
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # API Token
        tk.Label(cred_frame, text="API Token:", bg="#f0f0f0", font=("Arial", 9)).grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.api_token_entry = tk.Entry(cred_frame, width=50, font=("Arial", 9), show="*")
        self.api_token_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        # Frame de arquivo
        file_frame = tk.LabelFrame(
            self.root,
            text=" CARREGAR ARQUIVO ",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        file_frame.pack(fill="x", padx=15, pady=10)
        
        # Botão para carregar arquivo
        self.load_btn = tk.Button(
            file_frame,
            text="CARREGAR ARQUIVO (CSV ou XLSX)",
            command=self.load_file,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.load_btn.pack(side="top", pady=(0, 10))
        
        # Label para mostrar o arquivo selecionado
        self.file_label = tk.Label(
            file_frame,
            text="Nenhum arquivo selecionado",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#555"
        )
        self.file_label.pack(fill="x", pady=(0, 10))
        
        # Frame para seleção de coluna
        column_frame = tk.Frame(file_frame, bg="#f0f0f0")
        column_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            column_frame,
            text="Selecione a coluna com os SKUs:",
            font=("Arial", 9),
            bg="#f0f0f0"
        ).pack(side="left", padx=(0, 10))
        
        self.column_combobox = ttk.Combobox(
            column_frame,
            textvariable=self.selected_column,
            state="readonly",
            width=30
        )
        self.column_combobox.pack(side="left")
        
        # Frame de botões
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill="x", padx=15, pady=10)
        
        self.process_btn = tk.Button(
            button_frame,
            text="OBTER URLs DAS IMAGENS",
            command=self.start_processing,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            state="disabled"
        )
        self.process_btn.pack(side="left")
        
        self.cancel_btn = tk.Button(
            button_frame,
            text="CANCELAR",
            command=self.cancel_processing,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=8,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=10)
        
        # Barra de progresso
        self.progress_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.progress_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Carregue um arquivo CSV/XLSX e selecione a coluna de SKUs",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#555"
        )
        self.progress_label.pack(anchor="w")
        
        # Área de preview
        preview_frame = tk.LabelFrame(
            self.root,
            text=" PREVIEW DOS RESULTADOS (Máximo 50 linhas) ",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        preview_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            font=("Consolas", 10),
            wrap="none",
            height=15,
            bg="white"
        )
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.preview_text.insert(tk.END, "Os resultados aparecerão aqui...")
        self.preview_text.config(state="disabled")
        
        # Configurar tags para formatação
        self.preview_text.tag_config("header", foreground="blue", font=("Consolas", 10, "bold"))
        self.preview_text.tag_config("success", foreground="green")
        self.preview_text.tag_config("error", foreground="red")
        
        # Rodapé
        footer_frame = tk.Frame(self.root, bg="#e0e0e0")
        footer_frame.pack(side="bottom", fill="x")
        
        footer_text = tk.Label(
            footer_frame,
            text="Forneça suas credenciais VTEX antes de usar",
            bg="#e0e0e0",
            fg="#555",
            pady=5,
            font=("Arial", 9)
        )
        footer_text.pack()

    def load_file(self):
        self.file_path = filedialog.askopenfilename(
            title="Selecione um arquivo (CSV ou XLSX)",
            filetypes=[
                ("Arquivos CSV", "*.csv"),
                ("Arquivos Excel", "*.xlsx"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if self.file_path:
            filename = os.path.basename(self.file_path)
            self.file_label.config(text=filename)
            
            # Determinar tipo de arquivo
            if filename.lower().endswith('.csv'):
                self.file_type = 'CSV'
            elif filename.lower().endswith('.xlsx'):
                self.file_type = 'XLSX'
            else:
                messagebox.showerror("Erro", "Formato de arquivo não suportado!")
                return
            
            try:
                # Ler apenas o cabeçalho do arquivo
                if self.file_type == 'CSV':
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        headers = next(reader)
                else:  # XLSX
                    df = pd.read_excel(self.file_path, nrows=0)
                    headers = df.columns.tolist()
                
                # Atualizar combobox com as colunas
                self.column_combobox['values'] = headers
                if headers:
                    self.column_combobox.current(0)
                    self.process_btn.config(state="normal")
                    self.progress_label.config(text=f"Arquivo {self.file_type} carregado. Selecione a coluna de SKUs e clique em 'Obter URLs'")
                else:
                    messagebox.showerror("Erro", "O arquivo não contém cabeçalhos válidos")
                    self.process_btn.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{e}")
                self.file_label.config(text="Erro ao ler arquivo")
                self.process_btn.config(state="disabled")

    def start_processing(self):
        # Obter credenciais da interface
        self.API_KEY = self.api_key_entry.get().strip()
        self.API_TOKEN = self.api_token_entry.get().strip()
        self.ACCOUNT_NAME = self.account_name_entry.get().strip()  # Obter o account name
        
        if not self.ACCOUNT_NAME:
            messagebox.showerror("Erro", "Preencha o Account Name antes de continuar!")
            return
            
        if not self.API_KEY or not self.API_TOKEN:
            messagebox.showerror("Erro", "Preencha as credenciais da API antes de continuar!")
            return
            
        if not self.file_path:
            messagebox.showerror("Erro", "Selecione um arquivo primeiro!")
            return
            
        selected_col = self.selected_column.get()
        if not selected_col or selected_col == "Selecione uma coluna":
            messagebox.showerror("Erro", "Selecione uma coluna de SKUs!")
            return
            
        # Ler os SKUs do arquivo
        try:
            if self.file_type == 'CSV':
                df = pd.read_csv(self.file_path, usecols=[selected_col])
            else:  # XLSX
                df = pd.read_excel(self.file_path, usecols=[selected_col])
                
            self.sku_list = df[selected_col].astype(str).tolist()
            
            if not self.sku_list:
                messagebox.showerror("Erro", "A coluna selecionada não contém SKUs válidos!")
                return
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler SKUs do arquivo:\n{e}")
            return
            
        self.results = []
        self.processed_count = 0
        self.running = True
        
        self.process_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.load_btn.config(state="disabled")
        self.column_combobox.config(state="disabled")
        self.progress_label.config(text=f"Processando {len(self.sku_list)} SKUs...")
        
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "Iniciando processamento...\n")
        self.preview_text.insert(tk.END, "="*80 + "\n", "header")
        self.preview_text.insert(tk.END, "SkuId,FullURL\n", "header")
        self.preview_text.config(state="disabled")
        
        # Iniciar thread de processamento
        self.process_thread = threading.Thread(target=self.process_skus)
        self.process_thread.daemon = True
        self.process_thread.start()

    def cancel_processing(self):
        self.running = False
        self.progress_label.config(text="Processamento cancelado pelo usuário")
        self.preview_text.config(state="normal")
        self.preview_text.insert(tk.END, "\nProcessamento cancelado pelo usuário", "error")
        self.preview_text.config(state="disabled")
        self.enable_ui()

    def process_skus(self):
        for i, sku in enumerate(self.sku_list):
            if not self.running:
                break
                
            self.processed_count = i + 1
            self.progress_label.config(text=f"Processando SKU {self.processed_count}/{len(self.sku_list)}: {sku}")
            
            if not sku or sku.lower() == 'nan' or sku == 'None':
                self.log(f"SKU inválido ignorado: {sku}", "error")
                continue
                
            try:
                data = self.get_sku_images(sku)
                if data:
                    for item in data:
                        file_location = item.get('FileLocation', '')
                        if file_location:
                            full_url = f"https://{self.ACCOUNT_NAME}.{file_location}"  # Usa o account name fornecido
                            result = {
                                'SkuId': sku,
                                'FullURL': full_url
                            }
                            self.results.append(result)
                            self.log(f"{sku},{full_url}", "success")
            except Exception as e:
                self.log(f"Erro no SKU {sku}: {str(e)}", "error")
        
        if self.running:
            self.save_results()
        self.enable_ui()

    def get_sku_images(self, sku_id):
        url = f"https://{self.ACCOUNT_NAME}.vtexcommercestable.com.br/api/catalog/pvt/stockkeepingunit/{sku_id}/file"
        headers = {
            "X-VTEX-API-AppKey": self.API_KEY,
            "X-VTEX-API-AppToken": self.API_TOKEN
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def save_results(self):
        try:
            with open(self.DESKTOP_PATH, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['SkuId', 'FullURL']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
            
            self.progress_label.config(text=f"Processo concluído! {len(self.results)} URLs salvas")
            
            # Atualizar preview se houver muitos resultados
            if len(self.results) > 50:
                self.preview_text.config(state="normal")
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, f"Mostrando 50 de {len(self.results)} resultados\n", "header")
                self.preview_text.insert(tk.END, "SkuId,FullURL\n", "header")
                
                for row in self.results[:50]:
                    self.preview_text.insert(tk.END, f"{row['SkuId']},{row['FullURL']}\n")
                
                self.preview_text.insert(tk.END, f"\n... e mais {len(self.results)-50} linhas ...", "header")
                self.preview_text.config(state="disabled")
            
            messagebox.showinfo(
                "Sucesso", 
                f"Arquivo salvo com sucesso!\n\n"
                f"Local: {self.DESKTOP_PATH}\n"
                f"Total de URLs: {len(self.results)}\n"
                f"SKUs processados: {len(self.sku_list)}"
            )
            
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")
            self.progress_label.config(text="Erro ao salvar arquivo")

    def log(self, message, tag=None):
        self.root.after(0, lambda: self._update_log(message, tag))
        
    def _update_log(self, message, tag):
        self.preview_text.config(state="normal")
        if tag:
            self.preview_text.insert(tk.END, message + "\n", tag)
        else:
            self.preview_text.insert(tk.END, message + "\n")
        self.preview_text.see(tk.END)
        self.preview_text.config(state="disabled")

    def enable_ui(self):
        self.process_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.load_btn.config(state="normal")
        self.column_combobox.config(state="readonly")
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = SkuImageExporterApp(root)
    root.mainloop()