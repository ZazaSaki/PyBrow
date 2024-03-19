from types import FunctionType
from typing import List, Tuple
import gspread
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from oauth2client.service_account import ServiceAccountCredentials

from FeedbackDisplayer import remove_value_from, update_checker


## scope
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

## credencials
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

## Api Client Object
client_session = gspread.authorize(creds)

del creds, scope

from itertools import repeat
import json
from os import name, write
from re import search


from gspread.exceptions import APIError, CellNotFound, WorksheetNotFound, SpreadsheetNotFound

from pprint import pprint as pp

from Drive.DataBase.FacebookPageManager import getAllPagesSheet
from .DataBase.DataManager import filterList, insertInvalidProfiles, insertProfileNameNLinks
from General.general import ExplicitWait, get_col_by_num, getNotIncluded, listparse, run_with_timeout_checker, saveJSON, cleanTable, time_out_checker
from General.loadingBar import closeCounter, openCounter, updateCounter
from Drive.OptionManager import code, email, get_all_likes_name, get_highest_column, get_ignore_titles, get_ignore_words, get_new_profiles_name, get_query, names, code_col, names_col, code_title, names_title, script
from Drive.LossManager import submit, clear
from Drive.LockManager import getLockedRange, lockLinksCol, lockRange, lockSheet

## Refreshes the connection with *Google Api*
def connection():
    global client_session
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client_session = gspread.authorize(creds)
    
## Applies a given function to every non ignored worksheet.  
# @param funtion    function to be executed 
# @param args       ((*opcional*)) extra arguments need a part from the worksheet in array format
#
#
# @warning *The first argument of this* **function** **Need** *to be the* **worksheet object**
#
# ###Consider the hypothetical scenario
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.py
# def foo(worksheet):
#     return worksheet
#   
# def foo_with_more_args(worksheet, arg1, arg2):
#     worksheet.do_something(arg1, arg2)
#     return worksheet
#
# #utilization
# do_to_all(foo)
# do_to_all(foo_with_more_args, [arg1, arg2])
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
def do_to_all(function: FunctionType, args:List = None):
    
    validSheetsLinks = getAllPagesSheet()
    
    if not args == None:
        args.insert(0, "worksheet")
    else:
        args=["worksheet"]
    
    for sheetLink in validSheetsLinks:
        try:
            sheet = getSheetByLink(sheetLink)
        except:
            print('invalid Link : ' + sheetLink)
            continue
        
        for worksheet in sheet:
            args[0]=worksheet
            function(*args)


## Applies a given function to every spreadsheet.   
# @param funtion    function to be executed 
# @param args       ((*opcional*)) extra arguments need a part from the spreadsheet in array format
#
#
# @warning *The first argument of this* **function** **Need** *to be the* **spreadsheet object**
#
# ###Consider the hypothetical scenario
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.py
# def foo(spreadsheet):
#     return spreadsheet
#   
# def foo_with_more_args(spreadsheet, arg1, arg2):
#     spreadsheet.do_something(arg1, arg2)
#     return spreadsheet
#
# #utilization
# do_to_all_spreadsheets(foo)
# do_to_all_spreadsheets(foo_with_more_args, [arg1, arg2])
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def do_to_all_spreadsheets(function : FunctionType, args:List = None):
    validSheetsLinks = getAllPagesSheet()
    
    if not args == None:
        args.insert(0, "worksheet")
    else:
        args=["worksheet"]
    
    for sheetLink in validSheetsLinks:
        try:
            sheet = getSheetByLink(sheetLink)
        except:
            print('invalid Link : ' + sheetLink)
            continue

        args[0]=sheet
        function(*args)


