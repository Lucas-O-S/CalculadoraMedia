"""
Helper: implemente aqui o carregamento e o cálculo.
"""
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

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


class Helper:
    
    
    def load_and_compute(self, filepath: str, has_header: bool, column_name: str = ""):
        return None, None, {"erro": "Implemente helper.load_and_compute"}

    def calculate_statistics(self, df: pd.DataFrame, column_name: str, has_header: bool):
        
        allData = AllData()
        
        if has_header and column_name:
            tempDf = df[column_name]
        else:
            tempDf = df.iloc[:, 0]

        tempDf = pd.to_numeric(tempDf, errors="coerce").dropna().sort_values()
        
        allData.tabela = self.prepare_final_table(allData, tempDf)
        
        return allData
    
    def prepare_final_table(self, allData: AllData, tempDf: pd.Series):
        
        tabela = pd.DataFrame()
        
        allData.tamanho = len(tempDf)
        
        k = int(np.ceil(np.sqrt(allData.tamanho)))
        
        allData.k = k
        
        allData.H = tempDf.max() - tempDf.min()
        
        allData.h = math.ceil(allData.H / k)
        
        allData.amplitude = tempDf.max() - tempDf.min()
        
        allData.classes = self.create_classes(tempDf, k)
        
        allData.tabela = pd.DataFrame(allData.classes, columns=['min', 'max'])
        
        print(allData.tabela)
        
        return allData.tabela
    
    def create_classes(self, tempDf: pd.Series, k: int):
        classes = []
        start = int(tempDf.min())
        i = 0
        while start < tempDf.max():
            
            temp = start
            
            start = start + k
            
            classes.append([temp , start])
            
            i += 1
            
        return classes