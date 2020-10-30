""" Pythonista UI element to display a modal mail compose view.

Display a modal mail compose view, with pre-populated contents, on top of
the currently displayed view.

A demo app is shown when the module is run as a script.


**Credits** -- This is based on `tdamdouni's code
<https://github.com/tdamdouni/Pythonista/blob/master/objc/mail.py>`_ and
`jsbain's code <https://gist.github.com/jsbain/f82be8d8840f86b387a4>`_, with
an improvement picked up in an `omz post
<https://forum.omz-software.com/topic/2060/presenting-viewcontroller/2>`_.


**Revision history**

- 17-Avr-2020 TPO - Initial release. """


import os
from typing import Callable, List, Optional

import objc_util
from objc_util import create_objc_class, NSData, NSObject, ObjCClass, \
    ObjCInstance, on_main_thread, UIApplication


objc_util.retain = getattr(objc_util, 'retain', [])
objc_util.load_framework('MessageUI')


@on_main_thread
def mail_compose(
        subject: str = "",
        recipients: Optional[List[str]] = None,
        body: str = "",
        filename: str = '',
        mime_type: str = '',
        dismiss_callback: Optional[Callable[[], None]] = None) -> None:
    """ Modal mail compose view.

    Display a modal mail compose view, with pre-populated contents, on top of
    the currently displayed view.

    The function returns immediately. Use argument `dismiss_callback` if your
    application needs to be notified when the compose view is dismissed.


    Arguments
    ---------

    subject: `str`, defaults to ``""``
        Mail subject.

    recipients: `Optional[List[str]]`, defaults to ``None``
        List of mail addresses for the recipients of the email.

    body: `str`, defaults to ``""``
        Mail body.

    filename: `str`, defaults to ``''``
        If non-empty, name of a file to be attached to the email.

    mime_type: `str`, defaults to ``''``
        If `filename` is not empty, indicates the mime type of its contents,
        for instance ``'image/gif'``

    dismiss_callback: `Optional[Callable[[], None]]`, defaults to ``None``
        When set to a callable, it is called (with no arguments) when the mail
        composition view is dismissed. """

    def mailComposeController_didFinishWithResult_error_(
            self, sel, controller, result, error):
        nonlocal dismiss_callback
        mail_vc = ObjCInstance(controller)
        mail_vc.setMailComposeDelegate_(None)
        mail_vc.dismissViewControllerAnimated_completion_(True, None)
        ObjCInstance(self).release()
        if dismiss_callback:
            dismiss_callback()

    try:
        MailDelegate = ObjCClass('MailDelegate')
    except ValueError:
        MailDelegate = create_objc_class(
            'MailDelegate',
            superclass=NSObject,
            methods=[mailComposeController_didFinishWithResult_error_],
            protocols=['MFMailComposeViewControllerDelegate'])
        objc_util.retain.append(mailComposeController_didFinishWithResult_error_)
    MFMailComposeViewController = ObjCClass('MFMailComposeViewController')
    mail_vc = MFMailComposeViewController.alloc().init().autorelease()
    delegate = MailDelegate.alloc().init().autorelease()
    objc_util.retain.append(delegate)
    mail_vc.setMailComposeDelegate_(delegate)
    # Find a view controller which is not already presenting, see
    # https://forum.omz-software.com/topic/2060/presenting-viewcontroller/2
    root_vc = UIApplication.sharedApplication().keyWindow().rootViewController()
    while root_vc.presentedViewController():
        root_vc = root_vc.presentedViewController()
    mail_vc.setSubject_(subject)
    if recipients is not None:
        mail_vc.setToRecipients_(recipients)
    mail_vc.setMessageBody_isHTML_(body, body.startswith('<html>'))
    if filename and os.path.exists(filename):
        mail_vc.addAttachmentData_mimeType_fileName_(
            NSData.dataWithContentsOfFile_(os.path.abspath(filename)),
            mime_type,
            filename)
    root_vc.presentViewController_animated_completion_(mail_vc, True, None)


if __name__ == '__main__':
    mail_compose(subject="Test", body="Your message here")
