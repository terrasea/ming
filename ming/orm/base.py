from copy import deepcopy

def state(obj):
    '''The state of a mapped object'''
    return obj.__ming__.state

def session(v):
    '''The ORMSession object managing either a class or an instance'''
    if isinstance(v, type):
        return v.query.mapper.session
    else:
        return session(type(v))

def call_hook(obj, hook_name, *args, **kw):
    for e in obj.extensions:
        getattr(e, hook_name)(*args, **kw)

class with_hooks(object):
    'Decorator to use for Session/Mapper extensions'

    def __init__(self, hook_name):
        self.hook_name = hook_name

    def __call__(self, func):
        before_meth = 'before_' + self.hook_name
        after_meth = 'after_' + self.hook_name
        def inner(obj, *args, **kwargs):
            call_hook(obj, before_meth, *args, **kwargs)
            result = func(obj, *args, **kwargs)
            call_hook(obj, after_meth, *args, **kwargs)
            return result
        inner.__name__ = func.__name__
        inner.__doc__ = 'Hook wraper around\n' + repr(func.__doc__)
        return inner

class ObjectState(object):
    new, clean, dirty, deleted = 'new clean dirty deleted'.split()

    def __init__(self, options):
        self.status = self.new
        self.original_document = None # unvalidated, as loaded from mongodb
        self.document = None
        self.i_document = {}
        self.extra_state = {}
        self.tracker = _DocumentTracker(self)
        self.options = options

    def soil(self):
        if self.status == self.clean:
            self.status = self.dirty

    def validate(self, schema):
        status = self.status
        self.document = schema.validate(self.document)
        self.status = status

    def clone(self):
        return deepcopy(self.document)

    def __repr__(self):
        return '<ObjectState status=%s>' % self.status

    def instrumented(self, name):
        try:
            return self.i_document[name]
        except KeyError:
            from .icollection import instrument
            result = instrument(self.document[name], self.tracker)
            self.i_document[name] = result
        return result

    def set(self, name, value):
        self.document[name] = value
        self.i_document.pop(name, None)

    def delete(self, name):
        del self.document[name]
        self.i_document.pop(name, None)

class _DocumentTracker(object):
    __slots__ = ('state',)

    def __init__(self, state):
        self.state = state

    def soil(self, value):
        self.state.soil()
    added_items = soil
    added_item = soil
    removed_item = soil
    cleared = soil

