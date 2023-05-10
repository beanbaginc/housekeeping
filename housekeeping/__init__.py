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
"""

from housekeeping.base import (BaseDeprecationWarningMixin,
                               BasePendingRemovalWarning,
                               BaseRemovedInWarning,
                               DeprecationWarningType)


__all__ = [
    'BaseDeprecationWarningMixin',
    'BasePendingRemovalWarning',
    'BaseRemovedInWarning',
    'DeprecationWarningType',
]
