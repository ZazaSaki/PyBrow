import os
import dill
from types import FunctionType

## Stack of recovery files
stack = []

## Recover extention 
extention = ".pk"

## Files' path
name = "data/recover"

hold = "data/recover"

## Recovery Flag
# @note Is activated when an action breaks
recover_need = False


path_on_hold = ""

## Gets a path from the Last revovery file in the stack
# @returns path from the top of the stack
# @note Doesn't pop the item from the stack
def get_path()->str:
    global stack
    
    if len(stack) < 1:
        return None
    
    return stack[-1]

## @returns True if recover is needed or False if it doesn't
# @see recover_need
def get_recover()->bool:
    global recover_need
    return recover_need

## get all recover paths in order of creation  
def get_all_recover_path():
    global recover_need 

    files = [f for f in os.listdir('./data') if os.path.isfile(os.path.join('./data', f))]
    
    files.sort(key = lambda f : -os.path.getmtime(os.path.join('./data', f)))
    filtered = filter(lambda f : 'recover' in f, files) 
    filtered = map(lambda f : os.path.join('./data', f), filtered)
    filtered = list(filtered)
    
    for path in filtered:
        stack.append(path)

    recover_need =  len(stack)>0

## Sets recover_need to True
# @see recover_need
def activate_recover():
    global recover_need
    recover_need = True

## Sets recover_need to False
# @see recover_need
def deactivate_recover():
    global recover_need
    recover_need = False

## Creates a recover point to a function
# @param func function to insert 
# @return The path of the recover file
# @note the function is serialized and saved, 
# inserts the path of the saved file in the stack
# @warning some objects migth not be able to be serialized
def submit(func:FunctionType)->str:
    global stack
    hash = func.__hash__()

    path = put_on_hold_path(hash)
    

    file = open(path, "wb")
    dill.dump(func, file)
    file.close()

    stack.append(path)

    activate_recover()

    return path

## Recover a function from the top of the stack
# @param path   path of the file that contains the function
# @note         After recover the path is poped from the stack.
# @attention     If the function breaks in the midle of a recover 
# its not poped from the list
# @warning      Runs deactivate_recover() after recover
def recover(path:str):
    file = open(path, "rb")
    f = dill.load(file)
    
    file.close()
    del file
    
    f()

    clear(path)

## Recover all stack
# @note         cleans the stack
def full_recover():
    while not get_path() == None:
        recover(get_path())

## Removes a function from the stack
# @param path   path of the file that contains the function
def clear(path:str):
    global stack
    os.remove(path)
    stack.pop(stack.index(path))

    if get_path() == None:
        deactivate_recover()

## Generates a name for the recover file
# @param hash   hash code from the function
# @param i      *optional* num of iteration
# @note         This deals with repeat names 
# and assures no overwrites 
def put_on_hold_path(hash:int, i:int=0)->str:
    path_on_hold = hold + "_" + str(hash) + "_" + str(i) + extention
    
    if not os.path.exists(path_on_hold):
        return path_on_hold
    else:
        return put_on_hold_path(hash, i+1)
        
## Creates a recover point before runs a function and
# removes it if the function suceed
# @param func function to run with the recover system 
def run_with_recover(func:FunctionType):
    path = submit(func)

    func()

    clear(path)


#general
from General.general import *
from General.loadingBar import *

#Option Manager
from Drive.OptionManager import *

#database
from Drive.DataBase.DataManager import *
from Drive.DataBase.FacebookPageManager import *

#drive
from Drive.DataBase.DirtyCleanerBase import *
from Drive.docsUpdaterBase import *
from Drive.LockManager import *