"""
View Flet: tela pronta para enviar e receber valores.
Conecte seu backend em set_on_carregar(); use get_filepath(), get_has_header(), get_column_name()
para ler; use show_tabela(), show_resultados(), show_erro() para atualizar a tela.
Seletor de arquivo: tkinter em subprocess (funciona em Windows, macOS e Linux).
"""
import os
import subprocess
import sys

import flet as ft

# Paleta
_PRIMARY   = ft.Colors.BLUE_700
_SURFACE   = ft.Colors.WHITE
_OUTLINE   = ft.Colors.BLUE_GREY_100
_HEADER_BG = ft.Colors.BLUE_50


def _card(content, padding: int = 16) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=12,
        border=ft.border.all(1, _OUTLINE),
        bgcolor=_SURFACE,
        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
    )


def _section_title(text: str) -> ft.Text:
    return ft.Text(text, size=15, weight=ft.FontWeight.W_600, color=_PRIMARY)


class ViewFlet:
    def __init__(self, page: ft.Page):
        self.page = page
        self._on_carregar_callback = None
        self.controller = None

        page.title = "Calculadora de Média"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ft.Colors.BLUE_GREY_50
        page.padding = ft.padding.symmetric(horizontal=32, vertical=24)
        page.window.min_width = 680
        page.window.min_height = 520
        page.scroll = ft.ScrollMode.AUTO
        page.fonts = {}

        # Refs
        self._filepath_ref       = ft.Ref[ft.Text]()
        self._cb_header          = ft.Checkbox(
            label="Arquivo tem cabeçalho",
            value=False,
            on_change=self._on_header_changed,
            active_color=_PRIMARY,
        )
        self._field_name         = ft.Ref[ft.TextField]()
        self._field_row          = ft.Ref[ft.Row]()
        self._data_table         = ft.Ref[ft.DataTable]()
        self._resultados         = ft.Ref[ft.Column]()
        self._tabela_placeholder = ft.Ref[ft.Container]()
        self._tabela_container   = ft.Ref[ft.Container]()

        page.add(
            # ── Cabeçalho ──────────────────────────────────────────────
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.QUERY_STATS, color=_PRIMARY, size=32),
                        ft.Column(
                            [
                                ft.Text("Calculadora de Média", size=22, weight=ft.FontWeight.BOLD, color=_PRIMARY),
                                ft.Text("CSV / XLSX  •  Tabela de frequência e estatísticas", size=12, color=ft.Colors.BLUE_GREY_400),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                margin=ft.margin.only(bottom=20),
            ),

            # ── Seção: Arquivo ─────────────────────────────────────────
            _card(
                ft.Column(
                    [
                        _section_title("Arquivo"),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Selecionar arquivo",
                                    icon=ft.Icons.FOLDER_OPEN,
                                    on_click=self._on_select_file_click,
                                    style=ft.ButtonStyle(
                                        bgcolor=_PRIMARY,
                                        color=ft.Colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                    ),
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE_OUTLINED, size=16, color=ft.Colors.BLUE_GREY_400),
                                            ft.Text(
                                                "Nenhum arquivo selecionado",
                                                ref=self._filepath_ref,
                                                color=ft.Colors.BLUE_GREY_400,
                                                size=13,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                                max_lines=1,
                                            ),
                                        ],
                                        spacing=6,
                                    ),
                                    expand=True,
                                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                    border_radius=8,
                                    border=ft.border.all(1, _OUTLINE),
                                    bgcolor=ft.Colors.BLUE_GREY_50,
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
                        ft.Row(
                            [
                                self._cb_header,
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Text("Nome da coluna:", size=13, color=ft.Colors.BLUE_GREY_700),
                                            ft.TextField(
                                                ref=self._field_name,
                                                width=200,
                                                hint_text="ex.: Nota",
                                                on_change=self._on_field_name_changed,
                                                border_radius=8,
                                                content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                                text_size=13,
                                            ),
                                        ],
                                        ref=self._field_row,
                                        visible=False,
                                        spacing=10,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                ),
                            ],
                            spacing=16,
                            wrap=True,
                        ),
                        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
                        ft.ElevatedButton(
                            "Calcular",
                            icon=ft.Icons.CALCULATE_OUTLINED,
                            on_click=self._on_carregar_click,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREEN_700,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=24, vertical=14),
                            ),
                        ),
                    ],
                    spacing=0,
                ),
            ),

            ft.Container(height=20),

            # ── Seção: Tabela de frequência ────────────────────────────
            _card(
                ft.Column(
                    [
                        _section_title("Tabela de frequência"),
                        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
                        # placeholder visível enquanto a tabela está vazia
                        ft.Container(
                            ref=self._tabela_placeholder,
                            content=ft.Column(
                                [
                                    ft.Icon(ft.Icons.TABLE_CHART_OUTLINED, size=40, color=ft.Colors.BLUE_GREY_200),
                                    ft.Text(
                                        "Selecione um arquivo e clique em Calcular",
                                        size=13,
                                        color=ft.Colors.BLUE_GREY_300,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            alignment=ft.alignment.center,
                            height=120,
                            visible=True,
                        ),
                        # tabela real (oculta até ter dados)
                        ft.Container(
                            ref=self._tabela_container,
                            content=ft.Column(
                                controls=[
                                    ft.DataTable(
                                        ref=self._data_table,
                                        columns=[ft.DataColumn(ft.Text(""))],
                                        rows=[],
                                        border=ft.border.all(0),
                                        heading_row_color=_HEADER_BG,
                                        heading_row_height=44,
                                        data_row_min_height=40,
                                        data_row_max_height=40,
                                        column_spacing=0,
                                        divider_thickness=1,
                                        horizontal_margin=16,
                                    )
                                ],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True,
                                spacing=0,
                            ),
                            height=300,
                            border_radius=8,
                            border=ft.border.all(1, _OUTLINE),
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            visible=False,
                            expand=True,
                        ),
                    ],
                    spacing=0,
                ),
            ),

            ft.Container(height=20),

            # ── Seção: Resultados ──────────────────────────────────────
            _card(
                ft.Column(
                    [
                        _section_title("Resultados"),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        ft.Column(ref=self._resultados, spacing=8),
                    ],
                    spacing=0,
                ),
            ),

            ft.Container(height=24),
        )

    # ── Handlers ──────────────────────────────────────────────────────

    def _on_select_file_click(self, e):
        def run_dialog():
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                helper = os.path.join(script_dir, "file_dialog_helper.py")
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                r = subprocess.run(
                    [sys.executable, helper],
                    capture_output=True,
                    text=True,
                    cwd=script_dir,
                    creationflags=creationflags,
                    timeout=300,
                )
                path = (r.stdout or "").strip()
            except Exception:
                path = ""
            self._apply_selected_path(path)
            if path:
                self.controller.set_database(path)

        self.page.run_thread(run_dialog)

    def _apply_selected_path(self, path: str):
        if self._filepath_ref.current:
            self._filepath_ref.current.value = path or "Nenhum arquivo selecionado"
            self._filepath_ref.current.color = ft.Colors.BLUE_GREY_800 if path else ft.Colors.BLUE_GREY_400
            self._filepath_ref.current.update()
            self.page.update()

    def _on_header_changed(self, e):
        if self._field_row.current:
            self._field_row.current.visible = self._cb_header.value
            self.page.update()
        self.controller.set_headers(self._cb_header.value)

    def _on_carregar_click(self, e):
        if self._on_carregar_callback:
            self.controller.calculate_statistics()
        else:
            self.show_erro("Conecte o backend: view.set_on_carregar(sua_funcao)")

    def _on_field_name_changed(self, e):
        if self._field_name.current:
            self.controller.set_column_name(self._field_name.current.value)

    # ── API pública ────────────────────────────────────────────────────

    def set_controller(self, controller):
        self.controller = controller

    def set_on_carregar(self, callback):
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
        has_data = df is not None and not df.empty

        # alterna placeholder ↔ tabela
        if self._tabela_placeholder.current:
            self._tabela_placeholder.current.visible = not has_data
        if self._tabela_container.current:
            self._tabela_container.current.visible = has_data

        if not has_data:
            self.page.update()
            return

        cols = list(df.columns)
        # largura de cada coluna: divide o espaço da janela igualmente
        col_w = max(100, int((self.page.window.width or 700) - 80) // len(cols))

        self._data_table.current.columns = [
            ft.DataColumn(
                ft.Container(
                    ft.Text(str(c), weight=ft.FontWeight.W_600, color=_PRIMARY, size=13),
                    width=col_w,
                )
            )
            for c in cols
        ]
        self._data_table.current.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Container(
                            ft.Text(str(row[c])[:24], size=13),
                            width=col_w,
                        )
                    )
                    for c in cols
                ],
                color=ft.Colors.with_opacity(0.04, ft.Colors.BLUE) if i % 2 == 0 else None,
            )
            for i, (_, row) in enumerate(df.iterrows())
        ]
        self.page.update()

    def show_resultados(self, stats: dict):
        if self._resultados.current is None:
            return

        if stats.get("erro"):
            self._resultados.current.controls = [
                ft.Text(stats["erro"], color=ft.Colors.RED_700, size=13)
            ]
            self.page.update()
            return

        def _stat_card(label: str, value: str) -> ft.Container:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Text(label, size=11, color=ft.Colors.BLUE_GREY_500, weight=ft.FontWeight.W_500),
                        ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                border_radius=10,
                border=ft.border.all(1, _OUTLINE),
                bgcolor=_HEADER_BG,
                expand=True,
            )

        n   = stats.get("n", 0)
        med = stats.get("media", 0)
        mdn = stats.get("mediana", 0)
        var = stats.get("variancia", 0)
        dp  = stats.get("desvio_padrao", 0)
        cv  = stats.get("coeficiente_variacao", 0)

        self._resultados.current.controls = [
            ft.Row(
                [
                    _stat_card("n  (total)", str(n)),
                    _stat_card("Média", f"{med:.4f}"),
                    _stat_card("Mediana", f"{mdn:.4f}"),
                ],
                spacing=10,
            ),
            ft.Row(
                [
                    _stat_card("Variância", f"{var:.4f}"),
                    _stat_card("Desvio padrão", f"{dp:.4f}"),
                    _stat_card("Coef. de variação", f"{cv:.2f} %"),
                ],
                spacing=10,
            ),
        ]
        self.page.update()
