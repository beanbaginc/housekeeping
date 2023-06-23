"""Internal helpers for deprecation code.

This module is not public API, and may change.
"""

from __future__ import annotations

import inspect
import operator
from types import FunctionType
from typing import Any, Callable, Generic, Type, TypeVar, Union, cast

from housekeeping.base import (DEFAULT_STACK_LEVEL,
                               DeprecationWarningTypeOrCallable)


_T = TypeVar('_T')


# NOTE: This must be defined before LazyObject.
def _new_method_proxy(
    func_name: str,
) -> Callable:
    """Return a proxy for a method on a wrapped object.

    This will lazily initialize the object if required, and then call the
    function on it.

    Args:
        func (callable):
            The function to call on the wrapped object when this proxy is
            called.

    Returns:
        callable:
        The new proxy function.
    """
    def _inner(
        self: LazyObject,
        *args,
        **kwargs,
    ) -> Callable:
        return getattr(self._get_lazy_wrapped(), func_name)(*args, **kwargs)

    return _inner


class _Empty:
    """A class representing an empty state for a LazyObject."""


class LazyObject(Generic[_T]):
    """A wrapper around a lazily-instantiated object.

    This will act as the wrapped object, but only instantiate it when an
    instance is required.
    """

    ######################
    # Instance variables #
    ######################

    _lazy_wrapped: Union[_T, Type[_Empty]] = _Empty
    _lazy_init_func: Callable

    def __init__(
        self,
        init_func: Callable,
    ) -> None:
        """Initialize the object.

        This will store an init function that will be used when an instance
        is required.

        Args:
            init_func (callable):
                The function to call when initializing an object.
        """
        self.__dict__['_lazy_init_func'] = init_func

    def __setattr__(
        self,
        name: str,
        value: Any,
    ) -> None:
        """Set an attribute on the wrapped object.

        Args:
            name (str):
                The name of the attribute.

            value (object):
                The attribute value.
        """
        if name == '_lazy_wrapped':
            self.__dict__['_lazy_wrapped'] = value
        else:
            setattr(self._get_lazy_wrapped(), name, value)

    def __delattr__(
        self,
        name: str,
    ) -> None:
        """Delete an attribute on the wrapped object.

        Args:
            name (str):
                The name of the attribute.
        """
        if name == '_lazy_wrapped':
            raise TypeError('Cannot delete internal lazy state.')

        delattr(self._get_lazy_wrapped(), name)

    if 1:
        __bool__ = _new_method_proxy('__bool__')
        __bytes__ = _new_method_proxy('__bytes__')
        __contains__ = _new_method_proxy('__contains__')
        __delitem__ = _new_method_proxy('__delitem__')
        __dir__ = _new_method_proxy('__dir__')
        __eq__ = _new_method_proxy('__eq__')
        __getattr__ = _new_method_proxy('__getattr__')
        __getitem__ = _new_method_proxy('__getitem__')
        __gt__ = _new_method_proxy('__gt__')
        __hash__ = _new_method_proxy('__has__')
        __iter__ = _new_method_proxy('__iter__')
        __len__ = _new_method_proxy('__len__')
        __lt__ = _new_method_proxy('__lt__')
        __ne__ = _new_method_proxy('__ne__')
        __setitem__ = _new_method_proxy('__setitem__')
        __str__ = _new_method_proxy('__str__')

        __add__ = _new_method_proxy('__add__')
        __iadd__ = _new_method_proxy('__iadd__')
        __radd__ = _new_method_proxy('__radd__')
        __sub__ = _new_method_proxy('__sub__')
        __isub__ = _new_method_proxy('__isub__')
        __rsub__ = _new_method_proxy('__rsub__')
        __mul__ = _new_method_proxy('__mul__')
        __imul__ = _new_method_proxy('__imul__')
        __rmul__ = _new_method_proxy('__rmul__')
        __div__ = _new_method_proxy('__div__')
        __idiv__ = _new_method_proxy('__idiv__')
        __rdiv__ = _new_method_proxy('__rdiv__')

    # Pretend to be the class.
    __class__: Type[_T] = cast(  # type: ignore
        Type[_T],
        property(_new_method_proxy(operator.attrgetter('__class__'))))

    def _get_lazy_wrapped(self) -> _T:
        """Return the lazily-wrapped instance.

        This will initialize the instance if not already initialized.

        Returns:
            object:
            The wrapped instance.
        """
        _wrapped = self._lazy_wrapped

        if _wrapped is _Empty:
            _wrapped = self._lazy_init_func()
            self._lazy_wrapped = _wrapped

        return cast(_T, _wrapped)


def format_display_name(
    entity: Union[Callable, Type],
) -> str:
    """Format the display name for a function or class.

    The result will include the module name and qualified name within the
    module.

    Args:
        entity (type or object):
            The entity to format.

    Returns:
        str:
        The resulting string format in ``<module>.<qualname>`` form.
    """
    display_name: str = '%s.%s' % (entity.__module__, entity.__qualname__)

    if inspect.isfunction(entity):
        display_name = f'{display_name}()'

    return display_name


def emit_warning(
    warning_cls: DeprecationWarningTypeOrCallable,
    *,
    deprecation_msg: str,
    pending_deprecation_msg: str,
    stacklevel: int = DEFAULT_STACK_LEVEL,
    **kwargs,
) -> None:
    """Emit a warning with a message dependent on the warning type.

    This takes in a deprecation message and a pending deprecation message
    and emits a warning with the correct message for the type of warning
    class.

    Args:
        warning_cls (type or callable):
            The deprecation warning class.

        deprecation_msg (str):
            The message to use for deprecation warnings.

        pending_deprecation_msg (str):
            The message to use for pending deprecation warnings.

        stacklevel (int, optional):
            A level to use for stack trace.

            Housekeeping will adjust this to factor in any internal functions.

        **kwargs (dict):
            Additional keyword arguments to pass to
            :py:meth:`~housekeeping.base.BaseDeprecationWarningMixin.warn`.
    """
    message: str

    if isinstance(warning_cls, FunctionType):
        warning_cls = warning_cls()

    if not inspect.isclass(warning_cls):
        raise TypeError('Expected a deprecation warning class for %r'
                        % warning_cls)

    if issubclass(warning_cls, DeprecationWarning):
        message = deprecation_msg
    elif issubclass(warning_cls, PendingDeprecationWarning):
        message = pending_deprecation_msg
    else:
        raise TypeError('Invalid deprecation class %r' % warning_cls)

    warning_cls.warn(message,
                     stacklevel=stacklevel + 1,  # Factor in this function.
                     **kwargs)
