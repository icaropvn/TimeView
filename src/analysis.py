import os
import json
import openai
from dotenv import load_dotenv

# 1) Carrega sua API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 2) Monta o prompt a partir do dicionário de métricas
def build_prompt(all_metrics: dict) -> str:
    # Serializa só as métricas que interessam (exemplo: pontualidade e atraso médio)
    data = {
        month: {
            "pontualidade": vals["Pontualidade Geral"],
            "atraso_medio": vals["Atraso Médio na Entrada"],
            "horas_extras": vals["Horas Extras Totais"]
        }
        for month, vals in all_metrics.items()
    }

    return (
        "Você é um analista de RH. Compare estes indicadores mensais de pontualidade:\n\n"
        f"{json.dumps(data, indent=2)}\n\n"
        "Faça um parágrafo curto destacando se Maio 2025 melhorou ou piorou "
        "em relação à média de Fevereiro–Abril 2025."
        "Forneça o parágrafo de resposta entre aspas duplas, estritamente."
    )

# 3) Envia à API e retorna o texto gerado
def summarize_trends(all_metrics: dict) -> str:
    prompt = build_prompt(all_metrics)
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um analista de RH experiente."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )

    resp_text = resp.choices[0].message.content
    clean = resp_text.strip()

    if clean.startswith('"') and clean.endswith('"'):
        clean = clean[1:-1]

    return clean