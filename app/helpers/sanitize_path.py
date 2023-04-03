import os.path
from pathlib import Path

def sanitize_path(path: str):
    """
    Sanitize a path against directory traversals

    Based on https://stackoverflow.com/questions/13939120/sanitizing-a-file-path-in-python.

    Copied from: https://gist.github.com/kousu/bf5610187b608d79d415b1436091ab2d.
    >>> sanitize_path('../test')
    'test'
    >>> sanitize_path('../../test')
    'test'
    >>> sanitize_path('../../abc/../test')
    'test'
    >>> sanitize_path('../../abc/../test/fixtures')
    'test/fixtures'
    >>> sanitize_path('../../abc/../.test/fixtures')
    '.test/fixtures'
    >>> sanitize_path('/test/foo')
    'test/foo'
    >>> sanitize_path('./test/bar')
    'test/bar'
    >>> sanitize_path('.test/baz')
    '.test/baz'
    >>> sanitize_path('qux')
    'qux'
    """
    # - pretending to chroot to the current directory
    # - cancelling all redundant paths (/.. = /)
    # - making the path relative
    # asdf/sdaf/asdf
    return Path(os.path.relpath(os.path.join("/", path), "/")).stem
