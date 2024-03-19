from hashlib import sha256
from os import link, name
import sqlite3
from typing import List, Tuple

sqlite3.threadsafety = 2
## Connection with database
conn = sqlite3.connect('./Drive/DataBase/amis.db', check_same_thread=False)
# conn = sqlite3.connect(':memory:')

## Python Class : buffer/executer of SQL commands
cursor = conn.cursor()

## Hashes a string in sha256(doc.encode('utf-8')).hexdigest()
# @param doc            string to hash
# @returns              the hexadecimal hashcode in string format
# @see                  hasher
def defaultHash(doc : str)->str:
    return (sha256(doc.encode('utf-8')).hexdigest())

# with conn:
#     cursor.execute("""CREATE TABLE amis (
#             name text,
#             profile text,
#             invalid text
#             )""")

#     cursor.execute("""CREATE TABLE invalid (
#             name text,
#             profile text,
#             verifyed intiger,
#             valid integer
#             )""")


## Filters from a list the contacts not contained in the database after hashing the ids
# @param profiles           list of contacts
# @param table              name of the table in database
# @param comparatorIndex    index of the id
# @returns                  List of filtered contacts
def getNotIncludedWithHashing(profiles, table="amis", comparatorIndex=1)->List:
    if len(profiles) < 1:
        return profiles
    notIncluded = []
    with conn:
        for profile in profiles:
            adress = defaultHash(profile[comparatorIndex])
            cursor.execute(("SELECT * FROM " + table + " WHERE profile LIKE ?"), [adress])
            vals = cursor.fetchall()
            if len(vals) < 1:
                notIncluded.append(profile)
    return notIncluded


## Filters from a list the contacts not contained in the database 
# @param profiles           list of contacts
# @param table              name of the table in database
# @param comparatorIndex    index of the id
# @returns                  List of filtered contacts
# @attention                it also hashed the values to search the hashed version of the elements
# @see                      getNotIncludedWithHashing
def getNotIncluded(profiles, table="amis", comparatorIndex=1)->List:
    if len(profiles) < 1:
        return profiles
    notIncluded = []
    with conn:
        for profile in profiles:
            adress = (profile[comparatorIndex])
            cursor.execute(("SELECT * FROM " + table + " WHERE profile LIKE ?"), [adress])
            vals = cursor.fetchall()
            if len(vals) < 1:
                notIncluded.append(profile)


    notIncludedHash = getNotIncludedWithHashing(profiles, table, comparatorIndex)
    
    notIncluded = list(filter(lambda a : a in notIncludedHash, notIncluded))

    return notIncluded


## @param table             name of the table in database
# @returns                  every item in the database
def getAll(table:str="amis")->List:
    with conn:
        cursor.execute("SELECT * FROM "+table)
        return cursor.fetchall()

## @param table             name of the table in database
# @returns                  one item in the database
def getOne(table:str="amis")->List:
    cursor.execute("SELECT * FROM " + table)
    return cursor.fetchone()


## Hashes a gien tuple, in order to prepare it to insert
#
# @param t                 tuple of a table element
# @param comparatorIndex    index of the id's position
# @param table              the destination table of the tuble
# @returns                  the hashed version of the given tuble: 
# @warning                  Behavior :
#                           - if table different than "amis" : 
#                               - only it hashes the comparater idex position
#                           - else :  
#                               - it every single element of the tuple
# @attention                It hashes with defaultHash function
# @see                      defaultHash    
def hasher(t : Tuple, comparatorIndex:int = 1, table:str = 'amis')->tuple:
    t = list(t)
    
    
    if table=='amis':
        t = list(map(lambda a : defaultHash(a) if not a == '' else a, t))
        
    else:
        t[comparatorIndex] = defaultHash(t[comparatorIndex])

    t = tuple(t)
    return t

## Insert elements in a given table
# 
# @param elems              list of contacts
# @param table              name of the table in database
# @param comparatorIndex    index of the id
# 
# @returns                  not inserted
# 
# @note                     If contact is repeated, it used the 
#                           extra information to fill the gaps
def insertElems(elems:List, table:str="amis", comparatorIndex:int=1)->List:
    #elems - requested list
    #toInsert - list with the non included values from the requested list 

    #cheking the given list
    if len(elems) < 1:
        return []
    
    #filtering the not included values to insert
    toInsert = getNotIncluded(elems, table, comparatorIndex)
    if len(toInsert) < 1 : print("no new profiles founded")
    
    #creating the insert special string
    insertString = "("
    for e in elems[0] :
        insertString += " ? ,"
    insertString = insertString[:-1]+")"

    hashedElems = list(map(lambda a : hasher(a, comparatorIndex, table), elems))
    hashedToInsert = list(map(lambda a : hasher(a, comparatorIndex, table), toInsert))

    with conn:
        command ="INSERT INTO " + table + " VALUES "+ insertString
        cursor.executemany(command, hashedToInsert)
    return list(filter(lambda a : not a in toInsert, elems))



