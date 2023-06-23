"""Utilities to deprecate classes."""

from __future__ import annotations

from typing import Optional, Type

from housekeeping.base import DeprecationWarningTypeOrCallable
from housekeeping.helpers import emit_warning, format_display_name


class ClassDeprecatedMixin:
    """Mixin for classes that are deprecated.

    This will emit a deprecation warning when the class is first subclassed.

    Classes using this mixin must supply a ``warning_cls=...`` in the
    constructor, with optional ``subclass_deprecation_msg=...`` and
    ``init_deprecation_msg=...`` arguments.

    Subclass deprecation notices will show a variation on::

        `<subclass>` subclasses `<baseclass>`, which is deprecated and will be
        removed in <product> <version>.

    Subclass pending deprecation notices will show a variation on::

        `<subclass>` subclasses `<baseclass>`, which is scheduled to be
        deprecated in a future version of <product>.

    Initialization deprecation notices will show a variation on::

        `<class>` is deprecated and will be removed in <product> <version>.

    Initialization deprecation notices will show a variation on::

        `<class>` is scheduled to be deprecated in a future version of
        <product>.

    Custom messages can be provided through ``deprecation_msg`` and
    ``init_deprecation_msg=...``.

    Subclass deprecations only show when directly subclassing this class.
    A subclass of a subclass, for example, will not show a deprecation
    message.

    Similarly, a deprecation message will be shown when directly initializing
    this class, but not a subclass.

    Example:
        .. code-block:: python

            from housekeeping import ClassDeprecatedMixin


           class MyOldClass(ClassDeprecatedMixin,
                            warning_cls=RemovedInMyProject20Warning):
               pass

           # This will emit a deprecation warning.
           MyOldClass()

           # So will this.
           class MyChildClass(OldBaseClass):
               pass

           # But this will not.
           MyChildClass()

        With ``subclass_deprecation_msg``:

        .. code-block:: python

           class MyOldClass(ClassDeprecatedMixin,
                            warning_cls=RemovedInMyProject20Warning,
                            subclass_deprecation_msg='...'):
               ...

        With ``init_deprecation_msg``:

        .. code-block:: python

           class MyOldClass(ClassDeprecatedMixin,
                            warning_cls=RemovedInMyProject20Warning,
                            init_deprecation_msg='...'):
               ...
    """

    _housekeeping_base_cls: Optional[Type] = None
    _housekeeping_subclass_deprecation_msg: Optional[str] = None
    _housekeeping_init_deprecation_msg: Optional[str] = None
    _housekeeping_warning_cls: Optional[DeprecationWarningTypeOrCallable] = \
        None

    def __init_subclass__(
        cls,
        *,
        init_deprecation_msg: Optional[str] = None,
        subclass_deprecation_msg: Optional[str] = None,
        warning_cls: Optional[DeprecationWarningTypeOrCallable] = None,
        **kwargs,
    ) -> None:
        """Initialize a subclass.

        If this is a direct subclass of a deprecated class, a deprecation
        warning will be emitted.

        Args:
            init_deprecation_msg (str, optional):
                A custom deprecation message to use when initializing the
                class directly.

            subclass_deprecation_msg (str, optional):
                A custom deprecation message to use when subclassing the
                class directly.

            warning_cls (type or callable, optional):
                The type of warning class to use, or a callable returning one.

                This must be provided for the class using this mixin. It
                will be ignored for subclasses.

                A callable can be used to avoid circular references.

                Version Changed:
                    1.1:
                    This can now be either a warning class or a function
                    that returns one.

            **kwargs (dict):
                Additional keyword arguments to pass to the parent.
        """
        if ClassDeprecatedMixin in cls.__bases__:
            # This class is deprecated, so store information for immediate
            # subclasses to reference.
            if warning_cls is None:
                raise AssertionError(
                    'warning_cls=... must be set in the parent class list of '
                    '%(class_name)s to a deprecation warning class.'
                    % {
                        'class_name': format_display_name(cls),
                    })

            cls._housekeeping_base_cls = cls
            cls._housekeeping_init_deprecation_msg = init_deprecation_msg
            cls._housekeeping_subclass_deprecation_msg = \
                subclass_deprecation_msg
            cls._housekeeping_warning_cls = warning_cls
        else:
            deprecated_base_cls = cls._housekeeping_base_cls
            warning_cls = cls._housekeeping_warning_cls

            assert deprecated_base_cls is not None
            assert warning_cls is not None

            message = cls._housekeeping_subclass_deprecation_msg

            if (cls._housekeeping_base_cls in cls.__bases__ and
                not getattr(cls, 'housekeeping_skip_warning', False)):
                emit_warning(
                    warning_cls,
                    deprecation_msg=message or (
                        '`%(subclass_name)s` subclasses `%(class_name)s`, '
                        'which is deprecated and will be removed in '
                        '%(product)s %(version)s.'
                    ),
                    pending_deprecation_msg=message or (
                        '`%(subclass_name)s` subclasses `%(class_name)s`, '
                        'which is scheduled to be deprecated in a future '
                        'version of %(product)s.'
                    ),
                    class_name=format_display_name(deprecated_base_cls),
                    subclass_name=format_display_name(cls))

        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the object.

        If this class directly mixes in :py:class:`ClassDeprecatedMixin`, a
        deprecation warning will be emitted.

        Args:
            **args (dict):
                Positional arguments to pass to the parent.

            **kwargs (dict):
                Keyword arguments to pass to the parent.
        """
        cls = type(self)

        if cls is self._housekeeping_base_cls:
            warning_cls = cls._housekeeping_warning_cls

            assert warning_cls is not None

            message = cls._housekeeping_init_deprecation_msg

            emit_warning(
                warning_cls,
                deprecation_msg=message or (
                    '`%(class_name)s` is deprecated and will be removed in '
                    '%(product)s %(version)s.'
                ),
                pending_deprecation_msg=message or (
                    '`%(class_name)s` is scheduled to be deprecated in a '
                    'future version of %(product)s.'
                ),
                class_name=format_display_name(cls))

        super().__init__(*args, **kwargs)


class ClassMovedMixin:
    """Mixin for classes that have moved.

    This will emit a deprecation warning when the class is first subclassed,
    advising the consumer to switch to a different subclass.
    message.

    Classes using this mixin must supply a ``warning_cls=...`` in the
    constructor, with an optional ``deprecation_msg=...``.

    It may also supply ``new_base_cls=``, to specify a reference to the new
    class. This defaults to the last listed parent of the deprecated class.

    Deprecation notices will show a variation on::

        `<subclass>` subclasses `<old_baseclass>`, but `<old_baseclass>` is
        deprecated and will be removed in <product> <version>. You will need
        to subclass `<new_subclass>` instead.

    Pending deprecation notices will show a variation on::

        `<subclass>` subclasses `<baseclass>`, and `<baseclass>` is
        scheduled to be deprecated in a future version of <product>. To
        prepare, subclass `<new_subclass>` instead.

    Custom messages can be provided through ``deprecation_msg``.

    Example:
        .. code-block:: python

           from housekeeping import ClassDeprecatedMixin


           class MyOldClass(ClassMovedMixin, MyNewBaseClass,
                            warning_cls=RemovedInMyProject20Warning):
               pass

           # This will emit a deprecation warning.
           MyOldClass()

           # So will this.
           class MyChildClass(MyOldClass):
               pass

           # But this will not.
           MyChildClass()

           # Nor will this.
           class MyGrandChildClass(MyChildClass):
               pass

        With ``deprecation_msg``:

        .. code-block:: python

           class MyOldClass(ClassMovedMixin, MyNewBaseClass,
                            warning_cls=RemovedInMyProject20Warning,
                            deprecation_msg='...'):
               ...

        With ``new_base_cls``:

        .. code-block:: python

           class MyOldClass(ClassMovedMixin, MyNewBaseClass, SomeMixin,
                            warning_cls=RemovedInMyProject20Warning,
                            new_base_cls=MyNewBaseClass):
               ...
    """

    _housekeeping_base_cls: Optional[Type] = None
    _housekeeping_init_deprecation_msg: Optional[str] = None
    _housekeeping_new_base_cls: Optional[Type] = None
    _housekeeping_subclass_deprecation_msg: Optional[str] = None
    _housekeeping_warning_cls: Optional[DeprecationWarningTypeOrCallable] = \
        None

    def __init_subclass__(
        cls,
        *,
        init_deprecation_msg: Optional[str] = None,
        subclass_deprecation_msg: Optional[str] = None,
        new_base_cls: Optional[Type] = None,
        warning_cls: Optional[DeprecationWarningTypeOrCallable] = None,
        **kwargs,
    ) -> None:
        """Initialize a subclass.

        If this is a direct subclass of a deprecated class, a deprecation
        warning will be emitted.

        Args:
            init_deprecation_msg (str, optional):
                A custom deprecation message to use when initializing the
                class directly.

            subclass_deprecation_msg (str, optional):
                A custom deprecation message to use when subclassing the
                class directly.

            warning_cls (type or callable, optional):
                The type of warning class to use, or a callable returning one.

                This must be provided for the class using this mixin. It
                will be ignored for subclasses.

                A callable can be used to avoid circular references.

                Version Changed:
                    1.1:
                    This can now be either a warning class or a function
                    that returns one.

            **kwargs (dict):
                Additional keyword arguments to pass to the parent.
        """
        if ClassMovedMixin in cls.__bases__:
            # This class is deprecated, so store information for immediate
            # subclasses to reference.
            if warning_cls is None:
                raise AssertionError(
                    'warning_cls=... must be set in the parent class list of '
                    '%(class_name)s to a deprecation warning class.'
                    % {
                        'class_name': format_display_name(cls),
                    })

            cls._housekeeping_base_cls = cls
            cls._housekeeping_init_deprecation_msg = init_deprecation_msg
            cls._housekeeping_subclass_deprecation_msg = \
                subclass_deprecation_msg
            cls._housekeeping_new_base_cls = new_base_cls or cls.__bases__[-1]
            cls._housekeeping_warning_cls = warning_cls
        else:
            deprecated_base_cls = cls._housekeeping_base_cls
            new_base_cls = cls._housekeeping_new_base_cls
            warning_cls = cls._housekeeping_warning_cls

            assert deprecated_base_cls is not None
            assert new_base_cls is not None
            assert warning_cls is not None

            message = cls._housekeeping_subclass_deprecation_msg

            if (cls._housekeeping_base_cls in cls.__bases__ and
                not getattr(cls, 'housekeeping_skip_warning', False)):
                emit_warning(
                    warning_cls,
                    deprecation_msg=message or (
                        '`%(subclass_name)s` subclasses `%(old_class_name)s`, '
                        'which is deprecated and will be removed in '
                        '%(product)s %(version)s. You will need to subclass '
                        '`%(new_class_name)s` instead.'
                    ),
                    pending_deprecation_msg=message or (
                        '`%(subclass_name)s` subclasses `%(old_class_name)s`, '
                        'which is scheduled to be deprecated in a future '
                        'version of %(product)s. To prepare, subclass '
                        '`%(new_class_name)s` instead.'
                    ),
                    old_class_name=format_display_name(deprecated_base_cls),
                    new_class_name=format_display_name(new_base_cls),
                    subclass_name=format_display_name(cls))

        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the object.

        If this class directly mixes in :py:class:`ClassMovedMixin`, a
        deprecation warning will be emitted.

        Args:
            **args (dict):
                Positional arguments to pass to the parent.

            **kwargs (dict):
                Keyword arguments to pass to the parent.
        """
        cls = type(self)

        if cls is self._housekeeping_base_cls:
            new_base_cls = cls._housekeeping_new_base_cls
            warning_cls = cls._housekeeping_warning_cls

            assert new_base_cls is not None
            assert warning_cls is not None

            message = cls._housekeeping_init_deprecation_msg

            emit_warning(
                warning_cls,
                deprecation_msg=message or (
                    '`%(old_class_name)s` is deprecated and will be removed '
                    'in %(product)s %(version)s. You will need to use '
                    '%(new_class_name)s instead.'
                ),
                pending_deprecation_msg=message or (
                    '`%(old_class_name)s` is scheduled to be deprecated in a '
                    'future version of %(product)s. To prepare, use '
                    '%(new_class_name)s instead.'
                ),
                old_class_name=format_display_name(cls),
                new_class_name=format_display_name(new_base_cls))

        super().__init__(*args, **kwargs)
