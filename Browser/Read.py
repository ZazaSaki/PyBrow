from cgitb import text
from getpass import getpass
from pprint import pprint as pp
import pickle
import os
from typing import Dict, List

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

from Browser.FileReader import loadScroller
from General.general import ExplicitWait, getAplicableCleanList, wait_secs, linkparse
import json
from General.imagecomparator import getReact
import General.loadingBar as loadingBar

## Failed list
failed = []
timeout_flag = False
timeout_list = []
timeout_readed = ''

username = ""
password = ""

cookiesDir = "./Browser/browser_data/cookies.pkl"

# load scroll script
scrollFile = loadScroller()

# load
CoreFile = json.load(open('./Browser/browser_data/workSheet.json'))

# setting browser settings
opt = Options()
opt.add_argument("--disable-notifications")
opt.add_argument("--disable-cookies")

# setting driver path
PATH = "./chromedriver.exe"

driver = None

angrySrc = "https://scontent.xx.fbcdn.net/m1/v/t6/An8ph2gwH6WsvW6pxuYzGzrW8CdpQXACl5PKb5e3I8yS82dPyO-cHlpZDGDHuNFUBIPS8_rJmr6L5JKI6gpOd6GVgh3sLHS6qMD_fv-qg6FoJAzZC2k.png"



## Forget saved cookies
def forgetFacebookAccount():
    try:
        os.remove(cookiesDir)
    except:
        print("previous session not founded")


def getBrowser():
    global driver
    return driver
# open automated browser


def openBrowser():
    global driver
    driver = webdriver.Chrome(chrome_options=opt, executable_path=PATH)


def closeBrowser():
    global driver
    driver.close()

# -------------------------------------------------------------------
# general function


def getCreds():
    return input('username : '), getpass("pass : ")

## Checks if there is valid cookies stored
# @param towFactor          if true the program will wait for 
#                           user input to save the cookies
# 
# @note                     If the is no cookies, login credentials 
#                           will be requested
def checkLogin(towFactor:bool=False, towFactorConfirmation = lambda : input("Ready to proceed?"),getCreds = getCreds):
    openBrowser()
    login(towFactor, towFactorConfirmation, getCreds)
    closeBrowser()


