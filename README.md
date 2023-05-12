# Housekeeping for Python

Housekeeping is a Python package designed to make it easy for projects to mark
consumed code as deprecated or pending deprecation, with helpful instructions
for consumers using deprecated functionality.

It's built with the lessons we learned in
[Review Board](https://www.reviewboard.org),
[Djblets](https://github.com/djblets/djblets), and
[RBTools](https://www.reviewboard.org/downloads/rbtools/).

With Housekeeping, you can easily manage deprecations in your code, helping you
and any consumers of your code transition to the latest and greatest.

It offers decorators, mixins, and functions to help with deprecating functions,
methods, classes, modules, attributes, parameters, and dictionary keys.

Housekeeping is licensed under the MIT license.


## Installing Housekeeping

Housekeeping is built as a utility library for your project. It should be
added to your project's list of dependencies.

To install it manually, run:

```console
$ pip install housekeeping
```

Housekeeping follows [semantic versioning](https://semver.org/), meaning no
surprises when you upgrade.


## Using Housekeeping In Your Project

### Add Your Deprecation Classes

Add base deprecation warning classes to your project.

There are two categories of warnings:

* **Deprecation warnings**, which mark code as being deprecated and
 scheduled for removal in a specific upcoming version.

* **Pending deprecation warnings**, which mark code as being available but
 scheduled to be deprecated in an unknown future version. Projects should
 later transition these to full deprecation warnings.

You'll be creating classes for each type that identify your project and any
upcoming versions where deprecated code may be removed.

We recommend adding these to the ``<project_name>.deprecation`` module.

For example:

```python
from housekeeping import BasePendingRemovalWarning, BaseRemovedInWarning


class PendingRemovalInMyProjectWarning(BasePendingRemovalWarning):
   project = 'My Project'


class BaseRemovedInMyProjectWarning(BaseRemovedInWarning):
   project = 'My Project'


class RemovedInMyProject20Warning(BaseRemovedInMyProjectWarning):
   version = '2.0'


class RemovedInMyProject30Warning(BaseRemovedInMyProjectWarning):
   version = '3.0'

...
```


### Begin Deprecating Code

Housekeeping offers several deprecation helpers to deprecate code.

You can also call `.warn()` on your deprecation classes to warn about
deprecated code at any time.


#### Deprecating Functions

##### `@deprecate_non_keyword_only_args`

This decorator can help convert positional arguments to keyword-only arguments:

```python
from housekeeping import deprecate_non_keyword_only_args


@deprecate_non_keyword_only_args(RemovedInMyProject20Warning)
def add_abc(a, *, b, c=1):
    return a + b + c


add_abc(1, 2, 3)      # This will emit a deprecation warning.
add_abc(1, b=2, c=3)  # This will not.
````


##### `@func_deprecated`

This decorator marks a function as deprecated, or pending deprecation:

```python
from housekeeping import func_deprecated


@func_deprecated(RemovedInMyProject20Warning)
def my_func():
    ...


my_func()  # This will emit a deprecation warning.
```


##### `@func_moved`

This decorator marks a function as having moved elsewhere.

```python
from housekeeping import func_moved

from myproject.new_module import my_func as new_my_func


# This can be invoked with some special behavior:
@func_moved(RemovedInMyProject20Warning,
            new_func=new_my_func)
def my_func(a, b):
    new_my_func(a, b, True)


my_func()  # This will emit a deprecation warning.
```


##### `deprecated_arg_value`

This wraps values that, when accessed, emit a deprecation or pending
deprecation warning. It's useful for passing legacy data to callback handlers.

```python
from housekeeping import deprecated_arg_value


def callback_handler(username=None, user=None):
    user = get_user(username)  # This will emit a deprecation warning.
    user = get_user(user)      # This would not.


class User:
    ...

    def emit_did_thing(self):
        callback_handler(
            user=self,
            username=deprecated_arg_value(
                RemovedInMyProject20Warning,
                owner_name='User',
                value=self.username,
                old_name='username',
                new_name='user'))
```

#### Deprecating Classes

#### `ClassDeprecatedMixin`

This class mixin will emit warnings when you either instantiate or subclass
the class.

```python
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

# Nor will this.
class MyGrandChildClass(MyChildClass):
    pass
```


#### `ClassMovedMixin`

This class mixin will emit warnings when you either instantiate or subclass
the class, pointing you to a replacement class or import.

```python
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
```


#### Deprecating Modules

##### ``module_deprecated``

This function can be called within a module body to emit a warning when the
module is imported.

```python
from housekeeping import module_deprecated

from myproject.deprecation import RemovedInMyProject20Warning


module_deprecated(RemovedInMyProject20Warning, __name__)
```


##### ``module_moved``

This function can be called within a module body to emit a warning when the
module is imported, pointing the consumer to a replacement module. This is
useful when reorganizing the codebase and moving modules around.

```python
from housekeeping import module_moved

from myproject.deprecation import RemovedInMyProject20Warning
from myproject import newmodule


module_moved(RemovedInMyProject20Warning, __name__, newmodule.__name__)
```


Our Other Projects
------------------

* [Review Board](https://www.reviewboard.org) -
  Our free, open source, extensible code and document review tool.
* [Djblets](https://github.com/djblets/djblets/) -
  Our pack of Django utilities for datagrids, API, extensions, and more. Used
  by Review Board.
* [Review Bot](https://www.reviewboard.org/downloads/reviewbot/) -
  Automated code review for Review Board.

You can see more on [github.com/beanbaginc](https://github.com/beanbaginc) and
[github.com/reviewboard](https://github.com/reviewboard).
