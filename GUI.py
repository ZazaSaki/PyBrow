from ast import withitem
from asyncore import read
from pickle import FALSE, TRUE
from sys import prefix
import time
from turtle import title
from types import FunctionType
from typing import Dict, List, Tuple
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import popup_yes_no
from Browser.Read import checkLogin, forgetFacebookAccount
from Drive.DataBase.DataManager import IsInDataBase, RemoveDuplicateds, getProfile, hashInvalids, insertProfileLink
from Drive.DataBase.FacebookPageManager import addPage, getAllPagesNames, SearchPage, getAllPagesSheet, getPageByLink, getPageByName, getPageBySheet, removePage, updateLink, updateSheet
from Drive.LossManager import full_recover, get_all_recover_path, get_recover
from Drive.OptionManager import add_email, code_col, email, get_highest_column, get_query, names_col, remove_email, set_code_col, set_highest_column, set_names_col, set_query
from Drive.docsUpdaterBase import UpdateAllQuery, fix_all_sheets, smartLockAll
from FeedbackDisplayer import get_checker, get_stack, remove_value_from, update_all_checkers, update_checker
from ListManager import create_new_list, delete_list, get_all_paths_lists, get_list_from_index, get_name_by_path, get_path_by_index, read_a_list, read_a_list_as_array, save_a_list
from Main import UpdateDataBase, UpdateLikes, VerifyDataBase, VerifyIgnoreLinks, quick_update
import Drive.DataBase.FacebookPageManager
TITLE = 'Auto Cruz 0.1.1'
MENU_PREFIX = 'Menu'
MENU_BUTTON_PREFIX = 'Show_Menu'

WORKING = False
TRYED = False
WORKING_FLAG = ''
FINISH_WORD = 'FININSHED'
FAIL_WORD = 'FAILED'
sg.theme('DarkAmber')



get_all_recover_path()
True
#Sequencial runs manager------------------------------------------

## Submits the WORKING_FLAG until it is realesed
# @see release_core
def submit_work():
    global WORKING, WORKING_FLAG, FINISH_WORD
    WORKING_FLAG = FINISH_WORD
    WORKING=True

## Release the WORKING_FLAG
# @see submit_work
def release_core():
    global WORKING_FLAG, WORKING
    WORKING = 0==1
    WORKING_FLAG = ''

## Runs a given function if the is not a critical task 
# running with the WORKING_FLAG realesed
# @param function       the function to run
# @return               boolean if the function suceeded or not
# @see run_alone, submit_work
def run_with_work_check(function:FunctionType)->bool:
    global WORKING, TRYED
    if not WORKING:
        try :
            function()
        except:
            return False
        return True
    else:
        TRYED = True
        return False

## Runs and submits a given function
# Submits a given function to run in paralel as a critical task, 
# if there is not a critical task running.
# By submiting, it raises the WORKING_FLAG
# By submitings blocks other functions run in paralel
# @param function       the function to run
# @return               boolean if the function suceeded or not
# @see run_with_work_check, submit_work
def run_alone(function:FunctionType)->bool:
    global WORKING, TRYED, WORKING_FLAG
    TRYED = True
    try :
        if not WORKING:
            remove_value_from(name='general',id='error')
            update_checker(name='general',id='action_state', val='RUNNING')
            submit_work()
            TRYED = False
            function()
            update_checker(name='general',id='action_state', val='SUCCEEDED')
            release_core()
        return True
    except Exception as e:
        release_core()
        update_checker(name='general',id='action_state', val='FAILED')
        update_checker(name='general',id='error', val=f'{e}')
        sg.popup('Action failed \n check the General Stats for more')
        return False

## Runs and submits a given function
# Submits a given function to run, as a critical task, in paralel with the GUI, 
# if the is not a critical task running.
# By submitings blocks other functions run in paralel
# @param function       the function to run
# @param window         window of the GUI
# @return               boolean if the function suceeded or not
# @see run_alone
def run_in_paralel(function:FunctionType, window:sg.Window):
    if not WORKING_FLAG == FINISH_WORD:
        window.perform_long_operation(lambda : run_alone(function), FINISH_WORD)
    else:
        window.perform_long_operation(lambda : run_alone(function), FAIL_WORD)

