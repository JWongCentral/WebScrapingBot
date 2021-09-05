#Requested by a private client that wanted me to write a web scraping code that would
#look at the covers website and constantly update and write down the updated information such as
#the changing odds that each team will win. The purpose of this program was to help him make informed
#decisions on his gambling decisions based off of the data set that he acquired using this code.

#Author: Jack Wong






from bs4 import BeautifulSoup
import requests
import csv
import time
import datetime
import PySimpleGUI as sg
import sys
import os

def makeItLookGood(string):
    #function to just trim some unnecessary characters
    noNums = ''.join(filter(lambda x: not x.isdigit(), string)).replace(' ', '')
    trimmed = ''.join(noNums.split())
    return trimmed

def TrimSpecialCharacter(string,char):
    # function to just trim some unnecessary characters
    return string.replace(char,'')
def TrimSpaces(string):
    # function to just trim some unnecessary characters
    return ''.join(string.split()).replace(' ', '')
def extractNum(string):
    #returns an integer given from the string
    string = TrimSpecialCharacter(string, '%').replace('+', '')
    for word in string.split():
        if word.isdigit():
            return int(word)
def getTime():
    #return a string output of the time
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    d3 = now.strftime('%m/%d/%y')
    if int(current_time[0:2]) >= 12:
        current_time = current_time.replace(current_time[0:2], str(int(current_time[0:2]) - 12))
        return d3+' '+current_time + ' PM'
    return d3+' '+current_time + ' AM'


def findResult(month,day,year):
    #will find the result and write it into the csv files
    
    
    #first it will grab the link and grab the html code from the specific website
    link = 'https://www.covers.com/sports/NBA/matchups?selectedDate='+str(year)+'-'+str(month)+'-'+str(day)
    html_text = requests.get(link).text.encode('utf-8')
    soup = BeautifulSoup(html_text, 'html.parser')
    Dir = soup.find_all('div', class_='cmg_matchup_game_box cmg_game_data')
    if getattr(sys, 'frozen', False): 
        CurrentPath = os.path.dirname(sys.executable)
    else:
        CurrentPath = os.path.dirname(__file__)
    for x in Dir:
        #for each loop to run through the html code to look for the specific team names and filter through each
        #of the team names to grab the corresponding data
        #will return
        #MatchName
            #the name of the match typically the two teams playing
        #Team1, Team2 
            #the name of team 1 playing and team 2 playing
        #Team1Odds, Team2Odds
            #the odds provided on the website of when each time will win
        MatchName = x.find('div', class_='cmg_matchup_header_team_names')
        MatchName = MatchName.text.replace('\n', '').rstrip(' ')
        MatchName = MatchName[1:]
        team1 = x.find('div', class_='cmg_team_name').text
        team1 = makeItLookGood(team1)
        try:
            team1Odds = x.find('div', class_='cmg_matchup_list_column_1').find('div', class_='cmg_matchup_list_odds_value').text
            team1Odds = TrimSpaces(team1Odds)
        except AttributeError:
            team1Odds = '(N/A)'

        team2 = x.find('div', class_='cmg_matchup_list_column_3').find('div', class_='cmg_team_name').text
        team2 = makeItLookGood(team2)
        try:
            team2Odds = x.find('div', class_='cmg_matchup_list_column_3').find('div', class_='cmg_matchup_list_odds_value').text
            team2Odds = TrimSpaces(team2Odds)
        except AttributeError:
            team2Odds = '(N/A)'
            
        #checking CSV File Name to write
        name = str(month)+'_'+str(day)+'_'+str(year)+'_'+MatchName.replace(' ','_').replace('\r','')
        Location = '/posts/'
        FileName = CurrentPath + Location+name+'.csv'
        
        #if the directory does not exist we will make the file/folder names
        if not (os.path.exists(CurrentPath+Location)):
            os.makedirs(CurrentPath+Location)
        try:
            #if the CSV File exist we will read and grab the appropriate data from the file
            #Then check to see if there has been a change from the website and if there has
            #it will write it down to the CSV File
            with open(FileName,'r') as csv_file:
                csv_reader = csv.reader(csv_file,delimiter=',')
                next(csv_reader)
                added = False
                Wchange1 = Wchange2 = 0
                row = []
                for line in csv_reader:
                    row.append(line)
                lastRow = row[-1]
                Tteam1 = lastRow[3]
                Tteam1Odds = lastRow[4]
                Tteam2 = lastRow[6]
                Tteam2Odds = lastRow[7]
                if(Tteam1 == team1 and Tteam1Odds == team1Odds and Tteam2 == team2 and Tteam2Odds ==team2Odds or team1Odds == ''):
                    continue
                else:
                    #if the last row does not match previous results then we know that the odds have changed
                    #therefore we will jot it down, first we need to check if this is the first result or next result
                    team1change = team2change = 0
                    if(team1Odds == '(N/A)' or team1Odds == ''):
                        #no entry added, adding in new entry
                        team1change = Tteam1Odds
                        team2change = Tteam2Odds
                    else:
                        team1change = extractNum(team1Odds)-extractNum(Tteam1Odds)
                        team2change = -1*team1change

                    #Writing the change onto the CSV file
                    #Appending the next row to add the updated data and printing it on the console log
                    with open(FileName, 'a', newline='\n') as csv_file:
                        writer = csv.writer(csv_file, delimiter=',')
                        WTime = getTime()
                        WMatchName = ('' + MatchName).replace('\n', '')
                        WTeam1 = team1
                        WOdds1 = team1Odds
                        WTeam2 = team2
                        Wodds2 = team2Odds
                        if (WOdds1 == ''):
                            WOdds1 = Wodds2 = '(N/A)'
                        writer.writerow([WTime, WTeam1 + ' VS ' + WTeam2, WMatchName, WTeam1, WOdds1, team1change, WTeam2, Wodds2,team2change])
                        print("UPDATE:")
                        print(str(WTime) +  str(WTeam1) + ' VS ' + str(WTeam2) +  str(WMatchName) + str(WTeam1) + str(WOdds1) + str(team1change) + str(WTeam2) + str(WOdds1) + str(team2change))
        except OSError or FileNotFoundError:
            #Will only run if the CSV File we tried to open does not exist
            #therefore we will create the CSV File and write in the first entry
            with open(FileName,'w',newline='\n') as csv_file:
                print(FileName)
                writer = csv.writer(csv_file,delimiter=',')
                WTime = getTime()
                WMatchName = (''+MatchName).replace('\n','')
                WTeam1 = team1
                WOdds1 = team1Odds
                WTeam2 = team2
                Wodds2 = team2Odds
                if(WOdds1 == ''):
                    WOdds1 = Wodds2 = '(N/A)'
                writer.writerow(['Time', 'Playing','Match Name', 'Team1', 'Odds', 'Change','Team2','Odds','Change'])
                writer.writerow([WTime,WTeam1 + ' VS ' +WTeam2, WMatchName,WTeam1,WOdds1,'(N/A)', WTeam2,Wodds2,'(N/A)'])
