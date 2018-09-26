import os
from os import listdir
from os.path import isfile, join, abspath

DEFAULT_HASHES_AND_WORDLISTS_EXT = "txt"

hash_files = []

def getHashFiles():
    return hash_files

def findHashFiles(location):
    mypath = abspath(location)
    hashes = [ join(mypath, f) for f in listdir(mypath) if (isfile(join(location, f)) and f[f.rindex(".")+1:] == DEFAULT_HASHES_AND_WORDLISTS_EXT) ]
    return hashes