## Insert a list of given values into a given worksheet   
# @param profiles       the list of values to insert 
# @param sheet          worksheet to insert the values in
# @param col            column to start to insert the values in (*default value = 1, start counting on 1, ids are unique*)
# @param offset         index in the <profiles>, that has the ids to look up on (*deafault value = 0, start counting on 0*)
#
#
#
# ###Consider the hypothetical scenario
# \image html preInsertBoard.PNG
# Aplaying this code :
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.py
# 
# list_to_insert = [
#     ['row1', 'name', 'id1', 'age'], 
#     ['row2', 'name', 'id2', 'age'],
#     ['row3', 'name', 'id3', 'age']
# ]
#
# spreadsheet = client_session.open("spread")
#
# worksheet = spreadsheet.worksheet("sheet")
#
# #utilization
# insertProfiles(list_to_insert, worksheet, offset = 2)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# the output would be:
# \image html InsertBoard.PNG
# The *row* with \a "id2" is not reinserted once we already have it in the sheet, 
# and the offset is setted to lookup to that index 
def insertProfiles(profiles:List, sheet:Worksheet, col:int = 1, offset:int = 0):

    # check empty list exception
    if len(profiles) < 1:
        print("list is empty")
        update_checker('update', 'cells.readed', 'list is empty')
        return

    startCol = get_col_by_num(col-1)
    endCol = get_col_by_num(len(profiles[0])-2+col)

    ## filter values
    filtered, last = getNotIncludedByCol(
        profiles, col, sheet, offset=offset)

    # check lack of new values exception
    if len(filtered) == 0:
        print("no new profiles founded")
        update_checker('update', 'cells.readed', 'no values founded')
        return

    ## calculate positions
    start = last+1
    end = last+len(filtered)+1

    pp(len(filtered))
    pp(startCol + str(start) + ':' + endCol + str(end))

    ## setting the location
    location = startCol + str(start) + ':' + endCol + str(end)

    ## updating
    try :
        run_with_timeout_checker(lambda : sheet.update(location, filtered, raw = False), "update info")
    except APIError:
        sheet.add_rows(1)
        run_with_timeout_checker(lambda : sheet.update(location, filtered, raw = False), "update info")
    
    print(str(len(filtered)) + "/" + str(len(profiles)) + "update")
    update_checker('update', 'cells.readed', str(len(filtered)) + "/" + str(len(profiles)) + "update")

    pass


## Validate a sheet based on the names and expressions given by OptionManager.py . 
# @param        worksheet worksheet to validate
# @return       \a boolean : \a TRUE if is valid our \a FALSE if is invalid
#
# @see OptionManager.get_ignore_titles, OptionManager.get_ignore_words
def validate(worksheet:Worksheet) -> bool:
    if worksheet.title.lower() in get_ignore_titles():
            return False

    for ign in  get_ignore_words():
        if ign in worksheet.title.lower():
            return False

    return True

## Rebuild a worksheet based on a given \a spreadsheet's url and a given Returns a \textit{worksheet}.
# @param url            url of the spreadsheet that contains the wanted worksheet
# @param title          title of the wanted worksheet
# @return               \a worksheet 
def rebuild_sheet(url : str, title : str)->Worksheet:
    return getSheetByLink(url).worksheet(title)

## Reset a sheet based on a *New profiles links' sheet*
# @param sheet          worksheet to reset
# @warning              **DO NOT USE** unless it is used on a *New profiles links' sheet*.
def resetPage(sheet:Worksheet):
    run_with_timeout_checker(lambda : sheet.clear(), "clean sheet")
    run_with_timeout_checker(lambda : sheet.update("A1:D1", [["Links", "Names", "Post", "React"]]), "write headers")

## Get not included values of a given worksheet from a given list of values 
# and also filter the not included values from the intern database 
#   
# @param profiles       the list to filter 
# @param sheet          worksheet to filter with
# @param col            column to start to insert the values (*default value = 1, start counting on 1, ids are unique*)
# @param offset         index in the <profiles>, that has the ids to compare (*deafault value = 0, start counting on 0*)
#
# @return List of filtered values
#
# ### Assuming we have the next worksheet named \a "sheet" from a spreadsheet named \a "spread":
# \image html preInsertBoard.PNG
# Aplaying this code :
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.py
# 
# list_to_insert = [
#     ['row1', 'name', 'id1', 'age'], 
#     ['row2', 'name', 'id2', 'age'],
#     ['row3', 'name', 'id3', 'age']
# ]
#
# spreadsheet = client_session.open("spread")
#
# worksheet = spreadsheet.worksheet("sheet")
#
# #utilization
# getNotIncludedByCol(list_to_insert, worksheet, offset = 2)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# the output would be:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.py
# [
#     ['row1', 'name', 'id1', 'age'],
#     ['row3', 'name', 'id3', 'age']
# ]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Unless the data base already had the \a "id1" and \a "id3", 
# in that case the contained \a ids in data base would be removed.
# 
# @see DataManager.filterList
def getNotIncludedByCol(profiles:List, col:int, sheet:Worksheet, offset:int = 0)-> tuple[List, int]:
    # calculate Start End Cells
    previous = run_with_timeout_checker(lambda : sheet.col_values(col+offset), "get previous values from column")

    last = len(previous)
    temp = filterList(profiles, offset=offset)

    return getNotIncluded(temp, previous, offset=offset), last