## Checks if a profile link is in the database
# @param profiles           link to search
# @returns                  *True* if contains or *False* if it doesn't
def IsInDataBase(profile:str)->bool:
    invalids =[]
    valids = []

    id = defaultHash(profile)
    with conn:
        cursor.execute("SELECT * FROM amis WHERE profile LIKE ?", [id])
        valids = cursor.fetchall()
        cursor.execute("SELECT * FROM invalid WHERE profile LIKE ?", [id])
        invalids = cursor.fetchall()

        cursor.execute("SELECT * FROM amis WHERE profile LIKE ?", [profile])
        valids = valids + cursor.fetchall()
        cursor.execute("SELECT * FROM invalid WHERE profile LIKE ?", [profile])
        invalids = invalids + cursor.fetchall()
    
    if len(valids)+len(invalids)<1:
        return False
    else :
        return True

## Gets a contact from a given link
# @param link               link of the contact
# @returns                  contact if contained
def getProfile(link:str)->List:
    id = defaultHash(link)
    with conn:
        cursor.execute("SELECT * FROM amis WHERE profile LIKE ?", [id])
        return cursor.fetchone()

## Fills empty info of a contact from 
# a repeated given contact 
# @param profile            profile to write from
# @note                     contact = [name, link, verified, valid]
def FillEmptyInfo(profile:List):
    newName, link, newInvalid = profile

    link == defaultHash(link)

    name, link, invalid = getProfile(link)

    if len(name) < 1 and len(newName)>1:
        with conn:
            cursor.execute("UPDATE amis SET name = ? WHERE profile = ?", [newName, link])
    
    if len(invalid) < 1 and len(newInvalid)>1:
        with conn:
            cursor.execute("UPDATE amis SET invalid = ? WHERE profile = ?", [newName, link])

## Insert profiles in the table of the clean links 
# 
# @param profile            list of contacts
# 
# @returns                  number of not inserted
# 
# @note                     Contact = [name, profile(*id*), invalid link]
#                           if contact is repeated, it used the 
#                           extra information to fill the gaps
# @note                     contact = [name, link, invalid link]
def insertProfiles(profiles:List)->int:
    left = insertElems(profiles)
    for profile in left:
        FillEmptyInfo(profile)
    pass

    return len(left)

## Insert a profile in the table of the clean links 
# 
# @param profile            contacts
# @see insertProfiles
def insertProfile(profile:List)->int:
    return insertProfiles([profile])

## Insert profile links in the table of the clean links 
# 
# @param links            list of links
def insertProfileLinks(links:List)->int:
    profiles = list(map(lambda a: ("", a, ""), links))
    return insertProfiles(profiles)

## Insert a profile link in the table of the clean links 
# 
# @param link           link
# @see                  insertProfileLinks
def insertProfileLink(link:str)->int:
    return insertProfileLinks([link])


## Insert profile names and links in the 
# table of the clean links when invalid links are unknown 
# 
# @param links          list of contacts
# @note                 item = [name, profile link]
# @see                  insertProfileLinks
def insertProfileNameNLinks(links:List)->int:
    profiles = list(map(lambda a: (a[0], a[1], ""), links))
    return insertProfiles(profiles)

## Insert a profile without the invalid link 
# in the table of the clean links 
# 
# @param name           name of the contact
# @param link           link of the contact
# @see                  insertProfileNameNLinks
def insertProfileNameNLink(name:str, link:str)->int:
    return insertProfiles([name, link])

## Find duplicated contacts
# @return list of duplicates
# @attention Very long running time
def findDuplicateds()->List:
    All = getAll()
    Duplicateds = []
    with conn:
        for profile in All:
            adress = (profile[1])
            cursor.execute(
                "SELECT rowid, * FROM amis WHERE profile LIKE ?", [adress])
            vals = cursor.fetchall()
            if len(vals) > 1:
                if not vals[0][2] in Duplicateds:
                    Duplicateds.append(vals[0][2])

    return Duplicateds


