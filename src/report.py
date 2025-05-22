import os
import pandas as pd
from datetime import datetime

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListItem, ListFlowable, \
    PageBreak, Image
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas

def draw_page_border(canvas: Canvas, doc):
    canvas.saveState()
    width, height = A4
    margin = 30
    canvas.setLineWidth(1)
    canvas.rect(margin, margin, width - 2*margin, height - 2*margin)
    canvas.restoreState()

def generate_report(
    overall_metrics: dict,
    df_emp: pd.DataFrame,
    df_sector: pd.DataFrame,
    lunch_metrics: dict,
    additional_metrics: dict,
    df_data: pd.DataFrame,
    report_month: str = "Maio 2025",
    bar_path: str = None,
    pie_path: str = None,
    summary_text: str = "",
    output_path: str = "output/relatorio.pdf"
):
    # Criar pasta se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Criar documento
    doc = SimpleDocTemplate(
        output_path, pagesize=A4, title=f"Relatório de Pontualidade - {report_month}"
    )
    styles = getSampleStyleSheet()
    elements = []

    # Título com mês
    elements.append(Paragraph(f"Relatório de Pontualidade - {report_month}", styles['Title']))
    elements.append(Spacer(1, 6))

    # Intervalo de dados
    start = df_data['Data'].min().strftime('%d/%m/%Y')
    end = df_data['Data'].max().strftime('%d/%m/%Y')
    elements.append(Paragraph(f"Período de análise: {start} a {end}", styles['Normal']))
    elements.append(Spacer(1, 6))
    # Data de emissão
    hoje = datetime.now().strftime('%d/%m/%Y')
    elements.append(Paragraph(f"Data de emissão: {hoje}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # 1. Visão Geral
    elements.append(Paragraph("1. Visão Geral", styles['Heading2']))
    elements.append(Spacer(1, 6))
    bullet_para = ParagraphStyle(
        'bullet_para',
        parent=styles['Normal'],
        spaceAfter=12,
        leading=14
    )
    bullets = []
    for key, val in overall_metrics.items():
        label = key.replace('_', ' ').capitalize()
        para = Paragraph(f"<b>{label}</b>: {val}", bullet_para)
        bullets.append(
            ListItem(
                para,
                bulletText='•',
                leftIndent=30,
                spaceAfter=6
            )
        )
    elements.append(
        ListFlowable(
            bullets,
            bulletType='bullet'
        )
    )
    elements.append(Spacer(1, 12))

    # 2. Métricas por Colaborador
    elements.append(Paragraph("2. Métricas por Colaborador", styles['Heading2']))
    elements.append(Spacer(1, 6))
    emp_columns = df_emp.columns.tolist()
    emp_data = [emp_columns]
    for _, row in df_emp.iterrows():
        row_data = []
        for col in emp_columns:
            val = row[col]
            if isinstance(val, float):
                row_data.append(f"{val:.2f}")
            else:
                row_data.append(str(val))
        emp_data.append(row_data)
    table_emp = Table(emp_data, hAlign='LEFT')
    table_emp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.extend([table_emp, Spacer(1, 12)])

    # 3. Métricas por Setor
    elements.append(Paragraph("3. Métricas por Setor", styles['Heading2']))
    elements.append(Paragraph("3.1 Métricas por Setor", styles['Heading3']))
    elements.append(Spacer(1, 6))
    sec_columns = df_sector.columns.tolist()
    sec_data = [sec_columns]
    for _, row in df_sector.iterrows():
        row_data = []
        for col in sec_columns:
            val = row[col]
            row_data.append(val)
        sec_data.append(row_data)
    table_sec = Table(sec_data, hAlign='LEFT')
    table_sec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.extend([table_sec, Spacer(1, 12)])
    if bar_path:
        elements.append(Paragraph("3.2 Pontualidade por Setor", styles['Heading3']))
        elements.append(Spacer(1, 6))
        # ajusta o tamanho da imagem para caber na página
        img = Image(bar_path, width=400, height=250)
        img.hAlign = 'CENTER'
        elements.extend([img, Spacer(1, 12)])

    # 4. Métricas de Intervalo de Almoço
    elements.append(Paragraph("4. Métricas de Intervalo de Almoço", styles['Heading2']))
    elements.append(Spacer(1, 6))
    bullet_para = ParagraphStyle(
        'bullet_para',
        parent=styles['Normal'],
        spaceAfter=12,
        leading=14
    )
    bullets = []
    for key, val in lunch_metrics.items():
        label = key.replace('_', ' ').capitalize()
        para = Paragraph(f"<b>{label}</b>: {val}", bullet_para)
        bullets.append(
            ListItem(
                para,
                bulletText='•',
                leftIndent=30,
                spaceAfter=6
            )
        )
    elements.append(
        ListFlowable(
            bullets,
            bulletType='bullet'
        )
    )
    elements.append(Spacer(1, 12))

    # 5. Indicadores Adicionais
    elements.append(Paragraph("5. Indicadores Adicionais", styles['Heading2']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>Top 5 Funcionários Mais Atrasados:</b>", ParagraphStyle('Normal', parent=styles['Normal'], leftIndent=12)))
    elements.append(Spacer(1, 6))
    bullet_para = ParagraphStyle(
        'bullet_para',
        parent=styles['Normal'],
        spaceAfter=12,
        leading=14
    )
    bullets = []
    for nome in additional_metrics['Top 5 mais Atrasados']:
        label = key.replace('_', ' ').capitalize()
        para = Paragraph(f"{nome}", bullet_para)
        bullets.append(
            ListItem(
                para,
                bulletText='•',
                leftIndent=30,
                spaceAfter=6
            )
        )
    elements.append(
        ListFlowable(
            bullets,
            bulletType='bullet'
        )
    )
    elements.append(PageBreak())
    if pie_path:
        elements.append(Paragraph("5.1 Proporção de Faltas Justificadas", styles['Heading3']))
        elements.append(Spacer(1, 6))
        img2 = Image(pie_path, width=300, height=300)
        img2.hAlign = 'CENTER'
        elements.extend([img2, Spacer(1, 12)])

    # 6. Análise Comparativa
    elements.append(Paragraph("6. Análise Comparativa", styles['Heading2']))
    elements.append(Spacer(1, 6))

    justified = ParagraphStyle(
        'Justified',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        firstLineIndent=20
    )

    elements.append(Paragraph(summary_text, justified))

    # Gerar PDF com borda em todas as páginas
    doc.build(elements, onFirstPage=draw_page_border, onLaterPages=draw_page_border)