## Change pages info in the data base by the *Page Manager* menu
# @param display_id         id of the item that displays the information to change
# @param message            message to inform the user to insert the updated information
# 
# @param changer            function to updated the given information. 
#                           It shall accept only one argument (the updated value)
#                           and update the data base with it
# 
# @param window             GUI Window S
def change(display_id:str, message:str, changer:FunctionType, window):
    if not sg.popup_ok_cancel('Are you sure?') == 'OK':
            return
    val = sg.popup_get_text(message)
    Advice2 = 'changing to the wrong link may cause issues'
    Advice1 = 'Are you sure you want to change to this link:'
    confirmation = f'{Advice1} \n\n{val} \n\n{Advice2}'
    if (not val == None):
        if sg.popup_ok_cancel(confirmation) == 'OK':
            if run_with_work_check(lambda : changer(val)) :
                window[display_id].update(str(val))

## Creates the main menus by a list of *PySimpleGUI* elements
# @param menus          List if menus
# @return               sg.Window 
def Make_layout(menus:List, general_displayer)->sg.Window:
    i=0
    
    row_of_buttons = []
    row_of_menus   = []
    for menu in menus:

        name          = menu.Key
        menu.Key      = f'{MENU_PREFIX}{i}'
        
        button = sg.Button(name, key =f'{MENU_BUTTON_PREFIX}{i}', button_color='#ffb27a',pad=0, expand_x=True)

        row_of_buttons.append(button)
        row_of_menus.append(menu)
        i+=1

     
    my_layout = [[row_of_buttons, row_of_menus], [general_displayer]]
    return sg.Window(TITLE, my_layout, margins=(10, 10), resizable = True, size=(900,600))


#-----------------------------------------------------------------------
## Get the List of Pages according to a searched name
# @params name      name to search
# @return           Table List of founded pages
def get_list(name:str)->str:
    candidates = SearchPage(name)
    list_layout = []
    for candidate in candidates:
        
        list_layout.append([candidate[0]])

    return list_layout

## Page Information Dysplayer Layout
info_displayer = [
    [sg.Text('Name :', size=10),sg.InputText('', key='page_name', readonly=True, text_color='black', size= 60)],
    [sg.Text('Link :', size=10),sg.InputText('', key='page_link', readonly=True, text_color='black', size= 60)],
    [sg.Text('Spreadsheet :', size=10),sg.InputText('', key='page_spreadsheet', readonly=True, text_color='black', size= 60)]
]

## Page Information Dysplayer
info_displayer = sg.Column(info_displayer, key='displayer')

## Page Controller Buttons layout
control_buttons = [
    [sg.Button('Edit Link', key='edit_page_link')],
    [sg.Button('Edit Spreadsheet', key='edit_page_spreadsheet')],
    [sg.Button('Delete', key='delete_page')],
]

## Page Controller Buttons
control_buttons = sg.Column(control_buttons, key='control_buttons')

## Page Controller Layout
control_layout = [
    [info_displayer, control_buttons]
]


## Add Menu Layout
Add_layout = [
    [sg.Text('Name :', size=10),sg.InputText('', key='add_page_name', size= 60)],
    [sg.Text('Link :', size=10),sg.InputText('', key='add_page_link', size= 60)],
    [sg.Text('Spreadsheet :', size=10),sg.InputText('', key='add_page_spreadsheet', size= 60)],
    [sg.Button('Confirm', key='add_page')]
]

## Add Menu
Add_page_menu = sg.Column(Add_layout, key='add_page_menu', visible=False, expand_x=True)

## Search Layout
Search_layout = [
    [sg.Text('Search')],
    [sg.Text('type'), 
        sg.InputText(key = 'search_input', enable_events=True), 
    ],
    [sg.Table(values=get_list(''), 
        headings=['Names'], 
        key='search_table', 
        auto_size_columns=True,
        enable_events = True,
        expand_x=True)],
    [sg.Column(control_layout, key='page_controller', visible=False)],
    [sg.Button('Add Page', key='show_add_page_menu')],
    [Add_page_menu]
]     


## Search Menu
Search_menu = sg.Column(Search_layout, key='Page Manager', visible=False, expand_x=True)
#------------------------------------------------------------------------

## Read All Layout
Read_all_layout = [
    [sg.Button('Read All')],  
] 

## Read All Menu
Read_all = sg.Column(Read_all_layout, key='read_all')


## Read One Layout
Read_one_layout = [
    [sg.Text('Link'), sg.InputText(key = 'Read'),sg.Button('Read One')]
] 

## Read One Menu
Read_one = sg.Column(Read_one_layout, key='Read_one')

