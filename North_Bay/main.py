import requests
import csv
import json

def main():
    baseURL = "https://www.thebluealliance.com/api/v3" 
    key = "SBns9CVvJ6TAl3q6keafIY9DKuBd2tlyZLlrOqR6djId1C07TNQVcYaM3OmN6xso"
    header = {"X-TBA-Auth-Key": key}
    status = requests.get(baseURL + "/status", headers=header)
    if (status.status_code != 200):
        print("we not vibin")
        return

    teams_response = requests.get(baseURL + "/event/2023onnob/teams/keys", headers=header)
    teams = teams_response.json()
    events = []
    pictures = []
    data = [len(teams)][5]
    """
    data[0...i] -> rows where i == teams[i]
    data[i][0] team number
    data[i][1] team nickname
    data[i][2] picture
    data[i][3] rookie year
    data[i][4] district ranking
    data[i][5] opr
    data[i][6] events (this year)
    data[i][7] awards
    """
    i = 0
    
    for team in teams:
        print(team)

        media = requests.get(baseURL + "/team/"+team+"/media/2023", headers=header)
        if media != []:
            media_json = media.json()
            for item in media_json:
                if('direct_url' in item and item['direct_url'] != ''):
                    pictures.append({team: item['direct_url']})
                    data[i][1] = item['direct_url']

        """
        teamEvents = requests.get(baseURL + "/team/"+team+"/events/2023/keys", headers=header)
        for teamEvent in teamEvents.json():
            isInTeamEvent = False
            for event in events:
                if event == teamEvent:
                    isInTeamEvent = True
                    break
            if not isInTeamEvent:
                events.append(teamEvent)

            if teamEvent == "2023ilch":
                print(team + " is in illionoioi")
        """
        i++

    #oprs = requests.get(baseURL + "/event/{event_key}/oprs", headers=header)

    with open("data.csv", 'w', newline='') as data:
        writer = csv.writer(data)
        writer.writerow()

    print(pictures)



    return


if __name__ == "__main__":
    main()
