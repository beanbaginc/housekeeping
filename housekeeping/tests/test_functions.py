"""Unit tests for housekeeping.functions."""

from __future__ import annotations

from housekeeping.functions import (deprecate_non_keyword_only_args,
                                    deprecated_arg_value,
                                    func_deprecated,
                                    func_moved)
from housekeeping.tests.testcases import (MyPendingRemovalWarning,
                                          MyRemovedInWarning,
                                          TestCase)


class DeprecatedArgValueTests(TestCase):
    """Unit tests for deprecated_arg_value"""

    def test_with_deprecation_warning(self) -> None:
        """Testing deprecated_arg_value and deprecation"""
        value = deprecated_arg_value(
            MyRemovedInWarning,
            owner_name='my_func()',
            value=123,
            old_name='old_arg')

        message = (
            '`old_arg` for `my_func()` has been deprecated and will be '
            'removed in My Product 1.0.'
        )
        line = 'result = 1 + value'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = 1 + value

        self.assertEqual(result, 124)

    def test_with_warning_cls_as_callable(self) -> None:
        """Testing deprecated_arg_value with warning_cls as callable"""
        value = deprecated_arg_value(
            lambda: MyRemovedInWarning,
            owner_name='my_func()',
            value=123,
            old_name='old_arg')

        message = (
            '`old_arg` for `my_func()` has been deprecated and will be '
            'removed in My Product 1.0.'
        )
        line = 'result = 1 + value'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = 1 + value

        self.assertEqual(result, 124)


