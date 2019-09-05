# app_single_launch.py #


## Problem statement ##

@shinyformica (https://forum.omz-software.com/topic/5440/prevent-duplicate-launch-from-shortcut) :

> Is there a good, canonical way to prevent a script from launching again if
> there is already an instance running? Specifically, I want to prevent the
> scenario where a user launches the script from the home screen via an app 
> shortcut, then goes back to the home screen and launches it again.
>
>Right now that causes duplicate instances of my script to run. My current 
>method is to have the first instance put a small token in its directory which 
>any other instance can look for and immediately return without running if it 
>isn't the owner of that token. The token is removed by the first instance at 
>exit. This requires quite a bit of careful negotiation and has many difficult 
>edge cases...so I would prefer some simpler way to make sure only a single 
>instance of the script can be running at any time.


## Solution ##

I have come up with a solution based on a simple protocol. When applications follow the protocol, they will not "pile up on top of one another" when launched from the iOS home screen:

- When an app is already active in Pythonista and it is launched again with its home screen shortcut, the new instance of the app detects the situation and exits, leaving the already active instance of the app on screen.

- When an app is launched from its home screen shortcut and a previous (different) app is already active in Pythonista, the previous app will be notified that it should terminate, its main UI view will be closed, and the new app will be launched.

## Protocol ##

An application should create an instance of class `AppSingleLaunch`, and use it to test if the application is already active, using the `is_active` method. If yes, the application should simply exit. If not, the application should declare its main UI view, using the `will_present` method, and present the view. Here is an example:

     import app_single_launch

     app = AppSingleLaunch("MyApp")
     if not app.is_active():
         view = MyAppView(app)
         app.will_present(view)
         view.present()

The application should make a call to the `AppSingleLaunch.will_close` method, from the `will_close` method of its main UI view:

     class MyAppView(ui.View):

         def __init__(self, app):
             self.app = app

         def will_close(self):
           self.app.will_close()


## Demo ##

Save the code for `app_single_launch.py` and the two demo apps in the same directory.

Define home screen shortcuts for the two demo apps.

Launch demo app 1 using its home screen shortcut, type some text in the text field, then relaunch the app using its home screen shortcut : the text typed previously is still showing, meaning we are using the first launched instance, not the second one. Closing the app brings us back to the Pythonista IDE, not to previously piled up instances of the app.

Launch demo app 1 using its home screen shortcut, then Launch demo app 2 using its home screen shortcut, then close it : the Pythonista IDE shows, not a piled up instance of demo app 1.

Et voilà !