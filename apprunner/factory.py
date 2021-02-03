
import inspect
import importlib
from .exceptions import RunnerException

import logging
logger = logging.getLogger('apprunner')



class ClassAppFactory:
    """ 
    This object should be pickable
    """
    __slots__ = ("_factory_module", "_factory_class")

    def __init__(self, app_class):
        self._factory_module = app_class.__module__
        self._factory_class = app_class.__qualname__

    def __call__(self):
        try:
            module = importlib.import_module(self._factory_module)
        except ImportError as exc:
            msg = f"error importing '{self._module}': {exc}"
            raise RunnerException(msg) from exc

        try:
            factory_class = getattr(module, self._factory_class)
        except AttributeError as exc:
            msg = (f"Module '{module.__name__}' does not define a "
                f"'{self._factory_func}' attribute/class")
            raise RunnerException(msg) from exc

        return factory_class()


class ObjectAppFactory(ClassAppFactory):
    
    def __init__(self, app_obj):
        super().__init__(app_obj.__class__)

class FunctionAppFactory:
    """ 
    This object should be pickable
    """
    __slots__ = ("_factory_module", "_factory_func")

    def __init__(self, app_factory):
        self._factory_module = app_factory.__module__
        self._factory_func = app_factory.__qualname__

    def __call__(self):
        try:
            module = importlib.import_module(self._factory_module)
        except ImportError as exc:
            msg = f"error importing '{self._module}': {exc}"
            raise RunnerException(msg) from exc

        try:
            app_factory = getattr(module, self._factory_func)
        except AttributeError as exc:
            msg = (f"Module '{module.__name__}' does not define a "
                f"'{self._factory_func}' attribute/class")
            raise RunnerException(msg) from exc

        return app_factory()


def get_app_factory(app_or_factory):

    if inspect.iscoroutinefunction(app_or_factory):
        pass
    elif inspect.isfunction(app_or_factory):
        return FunctionAppFactory(app_or_factory)
    elif inspect.isclass(app_or_factory):
        return ClassAppFactory(app_or_factory)
    else:
        return ClassAppFactory(app_or_factory.__class__)