class DeprecateNonKeywordOnlyArgsTests(TestCase):
    """Unit tests for @deprecate_non_keyword_only_args."""

    def test_decorated_state(self) -> None:
        """Testing @deprecate_non_keyword_only_args preserves decorated
        function state
        """
        @deprecate_non_keyword_only_args(MyRemovedInWarning)
        def my_func(a, *, b, c=1):
            """My func docs."""
            return a + b + c

        self.assertEqual(my_func.__name__, 'my_func')
        self.assertEqual(my_func.__doc__, 'My func docs.')

    def test_with_using_kwonly_args(self) -> None:
        """Testing @deprecate_non_keyword_only_args with using keyword-only
        args
        """
        @deprecate_non_keyword_only_args(MyRemovedInWarning)
        def my_func(a, *, b, c=1):
            return a + b + c

        with self.assertNoWarnings():
            result = my_func(1, b=2, c=3)

        self.assertEqual(result, 6)

    def test_with_deprecation_warning_1_arg(self) -> None:
        """Testing @deprecate_non_keyword_only_args with 1 arg and deprecation
        """
        @deprecate_non_keyword_only_args(MyRemovedInWarning)
        def my_func(a, *, b, c=1):
            return a + b + c

        prefix = self.locals_prefix
        message = (
            f'Positional argument `b` must be passed as a keyword argument '
            f'when calling `{prefix}.my_func()`. Passing as a positional '
            f'argument will be required in My Product 1.0.'
        )
        line = 'result = my_func(1, 2, c=3)  # type: ignore'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2, c=3)  # type: ignore

        self.assertEqual(result, 6)

    def test_with_deprecation_warning_n_args(self) -> None:
        """Testing @deprecate_non_keyword_only_args with 2+ args and
        deprecation
        """
        @deprecate_non_keyword_only_args(MyRemovedInWarning)
        def my_func(a, *, b, c=1):
            return a + b + c

        prefix = self.locals_prefix
        message = (
            f'Positional arguments `b`, `c` must be passed as keyword '
            f'arguments when calling `{prefix}.my_func()`. Passing as '
            'positional arguments will be required in My Product 1.0.'
        )
        line = 'result = my_func(1, 2, 3)  # type: ignore'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2, 3)  # type: ignore

        self.assertEqual(result, 6)

    def test_with_deprecation_warning_and_message(self) -> None:
        """Testing @deprecate_non_keyword_only_args with deprecation and
        custom message
        """
        @deprecate_non_keyword_only_args(
            MyRemovedInWarning,
            message=(
                'Custom message: %(pos_args)s; %(func_name)s; %(product)s '
                '%(version)s.'
            )
        )
        def my_func(a, *, b, c=1):
            return a + b + c

        prefix = self.locals_prefix
        message = (
            f'Custom message: `b`, `c`; {prefix}.my_func(); My Product 1.0'
        )
        line = 'result = my_func(1, 2, 3)  # type: ignore'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2, 3)  # type: ignore

        self.assertEqual(result, 6)

    def test_with_pending_deprecation_warning_1_arg(self) -> None:
        """Testing @deprecate_non_keyword_only_args with 1 arg and pending
        deprecation
        """
        @deprecate_non_keyword_only_args(MyPendingRemovalWarning)
        def my_func(a, *, b, c=1):
            return a + b + c

        prefix = self.locals_prefix
        message = (
            f'Positional argument `b` should be passed as a keyword argument '
            f'when calling `{prefix}.my_func()`. Passing as a positional '
            f'argument is scheduled to be deprecated in a future version of '
            f'My Product.'
        )
        line = 'result = my_func(1, 2, c=3)  # type: ignore'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            result = my_func(1, 2, c=3)  # type: ignore

        self.assertEqual(result, 6)

    def test_with_pending_deprecation_warning_n_args(self) -> None:
        """Testing @deprecate_non_keyword_only_args with 2+ args and pending
        deprecation
        """
        @deprecate_non_keyword_only_args(MyPendingRemovalWarning)
        def my_func(a, *, b, c=1):
            return a + b + c

        prefix = self.locals_prefix
        message = (
            f'Positional arguments `b`, `c` should be passed as keyword '
            f'arguments when calling `{prefix}.my_func()`. Passing as '
            f'positional arguments is scheduled to be deprecated in a '
            f'future version of My Product.'
        )
        line = 'result = my_func(1, 2, 3)  # type: ignore'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            result = my_func(1, 2, 3)  # type: ignore

        self.assertEqual(result, 6)

    def test_with_warning_cls_callable(self) -> None:
        """Testing @deprecate_non_keyword_only_args with warning_cls as
        callable
        """
        @deprecate_non_keyword_only_args(lambda: MyRemovedInWarning)
        def my_func(a, *, b, c=1):
            return a + b + c

        prefix = self.locals_prefix
        message = (
            f'Positional argument `b` must be passed as a keyword argument '
            f'when calling `{prefix}.my_func()`. Passing as a positional '
            f'argument will be required in My Product 1.0.'
        )
        line = 'result = my_func(1, 2, c=3)  # type: ignore'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2, c=3)  # type: ignore

        self.assertEqual(result, 6)


