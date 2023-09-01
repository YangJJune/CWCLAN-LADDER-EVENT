import requests
import json
import sys
import pandas as pd
import subprocess
import asyncio
import numpy as np
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from bs4 import BeautifulSoup

def getPort():
    p = subprocess.run(["powershell.exe",".\\getPort.ps1"],stdout=subprocess.PIPE)
    
    return p.stdout.decode('UTF-8').strip()


class Player:
    name: str = ""
    win: int = 0
    lose: int = 0
    rating: int = 0
    winStreak: int = 0
    lossStreak: int = 0
    mod: str = "-"



f = open("players.txt","r")
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
key = ".\key\cwclanapp-8fd78a732972.json"
cred = ServiceAccountCredentials.from_json_keyfile_name(key,scope)

gc = gspread.authorize(cred)
sh = gc.open('CW클랜 래더 이벤트 순위표')
worksheet = sh.sheet1

players = []
playerdb = []
while True:
    line = f.readline()
    line = line.strip()
    if not line: break
    players.append(line)

port = getPort()

prevRank = {}
cnt = 3
while True:
    name = worksheet.acell('C'+str(cnt)).value
    rank = worksheet.acell('B'+str(cnt)).value
    prevRank[name]=rank
    if name is None:
        break
    cnt+=1

for player in players:
    url = "http://localhost:"+str(port)+"/web-api/v2/aurora-profile-by-toon/"+player+"/30?request_flags=scr_mmgameloading"
    res = requests.get(url)

    if res.status_code == 200 :
        jsonArr = json.loads(res.text)
        ids = jsonArr["matchmaked_stats"]
        isValid = False
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
                print(player+" Query Complete")
                isValid = True
                break
        
        if isValid==False :
            print(player+" query Failed!!!")
            print(ids)
        
    else :
        print("ERROR CODE : {res.status_code}")
    
    raw_data = {}


for i in playerdb:
    if i.winStreak == 0 : 
        test_str = str(i.lossStreak) + "연패"
    
    else :
        test_str = str(i.winStreak) + "연승"
    raw_data[i.name] = [i.name, i.mod, i.win+i.lose, i.win, i.lose, "100%", i.rating, test_str]

data = pd.DataFrame(raw_data,index=['아이디', '','경기' ,'승','패', '승률','MMR', '비고'])
data = data.transpose()
data = data.sort_values('MMR', ascending=False) 

for id, prev in prevRank.items():
    x, y = np.where(data == id)
    x = x.astype(int)
    if x.size == 0 : 
        continue
    now = int(x[0]) + 1
    
    print(str(prev),str(now))
    mode = int(prev) - int(now)
    if mode > 0 :
        mod_str = "▲"+str(mode)
    elif mode < 0 :
        mod_str = "▼"+str(mode)
    else:
        mod_str = "-"
    
    data[''][id] = mod_str

print(data)





worksheet.update('C2',[data.columns.values.tolist()] + data.values.tolist())

f.close()