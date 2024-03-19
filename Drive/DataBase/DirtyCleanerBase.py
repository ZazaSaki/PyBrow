from Browser.Read import closeBrowser, getBrowser, login, openBrowser
from Drive.DataBase.DataManager import getUnVerifyed, removeValids, validate
from General.general import wait_secs, linkparse
from General.loadingBar import closeCounter, complexUpdate, setDisplayInfo


## Clean all the no unique links in the data base
def cleanDirtyLinks():
    openBrowser()
    dirtylinks = getUnVerifyed()

    login()
    wait_secs(3)
    i = 0
    
    setDisplayInfo("item", 0, len(dirtylinks))
    setDisplayInfo("link", "holding", "")
    for link in dirtylinks:
        i += 1
        complexUpdate("item", i)
        complexUpdate("link", link[1])

        getBrowser().get(link[1])

        
        newLink = linkparse(getBrowser().current_url)
        complexUpdate("link", newLink)
        
        if newLink.split("/")[-1].isdigit():
            validate(newLink, False)
        else:
            validate(link[1], True, link[0], newLink)
        
        continue
    
    removeValids()
    closeCounter()
    closeBrowser()
