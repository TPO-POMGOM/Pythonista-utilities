""" Modal view which displays a spinning busy indicator.

Based on code by omz (https://gist.github.com/omz/e3433ebba20c92b63111)

Revision history:
13-Fev-2019 TPO - Initial release """

import ui


class BusyView(ui.View):
    """ Modal view which displays a spinning busy indicator. """
    def __init__(self):
        """ Initialize a BusyView instance. """
        self.flex = 'WH'
        self.background_color = (0, 0, 0, 0.35)
        backdrop = ui.View(frame=(self.center.x - 50, self.center.y - 50, 100, 100))
        backdrop.background_color = (0, 0, 0, 0.7)
        backdrop.corner_radius = 8.0
        backdrop.flex = 'TLRB'
        self.spinner = spinner = ui.ActivityIndicator()
        spinner.style = ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE
        spinner.center = (50, 50)
        backdrop.add_subview(spinner)
        self.add_subview(backdrop)
        self.hidden = True

    def show(self) -> None:
        """ Show the busy indicator, on top of its parent view. """
        self.spinner.start()
        self.hidden = False
        self.bring_to_front()

    def hide(self) -> None:
        """ Hide the busy indicator. """
        self.spinner.stop()
        self.hidden = True
