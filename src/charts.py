import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

def plot_punctuality_by_sector(df_sector, output_path="output/comparacao_setores.png"):
    # Extrair dados
    setores = df_sector['Setor'].tolist()
    # Detecta formato de valores: string com '%' ou numérico
    raw_vals = df_sector.get('Pontualidade_%', df_sector.get('Pontualidade'))
    pontualidades = []
    for v in raw_vals:
        if isinstance(v, str) and v.endswith('%'):
            pontualidades.append(float(v.strip('%')))
        else:
            pontualidades.append(float(v))

    # Criar figura e eixo com tamanho maior para legibilidade
    fig, ax = plt.subplots(figsize=(8, 5))
    positions = range(len(setores))
    bars = ax.bar(positions, pontualidades, tick_label=setores)

    # Formatar eixos
    ax.set_title('Pontualidade Média por Setor', fontsize=14)
    ax.set_xlabel('Setor', fontsize=12)
    ax.set_ylabel('Pontualidade (%)', fontsize=12)
    ax.set_ylim(0, max(pontualidades) * 1.1)
    # Exibe ticks do eixo Y como percentuais
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))

    # Rotaciona e ajusta fonte das labels do eixo X
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
    ax.tick_params(axis='y', labelsize=10)
    plt.tight_layout()

    # Anotar valores no topo de cada barra
    for bar, val in zip(bars, pontualidades):
        ax.annotate(f'{val:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, val),
                    xytext=(0, 3),  # desloca 3 pontos acima da barra
                    textcoords='offset points',
                    ha='center', va='bottom', fontsize=8)

    # Salvar ou mostrar
    if output_path:
        plt.savefig(output_path, dpi=300)
        plt.close(fig)
    else:
        plt.show()

def plot_absence_justification_pie(df, output_path="output/proporcao_faltas.png"):
    # Filtrar apenas registros de falta
    faltas = df[df['Tipo_Dia'].str.lower() == 'falta']
    # Contar justificadas vs não justificadas
    justificadas = faltas['Justificativa'].notna().sum()
    nao_just = faltas['Justificativa'].isna().sum()

    labels = ['Justificadas', 'Não Justificadas']
    sizes = [justificadas, nao_just]

    # Criar pizza
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct='%.1f%%',
        startangle=90
    )

    # Estilizar textos
    for text in texts + autotexts:
        text.set_fontsize(10)

    ax.set_title('Proporção de Faltas Justificadas', fontsize=14)
    ax.axis('equal')  # garante que o círculo fique redondo
    plt.tight_layout()

    # Salvar ou mostrar
    if output_path:
        plt.savefig(output_path, dpi=300)
        plt.close(fig)
    else:
        plt.show()