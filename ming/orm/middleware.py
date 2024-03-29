from webob import exc

from ming.orm import ThreadLocalORMSession, ContextualORMSession

class MingMiddleware(object):

    def __init__(self, app,
                 context_func=None,
                 flush_on_errors=(exc.HTTPRedirection,)):
        self.app = app
        self.flush_on_errors = flush_on_errors
        self._context_func = context_func or (lambda:None)

    def __call__(self, environ, start_response):
        try:
            result = self.app(environ, start_response)
            if isinstance(result, list):
                self._cleanup_request()
                return result
            else:
                return self._cleanup_iterator(result)
        except self.flush_on_errors as exc:
            self._cleanup_request()
            raise
        except:
            ThreadLocalORMSession.close_all()
            ContextualORMSession.close_all(self._context_func())
            raise

    def _cleanup_request(self):
        context = self._context_func()
        ThreadLocalORMSession.flush_all()
        ContextualORMSession.flush_all(context)
        ThreadLocalORMSession.close_all()
        ContextualORMSession.close_all(context)

    def _cleanup_iterator(self, result):
        for x in result:
            yield x
        self._cleanup_request()
    

def make_ming_autoflush_middleware(global_conf, **app_conf):
    def _filter(app):
        return MingMiddleware(app, **app_conf)
    return _filter
