# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id$

import os

impl = os.getenv('INFRAE_SUBVERSION_IMPL', 'PYSVN')

if impl == 'PYSVN':
    try:
        # Try to use a native binding, use native SVN.
        import Native
        Recipe = Native.Recipe
        uninstall = Native.uninstall
    except:
        # Or if the binding is not present, use slow py.
        impl = 'PY'

if impl == 'PY':
    import Py
    Recipe = Py.Recipe
    uninstall = Py.uninstall

