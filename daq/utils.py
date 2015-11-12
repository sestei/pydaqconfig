#!/usr/bin/env python

def get_filename_without_ext(filename):
    import os
    return os.path.splitext(os.path.basename(filename))[0]
