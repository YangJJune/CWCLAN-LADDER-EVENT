import requests
import json
import pandas as pd

from bs4 import BeautifulSoup

class Player:
    name: str = ""
    win: int = 0
    lose: int = 0
    rating: int = 0
    winStreak: int = 0
    lossStreak: int = 0
    
f = open("players.txt","r")
players = []
playerdb = []
while True:
    line = f.readline()
    line = line.strip()
    if not line: break
    players.append(line)


for player in players:
    port = 2426
    url = "http://localhost:"+str(port)+"/web-api/v2/aurora-profile-by-toon/"+player+"/30?request_flags=scr_mmgameloading"
    res = requests.get(url)

    if res.status_code == 200 :
        jsonArr = json.loads(res.text)
        ids = jsonArr["matchmaked_stats"]
        for i in ids :
            if i["toon"] == player and i["season_id"] == 14:
                tmp_player = Player()
                tmp_player.name = player
                tmp_player.win = i["wins"]
                tmp_player.lose = i["losses"]
                tmp_player.rating = i["rating"]
                tmp_player.winStreak = i["win_streak"]
                tmp_player.lossStreak = i["loss_streak"]
                playerdb.append(tmp_player)
        
    else :
        print("ERROR CODE : {res.status_code}")
    
    raw_data = {}
    for i in playerdb:
        raw_data[i.name] = { i.win, i.lose, i.rating, i.winStreak, i.lossStreak}
        

    
f.close()