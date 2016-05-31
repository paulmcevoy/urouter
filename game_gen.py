# -*- coding: utf-8 -*-
"""
Nice and simple py script to call the script that:
1. Loads the CSVs
2. Looks up the travel times for each route
3. Dumps the data to CSV
4. Uploads the data to a webpage
5. Opens the webpage to play the game!
"""
import os
import time
from urllib.request import pathname2url
import webbrowser

print("Fetching the travel times for every route...")
time.sleep(1)
print("Hold tight the game is about to start...")
time.sleep(2)
import urouter_get_routes 
print(".......")
time.sleep(1)
print("And..")
time.sleep(1)
print("here..")
time.sleep(1)
print("we..")
time.sleep(1)
print("GO!")
time.sleep(2)

#webbrowser.open("http://www.paulmcevoy.ie/urouter.html")
 
#backup in case we want to run local
#url1 = 'file:{}'.format(pathname2url(os.path.abspath('urouter.html')))



