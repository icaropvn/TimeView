# TimeView

Este projeto automatiza o processamento de dados de ponto de funcionários (faturas mensais em Excel), gera métricas de pontualidade, cria gráficos, produz um relatório em PDF e envia via e‑mail, além de usar o ChatGPT para gerar um breve texto de análise comparativa.

## 📁 Estrutura de Diretórios

```
├── data/
│   ├── 02-2025.xlsx       # Dados de fevereiro
│   ├── 03-2025.xlsx       # Dados de março
│   ├── 04-2025.xlsx       # Dados de abril
│   └── 05-2025.xlsx       # Dados de maio
├── output/                  # Gerada automaticamente ao rodar o projeto
├── charts.py                  # Geração de gráficos
├── metrics.py                 # Cálculo de todas as métricas
├── analysis.py                # Chamada à API OpenAI para sumário comparativo
├── report.py                  # Geração do PDF
├── email_sender.py            # Função para envio de relatório por e-mail
├── config.py                  # Constantes SMTP
├── main.py                    # Orquestra todo o fluxo
├── requirements.txt           # Dependências Python
└── .env.example               # Template do arquivo de variáveis de ambiente
```

## 🛠️ Pré-requisitos

* Python 3.8+ instalado
* Acesso à Internet (para chamadas à API do OpenAI)
* Servidor SMTP para envio de e‑mail

## 📦 Instalação

1. **Clone o repositório**

   ```bash
   git clone https://github.com/icaropvn/TimeView.git
   cd TimeView
   ```

2. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure variáveis de ambiente**

   * Duplique o arquivo `.env.example` para `.env`
   * Preencha suas credenciais:

     ```ini
     OPENAI_API_KEY={sua_chave_api_openai}
     SMTP_SERVER=smtp.{seuprovedor}.com
     SMTP_PORT=587
     SMTP_USER={seu_usuario@provedor.com}
     SMTP_PASS={sua_senha_smtp}
     SENDER_EMAIL={email_remetente}
     RECEIVER_EMAIL={email_destinatario}
     ```

## 🚀 Execução

No diretório `TimeView`, execute:

```bash
python src/main.py
```

O script `main.py` irá:

1. Carregar as planilhas (`data/02-2025.xlsx` a `data/05-2025.xlsx`);
2. Calcular métricas gerais e por colaborador/setor;
3. Gerar gráficos de barras e pizza (`charts.py`);
4. Gerar um texto de análise comparativa via ChatGPT (`analysis.py`);
5. Montar o PDF final em `output/relatorio_pontualidade.pdf` (`report.py`);
6. Enviar o PDF por e‑mail (`email_sender.py`).
