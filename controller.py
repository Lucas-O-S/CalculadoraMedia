"""
Controller: conecta a tela ao backend. Implemente on_carregar.
"""


class Controller:
    def __init__(self, view):
        self.view = view

    def on_carregar(self):
        self.view.show_erro("Implemente controller.on_carregar")
