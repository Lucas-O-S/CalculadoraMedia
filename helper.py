"""
Helper: implemente aqui o carregamento e o cálculo.
"""
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# ── Exceções específicas ───────────────────────────────────────────────────────

class ColunaNaoEncontradaError(Exception):
    """Coluna informada não existe no arquivo."""

class DadosInsuficientesError(Exception):
    """Menos de 2 valores numéricos após limpeza."""

class DadosNaoNumericosError(Exception):
    """Nenhum valor numérico encontrado na coluna."""


class AllData:
    media = 0
    mediana = 0
    variancia = 0
    desvio_padrao = 0
    coeficiente_de_variacao = 0
    tabela = pd.DataFrame()
    k = 0
    h = 0
    H = 0
    tamanho = 0
    amplitude = 0
    total_xm_fi = 0
        
    moda = 'Não foi possível calcular a moda'
    totalXmFi = 0
    totalXmMediaQuadrado = 0
    
    


class Helper:
    
    
    def load_and_compute(self, filepath: str, has_header: bool, column_name: str = ""):
        return None, None, {"erro": "Implemente helper.load_and_compute"}

    def calculate_statistics(self, df: pd.DataFrame, column_name: str, has_header: bool):
        if df is None:
            raise ValueError("Nenhum arquivo carregado. Selecione um arquivo antes de calcular.")

        allData = AllData()

        num_colunas = len(df.columns)

        if has_header:
            # Arquivo tem cabeçalho: exige nome da coluna quando há mais de uma
            if num_colunas > 1 and not column_name:
                disponiveis = ", ".join(str(c) for c in df.columns)
                raise ColunaNaoEncontradaError(
                    f"O arquivo tem {num_colunas} colunas. Informe o nome da coluna desejada.\n"
                    f"Colunas disponíveis: {disponiveis}"
                )
            if column_name:
                # Busca exata primeiro, depois case-insensitive
                if column_name in df.columns:
                    col_real = column_name
                else:
                    col_lower = column_name.strip().lower()
                    match = next((c for c in df.columns if str(c).lower() == col_lower), None)
                    if match is None:
                        disponiveis = ", ".join(str(c) for c in df.columns)
                        raise ColunaNaoEncontradaError(
                            f"Coluna '{column_name}' não encontrada.\n"
                            f"Colunas disponíveis: {disponiveis}"
                        )
                    col_real = match
                tempDf = df[col_real]
            else:
                tempDf = df.iloc[:, 0]
        else:
            # Sem cabeçalho: planifica todas as colunas em uma série única
            tempDf = pd.Series(df.values.flatten())

        tempDf = pd.to_numeric(tempDf, errors="coerce").dropna().sort_values().reset_index(drop=True)

        if len(tempDf) == 0:
            raise DadosNaoNumericosError(
                "Nenhum valor numérico encontrado na coluna selecionada.\n"
                "Verifique se o arquivo e a coluna estão corretos."
            )
        if len(tempDf) < 2:
            raise DadosInsuficientesError(
                "São necessários pelo menos 2 valores numéricos para calcular as estatísticas."
            )
            


        allData.tabela = self.prepare_final_table(allData, tempDf)
        return allData
    
    def prepare_final_table(self, allData: AllData, tempDf: pd.Series):

        allData.tamanho = len(tempDf)

        k = int(np.ceil(np.sqrt(allData.tamanho)))
        allData.k = k
        allData.H = float(tempDf.max() - tempDf.min())
        allData.h = math.ceil(allData.H / k)

        # classes usam k como passo (igual ao notebook original)
        allData.classes = self.create_classes(tempDf, k)

        allData.tabela = pd.DataFrame(allData.classes, columns=['min', 'max'])

        frequency = self.frequency_distribution(allData.tabela, tempDf)
        allData.tabela['fi'] = frequency

        allData.tabela['Xm'] = self.point_mean(allData.tabela)
        
        allData.tabela['fi*Xm'] = allData.tabela['fi'] * allData.tabela['Xm']

        allData.tabela['Fr%'] = self.calculate_Fr(allData.tabela, allData.tamanho)
        
        allData.tabela['fa'] = self.calculate_fa(allData.tabela)
        
        allData.amplitude   = allData.H
        allData.total_xm_fi = float(allData.tabela['fi*Xm'].sum())

        allData.media             = self.calculate_media(allData.tabela, allData.tamanho)
        allData.mediana           = self.calculate_median(allData.tabela, allData.tabela['fa'].values, allData.h, allData.tamanho)
        allData.variancia         = self.calculate_variance(allData.tabela, allData.media, allData.tamanho)
        allData.desvio_padrao     = self.calculate_standard_deviation(allData.variancia)
        allData.coeficiente_de_variacao = self.calculate_coefficient_of_variation(allData.desvio_padrao, allData.media)

        allData.tabela['Xm-média'] = (allData.tabela['Xm'] - allData.media).round(4)
        allData.tabela['(Xm-média)²'] = (allData.tabela['Xm-média'] ** 2).round(4)
        allData.totalXmMediaQuadrado = float(allData.tabela['(Xm-média)²'].sum())
        
        allData.tabela['Intervalo'] = allData.tabela.apply(lambda r: str(int(r['min'])) + " |---- " + str(int(r['max'])), axis=1)
        
        allData.tabela['Intervalo'].iloc[-1] = str(allData.tabela['min'].iloc[-1]) + " |----| " + str(allData.tabela['max'].iloc[-1])

        allData.tabela.drop(columns=['min', 'max'], inplace=True)
        
        cols = ['Intervalo'] + [c for c in allData.tabela.columns if c != 'Intervalo']
        
        allData.tabela = allData.tabela[cols]

        allData.moda = self.calculate_moda(allData.tabela, allData.h)


        
        return allData.tabela

    def create_classes(self, tempDf: pd.Series, k: int):
        """Intervalos com passo k (igual ao notebook original)."""
        classes = []
        start  = int(float(tempDf.min()))
        maximo = float(tempDf.max())
        while start < maximo:
            classes.append([start, start + k])
            start += k
        return classes

    def frequency_distribution(self, tabela: pd.DataFrame, dados: pd.Series):
        bins = list(tabela['min']) + [tabela['max'].iloc[-1]]
        fi = pd.cut(dados, bins=bins, right=False)
        frequency = fi.value_counts().sort_index().reindex(fi.cat.categories, fill_value=0)
        return frequency.values

    def point_mean(self, tabela: pd.DataFrame):
        """Xm = (min + max - 1) / 2, exceto última classe: (min + max) / 2."""
        xm = (tabela['min'] + tabela['max'] - 1) / 2
        xm.iloc[-1] = (tabela['min'].iloc[-1] + tabela['max'].iloc[-1]) / 2
        return xm.values

    def calculate_fa(self, tabela: pd.DataFrame):
        return tabela['fi'].cumsum().tolist()

    def calculate_media(self, tabela: pd.DataFrame, n: int):
        media = 0.0
        for i in range(len(tabela)):
            media += tabela['Xm'].iloc[i] * tabela['fi'].iloc[i]
        media = media / n
        print("media:", media)
        return float(media)

    def calculate_median(self, tabela: pd.DataFrame, frequenciaAcumulada, h: float, n: int):
        posicao = ((n / 2) + (n / 2 + 1)) / 2 if n % 2 == 0 else (n + 1) / 2
        for i in range(len(frequenciaAcumulada)):
            if frequenciaAcumulada[i] >= posicao:
                limiteInferior    = float(tabela['min'].iloc[i])
                frequenciaAnterior = float(frequenciaAcumulada[i - 1]) if i > 0 else 0.0
                fi                = float(tabela['fi'].iloc[i])
                mediana = limiteInferior + ((posicao - frequenciaAnterior) / fi) * h
                print("mediana:", mediana)
                return mediana
        return 0.0

    def calculate_variance(self, tabela: pd.DataFrame, media: float, n: int):
        """Variância sem ponderação por fi: Σ(Xm - média)² / n (igual ao notebook)."""
        variance = 0.0
        for i in range(len(tabela)):
            variance += (tabela['Xm'].iloc[i] - media) ** 2
        variance = variance / n
        print("variancia:", variance)
        return float(variance)

    def calculate_standard_deviation(self, variance: float):
        standard_deviation = math.sqrt(variance)
        print("desvio padrao:", standard_deviation)
        return standard_deviation

    def calculate_coefficient_of_variation(self, standard_deviation: float, media: float):
        coefficient_of_variation = (standard_deviation / media) * 100
        print("coeficiente de variacao:", coefficient_of_variation)
        return coefficient_of_variation
    
    def calculate_Fr(self, tabela: pd.DataFrame, total: int):
        return tabela['fi'] / total * 100
    
    def calculate_moda(self, tabela: pd.DataFrame, h: float):
   
        max_fi = tabela['fi'].idxmax()
        
        moda = tabela['Intervalo'].iloc[max_fi]
        
        return moda
