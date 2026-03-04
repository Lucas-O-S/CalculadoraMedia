"""
Controller: conecta a tela ao backend. Implemente on_carregar.
"""

import csv

import pandas as pd
from helper import Helper, ColunaNaoEncontradaError, DadosInsuficientesError, DadosNaoNumericosError

class Controller:

    headers = False
    columns = ""
    
    database = None
    
    allData = None
    
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
        try:
            header = 0 if self.headers else None
            ext = database.rsplit(".", 1)[-1].lower()

            if ext not in ("csv", "xlsx", "xls"):
                self.view.show_erro(f"Formato '{ext}' não suportado. Use CSV ou XLSX.")
                return

            if ext == "csv":
                with open(database, "r", encoding="utf-8", errors="replace") as f:
                    sample = f.read(4096)
                if sample.lstrip().startswith("{\\rtf"):
                    self.view.show_erro(
                        "Arquivo RTF com extensão .csv.\n"
                        "Abra no TextEdit → Formatar → Converter em Texto Simples e salve novamente."
                    )
                    return
                try:
                    sep = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
                except csv.Error:
                    sep = ","
                # Detecta automaticamente se tem cabeçalho quando usuário não marcou
                if not self.headers:
                    has_header_detected = csv.Sniffer().has_header(sample)
                    if has_header_detected:
                        self.headers = True
                        self.view.notify_header_detected()
                        header = 0
                self.database = pd.read_csv(database, header=header, sep=sep)
            else:
                # Para xlsx, verifica se a primeira linha é texto (cabeçalho)
                df_raw = pd.read_excel(database, header=None, engine="openpyxl")
                if not self.headers:
                    first_row = df_raw.iloc[0]
                    if all(isinstance(v, str) for v in first_row):
                        self.headers = True
                        self.view.notify_header_detected()
                        header = 0
                self.database = pd.read_excel(database, header=header, engine="openpyxl")

        except FileNotFoundError:
            self.view.show_erro("Arquivo não encontrado. Verifique se ele ainda existe.")
        except PermissionError:
            self.view.show_erro("Sem permissão para ler o arquivo. Feche-o se estiver aberto em outro programa.")
        except UnicodeDecodeError:
            self.view.show_erro("Erro de codificação no arquivo. Tente salvar o CSV como UTF-8.")
        except Exception as exc:
            self.view.show_erro(f"Erro ao carregar arquivo:\n{exc}")
        
    def get_database(self) -> pd.DataFrame:
        print(f"get_database: {self.database}")
        return self.database

    def reset(self):
        self.database = None
        self.columns  = ""
        self.headers  = False
        self.allData  = None
    
    def calculate_statistics(self):
        try:
            if self.database is None:
                self.view.show_erro("Nenhum arquivo carregado. Selecione um arquivo primeiro.")
                return

            allData = self.helper.calculate_statistics(self.database, self.columns, self.headers)

            self.view.show_tabela(allData.tabela)
            self.view.show_resultados({
                "n":                    allData.tamanho,
                "media":                allData.media,
                "mediana":              allData.mediana,
                "variancia":            allData.variancia,
                "desvio_padrao":        allData.desvio_padrao,
                "coeficiente_variacao": allData.coeficiente_de_variacao,
            })

        except ColunaNaoEncontradaError as exc:
            self.view.show_erro(str(exc))
        except DadosNaoNumericosError as exc:
            self.view.show_erro(str(exc))
        except DadosInsuficientesError as exc:
            self.view.show_erro(str(exc))
        except KeyError as exc:
            self.view.show_erro(f"Coluna não encontrada: {exc}\nVerifique o nome da coluna informado.")
        except Exception as exc:
            self.view.show_erro(f"Erro inesperado ao calcular:\n{exc}")

        