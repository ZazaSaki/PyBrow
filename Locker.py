from os import link
from pprint import pprint

import gspread
from Drive.docsUpdaterBase import getSheetByLink
from Drive.DataBase.FacebookPageManager import getAllPagesSheet
from General.general import ExplicitWait, get_col_by_num, time_out_checker

from gspread.exceptions import APIError

validSheetsLinks = getAllPagesSheet()

ignore = ["all likes", "paste here"]

def lockLinksCol(worksheet):
    ll = ["benjamin.de.angeli@missionary.org",
            "dataloader@database-328914.iam.gserviceaccount.com", "isac.marinho.da.cruz@missionary.org"]
    try:
        out = worksheet.add_protected_range(
            "C:C", editor_users_emails=ll, description="bot column")
    
    except gspread.exceptions.APIError as err:
        rep = err.response
        args = err.args

        pprint([rep, args])
        if args[0]["code"] == 400:
            pass
        pprint(args)

def lockSheet(worksheet):
    ll = ["benjamin.de.angeli@missionary.org",
            "dataloader@database-328914.iam.gserviceaccount.com", "isac.marinho.da.cruz@missionary.org"]

    max = worksheet.col_count-1

    range_name = "A:" + get_col_by_num(max)
    
    try : 
        out = worksheet.add_protected_range(
            range_name, editor_users_emails=ll, description="bot column")
    except gspread.exceptions.APIError as err:
        rep = err.response
        args = err.args

        pprint([rep, args])
        if args[0]["code"] == 400:
            pass
        pprint(args)
        pass

def get_cols_title(worksheet, col):
    cell = get_col_by_num(col) + '1'
    while True:
        try:
            command = worksheet.acell(
                cell, value_render_option='FORMULA').value
            print(command)
            break
        except gspread.exceptions.APIError as err:
            rep = err.response
            args = err.args

            pprint([rep, args])
            if args[0]["code"] == 400:
                return ""
            
            if time_out_checker(err):
                ExplicitWait("api", 60)
            pass
    return command

def lockSheet(worksheet):
    command = get_cols_title(worksheet, 2)

    if worksheet.title.lower() == "All Likes".lower() or worksheet.title.lower() == "New Profiles From Ads".lower():
        lockSheet(worksheet)
        return

    if command == "=GetUrl(A:A)":
        lockLinksCol(worksheet)
        pass

def update_code(worksheet):
    command = get_cols_title(worksheet, 2)

    if command == "=GetUrl(A:A)" or command == "=GetUrl(A2)" or command == "=GetUrl(A1)":
        while True:
            try :
                worksheet.update("C1", "=GetUrl(A2)", raw = False)
                worksheet.update("C1", "=GetUrl(A:A)", raw = False)
                break
            except APIError as err: 
                if time_out_checker(err):
                    ExplicitWait("timeout", 30)
                
                if err.args[0]["code"] == 400:
                    pprint("celula invalida")
                    pprint([worksheet.title, worksheet.spreadsheet.url, worksheet.col_count])
            pass

def do_to_all(function):
    for sheetLink in validSheetsLinks:
        try:
            sheet = getSheetByLink(sheetLink)
        except:
            print('invalid Link : ' + sheetLink)
            continue
        
        for worksheet in sheet:
            function(worksheet)

def update_all():
    do_to_all(update_code)

def lockAll():
    do_to_all(lockSheet)

update_all()