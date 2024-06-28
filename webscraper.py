import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json

def openingBrowser( indexName, gamesFoundedCont ):

    print("Wait 5 seconds...")
    time.sleep(5) #Website loading...

    acceptCookies()
    startingScrapper( indexName, gamesFoundedCont )

def acceptCookies():

    try:
        
        print("Accepting the cookies...")
        browser.find_element(By.ID, 'onetrust-accept-btn-handler').click() #Clicking in Accept cookies
    except:

        pass

def startingScrapper( indexName, gamesFoundedCont ):

    input = browser.find_element(By.XPATH, "//div[@class='MainNavigation_search__mL_ux']//input") #Getting the search input
    input.send_keys(gameName[indexName])
    input.send_keys(Keys.RETURN)
    
    time.sleep(5)
    #Verify if founded the game
    try:

        browser.find_element(By.XPATH, "//div[@class='GameCard_search_list_image__B2uLH']//a").click() #The game searched
        getDetails( gameName[indexName], indexName, gamesFoundedCont )

    except:

        print(f"\033[0;31m{gameName[indexName]} NOT FOUND!\033[m")
        gamesNotFound.append(gameName[indexName])

        anotherGame( indexName, gamesFoundedCont )

def getDetails( game, indexName, gamesFoundedCont ):

    print(f'\033[0;33m[{indexName + 1} / {len(gameName)}]\033[m')
    print(f"Getting the data of \033[0;33m{game}...\033[m")

    time.sleep(5)

    #Getting the details

    #Main Story, Main + Sides, Completionist and All Styles
    gameTime = browser.find_element(By.CSS_SELECTOR, '.GameStats_game_times__KHrRY.shadow_shadow') 
    gameTimeHTML = gameTime.get_attribute('outerHTML')

    #Description of the game
    gameDesc = browser.find_element(By.CSS_SELECTOR, '.GameSummary_profile_info__HZFQu.GameSummary_large__TIGhL')
    gameDescHTML = gameDesc.get_attribute('outerHTML')

    #Filtering the text

    #Because of the Read More button, we need remove this part of the text
    if ' ...Read More' in gameDescHTML:

        gameDescHTML = gameDescHTML.replace(' ...Read More', '')
    if '\r\n\r\n' in gameDescHTML:

        gameDescHTML = gameDescHTML.replace('\r\n\r\n', ' ')
    
    #Developer of the game

    extraDetailsDivs = browser.find_elements(By.CSS_SELECTOR, '.GameSummary_profile_info__HZFQu.GameSummary_medium___r_ia') #This var contains the developer and platforms of the game

    gameDeveloper = ''
    #This loop is necessary because the page of the game have more than one div with the same class, we want only the developer info
    for div in extraDetailsDivs:

        div = BeautifulSoup(div.get_attribute('outerHTML'), 'html.parser')

        if 'Developer' in div.text:

            gameDeveloper = div.text

    #Platforms
    
    gamePlatforms = ''
    for div in extraDetailsDivs:

        div = BeautifulSoup(div.get_attribute('outerHTML'), 'html.parser')

        if 'Platform' in div.text:

            gamePlatforms = div.text

    #Using BeautifulSoup4

    gameTimeSoup = BeautifulSoup(gameTimeHTML, 'html.parser')
    gameTimeSoup = gameTimeSoup.find(name='ul')
    gameDescSoup = BeautifulSoup(gameDescHTML, 'html.parser')
    
    #Converting HTML for Data frame with panda

    #Getting the main story, main + sides...
    data = []
    for li in gameTimeSoup.find_all('li'):

        h5 = li.find(name="h4").text #Title of the box
        h4 = li.find(name="h5").text #The time
        data.append({"title":h5, "time": h4})

    gameTimePd = pd.DataFrame(data)
    
    #Putting everthing in a Dictionary

    games={}
    games['name'] = game
    games['details'] = gameTimePd.to_dict("records")
    games['description'] = gameDescSoup.text
    games['developer'] = gameDeveloper
    games['Platforms'] = gamePlatforms

    savingTheJSON( games, indexName, gamesFoundedCont )

