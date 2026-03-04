"""
Helper: implemente aqui o carregamento e o cálculo.
"""
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class Helper:
    def load_and_compute(self, filepath: str, has_header: bool, column_name: str = ""):
        return None, None, {"erro": "Implemente helper.load_and_compute"}

    def calculate_statistics(self, df: pd.DataFrame, column_name: str, has_header: bool):
        if has_header and column_name:
            tempDf = df[column_name]
        else:
            tempDf = df.iloc[:, 0]

        tempDf = pd.to_numeric(tempDf, errors="coerce").dropna().sort_values()
        print("calculate_statistics:", tempDf)
        return tempDf