## Remove duplicates
# @attention Very long run time
# @see       findDuplicateds
def RemoveDuplicateds():
    Dupl = findDuplicateds()
    jump = []
    with conn:
        for d in Dupl:
            cursor.execute(
                "SELECT rowid, * FROM amis WHERE profile LIKE ?", [d])
            vals = cursor.fetchall()
            (id, name, profile, inv) = vals[0]
            for v in vals:
                if len(name) < len(v[1]):
                    name = v[1]
                if len(inv) < len(v[3]):
                    inv = v[3]
                if not id == v[0]:
                    cursor.execute("DELETE from amis WHERE rowid = ?", [v[0]])

            cursor.execute(
                "UPDATE amis SET name = ?, invalid = ? WHERE rowid = ?", [name, inv, id])

## Verifies if a clean link is in the database
# @param profile        link to search for
# @return               *True* if found or *False* if not 
def IsInCleanedLinks(profile:str)->bool:
    profile = defaultHash(profile)
    valids = []
    with conn:
        cursor.execute("SELECT * FROM amis WHERE profile LIKE ?", [profile])
        valids = cursor.fetchall()

    if len(valids)<1:
        return False
    else :
        return True

## Verifies if an invalid link is in the database
# @param link           link to search for
# @return               *True* if found or *False* if doesn't 
def IsInDirtyLinks(link:str)->bool:
    id = defaultHash(link)
    valids = []
    with conn:
        cursor.execute("SELECT * FROM amis WHERE invalid LIKE ?", [link])
        valids = cursor.fetchall()
        cursor.execute("SELECT * FROM amis WHERE invalid LIKE ?", [link])
        valids = valids + cursor.fetchall()

    if len(valids)<1:
        return False
    else :
        return True

## @return All invalid links that have been fixed
def getDirtyLinks()->List:
    with conn:
        cursor.execute("SELECT invalid FROM amis")
        return list(map(lambda a : a[0], cursor.fetchall()))

## Filters from a list the contacts' links not contained in the database
# @param profiles           list of contacts
# @param offset             index of the id
# @returns                  List of filtered contacts
# @note                     Contact = link
def filterList(profiles:List, offset:int = 0)->List:
    validList = []
    
    cursor.execute("SELECT profile FROM amis")
    validList = list(map(lambda a : a[0], cursor.fetchall()))

    return list(filter(lambda a : (not (defaultHash(a[offset])) in validList), profiles))

## Gets a contact from a given link in the invalids link table
# @param link               link of the contact
# @returns                  contact if contained
# @note                     Contact = [name, link, invalid]
def getInvalidProfile(link:str)->List:
    with conn:
        cursor.execute("SELECT * FROM invalid WHERE profile LIKE ?", [link])
        return cursor.fetchone()

## Fills empty info of a contact from 
# a repeat given contact, in invalid list
# @param profile            profile to write from
# @note                     contact = [name, link, verifyed, valid]
def FillEmptyInfoInvalid(profile:List):
    newName, link, v, vv = profile

    dataSample = getInvalidProfile(link)

    if dataSample == None:
        dataSample = getInvalidProfile(defaultHash(link))
    
    name, link, v, vv = dataSample


    if len(name) < 1 and len(newName)>1:
        with conn:
            cursor.execute("UPDATE invalid SET name = ? WHERE profile = ?", [defaultHash(newName), link])
    
## Inserts profiles in the table of the invalid links 
# @warning                  internal version
# 
# @param profile            list of contacts
# 
# @returns                  number of not inserted
# 
# @note                     Contact = [name, link, verifyed, valid]
#                           if contact is repeated, it used the 
#                           extra information to fill the gaps
#
# @see                      insertInvalidProfiles
def insertInvalid(profiles:List)->int:
    dt = getDirtyLinks()
    ins = list(filter(lambda a : not defaultHash(a[1]) in dt, profiles))
    left = insertElems(ins, table="invalid", comparatorIndex=1)
    for profile in left:
        FillEmptyInfoInvalid(profile)
    pass
    return len(left)

## Inserts profiles in the table of the invalid links 
# @attention                user version
# 
# @param profile            list of contacts
# 
# @returns                  number of not inserted
# 
# @note                     Contact = [name, link]
#                           if conatct is repeated it used the 
#                           extra information to fill the gaps
def insertInvalidProfiles(profiles:List)->int:
    invalids = list(map(lambda a: (a[0],a[1] , 0, 0), profiles))
    return insertInvalid(invalids)