class FuncDeprecatedTests(TestCase):
    """Unit tests for func_deprecated."""

    def test_decorated_state(self) -> None:
        """Testing @func_deprecated preserves decorated function state"""
        @func_deprecated(MyRemovedInWarning)
        def my_func(a, b):
            """My func docs."""
            return a + b

        self.assertEqual(my_func.__name__, 'my_func')
        self.assertEqual(my_func.__doc__, 'My func docs.')

    def test_with_deprecation_warning(self) -> None:
        """Testing @func_deprecated with deprecation"""
        @func_deprecated(MyRemovedInWarning)
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.my_func()` is deprecated and will be removed in My '
            f'Product 1.0.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_pending_deprecation_warning(self) -> None:
        """Testing @func_deprecated with pending deprecation"""
        @func_deprecated(MyPendingRemovalWarning)
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.my_func()` is scheduled to be deprecated in a future '
            f'version of My Product.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_deprecation_warning_and_message(self) -> None:
        """Testing @func_deprecated with deprecation and custom message"""
        @func_deprecated(
            MyRemovedInWarning,
            message=(
                'Custom message: %(func_name)s; %(product)s %(version)s.'
            )
        )
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = f'Custom message: {prefix}.my_func(); My Product 1.0.'
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_pending_deprecation_warning_and_message(self) -> None:
        """Testing @func_deprecated with pending deprecation"""
        @func_deprecated(
            MyPendingRemovalWarning,
            message=(
                'Custom message: %(func_name)s; %(product)s.'
            )
        )
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = f'Custom message: {prefix}.my_func(); My Product'
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_warning_cls_callable(self) -> None:
        """Testing @func_deprecated with warning_cls as callable"""
        @func_deprecated(lambda: MyRemovedInWarning)
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.my_func()` is deprecated and will be removed in My '
            f'Product 1.0.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)


class FuncMovedTests(TestCase):
    """Unit tests for func_moved."""

    def test_decorated_state(self) -> None:
        """Testing @func_moved preserves decorated function state"""
        @func_moved(MyRemovedInWarning, 'new_func')
        def my_func(a, b):
            """My func docs."""
            return a + b

        self.assertEqual(my_func.__name__, 'my_func')
        self.assertEqual(my_func.__doc__, 'My func docs.')

    def test_with_new_func_as_callable(self) -> None:
        """Testing @func_moved with new_func as callable"""
        def new_func(a, b):
            return a - b

        @func_moved(MyRemovedInWarning, new_func)
        def my_func(a, b):
            return new_func(a, b)

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.my_func()` has moved to `{prefix}.new_func()`. The '
            f'old function is deprecated and will be removed in My Product '
            f'1.0.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, -1)

    def test_with_new_func_as_string(self) -> None:
        """Testing @func_moved with new_func as string"""
        @func_moved(MyRemovedInWarning, new_func='my_new_func')
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.my_func()` has moved to `my_new_func()`. The old '
            f'function is deprecated and will be removed in My Product 1.0.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_deprecation_warning(self) -> None:
        """Testing @func_moved with deprecation"""
        @func_moved(MyRemovedInWarning, 'my_new_func')
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.my_func()` has moved to `my_new_func()`. The old '
            f'function is deprecated and will be removed in My Product 1.0.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_pending_deprecation_warning(self) -> None:
        """Testing @func_moved with pending deprecation"""
        @func_moved(MyPendingRemovalWarning, new_func='my_new_func')
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.my_func()` has moved to `my_new_func()`. The old '
            f'function is scheduled to be deprecated in a future version '
            f'of My Product.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_deprecation_warning_and_message(self) -> None:
        """Testing @func_moved with deprecation and custom message"""
        @func_moved(
            MyRemovedInWarning,
            new_func='my_new_func',
            message=(
                'Custom message: %(old_func_name)s -> %(new_func_name)s; '
                '%(product)s %(version)s.'
            )
        )
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'Custom message: {prefix}.my_func() -> my_new_func(); '
            f'My Product 1.0.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_pending_deprecation_warning_and_message(self) -> None:
        """Testing @func_moved with pending deprecation"""
        @func_moved(
            MyPendingRemovalWarning,
            new_func='my_new_func',
            message=(
                'Custom message: %(old_func_name)s -> %(new_func_name)s; '
                '%(product)s.'
            )
        )
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'Custom message: {prefix}.my_func() -> my_new_func(); My Product.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)

    def test_with_warning_cls_callable(self) -> None:
        """Testing @func_moved with warning_cls as callable"""
        @func_moved(lambda: MyRemovedInWarning,
                    'my_new_func')
        def my_func(a, b):
            return a + b

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.my_func()` has moved to `my_new_func()`. The old '
            f'function is deprecated and will be removed in My Product 1.0.'
        )
        line = 'result = my_func(1, 2)'

        with self.assertWarning(MyRemovedInWarning, message, line):
            result = my_func(1, 2)

        self.assertEqual(result, 3)
