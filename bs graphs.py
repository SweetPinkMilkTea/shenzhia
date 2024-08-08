import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import font_manager
import matplotlib as mpl
import numpy as np
import json
import datetime
import os

#os.chdir("C:/Users/s.ebensen/Desktop/shenzhitek")

limiter = False

fm = mpl.font_manager
fm._get_fontconfig_fonts.cache_clear()

font_dirs = ["C:/users/svene/appdata/local/microsoft/windows/fonts"]  # The path to the custom font file.
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

for font_file in font_files:
    font_manager.fontManager.addfont(font_file)


with open("bs_data.json") as f:
    savedata = json.load(f)
with open("dc_id_rel.json") as f:
    translatenames = json.load(f)
with open("bs_tags.json") as f:
    x = json.load(f)
    names = x.keys()
    tags = x.values()
    tag_dict = {}
    for i, k in zip(tags, names):
        tag_dict[i[0]] = k
    print(tag_dict)
with open("colorprefs.json") as f:
    colorprefs = json.load(f)

def calculate_brightness(hex_color):
    # Convert the hexadecimal color code to RGB values
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)

    # Calculate brightness using the following formula
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    return brightness

z = 1
for i in savedata.keys():
    try:
        if len(savedata[i]["history"]) > 3:
            try:
                colorcode = colorprefs[tag_dict[i]]
            except:
                colorcode = "#000000"
            print(f"Constructing #{z} @{tag_dict[i]}")
            xlist = []
            ylist = []
            xOrigin = savedata[i]['history'][0]["time"]
            for k in savedata[i]['history']:
                xlist.append((k["time"] - xOrigin)/86400)
                ylist.append(k["value"])
            brightness = calculate_brightness(colorcode)
            print(f"Brightness {brightness}")
            br_threshold = 128
            if brightness < br_threshold:
                plt.style.use('default')
            else:
                plt.style.use('dark_background')
            plt.rcParams['axes.axisbelow'] = True
            plt.rcParams["font.family"] = "Bahnschrift"
            #plt.rcParams["font.weight"] = "bold"
            plt.plot(xlist,ylist,color=colorcode,marker="x")
            plt.xlabel(f"DAYS SINCE FIRST RECORDING\n({datetime.datetime.utcfromtimestamp(savedata[i]['history'][0]['time']).strftime('%d.%m.%Y')})")
            plt.ylabel("TROPHIES")
            try:
                plt.title(f"Trophy-Progression for '{translatenames[tag_dict[i]]}'/{i}")
            except:
                plt.title(f"Trophy-Progression for 'UNKNOWN_TAG'/{i}")
            if brightness > br_threshold:
                plt.grid(which="major", color='gray')
                plt.grid(which="minor", color='#222222', linestyle="dashed")
            else:
                plt.grid(which="major", color='gray')
                plt.grid(which="minor", color='#DDDDDD', linestyle="dashed")
            plt.minorticks_on()
            plt.ylim(int(min(ylist)/500)*500,(int(max(ylist)/500)+2)*500)
            print(f"\033[3;38;5;240m(max timestamp {max(xlist)})\033[0m")
            if max(xlist) <= 15:
                margin_negative = 0.9
            else:
                margin_negative = int(max(xlist)/15)
            if not limiter:
                plt.xlim(0-margin_negative,round(max(xlist))+1+int(max(xlist)/10))
                plt.yticks(np.arange(int(min(ylist)/500)*500, (int(max(ylist)/500)+2)*500+1, 500))
            else:
                plt.xlim(max(xlist)-30 if max(xlist) > 30 else 0-margin_negative,round(max(xlist))+1+int(max(xlist)/10))
                plt.yticks(np.arange(int(min(ylist)/500)*500, (int(max(ylist)/500)+2)*500+1, 500))
                if max(xlist) > 30:
                    for k in reversed(xlist):
                        if max(xlist) - 30 > k:
                            breakstamp = k
                            break
                    adjusted_lim = ylist[xlist.index(breakstamp)]
                    plt.ylim(int(adjusted_lim/500)*500,(int(max(ylist)/500)+2)*500)
                    plt.yticks(np.arange(int(adjusted_lim/500)*500, (int(max(ylist)/500)+2)*500+1, 500))
            prev_y = 0
            for x,y in zip(xlist,ylist):
                if abs(y - prev_y) > ((max(ylist) - min(ylist))/10 if not (limiter and max(xlist) > 30) else (max(ylist) - adjusted_lim)/10) or (xlist.index(x) == len(xlist)-1):
                    if not((xlist.index(x) == len(xlist)-1)):
                        plt.annotate(str(y), # annotation text
                                    (x,y), # these are the coordinates to position the label
                                    textcoords="offset points", # how to position the text
                                    xytext=(0,10), # distance from text to points (x,y)
                                    ha='center') # horizontal alignment can be left, right or center
                        prev_y = y
                    else:
                        plt.annotate(str(y), # annotation text
                                    (x,y), # these are the coordinates to position the label
                                    textcoords="offset points", # how to position the text
                                    xytext=(3,0), # distance from text to points (x,y)
                                    ha='left', # horizontal alignment can be left, right or center
                                    va='center',
                                    color=colorcode,
                                    bbox=dict(boxstyle="square,pad=0.3",fc="black" if brightness > br_threshold else "white", ec=colorcode, lw=1)) 
            try:
                if tag_dict[i] != "UNKNOWN_TAG":
                    if limiter:
                        plt.savefig(f"graphs/{tag_dict[i]}_t.png", bbox_inches="tight")
                    else:
                        plt.savefig(f"graphs/{tag_dict[i]}_full_t.png", bbox_inches="tight")
            except:
                plt.savefig(f"graphs/unknown_{z}.png", bbox_inches="tight")
            print(f"\033[7mCompleted #{z} ({'Limited' if limiter else 'Full'}): {len(savedata[i]['history'])} Entries\033[0m\n")
            plt.style.use('default')
            plt.close()
            z += 1
        else:
            print(f"\033[7mSkipped #{z}: {len(savedata[i]['history'])} Entries\033[0m\n")
    except Exception as e:
        plt.clf()
        print(f"Skipped [{e}]")