def savingTheJSON( gameDetails, indexName, gamesFoundedCont ):

    #Verify if game.json exist
    try:
        
        with open('games.json', 'r') as jsonFileRead:

            print('\033[0;34mReading the games.json...\033[m')

            #If games.json have value, this will load
            try:
                    
                gamesJsonValue = json.load(jsonFileRead)

            #If dont, the file is blank
            except:

                gamesJsonValue = ''

            jsonFileRead.close()

        #Joining the old data with the new
    
        valueForJson = []
        if gamesJsonValue == '':

            valueForJson.append(gameDetails)

        else:

            valueForJson = gamesJsonValue 
            valueForJson.append(gameDetails)
        
        jsonValue = json.dumps(valueForJson)
        jsonFile = open("games.json", "w") #If the file dont exists, then will create

        print("\033[0;34mWriting in games.json...\033[m")
        jsonFile.write(jsonValue)
        jsonFile.close()

        gamesFoundedCont += 1
        anotherGame( indexName, gamesFoundedCont )

    except:

        print('\033[0;31mTHE [ games.json ] FILE WAS NOT FOUND! PLEASE, CHECK IF THE NAME IS CORRECT OR THA FILE HAS BEEN CREATED...\033[m')
        anotherGame( len(gameName), gamesFoundedCont )

def anotherGame( indexName, gamesFoundedCont ):

    cont = indexName
    cont += 1
    
    #Process finished
    if cont >= len(gameName):

        print('\033[0;33mClosing browser...\033[m')
        browser.quit()

        #Showing games not founded
        if gamesNotFound != []:

            print(f'\033[0;31m{len(gamesNotFound)} GAMES NOT FOUNDED!\033[m')
            print(f'\033[0;34mWriting in gamesNotFound.json\033[m')
            writingGamesNotFound()

        print(f'\033[0;33m[{gamesFoundedCont} / {len(gameName)}] games founded\033[m')   
        print('\033[0;33mAll done!\033[m')
        
    else:

        input = browser.find_element(By.XPATH, "//div[@class='MainNavigation_search__mL_ux']//input") #Getting the search input
        input.clear()
        browser.find_element(By.CLASS_NAME, "MainNavigation_brand__zco7a").click()
        time.sleep(5)

        indexName = cont
        startingScrapper( indexName, gamesFoundedCont )

def writingGamesNotFound():

    jsonValue = json.dumps(gamesNotFound)
    jsonFile = open("gamesNotFound.json", "w")
    jsonFile.write(jsonValue)
    jsonFile.close()

#Starts here

url = 'https://howlongtobeat.com/'
gameName = [''] #Put the name of the games here
  
gamesNotFound = []
indexName = 0 #This var choice the next game of the list gameName
gamesFoundedCont = 0 #This var count how many games have been founded

#Welcome message
print('=== \033[0;33mWelcome to Web Scraper HL2B\033[m ===')
print('\033[0;36mby Arthur de Araujo Neves\033[m')
print('\033[0;36mMy Github: https://github.com/ArthurDeAraujoNeves3 \033[m')
print('\033[0;36mJust chill and relax, and let me make the hard work for you ;)\033[m')
print('\033[0;33mOpening browser...\033[m')

#Starting the browser
option = Options()
option.add_argument('--headless') #Make all the process run in background 
browser = webdriver.Firefox() #Opening the browser
browser.get(url) #Opening the page howlongtobeat.com

#Getting the game names in youtGames.json
try:

    with open("yourGames.json", "r") as yourGamesFile:

        names = json.load(yourGamesFile)
        gameName = names

        openingBrowser( indexName, gamesFoundedCont )
    
except: 

    print("\033[0;31myourGames.json IS BLANK! PLEASE, INSERT THE NAME OF THE GAME THERE!\033[m")
    anotherGame( len(gameName), gamesFoundedCont )
