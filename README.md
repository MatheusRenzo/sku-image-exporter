# 🚀 Web Performance Suite

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

Aplicação desktop interativa composta por dois módulos que permitem analisar, visualizar e gerar relatórios detalhados de performance web com base nas **Core Web Vitals** do Google.

---

## 📦 Componentes

### 1. [`web-performance-analyzer`](https://github.com/MatheusRenzo/web-performance-analyzer)

Coleta automática de métricas do PageSpeed Insights da Google, para URLs públicas em dispositivos **mobile** e **desktop**.

**Principais recursos:**

- Coleta de métricas como LCP, CLS, FCP, TBT, etc.
- Interface amigável para análise por URL
- Exportação dos resultados para `.xlsx`
- Logs e cancelamento em tempo real

**Requisitos:**

- Python 3.7 ou superior
- Google Chrome + ChromeDriver

**Uso:**

```bash
git clone https://github.com/MatheusRenzo/web-performance-analyzer.git
cd web-performance-analyzer
pip install -r requirements.txt
python web_performance_analyzer.py
```

---

### 2. [`web-performance-report`](https://github.com/seu-usuario/web-performance-report)

Analisa os dados exportados do módulo anterior ou qualquer outro arquivo `.csv/.xlsx` com métricas Core Web Vitals, gera gráficos e produz um relatório **interativo em HTML**.

**Funcionalidades:**

- Leitura de arquivos `.csv` ou `.xlsx`
- Geração de gráficos com benchmarks
- Tendências por métrica, data e contexto
- Exportação de relatório completo com insights técnicos

**Instalação:**

```bash
git clone https://github.com/seu-usuario/web-performance-report.git
cd web-performance-report
pip install -r requirements.txt
```

**Uso:**

```bash
python main.py
```

---

## 🧾 Estrutura Esperada dos Dados

O arquivo de entrada deve conter:

- `Data` (formato: `YYYY-MM-DD HH-MM`)
- `Métrica` (ex: `LCP`, `FCP`, etc.)
- `Valor` (ex: `1.8s`, `120ms`, `0.15`)
- `Contexto` (ex: `Mobile - URL atual`, `Desktop - Origem`)

> O `web-performance-analyzer` já gera arquivos neste padrão automaticamente.

---

## 📈 Métricas Suportadas

| Métrica | Significado | Unidade | Bom | Ruim |
|--------|-------------|---------|-----|------|
| LCP | Largest Contentful Paint | s | < 2.5 | > 4.0 |
| FCP | First Contentful Paint | s | < 1.8 | > 3.0 |
| INP | Interaction to Next Paint | ms | < 200 | > 500 |
| CLS | Cumulative Layout Shift | (sem unidade) | < 0.1 | > 0.25 |
| TTFB | Time to First Byte | s | < 0.8 | > 1.8 |

---

## 📁 Saída Final

- Gráficos `.png` por métrica
- Arquivo `relatorio_performance.html` com:
  - Benchmarks
  - Tendências e estatísticas
  - Sugestões técnicas de melhoria
  - Visual estilizado e intuitivo

---

## 🧠 Tecnologias Usadas

- Python 3
- Pandas, Numpy
- Matplotlib, Scipy
- Tkinter
- Selenium (analyzer)
- HTML + CSS embutido

---

## ⚠️ Observações

- Sites com proteção anti-bot podem bloquear análises automáticas
- Necessário ChromeDriver compatível com sua versão do Chrome
- Análise pode demorar de 1 a 2 minutos por URL

---

## 🧑‍💻 Autor

Desenvolvido por [Matheus Renzo](mailto:matheus.renzo.gama@gmail.com)  
Instagram: [@matheusrenzo.exe](https://instagram.com/matheusrenzo.exe)  
GitHub: [@MatheusRenzo](https://github.com/MatheusRenzo)

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.