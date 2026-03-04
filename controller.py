"""
Controller: conecta a tela ao backend. Implemente on_carregar.
"""

import csv

import pandas as pd
from helper import Helper

class Controller:

    headers = False
    columns = ""
    
    database = None
    
    helper = Helper()

    def __init__(self, view):
        self.view = view

    def on_carregar(self):
        self.view.show_erro("Implemente controller.on_carregar")

    def set_headers(self, headers: bool):
        print(f"set_headers: {headers}")
        self.headers = headers
        
    def set_column_name(self, column_name: str):
        print(f"set_column_name: {column_name}")
        self.columns = column_name
        
    def set_database(self, database: str):
        print(f"set_database: {database}")
        header = 0 if self.headers else None
        ext = database.rsplit(".", 1)[-1].lower()
        if ext == "csv":
            with open(database, "r", encoding="utf-8", errors="replace") as f:
                sample = f.read(4096)
            # RTF disfarçado de CSV: arquivo salvo como .rtf mas com extensão .csv
            if sample.lstrip().startswith("{\\rtf"):
                raise ValueError(
                    "O arquivo parece ser RTF, não CSV.\n"
                    "Abra no TextEdit → Formatar → Converter em Texto Simples e salve novamente."
                )
            # Detecta o separador automaticamente (vírgula, ponto-e-vírgula, tab, etc.)
            try:
                sep = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                sep = ","
            self.database = pd.read_csv(database, header=header, sep=sep)
        else:
            self.database = pd.read_excel(database, header=header, engine="openpyxl")
        print(self.database)
        
    def get_database(self) -> pd.DataFrame:
        print(f"get_database: {self.database}")
        return self.database
    
    def calculate_statistics(self):
        print(f"calculate_statistics: {self.database}, {self.columns}, {self.headers}")
        self.helper.calculate_statistics(self.database, self.columns, self.headers)
        