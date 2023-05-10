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
