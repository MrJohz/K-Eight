import asyncore

class AsyncTimer(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
    
    def connect(self, *args):
        pass

class KeightTimer(object):
    """Asynchronously keeps track of time.

Essentially a fix because I couldn't be bothered to fiddle around with
threading.  It may not be the best way of doing this, but we'll see if
it works."""
    def __init__(self):
        self.a