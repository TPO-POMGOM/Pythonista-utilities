""" Ensure a Pythonista script can only be launched once from the iOS home screen.

This module provides a solution to the problem stated by shinyformica, which I
have also encountered (https://forum.omz-software.com/topic/5440/prevent-
duplicate-launch-from-shortcut):
    "Is there a good, canonical way to prevent a script from launching again if
    there is already an instance running? Specifically, I want to prevent the
    scenario where a user launches the script from the home screen via an app
    shortcut, then goes back to the home screen and launches it again.""

The solution is based on a simple protocol, which applications need to adhere
to. When this is the case, applications will not "pile up on top of one another"
when launched from the iOS home screen:
- When an app is already active in Pythonista and it is launched again with its
  home screen shortcut, the new instance of the app detects the situation and
  exits, leaving the already active instance of the app on screen.
- When an app is launched from its home screen shortcut and a previous app is
  already active in Pythonista, the previous app will be notified that it
  should terminate, its main UI view will be closed, and the new app will be
  launched.

Protocol:
1) An application should create an instance of class AppSingleLaunch, and use
   it to test if the application is already active, using the is_active()
   method. If yes, the application should simply exit. If not, the application
   should declare its main UI view, using the will_present() method, and
   present the view. Here is an example:

        import app_single_launch

        app = AppSingleLaunch("MyApp")
        if not app.is_active():
            view = MyAppView(app)
            app.will_present(view)
            view.present()

2) An application should make a call to the AppSingleLaunch.will_close()
   method, from the will_close() method of its main UI view:

        class MyAppView(ui.View):

            def __init__(self, app):
                self.app = app

            def will_close(self):
              self.app.will_close()

Implementation: in order to achieve the desired result, we need to remember the
last application launched according to the protocol, to determine if it is
still active, and, if it is, to close it. This is achieved by storing into a
lock file some information about the last application launched:
- Its name, as passed to single_launch.launching()
- The id of the ui.View instance for its main view, as passed to single_launch.
  launching(). This is later used to determine if the view is still on screen
  (when an object is still associated with the id), and to close the app's view.
  After several tests, it turns out we must use an ui.View object for this
  purpose, as they seem to persist better than other objects after the cleanup
  pykit-preflight.py does when an app is launched from the home screen.
The location of the lock file is defined by global variable LOCK_PATH. The
default location is in the 'site-packages' directory.

Known issue:
- When an app is on screen, then launched again from its home screen shortcut,
  some issues may happen with inline import statements (rare, would need to be
  qualified further).

26-Feb-2019 TPO - Created this module
28-Feb-2019 TPO - Initial release
 3-Mar-2019 TPO - Wrapped the code into the AppSingleLaunch class """


import gc
import json
from pathlib import Path
import time
from typing import Any

import ui


__all__ = [
    'AppSingleLaunch',
]


DEBUG = False
LOCK_PATH = '~/Documents/site-packages/single_launch.lock'


def _object_for_id(id_: int) -> Any:
    """ Return an object, given its id. """

    # Do a complete garbage collect, to avoid false positives in case the
    # object was still in use recently. In the context of AppSingleLaunch,
    # this would happen if an app was closed, then launched again immediately.
    gc.collect()
    for obj in gc.get_objects():
        if id(obj) == id_:
            return obj
    return None


class AppSingleLaunch:
    """ Wrapper class for all module functionnality. """

    def __init__(self, app: str):
        """ Initialize an AppSingleLaunch instance.

        Arguments:
        - app: application name, which should be unique (but this is not
        enforced). """
        self.app = app

    def is_active(self) -> bool:
        """ Test if the application is already active.

        Returns:
        - True if the application is already running, in which case the caller
          should do nothing and exit.
        - False if the application is not already running, in which case the
          caller should launch the application in a normal way, and declare its
          main view by calling the will_present() method."""
        if DEBUG:
            print(f"is_active(), app = {self.app}")
        lock_path = Path(LOCK_PATH).expanduser()
        if lock_path.exists():
            with open(lock_path) as lock_file:
                (lock_app, lock_view_id) = tuple(json.load(lock_file))
            lock_view = _object_for_id(lock_view_id)
            if DEBUG:
                print("- Lock file =", lock_app, lock_view_id,
                      "valid" if lock_view else "invalid")
            if lock_app == self.app and lock_view:
                if DEBUG:
                    print(f"- App {self.app} already active")
                return True
        if DEBUG:
            print(f"- App {self.app} not active")
        return False

    def will_present(self, view: ui.View) -> None:
        """ Declare that the application is about to present its main view.

        Arguments:
        - view: ui.View instance for the app's main view. """
        if DEBUG:
            print(f"will_present({id(view)}), app = {self.app}")
        lock_path = Path(LOCK_PATH).expanduser()
        if lock_path.exists():
            with open(lock_path) as lock_file:
                (lock_app, lock_view_id) = tuple(json.load(lock_file))
            lock_view = _object_for_id(lock_view_id)
            if DEBUG:
                print("- Lock file =", lock_app, lock_view_id,
                      "valid" if lock_view else "invalid")
            if lock_app == self.app and lock_view:
                raise ValueError(f"App {self.app} is already active, cannot "
                                 f"call will_present() against it.")
            else:
                if lock_view and isinstance(lock_view, ui.View):
                    if DEBUG:
                        print(f"- Closing app {lock_app}")
                    lock_view.close()
                    time.sleep(1)  # Required for view to close properly
                # else: lock is a leftover from a previous Pythonista session
                #       and can be safely ignored.
        with open(lock_path, 'w') as lock_file:
            json.dump([self.app, id(view)], lock_file)
        if DEBUG:
            print(f"- Launching app {self.app}\n- Lock file =", self.app, id(view))

    def will_close(self) -> None:
        """ Declare that the application is about to close its main view. """
        lock_path = Path(LOCK_PATH).expanduser()
        if lock_path.exists():
            with open(lock_path) as lock_file:
                (lock_app, lock_view_id) = tuple(json.load(lock_file))
            if lock_app != self.app:
                raise ValueError(f"App {self.app} if not active, "
                                 f"{lock_app} is active")
            lock_path.unlink()
