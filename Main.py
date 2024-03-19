from getpass import getpass
import json
from types import FunctionType
from typing import Dict, List
from Browser.FileReader import readList
from Drive.DataBase.DataManager import RemoveDuplicateds
from Drive.DataBase.FacebookPageManager import addPage, getAllPagesNames, SearchPage, getAllPagesSheet, getPageByLink, getPageByName, getPageBySheet, updateLink, updateSheet
from Drive.DataBase.DirtyCleanerBase import cleanDirtyLinks
from Drive.LossManager import full_recover, run_with_recover
from Drive.docsUpdaterBase import FullUpdate, UpdateAllQuery, UpdateAllVerifyers, VerifyUpdate, connection, fix_all_sheets, refreshLinksSheet, smartLockAll, update_all, updateNewLinksSheet, updateNewLinksSheetByLink, smartLockAll
from Browser.Read import checkLogin, forgetFacebookAccount, searchForlikes
from pprint import pprint

from Drive.OptionManager import add_email, code, email, remove_email, set_code_col, set_names_col
from FeedbackDisplayer import clean_display, update_checker

from General.general import ExplicitWait, run_with_timeout_checker, saveJSON
from General.loadingBar import show
from Drive.LossManager import get_recover, get_path ,recover

# credentials
username = ""
password = ""

ans = True
# while True:
#     ans = input("Do you have 2 factor authentication?(Y or n)").upper()

#     if (ans in "YES") or (ans in "NO"):
#         ans = ans in "YES"
#         break
#     elif len(ans) == 0:
#         ans = True
#     else:
#         print("invalid answer")

# checkLogin(towFactor=ans)

# load post
post = readList()
#post = ["https://www.facebook.com/DisciplesdeJesusChristenIledeFrance/photos/a.1879839242048518/4990763394289405/"]

## Full update routine, verifies, 
# fixes and pulls information from the google sheets, 
# and verifies the updated data
#
# @see UpdateFromDrive, VerifyDataBase, VerifyIgnoreLinks
# @note isolar fixer numa funcao a parte
def UpdateDataBase():
    update_checker('update', 'action', 'update code')
    update_all()
    ExplicitWait("Wait code to run", 30)
    clean_display('update')

    update_checker('update', 'action', 'fixing sheets')
    fix_all_sheets()
    ExplicitWait("Wait code to run", 30)
    clean_display('update')
    
    update_checker('update', 'action', 'fixing sheets')
    fix_all_sheets()
    clean_display('update')

    update_checker('update', 'action', 'update query')
    UpdateAllQuery()
    ExplicitWait("Wait for server to processe the request", 60)
    clean_display('update')

    quick_update()

def quick_update():
    update_checker('update', 'action', 'pull values from drive')
    UpdateFromDrive()
    clean_display('update')
    
    update_checker('update', 'action', 'Verify data base')
    VerifyDataBase()
    clean_display('update')

    update_checker('update', 'action', 'Update founded')
    VerifyIgnoreLinks()
    clean_display('update')


## Pull information from google api
def UpdateFromDrive():
    update_checker('update', 'action', 'pull values from drive')
    FullUpdate()
    print("Updated")
    
    update_checker('update', 'action', 'pull values from drive')
    VerifyUpdate()
    print("Update verified")

## Refresh the google sheets
def VerifyIgnoreLinks():
    update_checker('update', 'action', 'Update founded')
    refreshLinksSheet()
    print("new links vertifyed")

## Verify Database, clean invalid links
def VerifyDataBase():
    update_checker('update', 'action', 'Verify data base')
    cleanDirtyLinks()
    #RemoveDuplicateds()
    print("Database verified")

## Verify Data Base, clean invalid links
# and resolve duplicates
# @attention Slow
# @see VerifyDataBase, feed_likes
def FullVerify():
    VerifyDataBase()
    RemoveDuplicateds()
    VerifyIgnoreLinks()
    clean_display('update')

    pass

## Reads a list of posts and feeds the sheets
# with non-negative reaction
# @param post       list of posts
# @attention        Slow
# @see              feed_likes
def UpdateLikes(post:List=post):
    # gets all the profiles
    like_list, done, failed, timeout_list = searchForlikes(post)

    saveJSON("likeList", like_list)

    # feedback starts
    print("done :")
    pprint(done)

    print("\n failed:")
    pprint(failed)

    print("\n timeout list:")
    pprint(timeout_list)

    run_with_recover(lambda : feed_likes(like_list))

## Feeds the sheets with non-negative reaction
#
# @param like_list  dictionary of profiles
#                   organized by page
# @see              UpdateLikes
def feed_likes(like_list:Dict):
    updates_failed = []
    # update data base
    for group in like_list:
        
        try:
            spreadSheetLink = getPageByLink(group)[0][2]
        except:
            print(group, end= ' : ')
            print('failed')

        try :
            updateNewLinksSheetByLink(spreadSheetLink, profiles=like_list[group])
        except :
            updates_failed.append(spreadSheetLink)

