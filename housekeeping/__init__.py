"""Housekeeping deprecation handlers for Python.

This is the primary module for Housekeeping. Projects should import straight
from this module.

The following deprecation helpers and classes are available:

.. autosummary::
   :nosignatures:

   ~housekeeping.base.BaseDeprecationWarningMixin
   ~housekeeping.base.BasePendingRemovalWarning
   ~housekeeping.base.BaseRemovedInWarning
   ~housekeeping.base.DeprecationWarningType
   ~housekeeping.classes.ClassDeprecatedMixin
   ~housekeeping.classes.ClassMovedMixin
   ~housekeeping.functions.deprecate_non_keyword_only_args
   ~housekeeping.functions.deprecated_arg_value
   ~housekeeping.functions.func_deprecated
   ~housekeeping.functions.func_moved
"""

from housekeeping.base import (BaseDeprecationWarningMixin,
                               BasePendingRemovalWarning,
                               BaseRemovedInWarning,
                               DeprecationWarningType)
from housekeeping.classes import (ClassDeprecatedMixin,
                                  ClassMovedMixin)
from housekeeping.functions import (deprecate_non_keyword_only_args,
                                    deprecated_arg_value,
                                    func_deprecated,
                                    func_moved)


__all__ = [
    'BaseDeprecationWarningMixin',
    'BasePendingRemovalWarning',
    'BaseRemovedInWarning',
    'ClassDeprecatedMixin',
    'ClassMovedMixin',
    'DeprecationWarningType',
    'deprecate_non_keyword_only_args',
    'deprecated_arg_value',
    'func_deprecated',
    'func_moved',
]
