from cPickle import dumps, PicklingError # for memoize
import cPickle as pickle
import os
import tempfile

# Slightly evil, but there you go:
# module-level cache.
CACHE_FILENAME = './memoize-cache'

def save_cache(obj):
    # must make in cache_filename's dir to ensure rename() will work
    cache_filename_dir = os.path.dirname(os.path.abspath(CACHE_FILENAME))
    # Yes, some crazy mounts between the directory discovery above and the
    # tempfile creation below could theoretically cause rename() to fail.

    fileno, filename = tempfile.mkstemp(dir=cache_filename_dir, prefix='python_memoize')
    fd = os.fdopen(fileno, 'wb')
    pickle.dump(obj, fd, protocol=-1) # newest protocol
    fd.close()
    os.rename(filename, CACHE_FILENAME)

def read_from_cache():
    return pickle.load(open(CACHE_FILENAME))

try:
    _cache = read_from_cache()
except:
    save_cache({})
    _cache = read_from_cache()

class memoize(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated. Slow for mutable types."""
    # Ideas from MemoizeMutable class of Recipe 52201 by Paul Moore and
    # from memoized decorator of http://wiki.python.org/moin/PythonDecoratorLibrary
    # For a version with timeout see Recipe 325905
    # For a self cleaning version see Recipe 440678
    # Weak references (a dict with weak values) can be used, like this:
    #   self._cache = weakref.WeakValueDictionary()
    #   but the keys of such dict can't be int
    def __init__(self, func):
        self.func = func
        self.count = 0
    def __call__(self, *args, **kwds):
        self.count += 1
        key = args
        if kwds:
            items = kwds.items()
            items.sort()
            key = key + tuple(items)
        try:
            if key in _cache:
                return _cache[key]
            _cache[key] = result = self.func(*args, **kwds)
            #if self.count % 3000 == 0:
                #_cache.update(read_from_cache())
                #save_cache(_cache)
            return result
        except TypeError:
            try:
                dump = dumps(key, protocol=-1) # newest protocol
            except PicklingError:
                return self.func(*args, **kwds)
            else:
                if dump in _cache:
                    return _cache[dump]
                _cache[dump] = result = self.func(*args, **kwds)
                save_cache(_cache)
                return result


if __name__ == "__main__": # Some examples
    @memoize
    def fibonacci(n):
       "Return the n-th element of the Fibonacci series."
       if n < 3:
          return 1
       return fibonacci(n-1) + fibonacci(n-2)

    print [fibonacci(i) for i in xrange(1, 101)]

    @memoize
    def pow(x, p=2):
        if p==1:
            return x
        else:
            return x * pow(x, p=p-1)

    print [pow(3, p=i) for i in xrange(1, 6)]

    @memoize
    def printlist(l):
        print l
    printlist([1,2,3,4])
