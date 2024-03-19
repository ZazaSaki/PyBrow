@mainpage Cruzbot
@tableofcontents

@section sec1 Purpose

This bot is built to collect non-negative reactions from facebook page posts, 
compare them to all the collected profiles in google sheets, 
filter all not contacted profiles,
and write all of them back in the google sheets

@section sec2 Functionality

-# DataManager manages a database with all the collected contacts
-# FacebookPageManager manages all the pages that exist with their respective google sheets links:
    * It's loaded manually by Main.pagesMenu
-# OptionManager Loads default options, and manages desired alteration
-# docsUpdaterBase updates the database, collecting information from google sheets:
    * pull all sheets' links from database with FacebookPageManager.getAllPagesSheet()
    * according to the OptionManager information:
        * sets and fixes that google sheet 
        * reads contacts from google sheets 
    * Loads all new information from the sheets in the data base throught the DataManager
    * Update non contacted profiles' sheets (see Main.VerifyIgnoreLinks()) 

-# After updated: 
    * Can read reactions from facebook post's through Main.UpdateLikes() function:
        * with a given facebook account (see Read.checkLogin()):
            * the account cookies are saved for future reads but they can be deleted manually (see Main.forgetFacebookAccount())
        * Sort the collected Likes by page
    * Filter the profiles
    * Write the non-contacted profiles back into the google sheets (see Main.feed_likes())



