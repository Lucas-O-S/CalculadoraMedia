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


class Helper:
    
    
    def load_and_compute(self, filepath: str, has_header: bool, column_name: str = ""):
        return None, None, {"erro": "Implemente helper.load_and_compute"}

    def calculate_statistics(self, df: pd.DataFrame, column_name: str, has_header: bool):
        if df is None:
            raise ValueError("Nenhum arquivo carregado. Selecione um arquivo antes de calcular.")

        allData = AllData()

        if has_header and column_name:
            if column_name not in df.columns:
                disponiveis = ", ".join(str(c) for c in df.columns)
                raise ColunaNaoEncontradaError(
                    f"Coluna '{column_name}' não encontrada.\n"
                    f"Colunas disponíveis: {disponiveis}"
                )
            tempDf = df[column_name]
        else:
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
    
    def prepare_final_table(self, allData: AllData, tempDf: pd.DataFrame):
        
        tabela = pd.DataFrame()
        
        allData.tamanho = len(tempDf)
        
        k = int(np.ceil(np.sqrt(allData.tamanho)))
        
        allData.k = k
        
        allData.H = float(tempDf.max() - tempDf.min())
        
        allData.h = math.ceil(allData.H / k)
        
        allData.classes = self.create_classes(tempDf, k)
        
        allData.tabela = pd.DataFrame(allData.classes, columns=['min', 'max'])
        
        frequency = self.frequency_distribution(allData.tabela, tempDf)
        
        allData.tabela['fi'] = frequency
        
        allData.tabela['Xm'] = self.point_mean(allData.tabela)
        
        allData.tabela['fa'] = self.calculate_fa(allData.tabela)
        
        allData.media = self.calculate_media(allData.tabela, allData.tamanho)
        
        allData.mediana = self.calculate_median(allData.tabela, allData.tabela['fa'].values, allData.h, allData.tamanho)
        
        allData.variancia = self.calculate_variance(allData.tabela, allData.media, allData.tamanho)
        
        print(allData.tabela)
        
        allData.desvio_padrao = self.calculate_standard_deviation(allData.variancia)
        
        allData.coeficiente_de_variacao = self.calculate_coefficient_of_variation(allData.desvio_padrao, allData.media)
        
        return allData.tabela
    
    def create_classes(self, tempDf: pd.Series, k: int):
        
        classes = []
        
        start = int(float(tempDf.min()))
        maximo = float(tempDf.max())

        while start < maximo:
            
            temp = start
            
            start = start + k
            
            classes.append([temp , start])
            
            
        return classes
    
    def frequency_distribution(self, tabela: pd.DataFrame, dados: pd.Series):
        
        bins = list(tabela['min']) + [tabela['max'].iloc[-1]]

        fi = pd.cut(dados, bins=bins, right=False)

        frequency = fi.value_counts().sort_index()
        print(frequency.values)
        return frequency.values
    
    def point_mean(self, tabela: pd.DataFrame):
        
        xm = pd.DataFrame()
        
        xm['Xm'] = (tabela['min'] + tabela['max'] - 1) / 2
        
        xm.loc[xm.index[-1], 'Xm'] = (tabela['min'].iloc[-1] + tabela['max'].iloc[-1]) / 2
        
        print(xm)
        
        return xm.values
    
    def calculate_fa(self, tabela: pd.DataFrame):
        
        fa = []
        fa_acumulada = 0
        for i in range(len(tabela)):
            fa_acumulada += tabela['fi'].iloc[i]
            fa.append(fa_acumulada)
        
        
        return fa
    
    def calculate_media(self, tabela: pd.DataFrame, n: int):
        
        media = 0
        
        for i in range(len(tabela)):
            media += tabela['Xm'].iloc[i] * tabela['fi'].iloc[i]
            
        media = media / n
        
        print("media:", media)
        
        return media
    
    def calculate_median(self, tabela: pd.DataFrame, frequenciaAcumulada: list, h: float, n: int):
        
        mediana = 0
        
        posicao = 0
        
        if n % 2 == 0:
            posicao = ((n/2) + (n/2 + 1)) / 2
        
        else:
            posicao = (n+1)/2
            
        for i in range(len(frequenciaAcumulada)):
            
            if frequenciaAcumulada[i] >= posicao:
              
                classeMediana = tabela['min'].iloc[i]
              
                frequenciaAnterior = frequenciaAcumulada[i-1] if i > 0 else 0
              
                fi = tabela['fi'].iloc[i]
              
                limiteInferior = tabela['min'].iloc[i]
              
                break
            
        mediana = limiteInferior + ((posicao - frequenciaAnterior) / fi) * h
            
        print("mediana:", mediana)
        
        return mediana
    
    def calculate_variance(self, tabela: pd.DataFrame, media: float, n: int):
        
        variance = 0
        
        for i in range(len(tabela)):
            variance += (tabela['Xm'].iloc[i] - media) ** 2
            
        variance = variance / n
        
        print("variancia:", variance)
        
        return variance
    
    def calculate_standard_deviation(self, variance: float):
        
        standard_deviation = math.sqrt(variance)
        
        print("desvio padrao:", standard_deviation)
        
        return standard_deviation
    
    def calculate_coefficient_of_variation(self, standard_deviation: float, media: float):
        
        coefficient_of_variation = (standard_deviation / media) * 100
        
        print("coeficiente de variacao:", coefficient_of_variation)
        
        return coefficient_of_variation
    
    