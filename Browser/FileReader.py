import json
from os import read
from pprint import pprint as pp
from typing import List

# load code
scrollFile = open('./Browser/scroll.jes').read()

# load updated xpaths
code = (json.load(open('./Browser/browser_data/workSheet.json')))["page"]["list"]


def loadScroller():
    # update code with updated xpaths
    code = replace("mainPath", "main", scrollFile)
    code = replace("scrollablePath", "scrollable", code, main="main")
    code = replace("listPath", "List", code, main="main")
    code = replace("reactListPath", "reactList", code, main="main")

    # returning updated code
    return code

# code injecter


def replace(term, name, file, main=""):
    term = "<<"+term+">>"
    if main != "":
        main = code[main]
    inject = "\"" + main + code[name] + "\""
    return file.replace(term, inject)

# load list of post

## Reads a File called PostList.txt and extracts a list 
# of links from it
# @return List of links
def readList()->List[str]:
    try:
        file = open("PostList.txt", 'r')
        return file.readlines()
    except:
        return []
