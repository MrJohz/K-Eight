import shelve
import os.path
from sqlite3 import dbapi2 as sqlite
import sqlite3
import UserDict
try:
    import cPickle as pickle
except ImportError:
    import pickle

class PersistentDict(object, UserDict.DictMixin):
    """A persistent dictionary, saving to a sqlite3 database.

USAGE:
    >>> n = PersistentDict('filename.db')
    >>> n['score'] = 42
    >>> n['winners'] = ['Ed', 'Edd', 'Eddy'] # objects are pickled before storage.
    >>> n.close() # Should be automatically called if an instance drops out
                  # of scope, but it's good to stay safe."""
    
    def __init__(self, filename, init_vals=None):
        """Initialises into correct directory."""
        k_dir = os.path.split(os.path.dirname(__file__))[0]
        p_dir = os.path.join(k_dir, 'persistence')
        self._db_filename = os.path.abspath(os.path.join(p_dir, filename))
        if not os.path.isfile(self._db_filename):
            self._con = sqlite.connect(self._db_filename)
            self._con.execute("create table data (key PRIMARY KEY, value)")
        else:
            self._con = sqlite.connect(self._db_filename)
            
        # Check that the file really is a database by trying to grab some data:
        self._con.cursor().execute('select value from data').fetchone()
        
    def __getitem__(self, key):
        row = self._con.execute("select value from data where key=?", (key,)).fetchone()
        if not row:
            raise KeyError
        return pickle.loads(row[0].encode('utf-8'))
    
    def __setitem__(self, key, item):
        item = pickle.dumps(item).decode('utf-8')
        if self._con.execute("select key from data where key=?", (key,)).fetchone():
            self._con.execute("update data set value=? where key=?", (item, key))
        else:
            self._con.execute("insert into data (key, value) values (?,?)", (key, item))
        self._con.commit()
    
    def __delitem__(self, key):
        rows = self._con.execute("SELECT key FROM data WHERE key=?", (key,))
        if rows.fetchone():
            self._con.execute("DELETE FROM data WHERE key=?", (key,))
            self._con.commit()
        else:
            raise KeyError
    
    def keys(self):
        return [row[0] for row in self._con.execute("SELECT key FROM data").fetchall()]
    
    def iterkeys(self):
        for row in self._con.execute("SELECT key FROM data").fetchall():
            yield row[0]
    
    def __del__(self):
        self.close()
    
    def close(self):
        try:
            self._con.close()
        except AttributeError:
            pass
 
if __name__ == "__main__":
    pass