## Inserts a profile without the invalid link 
# in the table of the invalid links 
# 
# @param name           name of the contact
# @param profile        profile of the contact
# @see                  insertInvalidProfiles, insertInvalid
def insertInvalidProfile(name:str, profile:str)->int:
    return insertInvalidProfiles([[name, profile]])

## Inserts profile links in the table of the invalid links 
# 
# @param profiles            list of links
# @see                       insertInvalid
def insertInvalidLinks(profiles:List)->int:
    invalids = list(map(lambda a: ("", a, 0, 0), profiles))
    return insertInvalid(invalids)

## Inserts a profile link in the table of the invalid links 
# 
# @param profile            link
# @see                      insertInvalid
def insertInvalidLink(profile:str)->int:
    return insertInvalidLinks([profile])

## Validates a profile in invalid table 
# and adds the profile to the clean table
# @param dirtyProfile       invalid link
# @param valid              *bool* is validatable 
#                           to the invalid link
# @param name               name of the profile
# @param validLink          valid link relative
# @see                      DirtyCleanerBase
def validate(dirtyProfile:str, valid:bool, name:str = None, validLink:str=None):
    if valid:
        v = 1
        if IsInCleanedLinks(validLink):
            with conn:
                cursor.execute("UPDATE amis set invalid = ? WHERE profile LIKE ?", [dirtyProfile, validLink])
        else:
            insertProfile((name, validLink, dirtyProfile))
    else:
        v = 0

    with conn:
        cursor.execute("UPDATE invalid set verifyed = 1, valid = ? WHERE profile LIKE ?", [v, dirtyProfile])

## Remove all validated links in invalids table
# @see          DirtyCleanerBase
def removeValids():
    with conn:
        cursor.execute("DELETE FROM invalid WHERE verifyed = 1 AND valid = 1")
    pass

## @return      all unverified links from invalid table
# @see          DirtyCleanerBase
def getUnVerifyed()->List:
    with conn:
        cursor.execute("SELECT name, profile FROM invalid WHERE verifyed = 0")
        return cursor.fetchall()
# test

def getInvalid()->List:
    with conn:
        cursor.execute("SELECT name, profile FROM invalid WHERE valid = 0 AND verifyed = 1")
        return cursor.fetchall()

def hashInvalids():
    
    with conn : 
        mem = getInvalid()
        for elem in mem:
            cursor.execute("UPDATE invalid set profile = ? WHERE profile LIKE ? AND valid = 0 AND verifyed = 1", [defaultHash(elem[1]), elem[1]])
            cursor.execute("UPDATE invalid set name = ? WHERE profile LIKE ? AND valid = 0 AND verifyed = 1", [defaultHash(elem[0]), defaultHash(elem[1])])


        cursor.execute("UPDATE invalid set verifyed = -1 WHERE valid = 0 AND verifyed = 1")
    
    # with conn:
    #     cursor.execute("SELECT profile,name,invalid FROM amis")
    #     amis = cursor.fetchall()
    #     i = 0
    #     for ami in amis:
    #         i+=1
            
    #         if not ami[2] == '' and not ami[1] == '':
    #             cursor.execute("UPDATE amis SET profile = ?, name = ?, invalid = ?  WHERE profile LIKE ?", [defaultHash(ami[0]),defaultHash(ami[1]),defaultHash(ami[2]), ami[0]])
    #         elif not ami[2] == '':
    #             cursor.execute("UPDATE amis SET profile = ?, invalid = ? WHERE profile LIKE ?", [defaultHash(ami[0]),defaultHash(ami[2]), ami[0]])
    #         elif not ami[1] == '':
    #             cursor.execute("UPDATE amis SET profile = ?, name = ? WHERE profile LIKE ?", [defaultHash(ami[0]),defaultHash(ami[1]), ami[0]])
    #         else:
    #             cursor.execute("UPDATE amis SET profile = ? WHERE profile LIKE ?", [defaultHash(ami[0]), ami[0]])

    
    
    