## Get info from a given worksheet the names and profiles according to the option given by the OptionManager.
# 
# @param sheet          worksheet to get values from
# @note                 It is used to extract information from *All Likes*' sheets.
# @return               List of filtered values to insert **[["name", "profile"]]**
def getProfilesTable(sheet:Worksheet)->List:
    names = run_with_timeout_checker(lambda : sheet.col_values(names_col("number")), "get names column")
    links = run_with_timeout_checker(lambda : sheet.col_values(code_col("number")), "get links column")

    # pp(links[0:10])

    table = list(map(lambda a, b: [a, b], names, links))
    
    return cleanTable(table)

## Get the column title from a given worksheet and a given col.
# 
# @param worksheet  worksheet to get value from.
# @param col        col number.
# @return           the cell value in *formula* format
def get_cols_title(worksheet:Worksheet, col:int)->str:
    cell = get_col_by_num(col) + '1'
    while True:
        try:
            command = run_with_timeout_checker(
                lambda : worksheet.acell(
                    cell, value_render_option='FORMULA').value,
                "get column's title"
            )
            break
        except gspread.exceptions.APIError as err:
            args = err.args
            
            if args[0]["code"] == 400:
                print("Cell not found", end = ": ")
                return ""
            
    return command


## @param link   link of the spreadsheet.
# @return       the *spreadsheet object* from a given link.
def getSheetByLink(link:str)->Spreadsheet:
    return run_with_timeout_checker(lambda : client_session.open_by_url(link), "get sheet")


## Update all the *New Profiles From Ads*' worksheets
# @see updateNewLinksSheetByLink
def refreshLinksSheet():
    spreadsheetList = getAllPagesSheet()
    
    for sheet in spreadsheetList:
        updateNewLinksSheetByLink(sheet, profiles=[])


## Update the *Data Base* based on a given worksheet
# @param worksheet      worksheet to pull data from
# @note                 It's used to download *All Likes*' sheets' information to the *Data base*.
# It pull information according to the settings defined in OptionManager
def UpdateListsInDataBase(sheet:Worksheet):
    primary, secondary = getProfilesTable(sheet)
    print(insertProfileNameNLinks(primary))
    print(insertInvalidProfiles(secondary))


## Update the *New Profiles From Ads*' worksheets from a given worksheet
# if given, can insert new contacts on it
# @param sheet          worksheet to update
# @param profiles       (*opcional*) new profiles to insert if intended
# 
# @warning              **DO NOT USE** unless it's used with a *New Profiles From Ads*' worksheet
# 
# @warning              If the *New Profiles From Ads*' worksheet 
#                       **doesn't exist** the program will raise an exeption
def updateNewLinksSheet(sheet:Worksheet, profiles:List = []):
    url = sheet.spreadsheet.url
    title = sheet.title
    PostsAdresses = {}
    
    page = run_with_timeout_checker(lambda : rebuild_sheet(url, title).get_all_values(value_render_option='FORMULA')[1:], "get all values")

    if len(profiles)> 0:
        
        if len(profiles[0])>2 : 
            for item in profiles:
                PostsAdresses[item[0]] = item[2]


            for person in page : 
                post = PostsAdresses.get(person[0])
                

                if not post :
                    post = ''

                if len(person)>= 3 :
                    if len(person) >= 4:
                        if not 'facebook.com/' in person[2]:
                            person[3] = person[2]+person[3]
                        
                    else:
                        if not 'facebook.com/' in person[2]:
                            person.append(person[2])
                        else :
                            person.append('')
                    
                    if (not post == '') and (not 'facebook.com/' in person[2]):
                        person[2] = post

                    elif not 'facebook.com/' in person[2]:
                        person[2] = post
                else:
                    person.append(post)

    pageUpdater = lambda : run_with_timeout_checker(lambda : insertProfiles(page, sheet, col=1), "insert previous profiles")
    
    path = submit(lambda : run_with_timeout_checker(lambda : insertProfiles(page, rebuild_sheet(url, title), col=1), "insert previous profiles"))
    
    resetPage(sheet)

    pageUpdater()
    clear(path)
    
    run_with_timeout_checker(lambda : insertProfiles(profiles, sheet, col=1), "insert profiles")

