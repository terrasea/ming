"""Ming Base module.  Good stuff here.
"""
import decimal
from datetime import datetime

import bson

class Object(dict):
    'Dict providing object-like attr access'
    __slots__ = ()

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.__class__.__dict__:
            super(Object, self).__setattr__(name, value)
        else:
            self.__setitem__(name, value)

    @classmethod
    def from_bson(cls, bson):
        if isinstance(bson, dict):
            return cls((k, cls.from_bson(v))
                       for k,v in bson.items())
        elif isinstance(bson, list):
            return [ cls.from_bson(v) for v in bson ]
        else:
            return bson

    def make_safe(self):
        safe_self = _safe_bson(self)
        self.update(safe_self)

class Cursor(object):
    '''Python class proxying a MongoDB cursor, constructing and validating
    objects that it tracks
    '''

    def __init__(self, cls, cursor, allow_extra=True, strip_extra=True):
        self.cls = cls
        self.cursor = cursor
        self._allow_extra = allow_extra
        self._strip_extra = strip_extra

    def __iter__(self):
        return self

    def __len__(self):
        return self.count()

    def __next__(self):
        doc = next(self.cursor)
        if doc is None: return None
        return self.cls.make(
            doc,
            allow_extra=self._allow_extra,
            strip_extra=self._strip_extra)

    def count(self):
        return self.cursor.count()

    def limit(self, limit):
        self.cursor = self.cursor.limit(limit)
        return self

    def skip(self, skip):
        self.cursor = self.cursor.skip(skip)
        return self

    def hint(self, index_or_name):
        self.cursor = self.cursor.hint(index_or_name)
        return self

    def sort(self, *args, **kwargs):
        self.cursor = self.cursor.sort(*args, **kwargs)
        return self

    def one(self):
        try:
            result = next(self)
        except StopIteration:
            raise ValueError('Less than one result from .one()')
        try:
            next(self)
        except StopIteration:
            return result
        raise ValueError('More than one result from .one()')

    def first(self):
        try:
            return next(self)
        except StopIteration:
            return None

    def all(self):
        return list(self)

NoneType = type(None)
def _safe_bson(obj):
    '''Verify that the obj is safe for bsonification (in particular, no tuples or
    Decimal objects
    '''
    if isinstance(obj, list):
        return [ _safe_bson(o) for o in obj ]
    elif isinstance(obj, dict):
        return Object((k, _safe_bson(v)) for k,v in obj.items())
    elif isinstance(obj, (
            str, int, float, datetime, NoneType,
            bson.ObjectId)):
        return obj
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        assert False, '%s is not safe for bsonification: %r' % (
            type(obj), obj)
