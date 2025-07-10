# 📦 SKU Image Exporter

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![Interface](https://img.shields.io/badge/GUI-Tkinter-informational)
![Sistema](https://img.shields.io/badge/Sistema-Desktop-lightgrey)
![Entrada](https://img.shields.io/badge/Suporte-CSV%20%7C%20XLSX-orange)
![API](https://img.shields.io/badge/API-VTEX-red)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![Licença](https://img.shields.io/badge/Licença-MIT-green)

🖥️ Aplicação desktop para exportar URLs de imagens de SKUs da plataforma VTEX.

## ✨ Funcionalidades

- 🖼️ Exporta URLs de imagens de produtos da VTEX
- 📄 Suporte a arquivos CSV e Excel (XLSX)
- 🧑‍💻 Interface gráfica amigável
- 👀 Preview dos resultados
- ⚙️ Processamento em segundo plano

## 🧰 Requisitos

- 🐍 Python 3.6+
- 📦 Pacotes listados no `requirements.txt`

## ⚙️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/sku-image-exporter.git
cd sku-image-exporter
```

2. Crie um ambiente virtual (opcional):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## ▶️ Uso

Execute o aplicativo:

```bash
python sku_image_exporter.py
```

- 🔐 Preencha suas credenciais VTEX (API Key e API Token)
- 📁 Selecione um arquivo CSV ou Excel contendo SKUs
- 🧾 Selecione a coluna que contém os SKUs
- 🚀 Clique em "OBTER URLs DAS IMAGENS"
- 💾 Os resultados serão salvos automaticamente na área de trabalho

## ⚙️ Configuração

- 🛠️ As credenciais VTEX podem ser obtidas no admin da VTEX
- 🗂️ O arquivo de entrada deve conter uma coluna com IDs de SKU
- 📤 O arquivo de saída é gerado em CSV na área de trabalho

## 🗂️ Estrutura do Projeto

```
sku-image-exporter/
├── sku_image_exporter.py  # Código principal
├── requirements.txt       # Dependências
└── README.md              # Documentação
```

## 📜 Licença

Este projeto está licenciado sob a licença MIT.

---

## 🛠️ Principais Alterações

1. **🔐 Remoção de credenciais**:
   - As credenciais foram completamente removidas do código
   - Adicionados campos na interface para o usuário inserir suas próprias credenciais

2. **🌐 Dinamização da URL da API**:
   - Implementada função `get_account_name()` para extrair o nome da conta das credenciais
   - URL da API construída dinamicamente com base nas credenciais fornecidas

3. **🎨 Melhorias na interface**:
   - Adicionado seção específica para credenciais
   - Mensagens de erro mais claras para credenciais ausentes
   - Feedback visual aprimorado

4. **📝 Documentação completa**:
   - README com instruções de instalação e uso
   - Arquivo requirements.txt com dependências
   - Estrutura de projeto clara

💡 Para usar o aplicativo, basta executar os passos de instalação no README e preencher com suas próprias credenciais VTEX quando o programa for executado.

### 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:

Faça um fork do projeto

Crie sua branch (git checkout -b feature/sua-feature)

Faça commit das mudanças (git commit -m 'Adiciona nova funcionalidade')

Faça push para a branch (git push origin feature/sua-feature)

Abra um Pull Request

### 📄 Licença

Distribuído sob a licença MIT. Veja LICENSE para mais informações.

### ✉️ Contato

Matheus Renzo - @matheusrenzo.exe (intagram) - matheus.renzo.gama@gmail.com 