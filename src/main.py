from pprint import pprint

from metrics import load_data, calculate_overall_metrics, calculate_metrics_by_employee, calculate_metrics_by_sector, calculate_lunch_metrics, calculate_additional_indicators
from report import generate_report
from analysis import summarize_trends
from charts import plot_punctuality_by_sector, plot_absence_justification_pie
from email_sender import send_report

def main():
    months = ["02", "03", "04", "05"]
    all_metrics_raw = {}
    dfs = {}

    for m in months:
        path = f"data/{m}-2025.xlsx"
        df = load_data(path)
        dfs[m] = df
        metrics = calculate_overall_metrics(df)
        all_metrics_raw[f"2025-{m}"] = metrics['raw']

    df_may = dfs["05"]
    metrics_may = calculate_overall_metrics(df_may)
    overall_raw = metrics_may['raw']
    overall_fmt = metrics_may['formatted']

    emp_metrics = calculate_metrics_by_employee(df_may)
    emp_fmt = emp_metrics['formatted']

    sec_metrics = calculate_metrics_by_sector(df_may)
    sec_fmt = sec_metrics['formatted']

    lunch_metrics = calculate_lunch_metrics(df_may)
    lunch_fmt = lunch_metrics['formatted']

    add_metrics = calculate_additional_indicators(df_may)
    print("Métricas calculadas com sucesso.")

    plot_punctuality_by_sector(sec_fmt)
    plot_absence_justification_pie(df_may)
    print("Gráficos gerados com sucesso.")

    summary = summarize_trends(all_metrics_raw)
    print("Resumo por IA gerado com sucesso.")

    generate_report(
        overall_metrics=overall_fmt,
        df_emp=emp_fmt,
        df_sector=sec_fmt,
        lunch_metrics=lunch_fmt,
        additional_metrics=add_metrics,
        df_data=df_may,
        report_month="Maio 2025",
        bar_path="output/comparacao_setores.png",
        pie_path="output/proporcao_faltas.png",
        summary_text=summary,
    )
    print("Relatório gerado com sucesso.")

    send_report("output/relatorio.pdf", "Relatório de Pontualidade - Maio 2025", "Segue em anexo o Relatório de Pontualidade do mês de Maio de 2025.")
    print("Relatório enviado por e-mail com sucesso.")

if __name__ == '__main__':
    main()