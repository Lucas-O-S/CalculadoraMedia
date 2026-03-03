"""
View Flet: tela pronta para enviar e receber valores.
Conecte seu backend em set_on_carregar(); use get_filepath(), get_has_header(), get_column_name()
para ler; use show_tabela(), show_resultados(), show_erro() para atualizar a tela.
"""
import flet as ft


class ViewFlet:
    def __init__(self, page: ft.Page):
        self.page = page
        self._on_carregar_callback = None
        self.controller = None  # referência ao controller (definida em set_controller)

        page.title = "Calculadora de Média - CSV/XLSX"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.window.min_width = 720
        page.window.min_height = 560

        # Estado dos controles
        self._filepath_ref = ft.Ref[ft.Text]()
        self._cb_header = ft.Checkbox(label="Tem Cabeçalho", value=False, on_change=self._on_header_changed)
        self._field_name = ft.Ref[ft.TextField]()
        self._field_row = ft.Ref[ft.Row]()
        self._data_table = ft.Ref[ft.DataTable]()
        self._resultados = ft.Ref[ft.Column]()

        # Flet >=0.80: FilePicker não vai em overlay; cria-se na hora e chama pick_files().

        # Monta a UI
        page.add(
            # --- Arquivo ---
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Selecionar arquivo (xlsx/csv)",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=self._on_select_file_click,
                    ),
                    ft.Text("Nenhum arquivo selecionado", ref=self._filepath_ref, color=ft.Colors.GREY_600),
                ],
                wrap=True,
            ),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

            # --- Header + Nome do campo ---
            ft.Row(
                controls=[
                    self._cb_header,
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Nome do campo:"),
                                ft.TextField(ref=self._field_name, width=200, hint_text="ex.: Nota"),
                            ],
                            ref=self._field_row,
                            visible=False,
                        ),
                    ),
                ],
            ),
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT),

            # --- Botão Carregar ---
            ft.ElevatedButton(
                "Carregar e calcular",
                icon=ft.Icons.CALCULATE,
                on_click=self._on_carregar_click,
                style=ft.ButtonStyle(padding=16),
            ),
            ft.Divider(height=24, color=ft.Colors.TRANSPARENT),

            # --- Tabela de frequência ---
            ft.Text("Tabela de frequência", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    [ft.DataTable(
                            ref=self._data_table,
                            columns=[ft.DataColumn(ft.Text("—"))],
                            rows=[],
                            border=ft.border.all(1),
                            border_radius=8,
                        )],
                    scroll=ft.ScrollMode.AUTO,
                ),
                height=220,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=8,
                padding=8,
            ),
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT),

            # --- Resultados ---
            ft.Text("Resultados", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(ref=self._resultados, spacing=4),
                padding=12,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=8,
            ),
        )

    async def _on_select_file_click(self, e):
        file_picker = ft.FilePicker()
        files = await file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx", "csv"],
        )
        if files and len(files) > 0:
            f = files[0]
            path = getattr(f, "path", None) or getattr(f, "name", "") or ""
            if self._filepath_ref.current:
                self._filepath_ref.current.value = path
                self._filepath_ref.current.color = ft.Colors.ON_SURFACE
                self.page.update()

    def _on_header_changed(self, e):
        if self._field_row.current:
            self._field_row.current.visible = self._cb_header.value
            self.page.update()
        self.controller.set_headers(self._cb_header.value)

    def _on_carregar_click(self, e):
        if self._on_carregar_callback:
            self._on_carregar_callback()
        else:
            self.show_erro("Conecte o backend: view.set_on_carregar(sua_funcao)")

    # ---------- API para você conectar o backend ----------

    def set_controller(self, controller):
        """Guarda referência ao controller para acessar variáveis e métodos: self.controller.xxx"""
        self.controller = controller

    def set_on_carregar(self, callback):
        """Chamado quando o usuário clica em 'Carregar e calcular'. callback() sem argumentos."""
        self._on_carregar_callback = callback

    def get_filepath(self) -> str:
        if self._filepath_ref.current:
            return (self._filepath_ref.current.value or "").strip()
        return ""

    def get_has_header(self) -> bool:
        return self._cb_header.value

    def get_column_name(self) -> str:
        if self._field_name.current:
            return (self._field_name.current.value or "").strip()
        return ""

    def show_erro(self, msg: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.Colors.ON_ERROR_CONTAINER),
            bgcolor=ft.Colors.ERROR_CONTAINER,
            open=True,
        )
        self.page.update()

    def show_tabela(self, df):
        """Atualiza a tabela. df: pandas DataFrame (colunas e linhas)."""
        if df is None or df.empty:
            if self._data_table.current:
                self._data_table.current.columns = [ft.DataColumn(ft.Text("—"))]
                self._data_table.current.rows = []
                self.page.update()
            return
        cols = list(df.columns)
        self._data_table.current.columns = [
            ft.DataColumn(ft.Text(str(c), weight=ft.FontWeight.BOLD)) for c in cols
        ]
        self._data_table.current.rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(row[c])[:20])) for c in cols])
            for _, row in df.iterrows()
        ]
        self.page.update()

    def show_resultados(self, stats: dict):
        """Atualiza a área de resultados. stats: dict com n, media, mediana, variancia, desvio_padrao, coeficiente_variacao ou erro."""
        if self._resultados.current is None:
            return
        if stats.get("erro"):
            self._resultados.current.controls = [ft.Text(stats["erro"], color=ft.Colors.ERROR)]
        else:
            self._resultados.current.controls = [
                ft.Text(f"n (total): {stats.get('n', '')}", size=14),
                ft.Text(f"Média: {stats.get('media', 0):.4f}", size=14),
                ft.Text(f"Mediana: {stats.get('mediana', 0):.4f}", size=14),
                ft.Text(f"Variância: {stats.get('variancia', 0):.4f}", size=14),
                ft.Text(f"Desvio padrão: {stats.get('desvio_padrao', 0):.4f}", size=14),
                ft.Text(f"Coeficiente de variação: {stats.get('coeficiente_variacao', 0):.2f}%", size=14),
            ]
        self.page.update()
