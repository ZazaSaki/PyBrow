from typing import List
from General.general import saveJSON, get_col_by_num
import json

## Dictionary of all options
options={}
## generate a column option given a index number
# @param col_index      column index *starts counting on 0*
# @return a dictionary with the column settings
# ### Output in case of col_index = 2
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.py
# {"column" : {
#         "index" : 2,
#         "number" : 3,
#         "letter" : "C",
#         "location" : "C:C"
#     },
#    
#     "title_location" : "C1"
# }
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @see setup()
def set_col(col_index:int=2)->dict:
    letter = get_col_by_num(col_index)
    return {"column" : {
                "index" : col_index,
                "number" : col_index + 1,
                "letter" : letter,
                "location" : letter + ":" +letter
            },
            
            "title_location" : letter + "1"
        }

## generate a script base on a index column
# @param col_index      column index *starts counting on 0*
# @return               a script in js
# @note                 This script migth be pointing to the column with the hyperlinks 
# ### Output in case of col_index = 0
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.py
# "GetUrl(A:A)"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @see setup()
def build_script(col_index:int=0)->str:
    return "=GetUrl(" + get_col_by_num(col_index) + ":" + get_col_by_num(col_index) + ")"

## Generate default settings
# @note Is used if there is not a *options.json* file in \a /data folder
# ### Default Options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.py
# {
#     "data": {
#         "code": {
#             "column": {
#                 "index": 2,
#                 "number": 3,
#                 "letter": "C",
#                 "location": "C:C"
#             },
#             "title_location": "C1"
#         },
#         "names": {
#             "column": {
#                 "index": 0,
#                 "number": 1,
#                 "letter": "A",
#                 "location": "A:A"
#             },
#             "title_location": "A1"
#         },
#         "ignore": {
#             "titles": [
#                 "paste here",
#                 "all likes",
#                 "new profiles from ads",
#                 "all leads",
#                 "lead ad references",
#                 "grand est r\u00e9f\u00e9rences d'avril"
#             ],
#             "words": [
#                 "r\u00e9f\u00e9rences",
#                 "!"
#             ]
#         },
#         "email": [
#             <api email>,
#         ],
#         "sheets": {
#             "all likes": "All Likes",
#             "new profiles": "New Profiles From Ads"
#         },
#         "script": "=GetUrl(A:A)"
#     }
# }
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def setup():
    global options

    my_email = json.load(open("creds.json", "r"))["client_email"]

    emails = [my_email]

    all_likes_name = "All Likes"
    new_profiles_name = "New Profiles From Ads"

    ignore_titles = ["paste here", all_likes_name.lower(), new_profiles_name.lower(), "all leads", "lead ad references", "grand est références d'avril"]
    ignore_words = ["références", "!"]

    script = build_script()

    options = {
        "code": set_col(2),

        "names": set_col(0),

        "ignore" : {
            "titles" : ignore_titles,
            "words" : ignore_words
        },

        "email" : emails,

        "sheets" : {
            "all likes" : all_likes_name,
            "new profiles" : new_profiles_name,
            'query language selector' : '"select * where Col1 is not null order by Col3, Col2, Col7, Col1"',
            'highest column readed' : 7
        },

        "script" : script
    }

## Restore the default options
# @see setup()
def restore():
    setup()
    saveJSON("options", options)

## Load the \a options.js from \a /data
# @note If \a options.js doesn't exist it runs restore()
def load():
    global options

    try :
        options = json.load(open("data/options.json"))["data"]
    except FileNotFoundError:
        restore()

load()

def get_query():
    return options["sheets"]['query language selector']

def set_query(new_query):
    options["sheets"]['query language selector'] = new_query
    save()

def get_highest_column():
    return options["sheets"]['highest column readed']

def set_highest_column(highest_column):
    options["sheets"]['highest column readed'] = highest_column
    save()

## Change the code column, and saves the the changes
# @param col_index index of the pretended column
# @note it sets all the properties related to it.
# The *col_index* starts couting on 0
# @see set_col(int), build_script(int), save()
def set_code_col(col_index:int=2):
    options["code"] = set_col(col_index)
    save()

## Get code properties
# @return properties in dictinary format
# @see setup
def code()->dict:
    return options["code"]

## Get code column property
# @param prop wanted property
# @return property in string format
# @see set_col(int)
def code_col(prop:str)->str:
    return code()["column"][prop]

## Get code column title location property in A1 Notation
# @return property in string format
# @see set_col(int), docsUpdaterBase.update_code
def code_title()->str:
    return code()["title_location"]


## Change the names column, and saves the the changes
# @param col_index index of the pretended column
# @note it sets all the properties related to it.
# The *col_index* starts couting on 0
# @see set_col(int), build_script(int), save()
def set_names_col(col_index:int=0):
    options["names"] = set_col(col_index)
    options["script"] = build_script(col_index)
    save()

## Get names
def names()->dict:
    return options["names"]

## Get names column properties
# @param prop wanted property
# @return property in string format
# @see set_col(int)
def names_col(prop:str)->str:
    return names()["column"][prop]

# Get names column title location property in A1 Notation
# @return property in string format
# @see set_col(int)
def names_title()->str:
    return names()["title_location"]

## Get the script property
## @return property in string format
#  @see setup()
def script()->str:
    return options["script"]


#email
## Adds an email to the top priority list
# @see email()
def add_email(email:str):
    options["email"].append(email)
    save()

## Removes an email from the top priority list
# @see email()
def remove_email(email:str):
    options["email"].remove(email)
    save()

## @return The email top priority list used by ther Locker Manager
#  @see LockManager
def email()->List:
    return options["email"]


## @return List of worksheet's titles to ignore during the validation process
# @see docsUpdaterBase.validate
def get_ignore_titles()->List:
    return options["ignore"]["titles"]

## @return list of words to ignore during the validation process
# @note If a worksheet's title contains any of this words that worksheet is ignored
# @see docsUpdaterBase.validate
def get_ignore_words()->List:
    return options["ignore"]["words"]

## Save the changes
def save():
    saveJSON("options", options)

## Get *All Likes*' worksheet's title
def get_all_likes_name()->str:
    return options["sheets"]["all likes"]

## Get *New Profiles From Ads*' worksheet's title
def get_new_profiles_name()->str:
    return options["sheets"]["new profiles"]