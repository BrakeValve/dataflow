# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 10:23:38 2016

@author: SISQUAKE
"""
import os


def listFilePath(path):
    File = []
    Dir = []

    for (dirpath, dirnames, filenames) in os.walk(path):
        for name in filenames:
            tmp = os.path.join(dirpath, name)
            File.append({'path': tmp, 'name': name})
        for name in dirnames:
            tmp = os.path.join(dirpath, name)
            Dir.append({'path': tmp, 'name': name})
        break

    return {'file': File, 'dir': Dir}
