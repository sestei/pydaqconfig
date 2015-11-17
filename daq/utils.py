#!/usr/bin/env python

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