def test():
    many_amis = [
        ('nom', 'pro', 'inv'),
        ('nom', 'prof', 'inv'),
        ('other', 'hubfgoiuer', 'inv'),
        ('nom', 'pro', 'inviushogivseul'),
        ('nom', 'pro', 'inv')
    ]

    many_invalid = [
        ("name1", "prof1", 0, 0),
        ("name2", "prof2", 1, 1),
        ("name3", "prof3", 1, 0),
        ("name4", "prof4", 0, 0)
    ]

    insertInvalid(many_invalid)
    insertProfiles(many_amis)

    AllRecords = getAll()
    AllInvalids = getAll("invalid")

    print("List Test")

    # repeat list
    try:
        print("Refusing repeat List :", end=" ")
        insertProfiles(many_amis)
        insertProfileLinks([many_amis[1][1], many_amis[2][1]])
        if not len(AllRecords) == len(getAll()):
            print("failed, didn't filter")
            print(getAll())
        else:
            print("passed")

    except:
        print("failed run time error")

    # repeated value
    try:
        print("Refusing repeat profile :", end=" ")
        insertProfile(many_amis[1])
        insertProfileLink(many_amis[3][1])
        if not len(AllRecords) == len(getAll()):
            print("failed, didn't filter")
            print(getAll())
        else:
            print("passed")

    except:
        print("failed run time error")

    # new value
    try:
        print("Add profile :", end=" ")
        insertProfiles([('pro', 'praaaa', '')])
        insertProfileLinks(["peia", "novo"])
        if not (len(AllRecords)+3) == len(getAll()):
            print("didn't added")
            print(getAll())
        else:
            print("passed")

    except:
        print("failed run time error")

    AllRecords = getAll()

    # new value mixed with repeated value
    try:
        print("Add profile and refuse repeated :", end=" ")
        insertProfiles([('pro', 'pra', 'inv'), many_amis[1], ('pro', 'novo', 'qualquer')])
        if not (len(AllRecords)+1) == len(getAll()):
            print("didn't filter or added")
            print(getAll())
        else:
            print("passed")

    except:
        print("failed run time error")

    AllRecords = getAll()

    # delete duplicated values
    try:
        print("delete repeated :", end=" ")
        RemoveDuplicateds()
        if not (len(AllRecords)-2) == len(getAll()):
            print("didn't delete")
            print(getAll())
        else:
            print("passed")

    except:
        print("failed run time error")

    AllRecords = getAll()
    # duplicated values over delete
    try:
        print("refuse over delete :", end=" ")
        RemoveDuplicateds()
        if not (len(AllRecords) == len(getAll())):
            print("over delete")
            print(getAll())
        else:
            print("passed")

    except:
        print("failed run time error")

     # repeat list

    # Inavlid Table tests-----------------------------------------------------------------
    # refuse repeated list
    print("\n\nInvalid Lists tests\n")
    try:
        print("Refusing repeat List :", end=" ")
        insertInvalid(many_invalid)
        insertInvalidLinks([many_invalid[0][1], many_invalid[1][1]])
        if not len(AllInvalids) == len(getAll("invalid")):
            print("failed, didn't filter")
            print(getAll("invalid"))
        else:
            print("passed")

    except:
        print("failed run time error")

    # repeated value
    try:
        print("Refusing repeat profile :", end=" ")
        insertInvalid([many_invalid[1]])
        insertInvalidLink(many_invalid[1][1])
        if not len(AllInvalids) == len(getAll("invalid")):
            print("failed, didn't filter")
            print(getAll("invalid"))
        else:
            print("passed")

    except:
        print("failed run time error")

    # new value
    try:
        print("Add profile :", end=" ")
        insertInvalid([("", 'peia', 0, 0)])
        insertInvalidLink("prof5")
        insertInvalid([("name", 'peia', 0, 0)])
        insertInvalidProfile("name","prof5")
        if not (len(AllInvalids)+2) == len(getAll("invalid")):
            print("didn't added")
            print(getAll("invalid"))
        else:
            print("passed")

    except:
        print("failed run time error")

    AllInvalids = getAll("invalid")

    # new value mixed with repeated value
    try:
        print("Add profile and refuse repeated :", end=" ")
        insertInvalid([("name", 'proa', 0, 0), many_invalid[1]])
        insertInvalidLinks(["prof6", many_invalid[2][1]])
        if not (len(AllInvalids)+2) == len(getAll("invalid")):
            print("didn't filter or added")
            print(getAll())
        else:
            print("passed")

    except:
        print("failed run time error")

    AllInvalids = getAll("invalid")

    try:
        print("Validating one and Removing invalids :", end=" ")
        validate("proa", 0)
        validate("peia", 1, "newLink")
        removeValids()
        if not (len(AllInvalids)-2) == len(getAll("invalid")):
            print("not removed or not validated")
            print(getAll())
        else:
            print("passed")

    except:
        print("failed run time error")


# test()