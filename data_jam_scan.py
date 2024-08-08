with open("bs_data.txt") as f:
    savedata = eval(f.read())

try:
    for i in savedata.keys():
        print(f"\033[38;5;220m{i}\033[0m")
        timestamp = 0
        entry_first = savedata[i]["history"][0]["time"]
        entry_last = savedata[i]["history"][-1]["time"]
        for k in savedata[i]["history"]:
            ts_delta = k["time"] - timestamp
            if ts_delta < 3600:
                print("\033[38;5;196m",end="")
            elif ts_delta < 3600*12:
                print("\033[38;5;202m",end="")
            elif ts_delta < 3600*24:
                print("\033[38;5;220m",end="")
            else:
                print("\033[38;5;40m",end="")
            if timestamp != 0:
                print(f"{ts_delta}\033[0m >> {k}")
            else:
                print(f"START\033[0m >> {k}")
            timestamp = k["time"]
        print()
        
except:
    print("\033[31;3mProgram failed.\033[0m")
    print(i)

