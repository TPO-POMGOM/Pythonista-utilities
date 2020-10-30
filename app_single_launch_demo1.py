""" app_single_launch demo script #1. """
from app_single_launch import AppSingleLaunch
import ui


class MainView(ui.View):
    def __init__(self, app: AppSingleLaunch):
        self.app = app
        self.name = "Demo app 1"
        self.flex = 'WH'
        self.background_color = 'white'
        self.add_subview(ui.TextField(
            width=200,
            height=30,
            placeholder="Type some text"))

    def will_close(self) -> None:
        self.app.will_close()


if __name__ == '__main__':
    app = AppSingleLaunch("Demo app 1")
    if not app.is_active():
        view = MainView(app)
        app.will_present(view)
        view.present()
