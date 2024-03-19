import sqlite3
from typing import List
from .DataManager import conn, cursor

# with conn:
#     cursor.execute("""CREATE TABLE page (
#                     name text,
#                     link text,
#                     sheet text
#     )""")

## @return all pages' names
def getAllPagesNames()->List:
    cursor.execute("SELECT name FROM page")
    return list(map(lambda a : a[0], cursor.fetchall()))

## @return all pages' sheets' links
def getAllPagesSheet()->List:
    cursor.execute("SELECT sheet FROM page")
    return list(map(lambda a : a[0], cursor.fetchall()))

## @return all pages
def getAllPages()->List:
    cursor.execute("SELECT * FROM page")
    return cursor.fetchall()

## Add a page to the table
# @param name           name of the page
# @param link           link of the page
# @param sheet          page's sheet link
def addPage(name:str, link:str, sheet:str):
    with conn:
        cursor.execute("INSERT INTO page VALUES (?, ?, ?)", [name, link, sheet])


## Search for a name in pages
# @param name           name to search
# @return               all pages containing the name
def SearchPage(name:str)->List:
    cursor.execute("SELECT name FROM page WHERE name LIKE ?", ["%" + name + "%"])
    return cursor.fetchall()

## Search for a page name
# @param name           name to search
# @return               page with the exact name
def getPageByName(name:str)->List:
    cursor.execute("SELECT * FROM page WHERE name LIKE ?", [name])
    return cursor.fetchall()

## Search for a page link
# @param link           link to search
# @return               page with the exact link
def getPageByLink(link:str)->List:
    cursor.execute("SELECT * FROM page WHERE link LIKE ?", [link])
    return cursor.fetchall()

## Search for a page sheet
# @param sheet          sheet's link to search
# @return               page with the exact sheet
def getPageBySheet(sheet:str)->List:
    cursor.execute("SELECT * FROM page WHERE sheet LIKE ?", [sheet])
    return cursor.fetchall()

## Update a page's link with a given name
# @param name           pages's name to update
# @param link           pages's updated link
def updateLink(name:str, link:str):
    with conn:
        cursor.execute("UPDATE page SET link = ? WHERE name LIKE ?", [link, name])

## Update a page's sheet with a given name
# @param name           pages's name to update
# @param sheet          pages's updated sheet link
def updateSheet(name:str, sheet:str):
    with conn:
        cursor.execute("UPDATE page SET sheet = ? WHERE name LIKE ?", [sheet, name])

## Removes a page with a given name
# @param name           pages's name to remove
def removePage(name:str):
    with conn:
        cursor.execute("DELETE FROM page WHERE name LIKE ?", [name])
