import json
from typing import Dict, List

import gspread
from gspread.worksheet import Worksheet
from Drive.OptionManager import code_title
from Drive.docsUpdaterBase import client_session
from General.general import get_col_by_num, run_with_timeout_checker

## Gets the protected ranges from the api
# @param worksheet worksheet to get the protected ranges from
# @return a list with all protected ranges of a worksheet
def getProtectedRanges(worksheet:Worksheet)->List[Dict]:
    params = {}
    params["fields"] = "sheets(properties(title),protectedRanges)"

    id = worksheet.url
    
    data = run_with_timeout_checker(lambda : client_session.request("get", id, params=params), "Get all protected ranges data").json()["sheets"]
    
    data = list(filter(lambda x : x["properties"]["title"] == worksheet.title, data))
    data = list(filter(lambda x : "protectedRanges" in x.keys(), data))
    data = list(map(lambda x : {"title" : x["properties"]["title"], "protectedRanges" : x["protectedRanges"]}, data))
    
    if data == [] :
        return [] 

    data = list(map(lambda x : convert_ranges(x), data))[0]
    
    return data["protectedRanges"]

## Convert numeric ranges in A1 notation ranges
# @param sheet_object protected range object to get the A1 notation
# @return String with A1 notation of the location of the protected range
def convert_range(sheet_object:dict)->str:
    try : 
        startRow = sheet_object["range"]["startRowIndex"]+1
        endRow = sheet_object["range"]["endRowIndex"]
    except KeyError:
        startRow = ""
        endRow = ""

    try : 
        startCol = sheet_object["range"]["startColumnIndex"]
        endCol =sheet_object["range"]["endColumnIndex"]-1
    except:
        return "A:AA"

    startCol = get_col_by_num(startCol)
    endCol = get_col_by_num(endCol)

    if startRow == "":
        return startCol + ":" + endCol 

    if startRow == endRow and startCol==endCol:
        return startCol + str(startRow)
    else:
        return startCol + str(startRow) + ":" + endCol + str(endRow)

## Recieves a list of protected ranges and add to each one of an 
# *A1Notation* property with a A1 notation of the protected range
# @param sheet_object_list list of protected range objects to modify
# @return list of protected range objects, now with *A1Notation* property
def convert_ranges(sheet_object_list:List[dict])->dict:
    for item in sheet_object_list['protectedRanges']:
        A1 = convert_range(item)
        item["range"]["A1Notation"] = A1
        
    
    return sheet_object_list

## Get a protected range from the api acroding to a range and a sheet
# @param worksheet      worksheet to get the protected range from
# @param range          the pretended range
# @return               the range or *None* if not found
# @see                  getProtectedRanges
def getLockedRange(range:str, worksheet:Worksheet)->Dict:
    sheetRanges = getProtectedRanges(worksheet)
    sheetRanges = list(filter(lambda range : range["description"]=="bot column", sheetRanges))
    
    if sheetRanges == []:
        return None

    sheetRanges = list(filter(lambda  sheet : sheet["range"]["A1Notation"] == range.upper(), sheetRanges))
    
    if sheetRanges == []:
        return None
    
    return sheetRanges

## Lock the presetted links' column in a worksheet
# @param worksheet      worksheet to lock
# @param range          the pretended range to lock
# @see                  lockRange
def lockLinksCol(worksheet:Worksheet, emails:List[str]):
    lockRange(worksheet, code_title(), emails)

## Lock a range in a worksheet, manage repeated protected ranges
# @param worksheet      worksheet to lock
# @param emails         emails that can edit the range
# @param range          the pretended range to lock
# @see                  getProtectedRanges, editProtectedRange
# @attention            if the range already exist, it will be edited
def lockRange(worksheet:Worksheet, range:str, emails:List[str]):
    if not client_session.auth.service_account_email in emails: emails.append(client_session.auth.service_account_email)
    
    protectedRange = getLockedRange(range, worksheet)

    if not protectedRange == None: 
        protectedRange = protectedRange[0]
        editProtectedRange(worksheet, range, emails, protectedRange=protectedRange)
        return
    
    try:
        out = run_with_timeout_checker(
            lambda : worksheet.add_protected_range(
                range, editor_users_emails=emails, description="bot column"
            ),
            "lock column"
        )

    except gspread.exceptions.APIError as err:
        rep = err.response
        args = err.args

        print([rep, args])
        if args[0]["code"] == 400:
            pass
        print("lock col impossible")



## Edit a range in a worksheet, manage repeated protected ranges
# @param worksheet          locked worksheet
# @param emails             emails that can edit the range
# @param range              the pretended locked range to edit
# @param protectedRange     *(optional)* specifique range to edit
# @see                      getProtectedRanges
def editProtectedRange(worksheet:Worksheet, range:str, emails:List[str], protectedRange=None):
    message = ''
    if protectedRange == None:
        protectedRange = getLockedRange(range, worksheet)
        message = f'edit range {range}, of {worksheet.title} of {worksheet.spreadsheet.title}'
    else:
        id = protectedRange['protectedRangeId']
        message = f'edit range {range} of id {id}'

    if protectedRange == None : return

    protectedRange

    body = {
            "requests": [
                {
                    "updateProtectedRange": {
                        "protectedRange": {
                            "protectedRangeId": protectedRange['protectedRangeId'],
                            "editors": {
                                "users": emails,
                            },
                        },

                        'fields' : 'editors'
                    }
                }
            ]
        }

    run_with_timeout_checker(lambda : worksheet.spreadsheet.batch_update(body), message)

    True

## Lock a worksheet
# @param worksheet      worksheet to lock
# @param range          the pretended range to lock
# @see                  lockRange
def lockSheet(worksheet:Worksheet, emails:List[str]):
    if not client_session.auth.service_account_email in emails: emails.append(client_session.auth.service_account_email)
    max = worksheet.col_count-1

    range_name = "A:" + get_col_by_num(max)

    lockRange(worksheet, range_name, emails)

