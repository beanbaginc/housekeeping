"""Common support for Housekeeping unit tests."""

from __future__ import annotations

import re
import warnings
from contextlib import contextmanager
from typing import Dict, Iterator, List
from unittest import TestCase as BaseTestCase

from housekeeping.base import (BasePendingRemovalWarning,
                               BaseRemovedInWarning,
                               DeprecationWarningType)


class MyPendingRemovalWarning(BasePendingRemovalWarning):
    product = 'My Product'


class MyRemovedInWarning(BaseRemovedInWarning):
    product = 'My Product'
    version = '1.0'


_SOURCE_CACHE: Dict[str, List[str]] = {}


class TestCase(BaseTestCase):
    """Base class for Housekeeping test cases."""

    def setUp(self) -> None:
        super().setUp()

        cls = type(self)

        self.locals_prefix = '%s.%s.%s.<locals>' % (
            cls.__module__,
            cls.__name__,
            self._testMethodName)

    @contextmanager
    def assertWarning(
        self,
        warning_cls: DeprecationWarningType,
        message: str,
        line: str,
    ) -> Iterator[None]:
        """Assert that a warning is generated.

        This will check the warning type, message, and expected source line
        for the stack trace.

        Context:
            The test to run.
        """
        with self.assertWarnsRegex(warning_cls, re.escape(message)) as ctx:
            yield

        warning = ctx.warnings[-1]
        filename = warning.filename
        lineno = warning.lineno

        try:
            source = _SOURCE_CACHE[filename]
        except KeyError:
            with open(filename, 'r') as fp:
                source = fp.readlines()

            _SOURCE_CACHE[filename] = source

        self.assertEqual(source[lineno - 1].strip(), line)

    @contextmanager
    def assertNoWarnings(self) -> Iterator[None]:
        """Assert that a warning is not generated.

        Context:
            The test to run.
        """
        with warnings.catch_warnings(record=True) as w:
            # Some warnings such as DeprecationWarning are filtered by
            # default, stop filtering them.
            warnings.simplefilter('always')

            try:
                yield
            finally:
                self.assertEqual(len(w), 0)