Read_Displayer_Layout = [
    [sg.Table(values=get_all_paths_lists(), 
            headings=['Names'], 
            key='Read_table', 
            auto_size_columns=True,
            enable_events = True,
            expand_x=True
        ), 
        sg.Multiline(
            key='Read_file_input', 
            expand_x=True, 
            expand_y=True)
        ],
    [   
        sg.Button( 'Save', key='Read_save_file'),
        sg.Button( 'New File', key='Read_new_file'),
        sg.Button( 'Delete', key='Read_delete_file'),
    ]
]

Read_Displayer = sg.Column(Read_Displayer_Layout, key = 'read_display', expand_x=True, expand_y=True)

## Read Menu Layout
Read_Layout = [
    [Read_all],
    [Read_one],
    [Read_Displayer]
]
## Read Menu
Read_menu = sg.Column(Read_Layout, key='read', visible=False, expand_x=True, expand_y=True)
#------------------------------------------------------------------

## Update Menu Layout
Update_layout = [
    [sg.Button('Update Data Base', key= 'UDB'), sg.Button('Verify Database', key='VDB'), sg.Button('Verify new links', key='VNL')],
    [sg.Button('Quick Update', key='QUDB'),sg.Button('Fix Broken Pages', key='FBP'), sg.Button('Remove Duplicateds', key='RDp')],
    [
        sg.Table(
            values=get_checker('update'), 
            headings=['Current stats'], 
            key='update_display', 
            auto_size_columns=True,
            enable_events = True,
            expand_x=True,
            expand_y=True
        )
    ],
]

## Update Menu
Update_menu = sg.Column(Update_layout, key='update', visible=False, expand_x=True)

## Get the List of emails that access the locked sheets
# @return        table list of emails
def get_email_list()->List:
    return list(map(lambda a : [a], email()))



## Options Menu Layout
Option_layout = [
    [sg.Text('Links Column :'), sg.Text(f'{code_col("index")}', size = 10, key='code_col'), sg.Button('Change', key = 'change_code_col'),sg.Text('Names Column :'), 
        sg.Text(f'{names_col("index")}', size = 10, key='names_col'), sg.Button('Change', key = 'change_names_col'),
    ],
    [sg.Text('Highest Readed Column :'), sg.Text(f'{get_highest_column()}', size = 10, key='highest_column'), sg.Button('Change', key = 'change_highest_column'),
        sg.Text('Query :'), sg.Text(f'{get_query()}', size = 50, key='query'), sg.Button('Change', key = 'change_query')     
    ],
    [sg.Table(
        values=get_email_list(), 
        headings=['emails'], 
        key='emails_table', 
        auto_size_columns=True,
        enable_events = True,
        expand_x=True)],
    [sg.Button('Add', key ='add_email'), sg.Button('Remove', key = 'remove_email')],
    [sg.Button('Forget Saved Facebook Account', key = 'forget_account'), sg.Button('Lock All', key='LAll',)]
]

## Option Menu
Option_menu = sg.Column(Option_layout, key='option', visible= False, expand_x=True)

## Recover Menu Layout
Recover_layout = [
    [sg.Button('Recover', key = 'recover')]
]

## Recover Menu
Recover_menu = sg.Column(Recover_layout, key='recover_menu', visible=False)

## General Displayer
general_displayer = [
    [sg.Table(
        values=get_checker('general'), 
        headings=['General Stats'], 
        key='general_display', 
        auto_size_columns=True,
        enable_events = True,
        expand_x=True,
        expand_y=True
    )],
    [sg.MLine(
        size=(80, 12), 
        k='-ML-', 
        reroute_stdout=True,
        write_only=True, 
        autoscroll=True, 
        auto_refresh=True,
        expand_x=True)],
    [sg.ProgressBar(
        100, 
        size=(20, 20), 
        orientation='h', 
        key='-bar-',
        expand_x=True
    )]
]


## GUI Window
window = Make_layout([Read_menu, Search_menu, Update_menu, Option_menu, Recover_menu], general_displayer)

## Get credencials if there is none
# Uses popups to get the information
# returns       username, password
def getCreds()->Tuple[str,str]:
    username = sg.popup_get_text("username : ")
    password = sg.popup_get_text("password : ", password_char='*')

    return username, password

def confirmation():
    while True : 
        if sg.popup_yes_no('Continue') == 'Yes':
            break 


## Protocol to use in case of tow factor authentication
def checkCreds():
    ask = sg.popup_yes_no("Towfactor Autentication?")
    checkLogin(ask=='Yes', confirmation, getCreds)