def mainLoop(SYIN,SMIN,SDIN,EYIN,EMIN,EDIN):
    #Loop that will cycle through the data and write down the time in the console
    #as well as writing it down on the CSV File if needed
    StartDate = datetime.date(int(SYIN), int(SMIN), int(SDIN))
    EndDate = datetime.date(int(EYIN), int(EMIN), int(EDIN))
    delta = datetime.timedelta(days=1)
    while StartDate <= EndDate:
        findResult(StartDate.month, StartDate.day, StartDate.year)
        StartDate += delta
if __name__ == '__main__':
    #Using GUI Setup to create a menu to start and look for specific data sets
    status = display = 'Waiting'
    SMIN = SDIN = SYIN = EMIN= EDIN = EYIN = ''
    timewait = 10
    window = sg.Window('Bot')
    counter = 0;
    while True:
        if (counter <= 1):
            if(SMIN == ''):
                layout = [[sg.Text("Start Date:")],
                      [sg.Text("Month:"), sg.Input(key = '-SMIN-')],
                      [sg.Text("Day:"), sg.Input(key = '-SDIN-')],
                      [sg.Text("Year:"), sg.Input(key = '-SYIN-')],
                      [sg.Text("End Date:")],
                      [sg.Text("Month:"), sg.Input(key = '-EMIN-')],
                      [sg.Text("Day:"), sg.Input(key = '-EDIN-')],
                      [sg.Text("Year:"), sg.Input(key = '-EYIN-')],
                      [sg.Button('Run'), sg.Button('Exit')],
                      [sg.Text(display,key = '-STATUS-')]]
                window = sg.Window('Bot', layout)
                counter+=1
            else:
                layout = [[sg.Text("Start Date:"+SMIN+"-"+SDIN+"-"+SYIN)],
                          [sg.Text("Start Date:"+EMIN+"-"+EDIN+"-"+EYIN)],
                          [sg.Button('Exit')],
                          [sg.Text(display, key='-STATUS-')]]
                window = sg.Window('Bot',layout)
                counter+=1


        if(status == 'Running'):
            event, values = window.read(timeout=1000)
        else:
            event, values = window.read()

        if event == None or event == 'Exit':
            window.close()
            break
        elif(event == 'Run'):
            status = display = "Running"
            window['-STATUS-'].update('Running')
            SMIN = values['-SMIN-']
            SDIN = values['-SDIN-']
            SYIN = values['-SYIN-']
            EMIN = values['-EMIN-']
            EDIN = values['-EDIN-']
            EYIN = values['-EYIN-']
            mainLoop(SYIN,SMIN,SDIN,EYIN,EMIN,EDIN)
            window.close()
        else:
            print(getTime() + " Checked")
            mainLoop(SYIN, SMIN, SDIN, EYIN, EMIN, EDIN)
