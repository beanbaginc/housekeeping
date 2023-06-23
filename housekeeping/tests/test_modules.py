"""Unit tests for housekeeping.modules."""

from __future__ import annotations

from housekeeping.modules import module_deprecated, module_moved
from housekeeping.tests.testcases import (MyPendingRemovalWarning,
                                          MyRemovedInWarning,
                                          TestCase)


class ModuleDeprecatedTests(TestCase):
    """Unit tests for module_deprecated."""

    def test_with_deprecation_warning(self) -> None:
        """Testing module_deprecated and deprecation"""
        def _import_module():
            module_deprecated(MyRemovedInWarning, __name__)

        message = (
            '`housekeeping.tests.test_modules` is deprecated and will be '
            'removed in My Product 1.0.'
        )

        with self.assertWarning(MyRemovedInWarning, message,
                                '_import_module()'):
            _import_module()

    def test_with_pending_deprecation_warning(self) -> None:
        """Testing module_deprecated and pending deprecation"""
        def _import_module():
            module_deprecated(MyPendingRemovalWarning, __name__)

        message = (
            '`housekeeping.tests.test_modules` is scheduled to be '
            'deprecated in a future version of My Product.'
        )

        with self.assertWarning(MyPendingRemovalWarning, message,
                                '_import_module()'):
            _import_module()

    def test_with_message(self) -> None:
        """Testing module_deprecated and custom message"""
        def _import_module():
            module_deprecated(
                MyRemovedInWarning,
                __name__,
                message=(
                    'Custom message: %(module_name)s; %(product)s; '
                    '%(version)s'
                ))

        message = (
            'Custom message: housekeeping.tests.test_modules; My Product; 1.0'
        )

        with self.assertWarning(MyRemovedInWarning, message,
                                '_import_module()'):
            _import_module()

    def test_with_warning_cls_callable(self) -> None:
        """Testing module_deprecated and warning_cls as callable"""
        def _import_module():
            module_deprecated(lambda: MyRemovedInWarning, __name__)

        message = (
            '`housekeeping.tests.test_modules` is deprecated and will be '
            'removed in My Product 1.0.'
        )

        with self.assertWarning(MyRemovedInWarning, message,
                                '_import_module()'):
            _import_module()


class ModuleMovedTests(TestCase):
    """Unit tests for module_moved."""

    def test_with_deprecation_warning(self) -> None:
        """Testing module_moved and deprecation"""
        def _import_module():
            module_moved(MyRemovedInWarning, __name__, 'my.new.module')

        message = (
            '`housekeeping.tests.test_modules` is deprecated and will be '
            'removed in My Product 1.0. Import `my.new.module` instead.'
        )

        with self.assertWarning(MyRemovedInWarning, message,
                                '_import_module()'):
            _import_module()

    def test_with_pending_deprecation_warning(self) -> None:
        """Testing module_moved and pending deprecation"""
        def _import_module():
            module_moved(MyPendingRemovalWarning, __name__, 'my.new.module')

        message = (
            '`housekeeping.tests.test_modules` is scheduled to be '
            'deprecated in a future version of My Product. To prepare, '
            'import `my.new.module` instead.'
        )

        with self.assertWarning(MyPendingRemovalWarning, message,
                                '_import_module()'):
            _import_module()

    def test_with_message(self) -> None:
        """Testing module_moved and custom message"""
        def _import_module():
            module_moved(
                MyRemovedInWarning,
                __name__,
                'my.new.module',
                message=(
                    'Custom message: %(old_module_name)s; '
                    '%(new_module_name)s; %(product)s; %(version)s'
                ))

        message = (
            'Custom message: housekeeping.tests.test_modules; my.new.module; '
            'My Product; 1.0'
        )

        with self.assertWarning(MyRemovedInWarning, message,
                                '_import_module()'):
            _import_module()

    def test_with_warning_cls_callable(self) -> None:
        """Testing module_moved and warning_cls as callable"""
        def _import_module():
            module_moved(lambda: MyRemovedInWarning, __name__, 'my.new.module')

        message = (
            '`housekeeping.tests.test_modules` is deprecated and will be '
            'removed in My Product 1.0. Import `my.new.module` instead.'
        )

        with self.assertWarning(MyRemovedInWarning, message,
                                '_import_module()'):
            _import_module()
