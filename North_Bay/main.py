import requests
#import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#import json
import pprint

def main():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Scouting2023").sheet1

    baseURL = "https://www.thebluealliance.com/api/v3" 
    key = "SBns9CVvJ6TAl3q6keafIY9DKuBd2tlyZLlrOqR6djId1C07TNQVcYaM3OmN6xso"
    header = {"X-TBA-Auth-Key": key}
    status = requests.get(baseURL + "/status", headers=header)
    if (status.status_code != 200):
        print("we not vibin")
        return

    EVENT = '2023onnob'
    pp = pprint.PrettyPrinter()

    team_keys_response = requests.get(baseURL + "/event/"+EVENT+"/teams/keys", headers=header)
    teams_response = requests.get(baseURL + "/event/"+EVENT+"/teams", headers=header)
    teams = teams_response.json()
    if team_keys_response.status_code != 200:
        print("we key ain't vibin")
        return
    team_keys_json = team_keys_response.json()
    
    team_keys = TeamKeys(team_keys_json)
    teams_len = len(teams)
    # teams_formatted = [ ['']*8 for i in range(teams_len)]

    teams_formatted = [['' for _ in range(8)] for _ in range(teams_len)]


    events = []
    pictures = ['']*teams_len

    #data[0...i] -> rows where i == team_keys[i]
    #data[i][0] team number
    #data[i][1] team nickname
    #data[i][2] picture
    #data[i][3] rookie year
    #data[i][4] event ranking
    #data[i][5] district ranking
    #data[i][6] opr
    #data[i][7] awards
    #data[i][8] events (this year)



    
    i = 0
    for team in team_keys.team_keys:
        print(team)

        media = requests.get(baseURL + "/team/"+team+"/media/2023", headers=header)
        if media != []:
            media_json = media.json()
            for item in media_json:
                if('direct_url' in item and item['direct_url'] != ''):
                    # pictures[team_keys.team_key_to_index(team)] = item['direct_url']
                    pictures[i] = item['direct_url']


        teamEvents = requests.get(baseURL + "/team/"+team+"/events/2023/keys", headers=header)
        for teamEvent in teamEvents.json():
            isInTeamEvent = False
            for event in events:
                if event == teamEvent:
                    isInTeamEvent = True
                    break
            if not isInTeamEvent:
                events.append(teamEvent)

            # if teamEvent == "2023ilch":
            #     print(team + " is in illionoioi")

        i += 1


    #oprs = requests.get(baseURL + "/event/{event_key}/oprs", headers=header)

    for i in range(teams_len):
        team_list = [teams[i]['team_number'], 
                     teams[i]['nickname'], 
                     pictures[i], 
                     teams[i]['rookie_year'],
                     '',
                     '',
                     '']
        teams_formatted[i] = team_list
        print(i)

    pp.pprint(teams_formatted)
        
    sheet.update('A2:H'+str(teams_len+2), teams_formatted)

    return

class TeamKeys:
    def __init__(self, team_keys):
        self.hashmap = [-1]*9999
        self.team_keys = team_keys
        i = 0
        for team_key in team_keys:
            print(team_key)
            self.hashmap[i] = int(team_key[3:])
            i += 1

    def team_key_to_index(self, key):
        return self.hashmap[int(key[3:])]

    # def __iter__(self):
    #     return self

    # def __next__(self):
    #     return self.team_keys.next()


if __name__ == "__main__":
    main()
