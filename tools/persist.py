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
    
    def __init__(self, filename, writeback=False):
        """Initialises into correct directory."""
        self.cache = {}
        self.writeback = writeback
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
    
    def __contains__(self, item):
        return item in self.iterkeys()
    
    def __iter__(self):
        rows = self._con.execute('SELECT key FROM data')
        while rows:
            yield rows.fetchone()[0]
    
    def iteritems(self):
        self.sync()
        rows = self._con.execute("SELECT key, value FROM data")
        while rows:
            key, value = rows.fetchone()
            value = pickle.loads(value.encode('utf-8'))
            yield key, value
        
    def __getitem__(self, key):
        try:
            value = self.cache[key]
        except KeyError:
            rows = self._con.execute("select value from data where key=?", (key,)).fetchone()
            if not rows:
                raise KeyError
            value = pickle.loads(rows[0].encode('utf-8'))
            if self.writeback:
                self.cache[key] = value
        return value
    
    def __setitem__(self, key, item):
        if self.writeback:
            self.cache[key] = item
        
        item = pickle.dumps(item).decode('utf-8')
        if self._con.execute("select key from data where key=?", (key,)).fetchone():
            self._con.execute("update data set value=? where key=?", (item, key))
        else:
            self._con.execute("insert into data (key, value) values (?,?)", (key, item))
        self._con.commit()
    
    def __delitem__(self, key):
        try:
            del self.cache[key]
        except KeyError:
            pass
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
        self.sync()
        try:
            self._con.close()
        except AttributeError:
            pass
    
    def sync(self):
        if self.writeback and self.cache:
            self.writeback = False
            for key, entry in self.cache.iteritems():
                self[key] = entry
            self.writeback = True
            self.cache = {}
 
if __name__ == "__main__":
    pass