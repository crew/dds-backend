# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
# ***** BEGIN LICENCE BLOCK *****
#
# The Initial Developer of the Original Code is
# The Northeastern University CCIS Volunteer Systems Group
#
# Contributor(s):
#   Alex Lee <lee@ccs.neu.edu>
#
# ***** END LICENCE BLOCK *****

import os
import threading
import time


def module(file_path):
    """Returns the module name.
    >>> module('/a/b/c/xx.py')
    'c'
    """
    dir = os.path.dirname(file_path)
    dir_abs = os.path.abspath(dir)
    dir_norm = os.path.normpath(dir_abs)
    return dir_norm.split(os.sep)[-1]


def root(file_path):
    """Returns a 'lambda' that produces paths based on the given file_path.
    >>> x = root('/a/b/c/xx.py')
    >>> x('t')
    '/a/b/c/t'
    >>> x('t', 's')
    '/a/b/c/t/s'
    """
    dir = os.path.dirname(file_path)
    normpath = os.path.normpath
    join = os.path.join
    return (lambda *base: normpath(join(dir, *base)).replace('\\', '/'))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
