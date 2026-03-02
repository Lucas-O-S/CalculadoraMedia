"""
View: toda a interface (arquivo, checkbox, nome do campo, tabela e resultados).
"""
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class View:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculadora de Média - CSV/XLSX")
        self.root.geometry("720x560")
        self._filepath = tk.StringVar()
        self._has_header = tk.BooleanVar(value=False)
        self._column_name = tk.StringVar()
        self._build_ui()
        self._controller = None

    def _prepare_window(self):
        """Traz a janela para a frente (macOS: só funciona depois da janela estar visível)."""
        self.root.update_idletasks()
        self.root.lift()
        self.root.attributes("-topmost", True)
        delay = 200 if sys.platform == "darwin" else 150
        self.root.after(delay, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def set_controller(self, controller):
        self._controller = controller

    def _build_ui(self):
        # --- Arquivo ---
        f_file = ttk.Frame(self.root, padding=6)
        f_file.pack(fill=tk.X)
        ttk.Button(f_file, text="Selecionar arquivo (xlsx/csv)", command=self._on_select_file).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(f_file, textvariable=self._filepath, foreground="gray").pack(side=tk.LEFT)

        # --- Header + Nome do campo ---
        f_opts = ttk.Frame(self.root, padding=6)
        f_opts.pack(fill=tk.X)
        self._cb_header = ttk.Checkbutton(
            f_opts, text="Tem header", variable=self._has_header, command=self._on_has_header_changed
        )
        self._cb_header.pack(side=tk.LEFT, padx=(0, 12))
        self._f_field = ttk.Frame(f_opts)
        self._f_field.pack(side=tk.LEFT)
        ttk.Label(self._f_field, text="Nome do campo:").pack(side=tk.LEFT, padx=(0, 4))
        self._ent_field = ttk.Entry(self._f_field, textvariable=self._column_name, width=20)
        self._ent_field.pack(side=tk.LEFT)
        self._f_field.pack_forget()  # escondido até marcar "tem header"

        # --- Botão Carregar ---
        f_btn = ttk.Frame(self.root, padding=6)
        f_btn.pack(fill=tk.X)
        ttk.Button(f_btn, text="Carregar e calcular", command=self._on_carregar).pack()

        # --- Tabela de resultados ---
        ttk.Label(self.root, text="Tabela de frequência:", font=("", 10, "bold")).pack(anchor=tk.W, padx=8, pady=(4, 0))
        f_table = ttk.Frame(self.root, padding=6)
        f_table.pack(fill=tk.BOTH, expand=True)
        self._tree = ttk.Treeview(f_table, show="headings", height=10)
        vsb = ttk.Scrollbar(f_table, orient=tk.VERTICAL, command=self._tree.yview)
        hsb = ttk.Scrollbar(f_table, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Resultados (estatísticas) ---
        ttk.Label(self.root, text="Resultados:", font=("", 10, "bold")).pack(anchor=tk.W, padx=8, pady=(8, 0))
        self._txt_resultados = tk.Text(self.root, height=8, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10))
        self._txt_resultados.pack(fill=tk.X, padx=8, pady=6)

    def _on_has_header_changed(self):
        if self._has_header.get():
            self._f_field.pack(side=tk.LEFT)
        else:
            self._f_field.pack_forget()

    def _on_select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel/CSV", "*.xlsx *.csv"), ("Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos", "*.*")]
        )
        if path:
            self._filepath.set(path)

    def _on_carregar(self):
        if self._controller:
            self._controller.on_carregar()

    def get_filepath(self):
        return self._filepath.get().strip()

    def get_has_header(self):
        return self._has_header.get()

    def get_column_name(self):
        return self._column_name.get()

    def show_erro(self, msg):
        messagebox.showerror("Erro", msg)

    def show_tabela(self, df):
        for c in self._tree.get_children():
            self._tree.delete(c)
        cols = list(df.columns)
        self._tree["columns"] = cols
        for c in cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, width=80)
        for _, row in df.iterrows():
            self._tree.insert("", tk.END, values=[row[c] for c in cols])

    def show_resultados(self, stats):
        self._txt_resultados.config(state=tk.NORMAL)
        self._txt_resultados.delete("1.0", tk.END)
        if "erro" in stats:
            self._txt_resultados.insert(tk.END, stats["erro"])
        else:
            self._txt_resultados.insert(tk.END, f"n (total): {stats.get('n', '')}\n")
            self._txt_resultados.insert(tk.END, f"Média: {stats.get('media', 0):.4f}\n")
            self._txt_resultados.insert(tk.END, f"Mediana: {stats.get('mediana', 0):.4f}\n")
            self._txt_resultados.insert(tk.END, f"Variância: {stats.get('variancia', 0):.4f}\n")
            self._txt_resultados.insert(tk.END, f"Desvio padrão: {stats.get('desvio_padrao', 0):.4f}\n")
            self._txt_resultados.insert(tk.END, f"Coeficiente de variação: {stats.get('coeficiente_variacao', 0):.2f}%\n")
        self._txt_resultados.config(state=tk.DISABLED)

    def run(self):
        self.root.deiconify()
        self.root.update()
        # No macOS a janela só aparece à frente se preparar depois do loop iniciar
        self.root.after(50, self._prepare_window)
        self.root.mainloop()
