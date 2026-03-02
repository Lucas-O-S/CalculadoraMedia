"""
Ponto de entrada: cria View, Controller e inicia a aplicação.
"""
import sys


def main():
    try:
        from view import View
        from controller import Controller
        view = View()
        controller = Controller(view)
        view.set_controller(controller)
        view.run()
    except Exception as e:
        print("Erro ao abrir a aplicação:", file=sys.stderr)
        print(e, file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
