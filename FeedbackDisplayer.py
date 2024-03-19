from typing import Dict, List

Dysplay = {}

def exists(name:str)->bool:
    return name in Dysplay

def get_checker(name:str)->List:
    separator = ['-----------','-----------']
    checker = [ separator ]
    if exists(name):
        for word in Dysplay[name]['Last']:
            item = Dysplay[name]['Last'][word]
            checker.append([[word,item]])
    
    return checker

def get_stack(name:str)->List:
    if exists(name):
        return reverse(Dysplay[name]['Stack'])
    else:
        return get_checker(name)

def reverse(stack):
    rev = []
    for item in stack:
        rev.insert(len(stack)-1, item)
    
    return rev

def add_checker(name:str, id:str, val)->Dict:
    info = {id : val}
    Dysplay[name] = {'Last' : info, 'Stack' : [info]}

def update_checker(name:str, id:str, val:str)->bool:
    global Dysplay
    if exists(name):
        Dysplay[name]['Last'][id] = val
        for item in get_checker(name):
            Dysplay[name]['Stack'].append(item)
    else : 
        add_checker(name, id, val)

def remove_value_from(name:str, id:str):
    global Dysplay
    if exists(name):
        if id in Dysplay[name]['Last']:
            Dysplay[name]['Last'].pop(id)

def remove_all_contaning_id_from(name, id):
    if exists(name): 
        remove_list = []
        for word in Dysplay[name]['Last']:
            if id in word :
               remove_list.append(word) 

        for word in remove_list:
            remove_value_from(name, word)

def clean_display(name):
    if exists(name):
        Dysplay[name]['Last']={}

def update_all_checkers(id, val):
    for name in  Dysplay:
        update_checker(name, id, val)

def remove_from_all(id):
    for name in Dysplay:
        remove_value_from(name, id)

# update_checker('checker1', 'val1', 66)
# update_checker('checker1', 'val2', 33)
# update_checker('checker1', 'val1', 2)
# update_checker('checker2', 'val1', 2)
# update_checker('checker2', 'val2', 3)
# remove_value_from('checker2', 'val2')
# remove_value_from('checker2', 'val2')
# clean_display('checker1')
# update_all_checkers('new thing', 'all th same')
# remove_from_all('new thing')
# remove_from_all('new thing')

True
