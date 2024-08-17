import json, requests, urllib

with open("bs_spicyness.json") as f:
    spdict = json.load(f)
with open("bs_api_token.json") as f:
    apikey = json.load(f)[input("Select key [main/alt] > ")]

if input("Recalibrate? [Y/Else]: ").upper() == "Y":
    url = f"https://api.brawlstars.com/v1/brawlers"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {apikey}"
    }
    response = requests.get(url, headers=headers)

    for i in response.json()["items"]:
        while True:
            try:
                factor = input(f"Input [S/A/B/C/D/F] : [{i['name']}] > ").upper()
                spdict[i["name"]] = {"S":0,"A":25/9,"B":45/9,"C":55/9,"D":75/9,"F":100/9,}[factor]
            except:
                print("\033[31m Bad Input\033[0m")
            else:
                break

    with open("bs_spicyness.json","w") as f:
        json.dump(spdict,f)
print()
for i in ["#8VGY00G9","#8GQ8UGL","#9JQ92JUP2","#8YGJJQ8JV","#8P8VPPJLQ","#R9Y9CPP0","#Q2LYC08","#8P2PYG8U2"]:
    url = f"https://api.brawlstars.com/v1/players/{urllib.parse.quote(i)}/"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {apikey}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    spice = 0
    brawlerlist = data["brawlers"]
    def brawlersort(a):
        return a["trophies"]
    brawlerlist.sort(reverse=True,key=brawlersort)
    for j in range(9):
        spice += spdict[brawlerlist[j]["name"]] / [2,2,2,1,1,1,0.5,0.5,0.5][j]
    print(f"{data['name']} // {spice}")


input("Finished.")
