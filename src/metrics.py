import re
import pandas as pd
from datetime import time

ENTRY_TIME = pd.Timedelta(hours=8)
LUNCH_START_TIME = pd.Timedelta(hours=12)
LUNCH_END_TIME = pd.Timedelta(hours=13)
EXIT_TIME = pd.Timedelta(hours=17)

_RE_HM    = re.compile(r'^\s*(\d{1,2}):(\d{1,2})\s*$')
_RE_HMS   = re.compile(r'^\s*(\d{1,2}):(\d{1,2}):(\d{1,2})\s*$')

def parse_time_to_timedelta(x):
    if pd.isna(x) or x == '':
        return pd.Timedelta(0)
    if isinstance(x, pd.Timedelta):
        return x
    if isinstance(x, time):
        return pd.Timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)

    s = str(x).strip()
    # HH:MM:SS?
    m = _RE_HMS.match(s)
    if m:
        h, mm, ss = map(int, m.groups())
        return pd.Timedelta(hours=h, minutes=mm, seconds=ss)
    # HH:MM?
    m = _RE_HM.match(s)
    if m:
        h, mm = map(int, m.groups())
        return pd.Timedelta(hours=h, minutes=mm)
    # não reconheceu: trata como zero
    return pd.Timedelta(0)

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)

    time_cols = [
        'Hora_Entrada',
        'Hora_Saida_Almoco',
        'Hora_Entrada_Almoco',
        'Hora_Saida',
    ]

    for col in time_cols:
        df[col] = df[col].apply(parse_time_to_timedelta)

    return df

def calculate_overall_metrics(df: pd.DataFrame) -> dict:
    # 1) Filtrar só dias úteis (não faltas)
    util = df[df['Tipo_Dia'] == 'Útil']

    # 2) Pontualidade geral
    atrasos = (util['Hora_Entrada'] - ENTRY_TIME).clip(lower=pd.Timedelta(0))
    perc_pontual = 1 - (atrasos > pd.Timedelta(0)).mean()

    # 3) Atraso médio de entrada
    avg_delay_entry = atrasos.dt.total_seconds().mean() / 60

    # 4) Atraso médio no retorno do almoço
    lunch_delays = (util['Hora_Entrada_Almoco'] - LUNCH_END_TIME).clip(lower=pd.Timedelta(0))
    avg_delay_lunch = lunch_delays.dt.total_seconds().mean() / 60

    # 5) Horas extras totais
    overtime = (util['Hora_Saida'] - EXIT_TIME).clip(lower=pd.Timedelta(0))
    total_overtime_h = overtime.dt.total_seconds().sum() / 3600

    # 6) Taxa de ausência sem justificativa
    faltas = df[df['Tipo_Dia'] == 'Falta']
    n_faltas = len(faltas)
    n_sem_just = faltas['Justificativa'].isna().sum()
    taxa_ausencia = n_sem_just / n_faltas * 100

    # 7) % de faltas justificadas
    n_just = faltas['Justificativa'].notna().sum()
    pct_faltas_just = n_just / n_faltas * 100

    # Montar dicionário de métricas
    raw = {
        'Pontualidade Geral': (perc_pontual * 100),
        'Atraso Médio na Entrada': avg_delay_entry,
        'Atraso Médio no Almoço': avg_delay_lunch,
        'Horas Extras Totais': total_overtime_h,
        'Taxa de Ausência': taxa_ausencia,
        'Faltas Justificadas': pct_faltas_just
    }

    formatted = {
        'Pontualidade Geral': f"{(perc_pontual * 100):.2f}%",
        'Atraso Médio na Entrada': f"{avg_delay_entry:.2f} min",
        'Atraso Médio no Almoço': f"{avg_delay_lunch:.2f} min",
        'Horas Extras Totais': f"{total_overtime_h:.2f}h",
        'Taxa de Ausência': f"{taxa_ausencia:.2f}%",
        'Faltas Justificadas': f"{pct_faltas_just:.2f}%"
    }

    return {'raw': raw, 'formatted': formatted}