def update_table(id,window,display):
    time.sleep(5)
    while True :
        time.sleep(1)
        if not window[id].get() == get_checker(display):
            try :
                window[id].update(get_checker(display))
            except:
                pass

def update_table_stack(id,window,display):
    time.sleep(5)
    while True :
        time.sleep(1)
        if WORKING :
            window[id].update(get_stack(display))

def bar_update():
    i = 0
    while True :
        time.sleep(0.01)
        if WORKING :
            window['-bar-'].update_bar(i,1000)
            i=i+10
            if i > 1000 : i = 0
        elif not i == 0:
            time.sleep(1)
            i=0
            window['-bar-'].update_bar(i,10)


# hashInvalids()
# m = IsInDataBase('https://www.facebook.com/joao.dacruz.961')
# m = IsInDataBase('https://www.facebook.com/mehdi.oo.1')
# m = IsInDataBase('bob')
# m = getProfile('https://www.facebook.com/isac.cruz.99')
# m = getProfile('bob')
# insertProfileLink('bob')

event, values = window.read()
checkCreds()
base = 1
perfix = ''
window.perform_long_operation(lambda : update_table('update_display', window, 'update'),'update_display')
window.perform_long_operation(lambda : update_table('general_display', window, 'general'),'general_display')
window.perform_long_operation(bar_update,'bar_display')
#window['Read_table'].update()