def login(towFactor=False, towFactorConfirmation = lambda : input("Ready to proceed?"),getCreds = getCreds):
    global username, password
    # open website
    driver.get("https://www.facebook.com")
    previousSession = False

    try:
        cookies = pickle.load(open(cookiesDir, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        pass

        previousSession = True
    except:
        print("cookies not readed")

    driver.get("https://www.facebook.com")

    if not previousSession:
        closeBrowser()

        username, password = getCreds()

        openBrowser()

        # open website
        driver.get("https://www.facebook.com")

        # get xpaths
        cookieButton = driver.find_element(By.XPATH,
            "/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[2]")
        usernameSpace = driver.find_element(By.XPATH,
            "/html/body/div[1]/div[2]/div[1]/div/div/div/div[2]/div/div[1]/form/div[1]/div[1]/input")
        passwordSpace = driver.find_element(By.XPATH,
            "/html/body/div[1]/div[2]/div[1]/div/div/div/div[2]/div/div[1]/form/div[1]/div[2]/div/input")
        loginButton = driver.find_element(By.XPATH,
            "/html/body/div[1]/div[2]/div[1]/div/div/div/div[2]/div/div[1]/form/div[2]/button")

        # Execute Login
        cookieButton.click()
        usernameSpace.send_keys(username)
        passwordSpace.send_keys(password)
        loginButton.click()

        username = ""
        password = ""

        if towFactor:
            towFactorConfirmation()

        ExplicitWait(secs=10, message="waiting for page")
        pickle.dump(driver.get_cookies(), open(
            cookiesDir, "wb"))

    pass

# -------------------------------------------------------------
# List functions


def getChilren(list):
    return list.find_elements(By.XPATH,'//*[@style="padding-left: 8px; padding-right: 8px;"]')
    pass


def scrollBottom(list):
    # inject scroll script
    driver.execute_script(scrollFile, list)
    pass


def scrollAll(list, max):
    global timeout_flag
    # iniciating screen counter
    loadingBar.openCounter("Scrolling", max)

    # scroll while list is not completly loaded
    while len(getChilren(list)) < max:

        # measure list before scroll
        last = len(getChilren(list))

        # debug print
        #print(str(last) + "/" + str(max))

        # scrolling
        scrollBottom(list)

        # start timeout counter
        timeout = 0

        # wait while new items are not loaded
        while last == len(getChilren(list)):
            # safety waiting time
            waiTime = 3
            wait_secs(waiTime)

            # update screen counter
            loadingBar.updateCounter(last)

            # check and raise timeout exception
            timeout += 1
            if timeout*waiTime > 30:
                timeout_flag = True
                raise Exception("Site does not respond")
            pass

        pass

    # safety srcolls
    scrollBottom(list)
    wait_secs(1)
    scrollBottom(list)
    wait_secs(1)

    # dynamic counter last update
    loadingBar.updateCounter(len(getChilren(list))-30)
    # closing used counter
    loadingBar.closeCounter()
    pass


def readProfileList(inputList, total):
    global timeout_readed
    # read all profiles
    profilesList = []

    # inicializating screen counter
    loadingBar.openCounter("reading", total)
    count = 0
    for i in range(total+1):
        # debug print
        # print(i)

        try:
            # get list item by xpath
            item = inputList.find_element(By.XPATH,'.//div[' + str(i) + "]")

            # get link attributed elements
            refList = item.find_elements(By.XPATH,".//*[@role='link']")
            
            react = getReact(refList[0].find_element(By.TAG_NAME,"img").get_attribute('src')) 
            if react == 'angry' or react == 'haha':
                continue
            
            # choosing write link
            href = refList[1].get_attribute('href')
            name = refList[1].text
            
            # cleaning link
            href = linkparse(href)

            # debug print
            # print(href)

            # storing parsed link
            profilesList.append([href,name, react])

        except:
            count += 1
            # deal with unreadable items
            #print('\n.//div[' + str(i+1) + ']/div/div/div[1]/div/a not added')
            pass

        # update screen counter
        loadingBar.updateCounter(i+1)

    # closing used counter
    loadingBar.closeCounter()
    print("profiles readed : " + str(len(profilesList)) + "/" + str(total))
    print("ureadables : " + str(count))
    timeout_readed = str(len(profilesList)) + "/" + str(total)
    return profilesList


def loadAndRead(pathList, total):
    # get list
    list = driver.find_element(By.XPATH,pathList)
    wait_secs(2)

    # scrool all
    try:
        print("hehe")
        scrollAll(list, total)
        # safety scroll
        scrollAll(list, total)
    except BaseException:
        print("scroll went wrong, timeout exception maybe")

    # read all profiles
    return readProfileList(list, total)


# ---------------------------------------------------------------
# post funcions
def getButtonListPost(driver, CoreFile, mode, special = False):
    path : str = CoreFile["page"]["openList"][mode]

    if special : 
        path = path.replace('/span[2]/div/span[2]/', '/div/span/div/span[2]/')
    # path = path.replace('4','5') trouble line
    # val inicialization
    total = 0
    x = 0

    
    total = getButtonListPost(driver, CoreFile, mode, True) if not special else 0

    if total > 0 :
        return total

    # if element is not clickable, search for a parent that is clickable
    while x < 10:
        try:
            try:
                # get element or parent(in case of [element not clickable])
                path = getParentbyPath(path, x)
                # get button
                button = driver.find_element(By.XPATH,path)

                try:
                    # get total number of reaction (it's written in the element)
                    if x == 0:
                        total = int(button.text)
                except ValueError:
                    # deal with non readable values
                    # /html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[1]/span/span
                    # /html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[2]/span/span/text()[1]
                    
                    readable_Path = getCousinbyPath(path)
                    # get button
                    button = driver.find_element(By.XPATH,readable_Path)

                    try:
                        # get total number of reaction (it's written in the element)
                        if x == 0:
                            total = int(button.text)
                    except ValueError:
                        # get element or parent(in case of [element not clickable])
                        print("total not readable")
                        return -1


            except:
                # deal with missing element
                print("button not founded")
                return -1

            button.click()

            # return total of reactions
            return total
        except:
            # exception : element not clickable
            x += 1

    # deal with no valid buttons
    return -1


def getParentbyPath(path, rec=1):
    # if rec == 0 it just return just the path
    if rec < 1:
        return path
    return getParentbyPath(path[0:path.rfind("/")], rec-1)

def getCousinbyPath(path :str, force :bool =False):

    digitIndex = path.rfind("[")+1

    digit = int(path[digitIndex])

    if not digit == 0:
            
        if not force :
            digit = digit - 1
        else:
            digit = digit + 1
    else :
        digit = digit+1

    arr = list(path)
    arr[digitIndex] = str(digit)
    path = ''.join(arr)

    return path


# ---------------------------------------------------------------
# page
def getPageReactsPost(driver, ipost, atempt=2):
    global timeout_flag, timeout_list, timeout_readed
    if "photos" in ipost:
        mode = 0
    if "posts" in ipost:
        mode = 1
    if "videos" in ipost:
        mode = 2


    # get elements xpath
    Div = CoreFile["page"]["list"]
    pathMainDiv = Div["main"]
    pathList = pathMainDiv + Div["List"]

    # atempt couter iniciater
    current = 0

    # profile list iniciator
    profilesList = []

    # try to read for x atempts
    while current < atempt:

        # open post
        driver.get(ipost)

        wait_secs(3)

        # open list
        total = getButtonListPost(driver, CoreFile, mode)
        if total < 0:
            profilesList = []
            current += 1
            total = getButtonListPost(driver, CoreFile, 3)

            if total < 0 :continue

        wait_secs(2)

        try:
            profilesList = loadAndRead(pathList, total)
            if timeout_flag :
                timeout_list.append(ipost)
                timeout_list.append(timeout_readed)
                timeout_flag = False

        except:
            "somthing got wrong in load function"
            profilesList = [[-1]]

        # check timeout exception
        if profilesList[0][0] == -1:
            current += 1
            profilesList = []
        else:

            break

        continue
    # read all profiles
    return profilesList
# ---------------------------------------------------------------

## Reads a list of posts' links and returns the reaction lists
# @param post           posts' list
# 
# @return               dictionary of reaction's lists organized 
#                       by page of collection
def searchForlikes(post:List)->Dict:
    global timeout_list
    openBrowser()
    login()
    wait_secs(6)

    # inicializacions :

    # -success reads list
    done = []
    # -failed reads list
    failed = []
    # -accumulator
    templist = []

    out = {}
    PostsAdress = {}
    # reading all posts
    for item in post:
        print(item)
        linkList = getPageReactsPost(driver, item)
        page = "https://www.facebook.com/" + driver.current_url.split("/")[3]
        new = False

        templist = []

        print(page)
        # checking success and saving results
        if len(linkList) == 0:
            failed.append(item)
        else:
            done.append(item)

        # adding new profiles
        for link in linkList:
            if not link in templist:
                templist.append(link)

        id = driver.current_url.split("/")[3]
        page = linkparse("https://www.facebook.com/" + id)
        if id.isdigit():
            driver.get(page)
            page = "https://www.facebook.com/" + \
                driver.current_url.split("/")[3]

        page = linkparse(page)

        try:
            for collected in templist:
                if not collected in out[page]:
                    out[page].append(collected)
                    PostsAdress[collected[0]] = item

        except:
            out[page] = templist
            for collected in templist:
                PostsAdress[collected[0]] = item


    pp(failed)
    for word in out:
        if len(out[word])>2:
             out[word] = list(map(lambda i: i[:2] + [PostsAdress.get(i[0])] + i[2:], out[word]))
        else:
            out[word] = list(map(lambda i: i + [PostsAdress.get(i[0])], out[word]))

    closeBrowser()
    # read all profiles
    return getAplicableCleanList(out), done, failed, timeout_list


#post = CoreFile["post"]["post"]

#profilesList = searchForlikes(post, username, password)