import urllib, requests, json
bs_api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImM3YjBlYjc2LTcwMTEtNGEzOC1iZDQ4LTRkYTYzNWVjY2FhMSIsImlhdCI6MTcxMjU0OTA2Miwic3ViIjoiZGV2ZWxvcGVyL2RmMDEwYTRiLTg0MDgtNzg1Ni04ZTM5LTczYTcwMDNlYzY0OCIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiOTUuMzMuOTcuMTE3Il0sInR5cGUiOiJjbGllbnQifV19.jALBB8n1qweH9im5y7wg5-OHgBGFeXXpWBHWiG-72frrJMSBIYL8utAHWhDUxklW5Id5CvbZ_Kt1Ur-K_vfcgw"

# calc tsr
while False:
    k = int(input("> ")) - 500

    print(round(1.7777777*((k if k < 750 else 750)**2),0))


if 0:
    tag = urllib.parse.quote("#8GQ8UGL")
    url = f"https://api.brawlstars.com/v1/players/{tag}/"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bs_api_token}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    ssdv = data["soloVictories"]
    dsdv = data["duoVictories"]
    v3v = data["3vs3Victories"]
    print(ssdv+dsdv+v3v)
    print(v3v)
    print(v3v/(ssdv+dsdv+v3v)*100)

if 0:
    key = "#8GQ8UGL"
    tag = urllib.parse.quote(key)
    url = f"https://api.brawlstars.com/v1/players/{tag}/battlelog"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bs_api_token}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    wins = 0
    total = 0
    flukes = 0
    isPowerLeague = False
    try:
        for i in data["items"]:
            #PL background scanning
            if data["battle"]["type"].upper() in ["TEAMRANKED","SOLORANKED"] and not isPowerLeague:
                isPowerLeague = True
                with open("bs_powerleague.json", "r") as f:
                    pl_saves = json.load(f)
                pl_mode = "solo" if "SOLO" in data["battle"]["type"].upper() else "team"
                for j in range(3):
                    if data['battle']['teams'][0][j]['tag'] not in pl_saves or type(pl_saves[data['battle']['teams'][0][j]['tag']]) == int:
                        pl_saves[data['battle']['teams'][0][j]['tag']] = {"solo":0,"team":0}
                    pl_saves[data['battle']['teams'][0][j]['tag']][pl_mode] = data['battle']['teams'][0][j]['brawler']['trophies']
                for j in range(3):
                    if data['battle']['teams'][1][j]['tag'] not in pl_saves or type(pl_saves[data['battle']['teams'][1][j]['tag']]) == int:
                        pl_saves[data['battle']['teams'][1][j]['tag']] = {"solo":0,"team":0}
                    pl_saves[data['battle']['teams'][1][j]['tag']][pl_mode] = data['battle']['teams'][1][j]['brawler']['trophies']
                with open("bs_powerleague.json", "w") as f:
                    pl_saves = json.dump(pl_saves,f)
            try:
                if i["battle"]["result"] == "victory":
                    wins += 1
                if i["battle"]["result"] != "draw":
                    total += 1
                if i["battle"]["result"] == "defeat" and key == i["battle"]["starPlayer"]["tag"]:
                    flukes += 1
            except:
                pass
    except Exception as e:
        pass
    print(f"W:{wins},T:{total},F:{flukes}")

if 0:
    new_data = {}
    with open("bs_data.json") as f:
        data = json.load(f)
    with open("bs_tags.json") as f:
        tags = json.load(f)
    for i in data.keys():
        if i in tags.values():
            new_data[i] = data[i]
    with open("bs_data_edit.json","w") as f:
        json.dump(new_data,f)

if 0:
    with open("bs_tags.json") as f:
        tags = json.load(f)
    content = {}
    for i in tags.values():
        print(i)
        tag = urllib.parse.quote(i[0])
        url = f"https://api.brawlstars.com/v1/players/{tag}/"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        try:
            print(data["reason"])
            input()
        except:
            pass
        brawlerlist = data["brawlers"]
        for k in brawlerlist:
            if k["name"] not in content.keys():
                content[k["name"]] = []
            content[k["name"]].append([k["trophies"],i[0]])
    ex_content = {}
    for i in content:
        def sort_first(a):
            return a[0]
        ex_content[i] = sorted(content[i],key=sort_first,reverse=True)
    
    with open("bs_brawler_leaderboard.json","w") as f:
        json.dump(ex_content,f)

# find request amount
if 0:
    with open("bs_data.json","r") as f:
        bsdict = json.load(f)

    res = {}
    for i in bsdict.keys():
        res[i] = 0
        for ii in bsdict[i]["history"]:
            res[i] += 1 if ii["relevancy"] else 0
        
    with open("output.json","w") as f:
        json.dump(res,f)