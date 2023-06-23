"""Utilities to deprecate modules."""

from __future__ import annotations

from typing import Optional

from housekeeping.base import (DEFAULT_STACK_LEVEL,
                               DeprecationWarningTypeOrCallable)
from housekeeping.helpers import emit_warning


def module_deprecated(
    warning_cls: DeprecationWarningTypeOrCallable,
    module_name: str,
    *,
    message: Optional[str] = None,
    stacklevel: int = DEFAULT_STACK_LEVEL,
) -> None:
    """Mark a module as deprecated.

    This can be called within the body of a module to emit a deprecation
    warning when imported.

    Deprecation notices will show a variation of::

        `<module_name>` is deprecated and will be removed in <product>
        <version>.

    Pending deprecation notices will show a variation of:

        `<module_name>` is scheduled to be deprecated in a future version of
        <product>.

    Args:
        warning_cls (type, optional):
            The type of warning class to use, or a callable returning one.

            A callable can be used to avoid circular references.

            Version Changed:
                1.1:
                This can now be either a warning class or a function
                that returns one.

        module_name (str):
            The name of the deprecated module.

            Callers can pass ``__name__`` to get the current module name.

        message (str, optional):
            A custom deprecation message to use.

        stacklevel (int, optional):
            A level to use for stack trace.

            Housekeeping will adjust this to factor in any internal functions.
    """
    emit_warning(
        warning_cls,
        deprecation_msg=message or (
            '`%(module_name)s` is deprecated and will be removed in '
            '%(product)s %(version)s.'
        ),
        pending_deprecation_msg=message or (
            '`%(module_name)s` is scheduled to be deprecated in a future '
            'version of %(product)s.'
        ),
        module_name=module_name,
        stacklevel=stacklevel + 1)  # Factor in this function.


def module_moved(
    warning_cls: DeprecationWarningTypeOrCallable,
    old_module_name: str,
    new_module_name: str,
    *,
    message: Optional[str] = None,
    stacklevel: int = DEFAULT_STACK_LEVEL,
) -> None:
    """Mark a module as having moved to another location.

    This can be called within the body of a module to emit a deprecation
    warning when imported.

    Deprecation notices will show a variation of::

        `<old_module_name>` is deprecated and will be removed in <product>
        <version>.  Import `<new_module_name>` instead.

    Pending deprecation notices will show a variation of:

        `<old_module_name>` is scheduled to be deprecated in a future version
        of <product>. To prepare, import `<new_module_name>` instead.

    Args:
        warning_cls (type, optional):
            The type of warning class to use, or a callable returning one.

            A callable can be used to avoid circular references.

            Version Changed:
                1.1:
                This can now be either a warning class or a function
                that returns one.

        old_module_name (str):
            The name of the deprecated module.

            Callers can pass ``__name__`` to get the current module name.

        new_module_name (str):
            The name of the new module.

            Callers can pass :samp:`{newmodule}.__name__` to get the new
            module's name.

        message (str, optional):
            A custom deprecation message to use.

        stacklevel (int, optional):
            A level to use for stack trace.

            Housekeeping will adjust this to factor in any internal functions.
    """
    emit_warning(
        warning_cls,
        deprecation_msg=message or (
            '`%(old_module_name)s` is deprecated and will be removed in '
            '%(product)s %(version)s. Import `%(new_module_name)s` instead.'
        ),
        pending_deprecation_msg=message or (
            '`%(old_module_name)s` is scheduled to be deprecated in a future '
            'version of %(product)s. To prepare, import `%(new_module_name)s` '
            'instead.'
        ),
        old_module_name=old_module_name,
        new_module_name=new_module_name,
        stacklevel=stacklevel + 1)  # Factor in this function.
