#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
"""
    python script that cleans up by removing .pyc-files recursively
    inspired by solution found at:
    https://djangosnippets.org/snippets/899/

    to run, simply type:
    python cleanup.py
"""
def pyc_cleanup(directory, path):
    deleted = 0
    for filename in directory:
        if filename[-3:] == 'pyc':
            print(' - ' + filename)
            os.remove(path+os.sep+filename)
            deleted += 1
        elif os.path.isdir(path+os.sep+filename):
            deleted += pyc_cleanup(os.listdir(path+os.sep+filename), path+os.sep+filename)
    return deleted

if __name__ == '__main__':
    directory = os.listdir('.')
    print("Delete pyc files recursively in directory: " + os.getcwd())
    deleted = pyc_cleanup(directory, ".")
    print("Deleted", deleted, ".pyc files")
