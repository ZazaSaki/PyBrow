import time
import json
from types import FunctionType
from typing import Dict, List, Tuple
from gspread.exceptions import APIError

from FeedbackDisplayer import remove_from_all, remove_value_from, update_all_checkers, update_checker
from .loadingBar import closeCounter, openCounter, updateCounter

## Alphabet to convert numeric ranges in A1 Notation
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# -------------------------------------------------------------------
# general function

## Runs a function and waits for the server in case of time out
#
# @param task       function to run
# @param message    message to display while waiting
# @return           return the same as the the task
# @attention        This is build to be used with gspread requests
def run_with_timeout_checker(task:FunctionType, message:str = "do task"):
    while True : 
        try:
            return task()
        except APIError as err:
            if time_out_checker(err):
                ExplicitWait("Waiting for api to " + message + " : ")
            else :
                raise err

## Checks if an exception is a timeout exception
# @param err        exception to be checked
# @return           True if is a timeout exception
def time_out_checker(err:Exception):
    rep = err.response
    args = err.args

    if args[0]["code"] == 429:
        return True
    
    return False


## Splits a list of contacts in 2 lists, one with clean links, 
# other with dirty links
#
# @param NameLinkList   List of contacts
# @return               tuple of lists (clean, dirty)
def cleanTable(NameLinkList:List)->Tuple:
    primary = []
    secondary = []

    for item in NameLinkList[1:]:

        link = linkparse(item[1])

        try:
            number = link[link.rindex("/")+1:]
        except:
            #print(item[0] + "//" + link + "//" + item[0] + "//" + "not addded")
            continue

        if number.isdigit():
            secondary.append([item[0], link])
        else:
            primary.append([item[0], link])

    return primary, secondary


## Saves a dictionary in data directory
#
# @param name           name of the file
# @param fileInfo       file's information 
def saveJSON(name:str, fileInfo:Dict):
    file = open("data/"+name+".json", "w")
    data = {"data": fileInfo}

    file.write("")

    json.dump(data, file)
    file.close()
    pass

## Recieves two list, and filters the not included values
# of the first list according to the second list
#
# @param newList        list to filter 
# @param baseList       base list to filter with
# @param offset         *optiona* index of the id
# @return               List of not included items from \a newlist
def getNotIncluded(newList:List, baseList:List, offset:int = 0)->List:
    # inicializating screen counter
    #openCounter("filtering", len(newList))

    # filter values
    i = 0
    filtered = []
    for link in newList:

        if not link[offset] in baseList:
            filtered.append(link)

        i += 1

        # update screen counter
        # updateCounter(i)
        continue

    # closing used counter
    # closeCounter()
    return filtered

## Converts a column id in A1 Notation
# @param num        column id
# @return           A1 Notation of the given id *(2 = 'B', 26 = 'AA')*
def get_col_by_num(num:int)->str:
    if num >= len(Alpha):
        letters_num = int(num / len(Alpha))
        last_letter = num % len(Alpha)
        return get_col_by_num(letters_num-1) + Alpha[last_letter]

    return Alpha[num]


## Stops for a given number of seconds
#
# @param sec        number of seconds to wait
def wait_secs(sec:int=1):
    for i in range(sec):
        time.sleep(1)

## Stops the program for a given number of seconds
# and meanwhile displays a message
#
# @param message         message to display while waiting
# @param secs            number of seconds to wait  *defaul value = 30*
def ExplicitWait(message:str="Waiting for api to respond", secs:int=30):
    
    update_checker('general', 'wait_message', message)
    openCounter(message, secs)
    for x in range(secs):
        update_checker('general', 'wait_time', f'{x}/{secs}')
        updateCounter(x+1)
        wait_secs(1)
    remove_value_from('general', 'wait_message')
    remove_value_from('general', 'wait_time')
    closeCounter()

## Cleans a facebook profile link and assures that 
# it is in the shortest version possible
#
# @param link       facebook profile link to clean 
# @return           clean link
def linkparse(link:str)->str:
    if link == "":
        return link

    if "business.facebook.com/to" in link:
        link = link.replace("business.facebook.com/to", "www.facebook.com")

    if "business.facebook.com" in link:
        link = link.replace("business.facebook.com", "www.facebook.com")

    temp = ""
    splitter = ["__tn__", "__cft__"]
    sp = ""

    # search for existance of spliters
    for splt in splitter:
        # setting the founded spliter
        if splt in link:
            sp = splt
            break

    # return link if as no splitters (is clean) (stop recursion)
    if sp == "":
        if link[-1] == "/":
            return link[0:-1]
        return link

    # taking the clean part
    temp = link.split(sp)[0]

    # recursive cleaning
    temp = linkparse(temp)

    # taking the last character if is a splitter as well("?" or "&")
    last = temp[-1]
    if last == "?" or last == "&":
        return temp[0:-1]

    return temp

## Applies linkparse() to a list of links
# @param list       list of links
# @return           clean list of link
def listparse(list:List)->List:
    for i in range(len(list)):
        list[i] = [linkparse(list[i])]
    return list

## Forget this one
def containsPartsOf(group, word, patience=300):
    i = 0
    for item in group:
        i += 0
        if word in item:
            return True
        if i >= patience:
            return False

    return False
# -------------------------------------------------------------

## Converts a list of rows into a list of columns
# @param ListOfList     rows' list to convert
# @return               List of columns 
def listOfRowsToListOfCols(ListOfList:List)->List:
    comp = len(ListOfList[1])
    colFormat = []

    for i in range(comp):
        colFormat.append([])

    for row in ListOfList:
        col = 0
        for cell in row:
            colFormat[col].append(cell)

            col += 1

    return colFormat


## Converts dictionary of List of contacts {page : [[profile link, name] , ...] , ...}
# in a dictionary of list of contacts with hyperlinks {page : [[profile link, Hyperlink(name)] , ...] , ...}
# 
# @param dictionary             dictionary of List of contacts
# @return                       dictionary of List of contacts with hyperlinks
def getAplicableCleanList(dictionary:Dict)->Dict:
    for word in dictionary:
        dictionary[word] = list(map(lambda i: [i[0],'=HYPERLINK("'+i[0]+'", "'+ i[1] +'")'] + i[2:], dictionary[word]))

    return dictionary
