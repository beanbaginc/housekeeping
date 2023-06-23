"""Unit tests for housekeeping.classe."""

from __future__ import annotations

from housekeeping.classes import ClassDeprecatedMixin, ClassMovedMixin
from housekeeping.tests.testcases import (MyPendingRemovalWarning,
                                          MyRemovedInWarning,
                                          TestCase)


class ClassDeprecatedMixinTests(TestCase):
    """Unit tests for ClassDeprecatedMixin."""

    def test_subclass_with_deprecation_warning(self) -> None:
        """Testing ClassDeprecatedMixin subclassing with deprecation"""
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is deprecated and will be removed in My Product 1.0.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_pending_deprecation_warning(self) -> None:
        """Testing ClassDeprecatedMixin subclassing with pending deprecation"""
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=MyPendingRemovalWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is scheduled to be deprecated in a future version of My Product.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_warning_cls_callable(self) -> None:
        """Testing ClassDeprecatedMixin subclassing with warning_cls as
        callable
        """
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=lambda: MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is deprecated and will be removed in My Product 1.0.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_deprecation_msg(self) -> None:
        """Testing ClassDeprecatedMixin subclassing with deprecation and
        subclass_deprecation_msg=
        """
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=MyRemovedInWarning,
                         subclass_deprecation_msg=(
                             'Custom message: %(subclass_name)s; '
                             '%(class_name)s; %(product)s; %(version)s'
                         )):
            pass

        prefix = self.locals_prefix
        message = (
            f'Custom message: {prefix}.MySubclass; {prefix}.MyOldClass; '
            f'My Product; 1.0'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_grandchildren(self) -> None:
        """Testing ClassDeprecatedMixin subclassing with grandchildren of
        deprecated class
        """
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is deprecated and will be removed in My Product 1.0.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

        with self.assertNoWarnings():
            class MySubSubclass(MySubclass):
                pass

    def test_init_with_deprecation_warning(self) -> None:
        """Testing ClassDeprecatedMixin initialization with deprecation"""
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MyOldClass` is deprecated and will be removed in '
            f'My Product 1.0.'
        )
        line = 'MyOldClass()'

        with self.assertWarning(MyRemovedInWarning, message, line):
            MyOldClass()

    def test_init_with_pending_deprecation_warning(self) -> None:
        """Testing ClassDeprecatedMixin initialization with pending deprecation
        """
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=MyPendingRemovalWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MyOldClass` is scheduled to be deprecated in a '
            f'future version of My Product.'
        )
        line = 'MyOldClass()'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            MyOldClass()

    def test_init_with_deprecation_msg(self) -> None:
        """Testing ClassDeprecatedMixin initialization with deprecation and
        init_deprecation_msg=
        """
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=MyRemovedInWarning,
                         init_deprecation_msg=(
                             'Custom message: %(class_name)s; %(product)s; '
                             '%(version)s'
                         )):
            pass

        prefix = self.locals_prefix
        message = (
            f'Custom message: {prefix}.MyOldClass; My Product; 1.0'
        )
        line = 'MyOldClass()'

        with self.assertWarning(MyRemovedInWarning, message, line):
            MyOldClass()

    def test_init_on_subclass(self) -> None:
        """Testing ClassDeprecatedMixin initialization on subclass"""
        class MyOldClass(ClassDeprecatedMixin,
                         warning_cls=MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is deprecated and will be removed in My Product 1.0.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

        with self.assertNoWarnings():
            MySubclass()


class ClassMovedMixinTests(TestCase):
    """Unit tests for ClassMovedMixin."""

    def test_subclass_with_deprecation_warning(self) -> None:
        """Testing ClassMovedMixin subclassing with deprecation"""
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is deprecated and will be removed in My Product 1.0. You will '
            f'need to subclass `{prefix}.MyNewClass` instead.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_pending_deprecation_warning(self) -> None:
        """Testing ClassMovedMixin subclassing with pending deprecation"""
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=MyPendingRemovalWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is scheduled to be deprecated in a future version of My '
            f'Product. To prepare, subclass `{prefix}.MyNewClass` instead.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_warning_cls_callable(self) -> None:
        """Testing ClassMovedMixin subclassing with warning_cls as callable"""
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=lambda: MyPendingRemovalWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is scheduled to be deprecated in a future version of My '
            f'Product. To prepare, subclass `{prefix}.MyNewClass` instead.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_deprecation_msg(self) -> None:
        """Testing ClassMovedMixin subclassing with subclass_deprecation_msg=
        """
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=MyRemovedInWarning,
                         subclass_deprecation_msg=(
                             'Custom message: %(subclass_name)s; '
                             '%(old_class_name)s; %(new_class_name)s; '
                             '%(product)s; %(version)s'
                         )):
            pass

        prefix = self.locals_prefix
        message = (
            f'Custom message: {prefix}.MySubclass; {prefix}.MyOldClass; '
            f'{prefix}.MyNewClass; My Product; 1.0'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_new_base_cls(self) -> None:
        """Testing ClassMovedMixin subclassing with new_base_cls="""
        class MyNewClass:
            pass

        class MyOtherMixin:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass, MyOtherMixin,
                         warning_cls=MyRemovedInWarning,
                         new_base_cls=MyNewClass):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is deprecated and will be removed in My Product 1.0. You will '
            f'need to subclass `{prefix}.MyNewClass` instead.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

    def test_subclass_with_grandchildren(self) -> None:
        """Testing ClassMovedMixin subclassing with grandchildren of
        deprecated class
        """
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is deprecated and will be removed in My Product 1.0. You will '
            f'need to subclass `{prefix}.MyNewClass` instead.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

        with self.assertNoWarnings():
            class MySubSubclass(MySubclass):
                pass

    def test_init_with_deprecation_warning(self) -> None:
        """Testing ClassMovedMixin initialization with deprecation"""
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MyOldClass` is deprecated and will be removed in '
            f'My Product 1.0.'
        )
        line = 'MyOldClass()'

        with self.assertWarning(MyRemovedInWarning, message, line):
            MyOldClass()

    def test_init_with_pending_deprecation_warning(self) -> None:
        """Testing ClassMovedMixin initialization with pending deprecation
        """
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=MyPendingRemovalWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MyOldClass` is scheduled to be deprecated in a '
            f'future version of My Product.'
        )
        line = 'MyOldClass()'

        with self.assertWarning(MyPendingRemovalWarning, message, line):
            MyOldClass()

    def test_init_with_deprecation_msg(self) -> None:
        """Testing ClassMovedMixin initialization with deprecation and
        init_deprecation_msg=
        """
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=MyRemovedInWarning,
                         init_deprecation_msg=(
                             'Custom message: %(old_class_name)s; '
                             '%(new_class_name)s; %(product)s; %(version)s'
                         )):
            pass

        prefix = self.locals_prefix
        message = (
            f'Custom message: {prefix}.MyOldClass; {prefix}.MyNewClass; '
            f'My Product; 1.0'
        )
        line = 'MyOldClass()'

        with self.assertWarning(MyRemovedInWarning, message, line):
            MyOldClass()

    def test_init_on_subclass(self) -> None:
        """Testing ClassMovedMixin initialization on subclass"""
        class MyNewClass:
            pass

        class MyOldClass(ClassMovedMixin, MyNewClass,
                         warning_cls=MyRemovedInWarning):
            pass

        prefix = self.locals_prefix
        message = (
            f'`{prefix}.MySubclass` subclasses `{prefix}.MyOldClass`, which '
            f'is deprecated and will be removed in My Product 1.0.'
        )
        line = 'class MySubclass(MyOldClass):'

        with self.assertWarning(MyRemovedInWarning, message, line):
            class MySubclass(MyOldClass):
                pass

        with self.assertNoWarnings():
            MySubclass()
