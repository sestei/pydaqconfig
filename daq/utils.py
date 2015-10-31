#!/usr/bin/env python

def get_model_name(filename):
    import os
    return os.path.splitext(os.path.basename(filename))[0]
