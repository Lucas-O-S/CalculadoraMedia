"""
Helper para abrir diálogo nativo de arquivo (tkinter).
Usado como subprocess para funcionar em Windows, macOS e Linux.
Imprime o caminho do arquivo escolhido em stdout (uma linha); vazio se cancelar.
"""
import sys
from tkinter import Tk, filedialog

def main():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Selecionar arquivo CSV ou XLSX",
        filetypes=[
            ("CSV / XLSX", "*.csv *.xlsx"),
            ("CSV", "*.csv"),
            ("Excel", "*.xlsx"),
            ("Todos", "*.*"),
        ],
    )
    root.destroy()
    print(path or "")

if __name__ == "__main__":
    main()
    sys.exit(0)
