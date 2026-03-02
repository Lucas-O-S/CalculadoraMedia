"""
Controller: conecta View e Helper. Mínimo para você mexer.
"""
from helper import load_and_compute


class Controller:
    def __init__(self, view):
        self.view = view

    def on_carregar(self):
        path = self.view.get_filepath()
        if not path:
            self.view.show_erro("Selecione um arquivo .xlsx ou .csv")
            return
        has_header = self.view.get_has_header()
        column_name = self.view.get_column_name().strip() if has_header else ""
        if has_header and not column_name:
            self.view.show_erro("Informe o nome do campo (coluna).")
            return
        df_raw, df_freq, stats = load_and_compute(path, has_header, column_name)
        if stats.get("erro"):
            self.view.show_erro(stats["erro"])
            return
        self.view.show_tabela(df_freq)
        self.view.show_resultados(stats)