while True: 
    
    event, values = window.read()
    # print(event)
    # print(values)
    if event == sg.WIN_CLOSED or event == 'Cancel':
        if WORKING :
            if popup_yes_no('A task is being done, are you sure you want to close') == 'Yes':
                break 
            else :
                event, values = window.read()
                continue
        break

    # Search Page----------------------------------------------------------------------------
    if event == 'search_input':
        window['search_table'].update(values = get_list(values['search_input']))

    # Search Table Selector
    if event == 'search_table' and len(values['search_table'])==1:
        name_selected = get_list(values['search_input'])[values['search_table'][0]][0]
        page = getPageByName(name_selected)[0]
        window['page_name'].update(str(page[0]))
        window['page_link'].update(str(page[1]))
        window['page_spreadsheet'].update(str(page[2]))
        window['page_controller'].update(visible = True)

    # Page Controller killer
    if not values['search_table'] == None:
        if not len(values['search_table'])==1 : 
            window['page_controller'].update(visible = False)

    if event == 'edit_page_link':
        change(
            display_id='page_link',
            message="New Page Link : ",
            changer= lambda val: updateLink(values['page_name'], val),
            window=window
        )
        
        # if not sg.popup_ok_cancel('Are you sure?') == 'OK':
        #     continue
        # link = sg.popup_get_text("New Page Link : ")
        # if run_with_work_check(lambda : updateLink(values['page_name'], link)) and not link == None:
        #     window['page_link'].update(str(link))

    if event == 'edit_page_spreadsheet':
        change(
            display_id = 'page_spreadsheet', 
            message = "New Page Spreadsheet : ", 
            changer = lambda val : updateSheet(values['page_name'], val),
            window = window
        )

    if event == 'delete_page':
        if not sg.popup_ok_cancel('Are you sure?') == 'OK':
            continue
        name = sg.popup_get_text(f"Write the name of the spreadsheet: {values['page_name']}")
        if name == values['page_name']:
            run_with_work_check(removePage(values['page_name']))
        else:
            sg.popup('Name was not correct')

        window['search_table'].update(values = get_list(values['search_input']))

    if event == 'show_add_page_menu':
        if not window['add_page_menu'].visible :
            window['add_page_menu'].update(visible = True)
        else : 
            window['add_page_menu'].update(visible = False)

    if event == 'add_page': 
        name = values['add_page_name']
        link = values['add_page_link']
        spread = values['add_page_spreadsheet']

        readed = run_with_work_check(addPage(name, link, spread))

        window['search_table'].update(values = get_list(values['search_input']))
        
        if readed : 
            window['add_page_name'].update('')
            window['add_page_link'].update('')
            window['add_page_spreadsheet'].update('')


    # Read ----------------------------------------------------------
    if event == 'Read All':
        if len(values['Read_table']) > 0:
            index = values['Read_table'][0]
            path = window['Read_table'].get()[index]
            val = read_a_list_as_array(path)

            run_in_paralel(lambda : UpdateLikes(val), window)
        else:
            sg.popup('select a list')
        

    if event == 'Read One':
        run_in_paralel(lambda : UpdateLikes([values['Read']]), window)

    if event == 'Read_table':
        if len(values['Read_table']) > 0:
            index = values['Read_table'][0]
            path = window['Read_table'].get()[index]
            val = read_a_list(path)
        else:
            val = ''
        
        window['Read_file_input'].update(val)

    if event == 'Read_save_file':

        if not len(values['Read_table'])<1:
            index = values['Read_table'][0]
            content = values['Read_file_input']
            path = window['Read_table'].get()[index]
            if not path == None :
                save_a_list(get_name_by_path(path), content)
            else : 
                sg.popup('ficheiro invalido')

    if event == 'Read_new_file':
        name = sg.popup_get_text('nome do ficheiro')

        if (not name == None) or name == '' :
            create_new_list(name)
            window['Read_table'].update(get_all_paths_lists())
    
    if event == 'Read_delete_file':
        index = values['Read_table'][0]
        path = window['Read_table'].get()[index]
        delete_list(get_name_by_path(path))
        
        window['Read_table'].update(get_all_paths_lists())


    # Update --------------------------------------------------------
    if event == 'UDB':
        run_in_paralel(UpdateDataBase, window)

    if event == 'QUDB':
        run_in_paralel(quick_update, window)

    if event == 'VDB':
        run_in_paralel(VerifyDataBase, window)

    if event == 'VNL':
        run_in_paralel(VerifyIgnoreLinks, window)

    if event == 'FBP':
        run_in_paralel(fix_all_sheets, window)
    
    if event == 'RDp':
        run_in_paralel(RemoveDuplicateds, window)

    if event == 'LAll':
        run_in_paralel(lambda : smartLockAll(email()), window)
        

    # Options ------------------------------------------------------

    if event == 'change_names_col':
        num = None
        try:
            num = int(sg.popup_get_text('change Names Colum'))
        except:
            sg.popup('Invalid Number')
            continue

        run_with_work_check(lambda : set_names_col(num))
        window['names_col'].update(names_col('index'))
    
    if event == 'change_code_col':
        num = None
        try:
            num = int(sg.popup_get_text('change Names Colum'))
        except:
            sg.popup('Invalid Number')
            continue

        run_with_work_check(lambda : set_code_col(num))
        window['code_col'].update(code_col('index'))

    if event == 'change_highest_column':
        num = None
        try:
            num = int(sg.popup_get_text('change Highest Readed Colum'))
        except:
            sg.popup('Invalid Number')
            continue

        run_with_work_check(lambda : set_highest_column(num))
        window['highest_column'].update(get_highest_column())

    if event == 'change_query':
        num = None
        try:
            num = sg.popup_get_text('change Query (change only if you know the full system)')
        except:
            sg.popup('Invalid Number')
            continue

        run_with_work_check(lambda : set_query(num))
        window['query'].update(get_query())

    if event == 'add_email':
        email_val =  sg.popup_get_text('Insert the email')
        done = sg.PopupYesNo(f'Are you sure to add {email_val} to the list?') == 'Yes'

        if done : run_with_work_check(lambda : add_email(email_val))

        window['emails_table'].update(get_email_list())
    
    if event == 'remove_email' and len(values['emails_table'])==1:
        email_val =  email()[values['emails_table'][0]]
        done = sg.PopupYesNo(f'Are you sure to add {email_val} to the list?') == 'Yes'

        if done : run_with_work_check(lambda : remove_email(email_val))
        window['emails_table'].update(get_email_list())

    if event == 'forget_account' :
        if sg.popup_yes_no('Are you sure you want to delete the account credencials?') == 'Yes':
            
            run_with_work_check(forgetFacebookAccount)
            checkCreds()
            WORKING = 0==1
            WORKING_FLAG = ''
            

    #Recover---------------------------------------------------------
    if event == 'recover':
        if get_recover():
            run_in_paralel(full_recover, window)
        else : 
            sg.popup('No Recover to do')

    #Flags managment
    if (TRYED and WORKING) or event == FAIL_WORD: 
        sg.popup('working : can not preform task until finish the current one')
        TRYED = False

    if event == FINISH_WORD:
        release_core()
    # Menu Switcher
    if MENU_BUTTON_PREFIX in event:
        
         
        window[f'{perfix}{MENU_PREFIX}{base}'].update(visible=False)

        base = int(event.split(MENU_BUTTON_PREFIX)[1])
        perfix = event.split(MENU_BUTTON_PREFIX)[0]


        window[f'{perfix}{MENU_PREFIX}{base}'].update(visible=True)

    #print('You entered ', values)
    #print(event)