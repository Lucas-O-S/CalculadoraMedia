"""
Helper: carrega arquivo (xlsx/csv) e calcula tabela de frequência + estatísticas.
Mínimo para você estender.
"""
import math
import pandas as pd
import numpy as np


def load_and_compute(filepath: str, has_header: bool, column_name: str = ""):
    """
    Carrega xlsx ou csv e retorna (df_raw, df_frequencia, stats).
    has_header=True: usa coluna com nome column_name para os valores.
    has_header=False: achata toda a tabela e usa como série.
    """
    path = filepath.lower()
    if path.endswith(".xlsx"):
        df = pd.read_excel(filepath, header=None if not has_header else 0)
    elif path.endswith(".csv"):
        df = pd.read_csv(filepath, header=None if not has_header else 0)
    else:
        return None, None, {"erro": "Use arquivo .xlsx ou .csv"}

    if has_header and column_name and column_name in df.columns:
        temp_series = df[column_name].dropna()
    elif has_header and column_name:
        return None, None, {"erro": f"Coluna '{column_name}' não encontrada."}
    else:
        temp_series = pd.Series(df.values.flatten()).dropna()

    temp_series = pd.to_numeric(temp_series, errors="coerce").dropna()
    if temp_series.empty:
        return None, None, {"erro": "Nenhum valor numérico encontrado."}

    temp_series = temp_series.sort_values().reset_index(drop=True)
    n = len(temp_series)
    k = int(np.ceil(np.sqrt(n)))
    H = temp_series.max() - temp_series.min()
    h = math.ceil(H / k) if k else 1
    if h < 1:
        h = 1

    start = float(temp_series.min())
    classes = []
    while start < temp_series.max():
        end = start + k
        classes.append([start, end])
        start = end

    final = pd.DataFrame(classes, columns=["min", "max"])
    bins = list(final["min"]) + [final["max"].iloc[-1]]
    fi = pd.cut(temp_series, bins=bins, right=False)
    freq = fi.value_counts().sort_index()
    final["fi"] = freq.values
    final["Xm"] = (final["min"] + final["max"] - 1) / 2
    final.loc[final.index[-1], "Xm"] = (final["min"].iloc[-1] + final["max"].iloc[-1]) / 2

    fa = 0
    fas = []
    for i in range(len(final)):
        fa += final["fi"].iloc[i]
        fas.append(fa)
    final["fa"] = fas

    media = (final["Xm"] * final["fi"]).sum() / n
    posicao = n / 2
    limite_inferior = 0
    freq_anterior = 0
    fi_classe = 0
    for i in range(len(final)):
        if final["fa"].iloc[i] >= posicao:
            limite_inferior = final["min"].iloc[i]
            freq_anterior = final["fa"].iloc[i - 1] if i > 0 else 0
            fi_classe = final["fi"].iloc[i]
            break
    mediana = limite_inferior + ((posicao - freq_anterior) / fi_classe) * h if fi_classe else 0

    variancia = ((final["Xm"] - media) ** 2 * final["fi"]).sum() / n
    desvio = math.sqrt(variancia)
    cv = (desvio / media) * 100 if media else 0

    stats = {
        "n": n,
        "media": media,
        "mediana": mediana,
        "variancia": variancia,
        "desvio_padrao": desvio,
        "coeficiente_variacao": cv,
    }
    return df, final, stats
