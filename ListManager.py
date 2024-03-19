import os
from typing import List
from asyncore import read, write

dir = './'
ext = '.txt'

## get all recover paths in order of creation  
def get_all_paths_lists()->List:
    global dir

    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    
    files.sort(key = lambda f : -os.path.getmtime(os.path.join(dir, f)))
    filtered = filter(lambda f : '.txt' in f, files)
    filtered = map(lambda f : os.path.join(dir, f), filtered)
    filtered = list(filtered)
    
    return filtered

def get_list_from_index(index):
    try:
        return read_a_list(get_all_paths_lists()[index])
    except:
        return 'invalid list'

def get_path_by_index(index):
    try:
        return get_all_paths_lists()
    except:
        return None

def read_a_list(path:str)->str:
    file = open(path, 'r')
    res = ''.join(file.readlines())

    file.close()

    return res

def read_a_list_as_array(path:str)->List:
    file = open(path, 'r')
    res = file.readlines()

    file.close()

    return res


def get_name_by_path(path):
    global dir, ext
    name = path.split(dir)[1]
    name = name.split(ext)[0]

    return name

def get_path_by_name(name):
    global dir, ext
    file_path = dir+name+ext
    if os.path.exists(file_path):
        return file_path
    else :
        return None

def save_a_list(name:str, content:str):
    global dir, ext

    path = get_path_by_name(name)

    if path == None : 
        return

    f = open((path), 'w')
    
    f.write(content)
    f.close()

def create_new_list(name):
    global dir, ext

    path = dir + name + ext

    if path == None : 
        return

    f = open((path), 'w')
    
    f.write('')
    f.close()


def delete_list(name):
    path = get_path_by_name(name)

    if path == None : 
        return

    os.remove(path)
