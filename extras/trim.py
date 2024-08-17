import time, json


with open("bs_data.json") as f:
    savedata = json.load(f)
time_current = int(time.time())

nsave = {}
for i in savedata.keys():
    ok = True
    print(i)
    try:
        if time_current - savedata[i]["history"][-1]["time"] > 7776000*2:
            ok = False
    except Exception as e:
        ok = False
    if ok:
        nsave[i] = savedata[i]


with open("bs_data_new.json","w") as f:
    json.dump(nsave,f)