from gspread.worksheet import ValueInputOption
import requests
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#import json
import pprint
from PIL import Image
import io
import opr
import logging
from tqdm import tqdm

def update_basic_data():
    tqdm.write("Configuring Google Sheets and TBA credentials")
    logging.basicConfig(filename='main.log', encoding='utf-8', level=logging.DEBUG)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    baseURL = "https://www.thebluealliance.com/api/v3" 
    key = "SBns9CVvJ6TAl3q6keafIY9DKuBd2tlyZLlrOqR6djId1C07TNQVcYaM3OmN6xso"
    header = {"X-TBA-Auth-Key": key}

    tqdm.write("Starting TBA session")
    s = requests.Session()
    s.headers.update(header)

    status = s.get(baseURL + "/status")
    if (status.status_code != 200):
        logging.error("we not vibin")
        return

    EVENT = '2023onnob'
    DISTRICT = '2023ont'
    pp = pprint.PrettyPrinter()

    tqdm.write("Fetch team data")
    team_keys_response = s.get(baseURL + "/event/"+EVENT+"/teams/keys")
    teams_response = s.get(baseURL + "/event/"+EVENT+"/teams")
    teams = teams_response.json()
    if team_keys_response.status_code != 200:
        logging.error("we key ain't vibin")
        return
    team_keys_json = team_keys_response.json()
    
    team_keys = TeamKeys(team_keys_json)
    teams_len = len(teams)
    # teams_formatted = [ ['']*8 for i in range(teams_len)]

    teams_formatted = [['' for _ in range(8)] for _ in range(teams_len)]

    tqdm.write("Get district rankings")
    district_response = s.get(baseURL + "/district/"+DISTRICT+"/rankings")
    district_json = district_response.json()
    district_team_number_indices = {}
    i = 0
    for team in (pbar := tqdm(district_json)):
        pbar.set_description(f"Getting ranking of {team['team_key']}")
        district_team_number_indices[team['team_key']] = i
        i += 1

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
    for team in (pbar := tqdm(team_keys.team_keys)):
        pbar.set_description(f"Fetching {team} media")
        logging.info(team)

        media = s.get(baseURL + "/team/"+team+"/media/2023")
        if media != []:
            media_json = media.json()
            for item in media_json:
                if('direct_url' in item and item['direct_url'] != '' and item['type'] != "instagram-image"):
                    # pictures[team_keys.team_key_to_index(team)] = item['direct_url']
                    direct_url = item['direct_url']
                    imgcellval = '=IMAGE("' + direct_url + '", 1)'
                    pictures[i] = imgcellval
                elif ('direct_url' in item and item['direct_url'] != ''):
                    pictures[i] = item['view_url']
                    


        pbar.set_description(f"Fetching {team} events")
        teamEvents = s.get(baseURL + "/team/"+team+"/events/2023/keys")
        if team == 'frc1334':
            logging.debug("1334's events: %s", teamEvents.json())
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


    #oprs = s.get(baseURL + "/event/{event_key}/oprs")
    #matches = s.get(baseURL + "/event/"+EVENT+"/matches")

    matches = []
    opr_team_keys = []
    for event in (pbar := tqdm(events)):
        pbar.set_description(f"Processing Event {event}")
        match_response = s.get(baseURL + "/event/"+event+"/matches/simple")
        team_keys_response = s.get(baseURL + "/event/"+event+"/teams/keys")
        match_json = match_response.json()
        matches = matches + match_json
        opr_team_keys = opr_team_keys + team_keys_response.json()

    logging.debug("pre-set opr_team_keys: %s", opr_team_keys)
    opr_team_keys = list(set(opr_team_keys))

    oprs = opr.calculate_oprs(matches=matches, max_match=-1, total_teams=len(opr_team_keys))

    missing_oprs = set(team_keys.team_keys) - set(oprs.keys())
    logging.debug("Missing oprs: %s", list(missing_oprs))
    for missing_opr in list(missing_oprs):
        oprs[missing_opr] = 0.0
    
    logging.info("team_keys: %s",  str(team_keys.team_keys))
    logging.info("opr_team_keys: %s", opr_team_keys)
    logging.info("opr_team_keys len: %s", len(opr_team_keys))
    logging.info("oprs: %s", oprs)
    #pp.pformat(oprs)

    if 'frc1334' in oprs:
        logging.debug("ITS IN")
    else:
        logging.debug("ITS NOT IN")

    for i in (pbar := tqdm(range(teams_len))):
        pbar.set_description(f"Processing Row {i}")
        team_list = [teams[i]['team_number'], 
                     teams[i]['nickname'], 
                     pictures[i], 
                     teams[i]['rookie_year'],
                     district_json[district_team_number_indices[team_keys.index_to_team_key(i)]]['rank'],
                     oprs[team_keys.index_to_team_key(i)],
                     '']
        teams_formatted[i] = team_list
        logging.info(i)

    # pp.pprint(teams_formatted)
    logging.info("Teams formatted: %s", teams_formatted)


    tqdm.write("Data successfully aquired")
    tqdm.write("Opening Google Sheet")
    try:
        sheet = client.open("Scouting2023").sheet1
        sheet.update('A2:H'+str(teams_len+2), teams_formatted, raw=False)
    except:
        logging.error("Cannot open google sheet, writing to csv instead")
        with open("/home/peter/FRC/Scouting2023/Barrie/matches.json", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(teams_formatted)

    return

def get_picture_resolution(url):
    imgrequest = requests.get(url)
    imgstring = imgrequest.content
    imgiostream = io.BytesIO(imgstring)
    img = Image.open(imgiostream)
    return img.size

class TeamKeys:
    def __init__(self, team_keys):
        self.hashmap = [-1]*9999
        self.dict = {}
        self.team_keys = team_keys
        i = 0
        for team_key in team_keys:
            logging.debug(team_key)
            self.dict[team_key] = i
            self.hashmap[i] = int(team_key[3:])
            i += 1
        logging.debug(f"team keys dict: %s", str(self.dict))
        logging.debug(f"team keys list: %s", str(self.team_keys))


    def team_key_to_index(self, key):
        return self.hashmap[int(key[3:])]
    
    def index_to_team_key(self, index):
        # key = list(self.dict.keys())[list(self.dict.values()).index(index)]
        key = self.team_keys[index]
        logging.debug(f"index_to_team_key({index}) = {key}")
        return key
        # return (list(self.dict.keys())[list(self.dict.values()).index(index)])

    # def __iter__(self):
    #     return self

    # def __next__(self):
    #     return self.team_keys.next()


if __name__ == "__main__":
    update_basic_data();
