"""Base support for housekeeping warnings and types."""

from __future__ import annotations

import warnings
from typing import Callable, Type, TYPE_CHECKING, Union

from typing_extensions import TypeAlias

if TYPE_CHECKING:
    _BaseDeprecationWarningMixinClass = DeprecationWarning
    _BasePendingDeprecationWarningMixinClass = PendingDeprecationWarning
else:
    _BaseDeprecationWarningMixinClass = object
    _BasePendingDeprecationWarningMixinClass = object


#: The default stack level for warnings.
DEFAULT_STACK_LEVEL: int = 2


class BaseDeprecationWarningMixin(_BaseDeprecationWarningMixinClass):
    """Mixin for product deprecation and pending-deprecation warning classes.

    This can be used by projects as a mixin for any version-specific
    deprecation warning classes, for use with housekeeping functions.
    """

    #: The name of the product with the deprecated functionality.
    product: str = ''

    #: The version in which the functionality is expected to be removed.
    version: str = ''

    #: Whether a project version is required for this type of warning class.
    version_required: bool = False

    @classmethod
    def warn(
        cls,
        message: str,
        *,
        stacklevel: int = DEFAULT_STACK_LEVEL,
        **kwargs,
    ) -> None:
        """Emit the deprecation warning.

        This is a convenience function that emits a deprecation warning using
        this class, with a suitable default stack level. Callers can provide
        a useful message and a custom stack level.

        Args:
            message (str):
                The message to show in the deprecation warning.

            stacklevel (int, optional):
                The stack level for the warning.
        """
        assert cls.product, (
            f'{cls.__name__}.product must be set to a non-empty string.')

        assert cls.version or not cls.version_required, (
            f'{cls.__name__}.version must be set to a non-empty string.')

        kwargs.update({
            'product': cls.product,
            'version': cls.version,
        })

        warnings.warn(message % kwargs, cls, stacklevel=stacklevel + 1)


class BaseRemovedInWarning(BaseDeprecationWarningMixin, DeprecationWarning):
    """Base class for product deprecation warnings.

    This is used for functionality that is currently deprecated and is
    scheduled to be removed in a particular release.

    It's recommended that projects subclass this to create their own
    base class, and then subclass those for each version.
    """

    version_required = True


class BasePendingRemovalWarning(BaseDeprecationWarningMixin,
                                PendingDeprecationWarning):
    """Base class for product pending-deprecation warnings.

    This is used for functionality that is obsolete and planned for
    deprecation, but is not yet deprecated.

    It's recommended that projects subclass this to create their own
    base class.
    """


#: An alias for representing a BaseDeprecationWarningMixin subclass.
DeprecationWarningType: TypeAlias = Type[BaseDeprecationWarningMixin]


#: An alias for a DeprecationWarningType or a callable returning one.
#:
#: Version Added:
#:     1.1
DeprecationWarningTypeOrCallable: TypeAlias = Union[
    DeprecationWarningType,
    Callable[[], DeprecationWarningType],
]
