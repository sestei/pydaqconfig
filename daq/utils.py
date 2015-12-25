#!/usr/bin/env python
#
# === PYDAQCONFIG ===
#
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import hashlib

def get_filename_without_ext(filename):
    import os
    return os.path.splitext(os.path.basename(filename))[0]

def get_env_variable(variable):
    from PyQt4.QtCore import QProcessEnvironment
    env = QProcessEnvironment.systemEnvironment()
    if env.contains(variable):
        return str(env.value(variable))
    else:
        return None

def get_md5_checksum(obj):
    if type(obj) is str:    # it's the name of a file
        content = open(obj, 'rb').read()
    else:                   # file passed in
        idx = obj.tell()
        obj.seek(0)
        content = obj.read()
        obj.seek(idx)
    return hashlib.md5(content).hexdigest()