## Update the *New Profiles From Ads*' worksheet contaibed in a given spreadsheet
# if given, can insert new contacts on it
# @param Link          spreadsheet's link to update
# @param profiles      (*opcional*) new profiles to insert if intended
# 
# @note                If the *New Profiles From Ads*' worksheet doesn't exist, 
#                      one will be autogenerated 
# @see                 updateNewLinksSheet, OptionManager.get_new_profiles_name
def updateNewLinksSheetByLink(Link:str, profiles:List = []):
    
    try:
        spreadsheet = getSheetByLink(Link)
        update_checker('update', 'spreadsheet.title', spreadsheet.title)
    except:
        spreadsheet = ""
        print('{Link} failed')

    
    sheet = ""
    
    
    try:
        sheet = run_with_timeout_checker(lambda : spreadsheet.worksheet(get_new_profiles_name()), "get New Profiles From Ads")
    except gspread.exceptions.WorksheetNotFound:
        sheet = run_with_timeout_checker(lambda : spreadsheet.add_worksheet(get_new_profiles_name(), 10, 4), "create New Profiles From Ads")
        lockRange(sheet, "A:B", email())
    except :
        print("Not reachable : " + Link)
        update_checker('update', 'update', 'failed')
        return False

    if sheet == "" :
        print("Not reachable : " + Link)
        update_checker('update', 'update', 'failed')
        return False
    update_checker('update', 'worksheet.title', sheet.title)
    updateNewLinksSheet(sheet=sheet, profiles=profiles)
    update_checker('update', 'all_likes', 'done')
    return True

## Update routine, run through every spreadsheet 
# *All Likes* and pull all info from them
# @param just          (*opcional*) if *TRUE* will only analise the sheets contained in sheetGroup
# @param sheetGroup    (*opcional*) spreadsheet's link's list to analise
# @note                just is *FALSE* by default
def FullUpdate(just:bool = False, sheetGroup:List[str] = []):
    done = []
    failed = []
    i = 0

    validSheets = getAllPagesSheet()
    for sheet in validSheets:
        try : 
            title = get_all_likes_name()
            spread = getSheetByLink(sheet)
            SpreadsheetURL = spread.url
            sheet = run_with_timeout_checker(lambda : spread.worksheet(title))
            update_checker('update', 'worksheet.title', title)
            update_checker('update', 'spreadsheet.title', spread.title)
            
        except WorksheetNotFound : 
            print("failed")
            update_checker('update', 'all_likes', 'failed')
            failed.append({"title": title, "sheetURL": "None",
                          "spreadSheetUrl": SpreadsheetURL})
            continue
        
        except:
            print("failed")
            update_checker('update', 'all_likes', 'failed')
            failed.append({"title": title, "sheetURL": "None",
                          "spreadSheetUrl": SpreadsheetURL})
            continue


        i += 1
        sheetURL = sheet.url
        title = sheet.title
        

        if just:
            if (not title in sheetGroup) and (not sheetURL in sheetGroup):
                print("passed")
                update_checker('update', 'all_likes', 'passed')
                continue

        print(title)
        print(sheetURL)
        print(SpreadsheetURL)

        try:
            UpdateListsInDataBase(sheet)
            update_checker('update', 'all_likes', 'done')
            done.append({"title": title, "sheetURL": sheetURL,
                        "spreadSheetUrl": SpreadsheetURL})
            pass
        except:
            print("failed")
            update_checker('update', 'all_likes', 'failed')
            failed.append({"title": title, "sheetURL": sheetURL,
                          "spreadSheetUrl": SpreadsheetURL})
        # wait_secs(8)

    saveJSON("Not_updated", failed)
    saveJSON("Updated", done)
    remove_value_from('update', 'all_likes')
    return done, failed

## Updates the Worksheets left from the first update 
def VerifyUpdate():
    NotUpdated = json.load(open("data/Not_updated.json", "r"))["data"]

    sheetList = list(map(lambda a: a["spreadSheetUrl"], NotUpdated))

    print(sheetList)
    
    done, failed = FullUpdate(just=True, sheetGroup=sheetList)
    saveJSON("Not_updated", failed)
    saveJSON("Updated", done)

