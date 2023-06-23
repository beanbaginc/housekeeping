"""Utilities to deprecate functions/methods or arguments."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import (Any, Callable, Dict, List, Optional, Tuple, TypeVar,
                    Union, cast)

from housekeeping.base import (DEFAULT_STACK_LEVEL,
                               DeprecationWarningTypeOrCallable)
from housekeeping.helpers import LazyObject, emit_warning, format_display_name


_FuncT = TypeVar('_FuncT', bound=Callable[..., Any])
_ValueT = TypeVar('_ValueT')


def deprecated_arg_value(
    warning_cls: DeprecationWarningTypeOrCallable,
    *,
    owner_name: str,
    value: _ValueT,
    old_name: str,
    new_name: Optional[str] = None,
    message: Optional[str] = None,
    stacklevel: int = DEFAULT_STACK_LEVEL,
) -> LazyObject[_ValueT]:
    """Wrap a value in a lazy object to warn when used.

    This is useful when sending values to a consumer-provided callback
    function, or setting deprecated data in a dictionary.

    Deprecation notices will show a variation on::

        `<old name>` for `<owner>` has been deprecated and will be removed
        in <product> <version>. [Use `<new name>` instead.]

    Pending deprecation notices will show a variation on::

        `<old name>` for `<owner>` is scheduled to be deprecated in a future
        version of <product> <version>. [To prepare, use `<new name>`
        instead.]

    The variations are based on whether ``new_name`` is provided.

    Custom messages can also be provided.

    Args:
        warning_cls (type or callable):
            The type of warning class to use, or a callable returning one.

            A callable can be used to avoid circular references.

            Version Changed:
                1.1:
                This can now be either a warning class or a function
                that returns one.

        owner_name (str):
            The name of the owner of this argument.

        value (object):
            The argument value.

        old_name (str):
            The old name of the argument/key that was deprecated.

        new_name (str, optional):
            The new name of the argument/key to use instead, if one is
            available.

        message (str, optional):
            A custom deprecation message to use.

        stacklevel (int, optional):
            A level to use for stack trace.

            Housekeeping will adjust this to factor in any internal functions.

    Returns:
        housekeeping.helpers.LazyObject:
        The value wrapped in a lazy object. The first time it is accessed,
        a warning will be emitted.

    Example:
        .. code-block:: python

           from housekeeping import deprecated_arg_value

           def emit_my_signal():
               for func in callback_funcs:
                   # If a handler accesses old_arg, it will emit a deprecation
                   # warning.
                   func(new_arg={...},
                        old_arg=deprecated_arg_value(
                            RemovedInMyProduct20Warning,
                            owner_name='my_signal',
                            value={...},
                            old_name='old_arg',
                            new_name='new_arg'))
    """
    def _warn_on_use():
        if message:
            deprecation_msg = message
            pending_deprecation_msg = message
        elif new_name:
            deprecation_msg = (
                '`%(old_name)s` for `%(owner_name)s` has been deprecated '
                'and will be removed in %(product)s %(version)s. Use '
                '`%(new_name)s` instead.'
            )
            pending_deprecation_msg = (
                '`%(old_name)s` for `%(owner_name)s` is scheduled to be '
                'deprecated in a future version of %(product)s. To '
                'prepare, use `%(new_name)s` instead.'
            )
        else:
            deprecation_msg = (
                '`%(old_name)s` for `%(owner_name)s` has been '
                'deprecated and will be removed in %(product)s '
                '%(version)s.'
            )
            pending_deprecation_msg = (
                '`%(old_name)s` for `%(owner_name)s` is scheduled to be '
                'deprecated in a future version of %(product)s.'
            )

            emit_warning(
                warning_cls,
                deprecation_msg=deprecation_msg,
                pending_deprecation_msg=pending_deprecation_msg,
                old_name=old_name,
                owner_name=owner_name,
                new_name=new_name,
                stacklevel=stacklevel + 2)

        return value

    # NOTE: We do NOT want to use typing here (`LazyObject[...]`), or we'll
    #       trigger some typing logic that stores state on the instance, and
    #       that will load the backed object.
    return LazyObject(_warn_on_use)


def deprecate_non_keyword_only_args(
    warning_cls: DeprecationWarningTypeOrCallable,
    *,
    message: Optional[str] = None,
    stacklevel: int = DEFAULT_STACK_LEVEL,
) -> Callable[[_FuncT], _FuncT]:
    """Deprecate calls passing keyword-only arguments as positional arguments.

    This decorator allows code transitioning to keyword-only arguments to
    continue working when passing values as positional arguments.

    Upon the first call, it will record information about the signature of the
    function and then compare that to any future calls. If any positional
    argument values are passed to keyword-only arguments, the arguments will
    be rewritten to work correctly, and a deprecation warning will be emitted.

    Deprecation notices will show a variation on::

        Positional argument(s) <arg1, arg2, ...> must be passed as keyword
        arguments when calling `<func_name>()`. This will be required in
        <product> <version>.

    Pending deprecation notices will show a variation on::

        Positional argument(s) <arg1, arg2, ...> should be passed as keyword
        arguments when calling `<func_name>()`. Passing as positional
        arguments is scheduled to be deprecated in a future version of
        <product>.

    Custom messages can also be provided.

    Args:
        warning_cls (type or callable):
            The type of warning class to use, or a callable returning one.

            A callable can be used to avoid circular references.

            Version Changed:
                1.1:
                This can now be either a warning class or a function
                that returns one.

        message (str, optional):
            An optional message to use instead of the default.

        stacklevel (int, optional):
            A level to use for stack trace.

            Housekeeping will adjust this to factor in any internal functions.

    Returns:
        callable:
        The function decorator.

    Raises:
        AssertionError:
            The function being called does not provide keyword-only arguments.

    Example:
        .. code-block:: python

           from housekeeping import deprecate_non_keyword_only_args


           @deprecate_non_keyword_only_args(RemovedInMyProduct20Warning)
           def add_abc(a, *, b, c=1):
               return a + b + c

           add_abc(1, 2, 3)      # This will emit a deprecation warning.
           add_abc(1, b=2, c=3)  # This will not.
    """
    def _get_argspec_info(
        func: Callable,
    ) -> Tuple[List[str], int]:
        """Return cached signature and keyword-only argument index information.

        This will compute a signature for the provided function and determine
        the index of the first keyword-only argument. These values will be
        cached on the function for future lookup, so additional calls don't
        incur a penalty.

        Args:
            func (callable):
                The decorated function to inspect.

        Returns:
            tuple:
            Information on the signature:

            Tuple:
                0 (list of str):
                    The list of parameter names for the function.

                1 (int):
                    The index of the first keyword-only argument.

        Raises:
            AssertionError:
                The function being called does not provide keyword-only
                arguments.
        """
        args_cache: Dict[str, Any]
        param_names: List[str]
        first_kwonly_arg_index: int

        try:
            args_cache = getattr(func, '_housekeeping_dep_kwonly_args_cache')
        except AttributeError:
            args_cache = {}
            setattr(func, '_housekeeping_dep_kwonly_args_cache', args_cache)

        if args_cache:
            param_names = args_cache['param_names']
            first_kwonly_arg_index = args_cache['first_kwonly_i']
        else:
            sig = inspect.signature(func)
            first_kwonly_arg_index = -1
            param_names = []
            i = 0

            # This is guaranteed to be in the correct order.
            for param in sig.parameters.values():
                if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                    param_names.append(param.name)

                    if (param.kind == param.KEYWORD_ONLY and
                        first_kwonly_arg_index == -1):
                        first_kwonly_arg_index = i

                    i += 1

            assert first_kwonly_arg_index != -1, (
                '@deprecate_non_keyword_only_args can only be used on '
                'functions that contain keyword-only arguments.')

            args_cache.update({
                'first_kwonly_i': first_kwonly_arg_index,
                'param_names': param_names,
            })

        return param_names, first_kwonly_arg_index

    def _check_call(
        func: Callable,
        args: Tuple,
        kwargs: Dict,
    ) -> Tuple[Tuple, Dict]:
        """Check arguments to a call and modify if necessary.

        This will check if there are any positional arguments being passed as
        keyword arguments. If found, they'll be converted to keyword arguments
        and a warning will be emitted.

        Args:
            func (callable):
                The function being decorated.

            args (tuple):
                The caller-provided positional arguments.

            kwargs (dict):
                The caller-provided keyword arguments.

        Returns:
            tuple:
            A tuple of:

            Tuple:
                0 (tuple):
                    Positional arguments to pass to ``func``.

                1 (dict):
                    Keyword arguments to pass to ``func``.
        """
        param_names, first_kwonly_arg_index = _get_argspec_info(func)
        num_args = len(args)

        if num_args <= first_kwonly_arg_index:
            # The call doesn't have to be modified.
            return args, kwargs

        # Figure out which we need to move over to keyword-only
        # arguments.
        new_args: List = []
        new_kwargs: Dict[str, Any] = kwargs.copy()
        moved_args: List[str] = []
        i = 0

        for param_name in param_names:
            if param_name not in kwargs:
                if i < first_kwonly_arg_index:
                    new_args.append(args[i])
                elif i < num_args:
                    # This must be converted to a keyword argument.
                    new_kwargs[param_name] = args[i]
                    moved_args.append(param_name)
                else:
                    # We've handled all positional arguments. We're done.
                    break

                i += 1

        new_args += args[i:]

        if message:
            deprecation_msg = message
            pending_deprecation_msg = message
        elif len(moved_args) == 1:
            deprecation_msg = (
                'Positional argument %(pos_args)s must be passed as a '
                'keyword argument when calling `%(func_name)s`. Passing as '
                'a positional argument will be required in %(product)s '
                '%(version)s.'
            )
            pending_deprecation_msg = (
                'Positional argument %(pos_args)s should be passed as a '
                'keyword argument when calling `%(func_name)s`. Passing as '
                'a positional argument is scheduled to be deprecated in a '
                'future version of %(product)s.'
            )
        else:
            deprecation_msg = (
                'Positional arguments %(pos_args)s must be passed as '
                'keyword arguments when calling `%(func_name)s`. Passing as '
                'positional arguments will be required in %(product)s '
                '%(version)s.'
            )
            pending_deprecation_msg = (
                'Positional arguments %(pos_args)s should be passed as '
                'keyword arguments when calling `%(func_name)s`. Passing as '
                'positional arguments is scheduled to be deprecated in a '
                'future version of %(product)s.'
            )

        emit_warning(
            warning_cls,
            deprecation_msg=deprecation_msg,
            pending_deprecation_msg=pending_deprecation_msg,
            func_name=format_display_name(func),
            pos_args=', '.join(
                '`%s`' % _arg_name
                for _arg_name in moved_args
            ),
            stacklevel=stacklevel + 1)

        return tuple(new_args), new_kwargs

    def _dec(
        func: _FuncT,
    ) -> _FuncT:
        """Return the decorator for the function.

        Args:
            func (callable):
                The function being decorated.

        Returns:
            callable:
            The decorator for the function configured via the outer
            function's arguments.
        """
        @wraps(func)
        def _call(*args, **kwargs) -> Any:
            new_args, new_kwargs = _check_call(func, args, kwargs)

            return func(*new_args, **new_kwargs)

        return cast(_FuncT, _call)

    return _dec


def func_deprecated(
    warning_cls: DeprecationWarningTypeOrCallable,
    *,
    message: Optional[str] = None,
    stacklevel: int = DEFAULT_STACK_LEVEL,
) -> Callable[[_FuncT], _FuncT]:
    """Decorator to mark an old function as deprecated or pending deprecation.

    This will emit a deprecation warning when called, advising against using
    the function.

    Deprecation notices will show a variation on::

        `<func_name>` is deprecated and will be removed in <product> <version>.

    Pending deprecation notices will show a variation on::

        `<func_name>` is scheduled to be deprecated in a future version of
        <product>.

    Custom messages can also be provided.

    Args:
        warning_cls (type or callable):
            The type of warning class to use, or a callable returning one.

            A callable can be used to avoid circular references.

            Version Changed:
                1.1:
                This can now be either a warning class or a function
                that returns one.

        message (str, optional):
            A custom message to display for the deprecation message.

        stacklevel (int, optional):
            A level to use for stack trace.

            Housekeeping will adjust this to factor in any internal functions.

    Returns:
        callable:
        The decorator function.

    Example:
        .. code-block:: python

           from housekeeping import func_deprecated


           @func_deprecated(RemovedInMyProduct20Warning)
           def my_func():
               ...

           my_func()  # This will emit a deprecation warning.
    """
    def _dec(
        func: _FuncT,
    ) -> _FuncT:
        @wraps(func)
        def _call(*args, **kwargs):
            emit_warning(
                warning_cls,
                deprecation_msg=message or (
                    '`%(func_name)s` is deprecated and will be removed in '
                    '%(product)s %(version)s.'
                ),
                pending_deprecation_msg=message or (
                    '`%(func_name)s` is scheduled to be deprecated in a '
                    'future version of %(product)s.'
                ),
                func_name=format_display_name(func),
                stacklevel=stacklevel)

            return func(*args, **kwargs)

        return cast(_FuncT, _call)

    return _dec


def func_moved(
    warning_cls: DeprecationWarningTypeOrCallable,
    new_func: Union[str, Callable],
    *,
    message: Optional[str] = None,
    stacklevel: int = DEFAULT_STACK_LEVEL,
) -> Callable[[_FuncT], _FuncT]:
    """Decorator to mark an old function as having moved.

    This will emit a deprecation warning when called, pointing consumers to
    the new location of the function.

    Deprecation notices will show a variation on::

        `<old_func_name>` has moved to `<new_func_name>`. The old function
        is deprecated and will be removed in <product> <version>.

    Pending deprecation notices will show a variation on::

        `<old_func_name>` has moved to `<new_func_name>`. The old function
        is scheduled to be deprecated in a future version of <product>.

    Custom messages can also be provided.

    Args:
        warning_cls (type or callable):
            The type of warning class to use, or a callable returning one.

            A callable can be used to avoid circular references.

            Version Changed:
                1.1:
                This can now be either a warning class or a function
                that returns one.

        new_func (str):
            The new function, or a descriptive string referencing the new
            function.

        message (str, optional):
            A custom message to display for the deprecation message.

        stacklevel (int, optional):
            A level to use for stack trace.

            Housekeeping will adjust this to factor in any internal functions.

    Returns:
        callable:
        The decorator function.

    Example:
        .. code-block:: python

           from housekeeping import func_moved


           # This can be invoked with some special behavior:
           @func_moved(RemovedInMyProject20Warning,
                       new_func=new_my_func)
           def my_func(a, b):
               new_my_func(a, b, True)
    """
    def _dec(
        func: _FuncT,
    ) -> _FuncT:
        @wraps(func)
        def _call(*args, **kwargs):
            nonlocal stacklevel

            if isinstance(new_func, str):
                new_func_name = f'{new_func}()'
            else:
                assert callable(new_func)

                new_func_name = format_display_name(new_func)

            emit_warning(
                warning_cls,
                deprecation_msg=message or (
                    '`%(old_func_name)s` has moved to `%(new_func_name)s`. '
                    'The old function is deprecated and will be removed in '
                    '%(product)s %(version)s.'
                ),
                pending_deprecation_msg=message or (
                    '`%(old_func_name)s` has moved to `%(new_func_name)s`. '
                    'The old function is scheduled to be deprecated in a '
                    'future version of %(product)s.'
                ),
                old_func_name=format_display_name(func),
                new_func_name=new_func_name,
                stacklevel=stacklevel)

            return func(*args, **kwargs)

        return cast(_FuncT, _call)

    return _dec
