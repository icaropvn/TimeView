import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente de um arquivo .env
load_dotenv()

# Configurações de API e email via variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMTP_SERVER     = os.getenv("SMTP_SERVER")
SMTP_PORT       = int(os.getenv("SMTP_PORT", 587))
SMTP_USER       = os.getenv("SMTP_USER")
SMTP_PASS       = os.getenv("SMTP_PASS")
SENDER_EMAIL    = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL  = os.getenv("RECEIVER_EMAIL")