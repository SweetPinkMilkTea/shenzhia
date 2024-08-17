import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import time
from random import choice as ch



# 0 for regular use, 1 for AllTags
allTag = 1




def brightness(hex_color):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return (r * 299 + g * 587 + b * 114) / 1000

def colorpick():
    while True:
        output = "#"
        for i in range(6):
            output += ch(["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"])
        if brightness(output) < 128:
            return output

with open("bs_data.txt") as f:
    savedata = eval(f.read())
with open("bs_tags.txt") as f:
    x = eval(f.read())
    names = x.keys()
    tags = x.values()
    tag_dict = {}
    for i, k in zip(tags, names):
        tag_dict[i] = k
    print(tag_dict)


keylist = []
colors = ["green","red","blue","yellow","purple","white","cyan"]
for i in range(len(tag_dict)-7):
    colors.append(colorpick())
if not allTag:
    for i in range(len(colors)):
        tag = input(f"Tag {i+1} > #").upper().strip()
        if tag == "":
            break
        keylist.append("#" + tag)
if allTag:
    keylist = tag_dict.keys()
keydict = {}
for i in keylist:
    if len(savedata[i]["history"]) > 1:
        keydict[i] = savedata[i]["history"]
trim = int(input("Trim > "))

xlist = []
ylist = []
minylist = []
for i in keydict.keys():
    minylist.append(savedata[i]["history"][0]["time"])
for i in keydict.keys():
    for k in savedata[i]["history"]:
        if (k["time"] - min(minylist))/86400+1 >= trim:
            xlist.append((k["time"] - min(minylist))/86400+1)
            ylist.append(k["value"])

plt.style.use('dark_background')
plt.rcParams['axes.axisbelow'] = True
plt.rcParams["font.family"] = "Bahnschrift"
plt.xlabel(f"DAYS SINCE FIRST RECORDING")
plt.ylabel("TROPHIES")
plt.title(f"Trophy-Comparison")
print(f"min {min(ylist)}\nmax {max(ylist)}")
#plt.ylim(int(min(ylist)/500)*500,(int(max(ylist)/500)+1)*500)
#plt.yticks(np.arange(int(min(ylist)/500)*500, (int(max(ylist)/500)+1)*500+1, 500))
plt.grid(which="major", color='gray')
plt.grid(which="minor", color='#111111', linestyle="dashed")
plt.minorticks_on()
           
z = 1
for i in keydict.keys():
    xlist = []
    ylist = []
    for k in savedata[i]["history"]:
        if (k["time"] - min(minylist))/86400+1 >= trim:
            xlist.append((k["time"] - min(minylist))/86400+1)
            ylist.append(k["value"])
    plt.plot(xlist,ylist,color=colors[z-1],marker="x" if allTag == 0 else "",label=tag_dict[i])
    prev_y = 0
    if not allTag:
        for x,y in zip(xlist,ylist):
            if abs(y - prev_y) > (max(ylist) - min(ylist))/20:
                plt.annotate(str(y), # annotation text
                            (x,y), # these are the coordinates to position the label
                            textcoords="offset points", # how to position the text
                            xytext=(0,10), # distance from text to points (x,y)
                            ha='center') # horizontal alignment can be left, right or center
                prev_y = y
    z += 1
plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)
plt.savefig(f"graphs/comp/comparison{int(time.time())}.png", bbox_inches="tight")
print(f"Saved under ID {int(time.time())-1}")
