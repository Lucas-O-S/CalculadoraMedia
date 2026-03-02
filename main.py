"""
Ponto de entrada: inicia a aplicação Flet.
"""
import flet as ft

from view_flet import ViewFlet
from controller import Controller


def main(page: ft.Page):
    view = ViewFlet(page)
    controller = Controller(view)
    view.set_on_carregar(controller.on_carregar)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