def calculate_metrics_by_employee(df: pd.DataFrame) -> dict:
    recordsRaw = []
    recordsFormatted = []
    grouped = df.groupby(['ID_Funcionario', 'Nome_Funcionario'])

    for (emp_id, emp_name), group in grouped:
        util = group[group['Tipo_Dia'] == 'Útil']
        faltas = group[group['Tipo_Dia'] == 'Falta']

        # % dias pontuais
        atrasos = (util['Hora_Entrada'] - ENTRY_TIME).clip(lower=pd.Timedelta(0))
        pontualidade = 1 - (atrasos > pd.Timedelta(0)).mean()

        # atraso médio de entrada
        avg_delay_entry = atrasos.dt.total_seconds().mean() / 60

        # duração média do almoço
        lunch_durations = (util['Hora_Entrada_Almoco'] - util['Hora_Saida_Almoco']).dt.total_seconds() / 60
        avg_lunch = lunch_durations.mean()

        # horas extras totais
        overtime = (util['Hora_Saida'] - EXIT_TIME).clip(lower=pd.Timedelta(0))
        total_overtime = overtime.dt.total_seconds().sum() / 3600

        # faltas
        n_faltas = len(faltas)
        n_just = faltas['Justificativa'].notna().sum()
        pct_faltas_just = (n_just / n_faltas) * 100 if n_faltas > 0 else 0

        recordsRaw.append({
            'ID': emp_id,
            'Nome': emp_name,
            'Pontualidade': pontualidade * 100,
            'Atraso Médio': avg_delay_entry,
            'Almoço Médio': avg_lunch,
            'Horas Extras': total_overtime,
            'Faltas': n_faltas,
            'Faltas Justificadas': pct_faltas_just
        })

        recordsFormatted.append({
            'ID': emp_id,
            'Nome': emp_name,
            'Pontualidade': f"{(pontualidade * 100):.2f}%",
            'Atraso Médio': f"{(avg_delay_entry):.2f} min",
            'Almoço Médio': f"{(avg_lunch):.2f} min",
            'Horas Extras': f"{total_overtime:.2f}h",
            'Faltas': f"{n_faltas}",
            'Faltas Justificadas': f"{pct_faltas_just:.2f}%"
        })

    df_raw = pd.DataFrame.from_records(recordsRaw)
    df_fmt = pd.DataFrame.from_records(recordsFormatted)
    return {
        'raw': df_raw,
        'formatted': df_fmt
    }

def calculate_metrics_by_sector(df: pd.DataFrame) -> dict:
    recordsRaw = []
    recordsFormatted = []
    for sector, group in df.groupby('Setor'):
        util = group[group['Tipo_Dia'] == 'Útil']
        faltas = group[group['Tipo_Dia'] == 'Falta']

        # Pontualidade média do setor
        atrasos = (util['Hora_Entrada'] - ENTRY_TIME).clip(lower=pd.Timedelta(0))
        pontualidade = 1 - (atrasos > pd.Timedelta(0)).mean()

        # Atraso médio de entrada no setor (min)
        avg_delay = atrasos.dt.total_seconds().mean() / 60

        # Horas extras totais no setor (h)
        overtime = (util['Hora_Saida'] - EXIT_TIME).clip(lower=pd.Timedelta(0))
        total_overtime = overtime.dt.total_seconds().sum() / 3600

        # Taxa de faltas no setor (sem distinguir justificativa)
        taxa_faltas = len(faltas) / len(group) * 100

        # % faltas justificadas
        n_faltas = len(faltas)
        n_just = faltas['Justificativa'].notna().sum()
        pct_faltas_just = (n_just / n_faltas * 100) if n_faltas > 0 else 0

        recordsRaw.append({
            'Setor': sector,
            'Pontualidade': pontualidade * 100,
            'Atraso Médio na Entrada': avg_delay,
            'Horas Extras': total_overtime,
            'Taxa de Faltas': taxa_faltas,
            'Faltas Justificadas': pct_faltas_just
        })

        recordsFormatted.append({
            'Setor': sector,
            'Pontualidade': f"{(pontualidade * 100):.2f}%",
            'Atraso Médio na Entrada': f"{avg_delay:.2f} min",
            'Horas Extras': f"{total_overtime:.2f}h",
            'Taxa de Faltas': f"{taxa_faltas:.2f}%",
            'Faltas Justificadas': f"{pct_faltas_just:.2f}%"
        })

    df_raw = pd.DataFrame.from_records(recordsRaw)
    df_fmt = pd.DataFrame.from_records(recordsFormatted)
    return {
        'raw': df_raw,
        'formatted': df_fmt
    }

def calculate_lunch_metrics(df: pd.DataFrame) -> dict:
    # Filtrar apenas dias úteis
    util = df[df['Tipo_Dia'] == 'Útil']

    # Calcular duração em minutos
    durations = (util['Hora_Entrada_Almoco'] - util['Hora_Saida_Almoco']).dt.total_seconds() / 60

    # Estatísticas
    avg_lunch = durations.mean()
    std_lunch = durations.std()
    pct_short = (durations < 45).mean() * 100

    raw = {
        'Tempo de Almoço Médio': avg_lunch,
        'Desvio Padrão': std_lunch,
        'Intervalos com tempo menor que 45 min': pct_short
    }

    formatted = {
        'Tempo de Almoço Médio': f"{avg_lunch:.2f} min",
        'Desvio Padrão': f"{std_lunch:.2f}",
        'Intervalos com tempo menor que 45 min': f"{pct_short:.2f}%"
    }

    return {'raw': raw, 'formatted': formatted}

def calculate_additional_indicators(df: pd.DataFrame) -> dict:
    # Filtra apenas dias úteis
    util = df[df['Tipo_Dia'] == 'Útil']

    # Calcula atrasos em minutos (clip lower 0)
    delays = (util['Hora_Entrada'] - ENTRY_TIME).clip(lower=pd.Timedelta(0))
    delays_min = delays.dt.total_seconds() / 60

    # Top 5 funcionários mais atrasados (por atraso médio)
    by_emp = util.copy()
    by_emp['Delay_Min'] = delays_min
    avg_by_emp = by_emp.groupby('Nome_Funcionario')['Delay_Min'].mean()
    top5 = avg_by_emp.sort_values(ascending=False).head(5).index.tolist()

    return {
        'Top 5 mais Atrasados': top5
    }
