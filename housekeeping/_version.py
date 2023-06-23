"""Basic version and package information."""

# The version of housekeeping.
#
# This is in the format of:
#
#   (Major, Minor, Micro, alpha/beta/rc/final, Release Number, Released)
#
VERSION = (1, 1, 0, 'final', 0, True)


def get_version_string() -> str:
    """Return the display version of Housekeeping.

    Returns:
        str:
        The display version.
    """
    major, minor, micro, tag, release_num, released = VERSION

    version = f'{major}.{minor}'

    if micro:
        version = f'{version}.{micro}'

    if tag != 'final':
        if tag == 'rc':
            version = f'{version} RC{release_num}'
        else:
            version = f'{version} {tag} {release_num}'

    if not is_release():
        version = f'{version} (dev)'

    return version


def get_package_version() -> str:
    """Return the package version of Housekeeping.

    Returns:
        str:
        The display version.
    """
    major, minor, micro, tag, release_num, released = VERSION

    version = f'{major}.{minor}'

    if micro:
        version = f'{version}.{micro}'

    if tag != 'final':
        if tag == 'alpha':
            tag = 'a'
        elif tag == 'beta':
            tag = 'b'

        version = f'{version}{tag}{release_num}'

    return version


def is_release() -> bool:
    """Return whether the package is released.

    Returns:
        bool:
        ``True`` if the package is a released build, or ``False`` if it is not.
    """
    return VERSION[5]


__version_info__ = VERSION[:-1]
__version__ = get_package_version()