## Update the code column of a given worksheet
# @param worksheet worksheet to update 
# @see OptionManager.code_title
def update_code(worksheet:Worksheet):

    if not validate(worksheet):
        return

    print(worksheet.title, end= ": ")
    update_checker('update', 'worksheet.title', worksheet.title)
    update_checker('update', 'spreadsheet.title', worksheet.spreadsheet.title)
    command = get_cols_title(worksheet, code_col("index"))
    

    if command == None:
        print(print("Code not found"))
        update_checker('update', 'command', "Code not found")
        return

    if command == script():
        print("\"" + command + "\" found")
        update_checker('update', 'command', command)
        try :
            #defining critic function
            #submiting to the loss manager
            url = worksheet.spreadsheet.url
            title = worksheet.title
            path = submit(lambda : run_with_timeout_checker(lambda : rebuild_sheet(url, title).update(code_title(), script(), raw = False), "update code"))  
            
            #running code
            run_with_timeout_checker(lambda : worksheet.batch_clear([code_col("location")]), "clear column")
            run_with_timeout_checker(lambda : worksheet.update(code_title(), script(), raw = False), "update code")
            
            #clearing loss manager in case of success
            clear(path)

            

        except APIError as err:                 
            if err.args[0]["code"] == 400:
                pp("celula invalida")
                pp([worksheet.title, worksheet.spreadsheet.url, worksheet.col_count])
            raise err
        
        except KeyboardInterrupt:
             run_with_timeout_checker(lambda : worksheet.update(code_title(), script(), raw = False), "update code")
        pass

        print()
    else:
        print("Code not found; command : " + command)
        update_checker('update', 'command', f'not valid : {command}')
        

## Apply update_code() to all validated worksheets
# @see validate, do_to_all, update_code
def update_all():
    do_to_all(update_code)


## Fix the code column of a given worksheet, 
# in case of missing code or server crash
# @param worksheet worksheet to update 
# @see OptionManager.code_title
def fix_no_code_sheet(worksheet:Worksheet):
    if not validate(worksheet):
        return

    try:
        formula = run_with_timeout_checker(lambda : worksheet.get(code_title(), value_render_option='FORMULA').first(), "get formula")
        val = run_with_timeout_checker(lambda : worksheet.acell(code_title(), value_render_option='UNFORMATTED_VALUE').value, "get unformatted value")
    except CellNotFound:
        pass
    update_checker('update', 'worksheet.title', worksheet.title)
    update_checker('update', 'spreadsheet.title', worksheet.spreadsheet.title)
    
    if (not formula == script()):
        print("Fixing " + worksheet.title + " : " + worksheet.spreadsheet.url)
        run_with_timeout_checker(lambda : worksheet.update(code_title(), script(), raw = False))

    if not val == None:
        print(val, end = " : ")
        update_checker('update', 'cell.value', val)
        if "Loading..." in val or "#ERROR!" in val:
            print("Refreshing " + worksheet.title + " : " + worksheet.spreadsheet.url)
            update_checker('update', 'refreshing', True)
            update_code(worksheet)
            remove_value_from('update', 'refreshing')


## Fix all the validated worksheets
# @see do_to_all, fix_no_code_sheet, validate
def fix_all_sheets():
    run_with_timeout_checker(UpdateAllQuery)
    run_with_timeout_checker(lambda : do_to_all(fix_no_code_sheet))


## Locks the sheet according to it
# If it's a valid sheet it locks the OptionManager.code_title range
# Else if is an *All Likes* or *New Profiles From Ads* it locks it
# @param worksheet      worksheet to lock
# @param emails         emails that can access the worksheet
def smartLockSheet(worksheet:Worksheet, emails:List[str]):
    command = get_cols_title(worksheet, 2)

    if command == "" : 
        print(worksheet.title + " -> " + worksheet.spreadsheet.title)
        update_checker('update', 'worksheet.title', worksheet.title)
        update_checker('update', 'spreadsheet.title', worksheet.spreadsheet.title)

    if worksheet.title.lower() == get_all_likes_name().lower():
        lockSheet(worksheet, emails)
        return

    if worksheet.title.lower() == get_new_profiles_name().lower():
        lockRange(worksheet, "A:C", emails)
        return

    if command == script():
        lockLinksCol(worksheet, emails)
        pass

## Locks all worksheets according to each one of them
# @param emails         emails that can access the worksheet
# @see smartLocksheet, do_to_all
def smartLockAll(emails:List[str]):
    do_to_all(smartLockSheet, [emails])


## Build Query Language of *All Likes*' sheet of a given spreadsheet
# @param spreadSheet    spreadsheet to build the command from
# @return               Query Language command with the valid worksheets
# @see                  validate, QueryUpdater
def QueryBuilderAllLikes(SpreadSheet:Spreadsheet)->str:
    queryLanguageSelector = get_query()
    sheetListCode = ""
    measured = False
    for workSheet in SpreadSheet:
        if not validate(workSheet):
            continue

        if not measured :
            line = run_with_timeout_checker(lambda : workSheet.row_values(1), "Measure title row")

            if not len(line) > get_highest_column():
                range = get_col_by_num(0) + "2:" + get_col_by_num(len(line))
            else :
                range = get_col_by_num(0) + "2:" + get_col_by_num(get_highest_column())
            
            measured = True

        sheetListCode += "'" + workSheet.title.replace("'", "''") + "'!" + range + ";"

    sheetListCode = sheetListCode[0:-1]

    return "=QUERY({"+ sheetListCode + "}," + queryLanguageSelector + ", 0 )"

