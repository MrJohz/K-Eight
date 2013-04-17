import shelve

class KeightShelf(shelve.Shelf, object):
    """K-Eight implementation of the shelve.DbfilenameShelf class."""
    def __init__(self, filename, flag='c', protocol=-1, writeback=False):
        """Initialises into correct directory."""
        filename = '.\persistence\{}'.format(filename)
        import anydbm
        shelve.Shelf.__init__(self, anydbm.open(filename, flag), protocol, writeback)

def open(filename, flag='c', protocol=-1, writeback=False):
    """Opens a persistent dictionary in the correct directory.

The filename parameter should be just a filename, with no path, and should
be the filename for the underlying database.  The flag parameter is passed
to anydbm.open(), and the protocol and writeback parameters are passed to
shelve.Shelf.__init__()."""
    return KeightShelf(filename, flag, protocol, writeback)