## Allows the user to pick up a page
# @return Page item from database
def PagePicker()->List:
    possible = SearchPage(input("search : "))
    print()
    if len(possible)<1:
        return ""
    i = 0
    for elem in possible:
        i += 1
        print(i, end = " ")
        print(elem[0])
    
    print()
    input("Choose : ")
    print()
    return possible[i-1][0]

## Displays all information of pages from a given list of pages
# @param pageList   list of pages
def PageDisplayer(pageList:List):
    if len(pageList)<1: print("No page Founded")
    for page in pageList:
        print("Name :" + page[0])
        print("Link :" + page[1])
        print("Sheet :" + page[2])
        print()

## Executes a given function and waits 
# for user input to continue
# @param function   function to execute
def doAndWait(function:FunctionType):
    print("\n")
    function()
    getpass("\n\nPress Enter")

def get_input_vals():
    out = []
    txt = "111"
    while not txt == "enter":
        out.append(input("(write \"enter\" to continue)\n email:"))


## Displays a menu of a given dictionary of option, 
# and allow the user to pick up an option and execute it
# @param defList        list of option
# @param title          title to be displayed
# @see printMenu
def menu(defList:Dict, title:str="Menu"):
    defList["exit"]= "exit"

    

    while True:
        if get_recover():
            defList["recover"] = full_recover
        else:
            if "recover" in defList:
                defList.pop("recover")

        try:
            choosen = printMenu(defList, title=title)
            if choosen == "exit":
                break

        except ValueError:
            print("invalid option")
        else:
            try:
                defList[choosen]()
            except Exception as e:
                print(e)
                e.with_traceback
                #e.__traceback__.tb_frame.
                print("Operation falied")

    pass

## Displays a menu of a given dictionary of option
# @param defList        list of option
# @param title          title to be displayed
# @see menu
def printMenu(optionsMenu:Dict, title:str="Menu"):
    print("\n\n" + title + " :")
    i = 0
    cache = []
    for value in optionsMenu:
        i += 1
        cache.append(value)
        print("     " + str(i) + " " + value)

    try:
        return cache[(int(input("Chose : "))-1)]
    except IndexError:
        raise ValueError

## Update Options
updateMenu = {"Update": UpdateDataBase,
              "Verify Database": VerifyDataBase,
              "Verify new links": VerifyIgnoreLinks,
              "Fix Broken Pages": fix_all_sheets,
              "Remove Duplicateds" : RemoveDuplicateds,
              "Lock All" : lambda : smartLockAll(email())}

## Pages' search engine manager 
searchPageMenu = {"All Names" : lambda : doAndWait(lambda : pprint(getAllPagesNames())),
                  "All Sheets" : lambda : doAndWait(lambda : pprint(getAllPagesSheet())),
                  "Search Page" : lambda : doAndWait(lambda : PageDisplayer(getPageByName(PagePicker()))),
                  "Search Page By Link" : lambda : doAndWait(lambda : PageDisplayer(getPageByLink(input("Link :")))),
                  "Search Page By Sheet" : lambda : doAndWait(lambda : PageDisplayer(getPageBySheet(input("Sheet :")))),
                  }

## Page Manager option
pagesMenu = {"Search " : lambda : menu(searchPageMenu, "Search"),
             "Add Page" : lambda : addPage(input("Name :"), input("Link :"), input("Sheet Link :")),
             "Update Link" : lambda : updateLink(PagePicker(), input("Link :")),
             "Update Google Sheet" : lambda : updateSheet(PagePicker(), input("Google Sheet :")),
             }

# Facebook Reader Menu
readMenu = {"Read Likes From Post's File": UpdateLikes,
            "Read Likes From Post": lambda: UpdateLikes(post=[input("Link:")]),
            }

## Inner Settings Menu
option_menu = {"Change Links Column" : lambda : set_code_col(int(input("Choose a column (0=A, 1=B, C=3 ...) : "))),
               "Change Names Column" : lambda : set_names_col(int(input("Choose a column (0=A, 1=B, C=3 ...) : "))),
               "Show emails" : lambda : doAndWait(lambda : print(email())),
               "Add emails" : lambda : add_email(input("email:")),
               "Remove emails" : lambda : remove_email(input("email:")),
            }

## Main Menu
defList = {"Read" : lambda : menu(readMenu, "Read"),
           "Pages" : lambda : menu(pagesMenu, "Pages"),
           "DataBase": lambda: menu(updateMenu, "DataBase"),
           "Options" : lambda: menu(option_menu, "Options"),
           "Forget Facebook Account": forgetFacebookAccount,
           "Reconect" : connection,
           }

#menu(defList)