## Updates Query Language of *All Likes*' sheet
# @param spreadSheet    spreadsheet to update
#
# @warning              **DO NOT USE** unless it's used with a *All Likes*' worksheet
#
# @note                 If the *All Likes*' worksheet doesn't exist, 
#                       one will be autogenerated 
#
# @see                  OptionManager.get_all_likes_name, 
#                       QueryBuilderAllLikes
def QueryUpdater(SpreadSheet:Spreadsheet):
    print("Update : " + SpreadSheet.title, end=" : ")
    update_checker('update', 'spreadsheet.title', SpreadSheet.title)
    update_checker('update', 'updating.query', True)

    created = False
    try:
        sheet = run_with_timeout_checker(lambda : SpreadSheet.worksheet(get_all_likes_name()), "get All Likes")
    except WorksheetNotFound:
        created = True
        sheet = run_with_timeout_checker(lambda : SpreadSheet.add_worksheet(get_all_likes_name(), 2,2), "create All Likes")
        lockSheet(sheet, email())

    code = QueryBuilderAllLikes(SpreadSheet)

    run_with_timeout_checker(lambda : sheet.update("A2", code, raw=False), "Update All Likes")

    print("done")
    remove_value_from('update', 'updating.query')


## Apply QueryUpdater() to all spreadsheets
# @see do_to_all_spreadsheets, QueryUpdater
def UpdateAllQuery():
    do_to_all_spreadsheets(QueryUpdater)


## Build Query Language of *Verifyer*'s sheet of a given spreadsheet 
# for debugging purposes, It looks up on every valid worksheet
#
# @param spreadSheet    spreadsheet to build the command from
# @return               Query Language command with the valid worksheets
# ~~~~~~~~~~~~~~~~~~~.py
# [[GeneralCode], tableList], range
# ~~~~~~~~~~~~~~~~~~~
# @see                  validate, VerityerUpdater
def VerifyerBuilder(SpreadSheet:Spreadsheet)->Tuple:
    queryLanguageSelector = '"select *"'
    GeneralCode = ""
    tableList = []
    for workSheet in SpreadSheet:
        if not validate(workSheet):
            continue

        range = code_title()
        iteration_code = "'" + workSheet.title.replace("'", "''") + "'!" + range
        GeneralCode += iteration_code + ","
        
        tableList.append( "=QUERY({"+ iteration_code + "}," + queryLanguageSelector + ", 0 )")

    GeneralCode = "{" + GeneralCode[0:-1] + "}"
    
    range = "A1:{col}2".format(col = get_col_by_num(len(tableList)))
    GeneralCode =  "=QUERY({iteration_code},{query}, 0 )".format(iteration_code = GeneralCode, query = queryLanguageSelector)

    return [[GeneralCode], tableList], range

## Updates Query Language of *Verifyer*'s sheet
# @param spreadSheet    spreadsheet to update 
# @note                 If the *Verifyer*' worksheet doesn't exist, one will be autogenerated 
# @see                  VerifyerBuilder
def VerityerUpdater(SpreadSheet:Spreadsheet):
    print("Update : " + SpreadSheet.title, end=" : ")
    update_checker('update', 'spreadsheet.title', SpreadSheet.title)
    update_checker('update', 'updating.verify', True)
    try:
        sheet = run_with_timeout_checker(lambda : SpreadSheet.worksheet("!Verifyer"), "get !Verifyer")
    except WorksheetNotFound:
        created = True
        sheet = run_with_timeout_checker(lambda : SpreadSheet.add_worksheet("!Verifyer", 2,10), "create !Verifyer")
        lockSheet(sheet, email(), secure=False)

    code, range = VerifyerBuilder(SpreadSheet)

    run_with_timeout_checker(lambda : sheet.update(range, code, raw=False), "Update Verifyer")

    print("done")
    remove_value_from('update', 'updating.verify')


## Apply VerityerUpdater() to all spreadsheets
# @see do_to_all_spreadsheets, VerityerUpdater
def UpdateAllVerifyers():
    do_to_all_spreadsheets(VerityerUpdater)
