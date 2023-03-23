import numpy as np
import time
import json
import pprint
import logging
logger = logging.getLogger(__name__)

def calculate_oprs(matches: list, max_match: int, total_teams:int) -> dict:
    """Calulates the opr for a given set of matches


    """
    if max_match == -1:
        max_match = len(matches)
    if max_match < 0 or max_match > len(matches):
        raise ValueError("max_match out of range")

    if matches == []:
        raise ValueError("matches empty")

    matches = matches[:max_match]

    # team_keys_list.sort()
    # team_keys = {}
    generated_team_keys = {}
    i = 0
    # for team_key in team_keys_list:
    #     team_keys[team_key] = i
    #     i += 1

    M = np.zeros((len(matches)*2, total_teams), dtype=np.float64)
    s = np.zeros((len(matches)*2), dtype=np.float64)

    currentTime = time.time()

    i = 0
    for match in matches:
        if "actual_time" not in match or match["actual_time"] > currentTime:
            print("Match not in time")
            break

        for team_key in match["alliances"]["red"]["team_keys"]:
            if(team_key not in generated_team_keys):
                generated_team_keys[team_key] = len(generated_team_keys)
                # print(generated_team_keys)
            M[i][generated_team_keys[team_key]] = 1
        s[i] = match["alliances"]["red"]["score"]
        i += 1

        for team_key in match["alliances"]["blue"]["team_keys"]:
            if(team_key not in generated_team_keys):
                generated_team_keys[team_key] = len(generated_team_keys)
            M[i][generated_team_keys[team_key]] = 1
        s[i] = match["alliances"]["red"]["score"]

        i += 1

    logger.info("generated_team_keys: %s", generated_team_keys)
    # Mt = np.transpose(M)
    # MMt = np.dot(Mt, M)

    # s_aligned = np.zeros((1, len(s)), dtype=np.float64)
    # for i in range(len(s)):
    #     s_aligned[0][i] = s[i]

    # sMt = np.dot(s_aligned, Mt)

    # oprs_by_hand = np.dot(np.dot(np.linalg.inv(MMt), MMt), sMt)
    # oprs_by_hand_list = np.ndarray.flatten(oprs_by_hand).tolist()
    # oprs_by_hand_dict = dict(zip(team_keys_list, oprs_by_hand_list))


    oprs = np.linalg.lstsq(M, s, rcond=None)
    #print(oprs)
    oprs_flat = np.ndarray.flatten(oprs[0])
    #print(oprs_flat)
    oprs_list = list(oprs_flat.tolist())
    oprs_dict = dict(zip(generated_team_keys.keys(), oprs_list))
    oprs_sorted_dict = dict(sorted(oprs_dict.items()))

    return oprs_sorted_dict

def main():
    logging.basicConfig(filename='opr.log', encoding='utf-8', level=logging.DEBUG)
    with open("/home/peter/FRC/Scouting2023/Barrie/matches.json") as f:
        matches = json.load(f)

    with open("/home/peter/FRC/Scouting2023/Barrie/team_keys.json") as f:
        key_teams = json.load(f)

    oprs = calculate_oprs(matches, -1, len(key_teams))

    p = pprint.PrettyPrinter()
    p.pprint(oprs)

    with open("/home/peter/FRC/Scouting2023/Barrie/oprs_by_hand.json", 'w', encoding='utf-8') as f:
        json.dump(oprs, f, ensure_ascii=False, indent=4)

    p = pprint.PrettyPrinter()
    p.pprint(oprs)

if __name__ == '__main__':
    main()
