import os, sys
import random
import asyncio

class ManualRaisedException(Exception):
    pass
class APIConnectionException(Exception):
    pass

import re
import sys
import interactions
from interactions.ext.paginators import Paginator
import json
import time, datetime
import aiohttp
import sentry_sdk
import traceback
import urllib, requests
from interactions.api.events import CommandError

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import font_manager
import matplotlib as mpl
import numpy as np

fm = mpl.font_manager
fm._get_fontconfig_fonts.cache_clear()

font_dir = ["./font"]  # The path to the custom font file.
font_files = font_manager.findSystemFonts(font_dir)

for font_file in font_files:
    font_manager.fontManager.addfont(font_file)

# First Setup
## Create directories
if "graphs" not in os.listdir():
    os.mkdir("graphs")
## Create Files
req_files = ["symbols.json","dev_env.json","fastlogin.json","bs_tags.json","bs_data.json","bs_powerleague.json","bs_ar_supplementary.json","verbose_silence.json","bs_guild_leaderboard_data.json","bs_spicyness.json","bs_hc_info.json","dc_bot_tokens.json","bs_club_member_cache.json","bs_brawler_leaderboard.json","sentry_dsn.json","bs_ar.json","dc_id_rel.json","tsr_best.json","bs_api_token.json","bs_brawler_best.json"]
if not all(x in os.listdir() for x in req_files):
    for i in req_files:
        if i not in os.listdir():
            with open(i,"w") as f:
                print(f"Generated new file: {i}")
                if i == "fastlogin.json":
                    json.dump({"name":""},f)
                else:
                    json.dump({},f)
    input("Welcome to the first-run setup. Press Enter to continue.\n\nIf you see this message more than once already, stop the script and run again to avoid overwriting tokens.")
    with open("dc_bot_tokens.json","w") as f:
        print("Discord Bottoken Setup\n---")
        a = ""
        while a == "":
            a = input("Name: ").strip()
        b = input("Key: ")
        json.dump({a:b},f)
    with open("bs_api_token.json","w") as f:
        print(f"\nBrawl Stars API Token Setup\nYour IP is [{urllib.request.urlopen('https://api4.ipify.org').read().decode('utf8')}]\n---")
        a = ""
        while a == "":
            # Static for now
            # a = input("Name: ").strip()
            a = "main"
        b = input("Key: ")
        json.dump({a:b},f)
    with open("sentry_dsn.json","w") as f:
        print(f"\nSentry DSN\n---")
        a = "main"
        b = input("Key: ")
        json.dump({a:b},f)
    with open("dev_env.json","w") as f:
        print(f"\nChannel for logging purposes\nChange this by modifying 'dev_env.json'\n---")
        a = "loggingchannel"
        b = input("Channel-ID: ")
        print(f"\nServer for administrative commands\nChange this by modifying 'dev_env.json'\n---")
        c = "scopedguild"
        d = input("Channel-ID: ")
        json.dump({a:b,c:d},f)
    with open("symbols.json","w") as f:
        print("Set emojis\nNeed help? Visit the wiki for instructions and for emoji name meanings.\n---")
        emojidict = {}
        for i in ["Power1","Power2","Power3","Power4","Power5","Power6","Power7","Power8","Power9","Power10","Power11","Gadget_OK","SP_OK","Gear_OK","Slot_Empty","Bronze","Silver","Gold","Trophy","Bling","PPoint","GadgetIcon","SPIcon","GearIcon","HChargeIcon","ExtraSparkles","Error","Warning","Info","Connected","RankNone","RankE","RankD","RankD+","RankC-","RankC","RankC+","RankB-","RankB","RankB+","RankA-","RankA","RankA+","RankS-","RankS","RankS+","RankSS","RankEX"]:
            while True:
                x = input(f"| {i} > ")
                if bool(re.match(r'^<:.*:\d+>$', x)):
                    break
                else:
                    print("Not a emoji reference. Try again.")
            emojidict[i] = x
        json.dump(emojidict,f)


# Fast Login
# Provide a non-empty string to auto-pick a saved bot token
# Useful if working with "headless" hardware
with open("fastlogin.json") as f:
    fastlogin = json.load(f)["name"]

print("\033c",end="")

with open("bs_api_token.json") as f:
    bs_api_token = json.load(f)
    # Make dynamic someday maybe
    bs_api_token = bs_api_token["main"]
with open("dc_bot_tokens.json") as f:
    discord_bot_token = json.load(f)
with open("sentry_dsn.json") as f:
    dsn = json.load(f)["main"]
with open("verbose_silence.json") as f:
    try:
        silence = json.load(f)["dur"]
    except:
        silence = 0
with open("symbols.json") as f:
    emojidict = json.load(f)
    powericonlist = []
    for i in range(1,12):
        powericonlist.append(emojidict[f"Power{i}"])
with open("dev_env.json") as f:
    dev_env = json.load(f)
    logger = int(dev_env["loggingchannel"])
    scope = int(dev_env["scopedguild"])
tsr_rank_thresholds = [1,17778,36111,54444,73333,92222,111111,127407,143703,160000,201481,242962,284444,364444,444444,751111,1000000,999999999]

if fastlogin == "":
    print("\033cSelect Discord Login:\nEnter nothing to create a new one or edit one.\n\n")
    for i in discord_bot_token:
        print(f"[{i}]")
    print()
    choice = input().strip()
    if choice == "":
        with open("dc_bot_tokens.json","r") as f:
            discord_bot_token = json.load(f)
        with open("dc_bot_tokens.json","w") as f:
            print("Discord Bottoken Setup\n---")
            a = ""
            while a == "":
                a = input("Name: ").strip()
            b = input("Key: ")
            discord_bot_token[a] = b
            json.dump(discord_bot_token,f)
            login = a
else:
    choice = fastlogin
    print("Fastlogin is active!")
login = choice
if choice not in discord_bot_token.keys():
    sys.exit("Invalid key for bot token provided.")

calStatus = 0
brawlerIDs = {}
maxGadgets = maxStarpower = maxGear = maxCurrency = maxCurrencyAdv = maxBrawlers = maxHypercharges = 0
def calibrate():
    global brawlerIDs, maxGadgets, maxStarpower, maxGear, maxCurrency, maxCurrencyAdv, maxBrawlers, maxHypercharges, calStatus
    try:
        url = f"https://api.brawlstars.com/v1/brawlers/"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }       
        response = requests.get(url, headers=headers)
        data = response.json()
        try:
            if data["message"] == "API at maximum capacity, request throttled.":
                calStatus = response.status_code
        except:
            pass
        try:
            if data["reason"] == "unknownException":
                calStatus = response.status_code
        except:
            pass
        try:
            print(data["reason"])
            calStatus = response.status_code
        except:
            brawlerIDs = {}
            maxGadgets = maxStarpower = maxGear = maxCurrency = maxCurrencyAdv = 0
            maxBrawlers = len(data["items"])
            for i in data["items"]:
                brawlerIDs[i["id"]] = i['name']
                maxGadgets += len(i["gadgets"])
                maxStarpower += len(i["starPowers"])
                maxCurrency += 20245
                maxCurrencyAdv += 20245 + 6000
            maxHypercharges = 43
            maxCurrency += maxHypercharges * 5000
            maxCurrencyAdv += maxHypercharges * 5000
            calStatus = 200
    except:
        calStatus = 900
    print(calStatus)

            
"""maxBrawlers = 80
for i in range(maxBrawlers):
    maxGadgets += 2
    maxStarpower += 2
    maxCurrency += 20245
    maxCurrencyAdv += 20245 + 6000"""
                
def send_api_error(reason):
    if "accessDenied" in reason:
        return f"{emojidict['Error']} The current API key for the BS-API is outdated. Please wait for a fix."
    elif reason == "inMaintenance":
        return f"{emojidict['Error']} BS API under Maintenance. Please wait until it's over, this often only takes a few minutes."
    elif reason == "notFound":
        return f"{emojidict['Warning']} This profile doesn't exist."
    else:
        return f"{emojidict['Error']} BS API couldn't respond. Check '/status'?"


startuptime = int(time.time())
bot = interactions.Client(intents=interactions.Intents.DEFAULT, delete_unused_application_cmds=True, send_command_tracebacks=False)
bot.load_extension('interactions.ext.sentry', token=dsn)

# ----------------
# ROUTINE TASKS
# ----------------

@interactions.listen(CommandError, disable_default_listeners=False)
async def on_command_error(event: CommandError):
    traceback.print_exception(event.error)
    embed = interactions.Embed(title=random.choice(["Yikes!","Ouch...","Aw...","Oops.",":("]),
                        color=0xff0000,
                        timestamp=datetime.datetime.now(),
                        description=f"An unexpected error occured.\nAn error log was generated and sent internally.")
    if not event.ctx.responded:
        await event.ctx.send(embed=embed)

@interactions.listen()
async def on_startup():
    global exitcode, activity, calStatus
    print("Initializing...")
    try:
        with open("quick_restart.txt","r") as f:
            exitcode = int(f.read())
    except:
        exitcode = 1
        with open("quick_restart.txt","w") as f:
            f.write(str(exitcode))
    await bot.change_presence(status=interactions.Status.ONLINE)
    print(f'\nStarted Session as [{bot.user}] on code [{exitcode}]')
    try:
        autosync.start()
        bs_player_leaderboard.start()
        ar_refresh.start()
        await bs_player_leaderboard()
        if exitcode == 0:
            await autosync()
            await ar_refresh()
    except:
        print("Task error!")
    calibrate()
    channel = bot.get_channel(logger)
    if calStatus == 200:
        await channel.send(f"{emojidict['Connected']} Bot has started/recovered.")
    else:
        await channel.send(f"{emojidict['Connected']} Bot has started/recovered.\n{emojidict['Warning']} API Connection encountered issues! Status Code: {calStatus}\nUse `/resetbasedata` as soon as problems are resolved.")
    exitcode = 0
    with open("quick_restart.txt","w") as f:
        f.write(str(exitcode))
    with open("datadump.txt","w") as f:
        f.write(str([v for v in dir() if not v.startswith('_')]))
    return

@interactions.Task.create(interactions.IntervalTrigger(hours=12))
async def autosync():
    global bsdict
    with open("bs_data.json") as f:
        bsdict = json.load(f)
    channel = bot.get_channel(logger)
    try:
        with open("dc_id_rel.json") as f:
            namerel = json.load(f)
    except:
        await channel.send(f"ID-Name Relation Sheet missing! Run '/linknames' as soon as possible.\n*Auto-Request aborted.*", silent=True)
        return
    if silence <= time.time():
        await channel.send(f"Starting Auto-Request...", silent=True)
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    z = 1
    errors = 0
    for k in tags.keys():
        try:
            try:
                if bsdict[tags[k][0]]["updates"]:
                    try:
                        x = bsdict[tags[k][0]]
                    except:
                        bsdict[tags[k][0]] = {"history":[],"updates":False}
                    tag = urllib.parse.quote(tags[k][0])
                    url = f"https://api.brawlstars.com/v1/players/{tag}/"

                    headers = {
                        "Accept": "application/json",
                        "Authorization": f"Bearer {bs_api_token}"
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            data = await response.json()
                            try:
                                print(data["reason"])
                                #Send error to dev channel and stop task
                                channel = bot.get_channel(logger)
                                await channel.send(f"{emojidict['Error']} Auto-Request failed! Task was abandoned.\n\nReason: {data['reason']}")
                                return
                            except:
                                pass
                            try:
                                if k not in namerel.keys():
                                    namerel[k] = k
                                if not(data["trophies"] == bsdict[tags[k][0]]["history"][-1]["value"] or time.time() - bsdict[tags[k][0]]["history"][-1]["time"] < 43200):
                                    try:
                                        bsdict[tags[k][0]]["history"].append({"value":data['trophies'],"time":int(time.time()),"tsr":bsdict[tags[k][0]]["history"][-1]["tsr"],"relevancy":False})
                                    except:
                                        bsdict[tags[k][0]]["history"].append({"value":data['trophies'],"time":int(time.time()),"tsr":-1,"relevancy":False})
                                    try:
                                        print(f"Appended ({namerel[k]}@{z})\n | {bsdict[tags[k][0]]['history'][-2]['value']} >>>> {data['trophies']}")
                                    except:
                                        print(f"Appended ({namerel[k]}@{z})\n | >>>> {data['trophies']}") 
                                else:
                                    print(f"Dupe and/or too soon, skipped ({namerel[k]}@{z})\n | {data['trophies']} <--> {bsdict[tags[k][0]]['history'][-1]['value']} [~{int((time.time() - bsdict[tags[k][0]]['history'][-1]['time'])/360)}min dif]")
                            except:
                                print(f"Empty log, skipped ({namerel[k]}@{z})\n | ---")
                else:
                    print(f"No AutoSync, skipped ({namerel[k]}@{z})\n | ---")
            except:
                print(f"Uninitiated log, skipped ({namerel[k]}@{z})\n | ---")
        except Exception as e:
            print(f"Tag cant be resolved. Please check. ({k}@{z})\n | {tags[k][0]} // {e}")
            errors += 1
    
        z += 1
    with open("bs_data.json","w") as f:
        json.dump(bsdict,f)
    # Send success message to dev channel
    channel = bot.get_channel(logger)
    if silence <= time.time():
        nl = "\n"
        await channel.send(f"Auto-Request completed. {'' if not errors else nl+str(errors)+'x errors encountered.'}", silent=True)

@interactions.Task.create(interactions.IntervalTrigger(hours=1))
async def bs_player_leaderboard():
    global bs_leaderboard_data, bs_local_leaderboard_data, bsdict
    with open("bs_data.json") as f:
        bsdict = json.load(f)
    # global
    url = f"https://api.brawlstars.com/v1/rankings/global/players"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bs_api_token}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
    try:
        print(data["reason"])
        channel = bot.get_channel(logger)
        await channel.send(f"{emojidict['Error']} Leaderboard data request failed! Task was abandoned.\n\nReason: {data['message']}")
        return
    except:
        pass
    bs_leaderboard_data = []
    for i in data["items"]:
        bs_leaderboard_data.append(i["tag"])
    channel = bot.get_channel(logger)
    # local
    bs_local_leaderboard_data_temp = []
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("tsr_best.json") as f:
        tsrbest = json.load(f)
    for i in tags.values():
        try:
            bs_local_leaderboard_data_temp.append([tsrbest[i[0]],i[0]])
        except:
            pass
    bs_local_leaderboard_data_temp.sort(reverse=True)
    bs_local_leaderboard_data = []
    for i in bs_local_leaderboard_data_temp:
        try:
            if len(bsdict[i[1]]['history']) != 0:
                bs_local_leaderboard_data.append(i[1])
        except:
            pass
    # finish
    with open("bs_guild_leaderboard_data.json","w") as f:
        json.dump(bs_local_leaderboard_data,f)
    if silence <= time.time():
        await channel.send(f"Global Leaderboard data updated.", silent=True)
    print("Global Leaderboard data updated.")

@interactions.Task.create(interactions.IntervalTrigger(hours=3))
async def ar_refresh():
    with open("bs_tags.json") as f:
        tagdict = json.load(f)
    tags = []
    for i in tagdict:
        for j in tagdict[i]:
            tags.append(j)

    ar = {}
    with open("bs_powerleague.json") as f:
        ranked = json.load(f)
    with open("bs_ar_supplementary.json") as f:
        extra = json.load(f)
    with open("tsr_best.json") as f:
        tsr = json.load(f)
    for tag in tags:
        arscore = 0
        #ranked
        if tag in ranked:
            arscore += ranked[tag]["best"]
        else:
            pass
        #tsr
        if tag in tsr:
            tsrscore = 0
            for i in tsr_rank_thresholds:
                if tsr[tag] < i:
                    break
                else:
                    tsrscore += 1
            arscore += tsrscore
        else:
            pass
        #sdr
        if tag in extra:
            arscore += int(abs(extra[tag]["sdr"]-100)/10)
        else:
            pass
        #abt
        if tag in extra:
            if extra[tag]["abt"] != -1:
                j = extra[tag]["abt"] - 500
                if j < 0:
                    j = 0
                abt_tsr = int(round(1.7777777*((j if j < 750 else 750)**2),0))
                tsrscore = 0
                for i in tsr_rank_thresholds:
                    if abt_tsr < i:
                        break
                    else:
                        tsrscore += 1
                arscore += int(tsrscore / 2)
            else:
                pass
        else:
            pass

        ar[tag] = arscore

    with open("bs_ar.json","w") as f:
        json.dump(ar,f)
    channel = bot.get_channel(logger)
    if silence <= time.time():
        await channel.send(f"AR compiled.",silent=True)
    print("AR updated.")

# ------------------------
# COMMANDS BELOW THIS LINE
# LOCAL SCOPE ONLY 
# ------------------------

@interactions.slash_command(name="say", description="Send a message somewhere as Shen", scopes=[scope])
@interactions.slash_option(name="content", description="The message. Use links for embeds or Discord Objects (as <...>)", required=True, opt_type=interactions.OptionType.STRING)
@interactions.slash_option(name="channel", description="Where to send (ID).", required=True, opt_type=interactions.OptionType.STRING)
async def say(ctx: interactions.SlashContext, content: str, channel: str):
    try:
        channel = bot.get_channel(int(channel))
        if silence <= time.time():
            await channel.send(content)
            await ctx.send("Sent.")
    except Exception as e:
        await ctx.send(f"An error occured.\n{e} : {str(e)}")

@interactions.slash_command(name="close", description="Quit the current session.", scopes=[scope])
@interactions.slash_option(name="quick_restart", description="Whether to skip autosync - Only use this when debugging.", required=False, opt_type=interactions.OptionType.BOOLEAN)
async def close(ctx: interactions.SlashContext, quick_restart: bool = False):
    exitcode = 0 if not quick_restart else 1
    with open("quick_restart.txt","w") as f:
        f.write(str(exitcode))
    await ctx.defer()
    await ctx.send("Session closing.")
    sys.exit(0)

@interactions.slash_command(name="tokenswitch", description="Overwrite the API-Key used to communicate with the Supercell API.", scopes=[scope])
@interactions.slash_option(name="new_key", description="The new API key received by the developer portal", required=True, opt_type=interactions.OptionType.STRING)
async def tokenswitch(ctx: interactions.SlashContext, new_key: str):
    await ctx.defer()
    global bs_api_token
    bs_api_token = new_key
    with open("bs_api_token.json","r") as f:
        tokendict = json.load(f)
        tokendict["main"] = bs_api_token
    with open("bs_api_token.json","w") as f:
        json.dump(tokendict,f) 
    await ctx.send("API Token overwritten.")

@interactions.slash_command(name="ip", description="Get the current IPv4-Address used by the current instance host device.", scopes=[scope])
async def ip(ctx: interactions.SlashContext):
    await ctx.send(urllib.request.urlopen('https://api4.ipify.org').read().decode('utf8'))

@interactions.slash_command(name="linknames", description="Save username-id relations to archive", scopes=[scope])
async def linknames(ctx: interactions.SlashContext):
    await ctx.defer()
    with open("bs_tags.json") as f:
        tag_dict = json.load(f)
    name_dict = {}
    for i in tag_dict.keys():
        try:
            j = await bot.fetch_user(int(i))
            name_dict[i] = j.username
        except:
            name_dict[i] = "Unknown"+str(i)[:6]
    with open("dc_id_rel.json","w") as f:
        json.dump(name_dict,f)
    await ctx.send(f"Done.",ephemeral=True)

@interactions.slash_command(name="reset_ranked_elo", description="Set EVERYONE'S saved elo under 'current' to 0. Use on season switch if the hpdevfox API is down.", scopes=[scope])
async def reset_ranked_elo(ctx: interactions.SlashContext):
    await ctx.defer()
    with open("bs_powerleague.json") as f:
        pl_saves = json.load(f)
    for i in pl_saves:
        pl_saves[i]["current"] = 0
    with open("bs_powerleague.json","w") as f:
        json.dump(pl_saves,f)
    ctx.send("Completed.")

@interactions.slash_command(name="export", description="Search for a resource in the bot directory and send it", scopes=[scope])
@interactions.slash_option(name="query", description="(!listdir) : Query of file | (listdir) : subdirectory", required=True, opt_type=interactions.OptionType.STRING)
@interactions.slash_option(name="listdir", description="Instead of sending a resource, list items in subdirectory", required=False, opt_type=interactions.OptionType.BOOLEAN)
async def export(ctx: interactions.SlashContext, listdir: bool = False, query: str = ""):
    if listdir:
        try:
            await ctx.send(f"```\n{os.listdir((query) if query != '' else None)}\n```")
            return
        except:
            await ctx.defer(ephemeral=True)
            await ctx.send(f"{emojidict['Warning']} Subdirectory does not exist. Typo?")
            return
    else:
        try:
            file = interactions.File(query)
            await ctx.send(file=file)
            return
        except:
            await ctx.defer(ephemeral=True)
            await ctx.send(f"{emojidict['Warning']} Resource does not exist. Typo?")
            return

@interactions.slash_command(name="silenceverbose", description="Mute the periodic task output for a set amount to time", scopes=[scope])
@interactions.slash_option(name="duration", description="Amount of minutes to mute for. Set to 0 to remove any currently active silence.", required=True, opt_type=interactions.OptionType.INTEGER, min_value=0)
async def silenceverbose(ctx: interactions.SlashContext, duration: int):
    global silence
    await ctx.defer()
    with open("verbose_silence.json") as f:
        silence = json.load(f)
    if duration == 0:
        silence["dur"] = 0
        await ctx.send(f"{emojidict['Info']} Logging silence at 0")
    else:
        silence["dur"] = int(time.time()) + duration*60
        await ctx.send(f"{emojidict['Info']} Logging disabled until <t:{silence['dur']}:f> | <t:{silence['dur']}:R>")
    with open("verbose_silence.json","w") as f:
        json.dump(silence,f)
    silence = silence["dur"]
    
@interactions.slash_command(name="forcerefresh", description="Instantly rerun a task.", scopes=[scope])
@interactions.slash_option(name="subject", description="Task to push", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="AutoSync",value="AS"),interactions.SlashCommandChoice(name="Leaderboard (Player)",value="LBp"),interactions.SlashCommandChoice(name="AR Compilation",value="AR")])
async def forcerefresh(ctx: interactions.SlashContext, subject: str):
    await ctx.defer()
    await ctx.send(f"<{subject}> initiated.")
    if subject == "AS":
        await autosync()
    elif subject == "LBp":
        await bs_player_leaderboard()
    elif subject == "AR":
        await ar_refresh()

@interactions.slash_command(name="resetbasedata", description="Reload all .json files and try to fetch newest info from the BS API", scopes=[scope])
async def resetbasedata(ctx: interactions.SlashContext):
    global bs_api_token, dsn, silence, calStatus
    await ctx.defer()
    with open("bs_api_token.json") as f:
        bs_api_token = json.load(f)["main"]
    with open("sentry_dsn.json") as f:
        dsn = json.load(f)["main"]
    try:
        with open("verbose_silence.json") as f:
            silence = json.load(f)["dur"]
    except:
        silence = 0
        with open("verbose_silence.json","w") as f:
            json.dump({"dur":0},f)
    calibrate()
    await ctx.send("Done.")

@interactions.slash_command(name="paginator_test", description="Testing callbacks over pages", scopes=[scope])
async def paginatortest(ctx: interactions.SlashContext):
    embeds = []
    for i in range(5):
        embeds.append(interactions.Embed(title=f"EMBED {i}",
            color=0x6f07b4))
    paginator = Paginator.create_from_embeds(bot, *embeds,)
    paginator.callback = test()
    await paginator.send(ctx)

def test():
    print("!!!")

#---------------------------
# GLOBAL COMMANDS BELOW
#---------------------------

@interactions.slash_command(name="whois", description="Get linked tags for users of Shenzhia.")
@interactions.slash_option(name="id", description="ID of the user in question", required=True, opt_type=interactions.OptionType.STRING)
async def whois(ctx: interactions.SlashContext, id: str):
    await ctx.defer()
    with open("bs_tags.json") as f:
        tags = json.load(f)
    if id not in tags.keys():
        await ctx.send(f"{emojidict['Warning']} Nothing found under this ID.")
    else:
        embed = interactions.Embed(title=f"LINKED PROFILES",
                        color=0x6f07b4,
                        timestamp=datetime.datetime.now())
        for i in range(5):
            try:
                embed.add_field(name=f"[{i+1}] - {tags[id][i]}",value=f" ")
            except:
                pass
        embed.set_footer(text="Shenzhia",
                        icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
        await ctx.send(embed=embed)
        return
    
@interactions.slash_command(name="leaderboard", description="Find the best Shenzhia users!")
async def leaderboard(ctx: interactions.SlashContext):
    await ctx.defer()
    with open("bs_data.json") as f:
        bsdict = json.load(f)
    with open("tsr_best.json") as f:
        tsrbest = json.load(f)
    with open("bs_tags.json") as f:
        x = json.load(f)
        names = x.keys()
        tags = x.values()
        tag_dict = {}
        for i, k in zip(tags, names):
            for j in i:
                tag_dict[j] = k
    embed = interactions.Embed(title=f"BEST SHENZHIA USERS",
                color=0x6f07b4,
                timestamp=datetime.datetime.now())
    index = 0
    placement = 1
    for i in bs_local_leaderboard_data[:9]:
        userelement = await bot.fetch_user(tag_dict[i])
        rank = emojidict['RankNone']
        rlist = list({"E":emojidict['RankE'],"D":emojidict['RankD'],"D+":emojidict['RankD+'],"C-":emojidict['RankC-'],"C":emojidict['RankC'],"C+":emojidict['RankC+'],"B-":emojidict['RankB-'],"B":emojidict['RankB'],"B+":emojidict['RankB+'],"A-":emojidict['RankA-'],"A":emojidict['RankA'],"A+":emojidict['RankA+'],"S-":emojidict['RankS-'],"S":emojidict['RankS'],"S+":emojidict['RankS+'],"SS":emojidict['RankSS'],"X":emojidict['RankEX']}.values())
        index2 = 0
        for j in tsr_rank_thresholds:
            if tsrbest[i] < j:
                break
            else:
                rank = rlist[index2]
                index2 += 1
        l_value = bsdict[i]['history'][-1]['value']
        l_indicator = [emojidict['Gold'],emojidict['Silver'],emojidict['Bronze'],''][index] + " "
        embed.add_field(name=f"{l_indicator}#{placement} {userelement.username}",value=f"{rank} | {tsrbest[i]:,} tsr\n{emojidict['Trophy']} {l_value}",inline=True)
        if index != 3:
            index += 1
        placement += 1
    embed.set_footer(text="Shenzhia",
                icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
    await ctx.send(embed=embed)
    return

@interactions.slash_command(name="roll", description="Get a random number from a specified range.")
@interactions.slash_option(name="maximum", description="The highest possible value", required=True, opt_type=interactions.OptionType.INTEGER, min_value=2, max_value=9999999)
@interactions.slash_option(name="multiplier", description="How often to roll", required=False, opt_type=interactions.OptionType.INTEGER, min_value=1, max_value=10)
async def roll(ctx: interactions.SlashContext, maximum: int, multiplier: int = 1):
    await ctx.defer()
    output = ""
    for i in range(multiplier):
        output += "[" + str(random.randint(1,maximum)) + "]"
        output += ", " if i+1 != multiplier else ""
    await ctx.send(f"```\n@{maximum} // x{multiplier}\n```\n{output}")

@interactions.slash_command(name="shuffle", description="Get a random item from a specified list.")
async def shuffle(ctx: interactions.SlashContext):
    list_modal = interactions.Modal(interactions.ShortText(label="List to shuffle", placeholder="Seperate items with ','!", custom_id="userinput"), title="List-Shuffle", custom_id="shuffle")
    await ctx.send_modal(modal=list_modal)

@interactions.slash_command(name="autosync", description="Enable automatic trophy saving for your primary linked tag. (Requires linked profile)")
async def enable_autosync(ctx: interactions.SlashContext):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_data.json","r") as f:
        bsdict = json.load(f)
    if not str(ctx.author.id) in tags.keys():
        await ctx.send(f"{emojidict['Warning']} You are not linked to a BS-Account to sync.")
        return
    for i in tags[str(ctx.author.id)]:
        if not i in bsdict.keys():
            await ctx.send(f"{emojidict['Warning']} You have yet to use '/performance' {'at at least one of your linked accounts ' if len(tags[str(ctx.author.id)]) > 1 else ''}to initiate a save.")
            return
    for i in tags[str(ctx.author.id)]:
        bsdict[i]["updates"] = True
    await ctx.send(f"{emojidict['Info']} AutoSync is turned on.")
    with open("bs_data.json","w") as f:
        json.dump(bsdict,f)

@interactions.slash_command(name="profilelink", sub_cmd_description="Set your own tag, so you can quickly use commands and access other special utility.", sub_cmd_name="add")
@interactions.slash_option(name="tag", description="Your tag, with '#' in front.", required=True, opt_type=interactions.OptionType.STRING)
async def profilelinkadd(ctx: interactions.SlashContext, tag: str = ""):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_data.json","r") as f:
        bsdict = json.load(f)
    with open("tsr_best.json","r") as f:
        tsrbest = json.load(f)
    with open("dc_id_rel.json") as f:
        name_dict = json.load(f)
    name = await bot.fetch_user(int(ctx.author_id))
    try:
        name_dict[int(ctx.author_id)] = str(name)
    except:
        name_dict[int(ctx.author_id)] = int(ctx.author_id)
    with open("dc_id_rel.json","w") as f:
        json.dump(name_dict,f) 
    if str(ctx.author.id) in tags:
        if len(tags[str(ctx.author.id)]) >= 3:
            await ctx.send(f"{emojidict['Warning']} Max # of links created.",ephemeral=True)
            return
        if tag.upper() in tags[str(ctx.author.id)]:
            await ctx.send(f"{emojidict['Warning']} You already linked this tag to yourself.",ephemeral=True)
            return
        saved_tags = []
        for i in tags:
            saved_tags += tags[i] if i != str(ctx.author.id) else []
        if tag.upper() in saved_tags:
            await ctx.send(f"{emojidict['Warning']} This tag has been blocked for linking as it has been linked to somebody else.",ephemeral=True)
            return
    url = f"https://api.brawlstars.com/v1/players/{urllib.parse.quote(tag)}/"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bs_api_token}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 429:
                await ctx.send(f"{emojidict['Error']} API is overloaded.\n-# Try again later.",ephemeral=True)
                return
            if response.status != 200:
                await ctx.send(f"{emojidict['Warning']} '#' missing, Tag incorrect and/or API unavailable.\n-# Use '/status' to check for connectivity.")
                return
    try:
        tags[str(ctx.author.id)].append(tag.upper())
    except:
        tags[str(ctx.author.id)] = [tag.upper()]
    await ctx.send(f"{emojidict['Info']} Your profile was linked.")
    with open("bs_tags.json","w") as f:
        json.dump(tags,f)
    
@interactions.slash_command(name="profilelink", sub_cmd_description="Remove a tag you have set previously.", sub_cmd_name="remove")
@interactions.slash_option(name="tag", description="Your tag, with '#' in front.", required=True, opt_type=interactions.OptionType.STRING)
async def profilelinkremove(ctx: interactions.SlashContext, tag: str = ""):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_data.json","r") as f:
        bsdict = json.load(f)
    with open("tsr_best.json","r") as f:
        tsrbest = json.load(f)
    if str(ctx.author.id) not in tags:
        await ctx.send(f"{emojidict['Warning']} No profiles linked yet.")
        return
    if tag.upper() not in tags[str(ctx.author.id)]:
        await ctx.send(f"{emojidict['Warning']} This tag is not linked to your account.")
        return
    tags[str(ctx.author.id)].remove(tag.upper())
    await ctx.send(f"{emojidict['Info']} Removed successfully.")
    with open("bs_tags.json","w") as f:
        json.dump(tags,f)
    
@interactions.slash_command(name="profilelink", sub_cmd_description="View your linked tags.", sub_cmd_name="view")
async def profilelinkview(ctx: interactions.SlashContext):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_data.json","r") as f:
        bsdict = json.load(f)
    with open("tsr_best.json","r") as f:
        tsrbest = json.load(f)
    if str(ctx.author.id) not in tags:
        await ctx.send(f"{emojidict['Warning']} No profiles linked yet.",ephemeral=True)
        return
    embed = interactions.Embed(title=f"LINKED PROFILES",
                    color=0x6f07b4,
                    timestamp=datetime.datetime.now())
    for i in range(3):
        if i > len(tags[str(ctx.author.id)]) - 1:
            embed.add_field(name=f"[{i+1}] - ///",value="*Empty slot*")
        else:
            try:
                embed.add_field(name=f"[{i+1}] - {tags[str(ctx.author.id)][i]}",value=f"Most recent Trophies: {bsdict[tags[str(ctx.author.id)][i]]['history'][-1]['value']:,} / Best TSR: {tsrbest[tags[str(ctx.author.id)][i]]:,}")
            except:
                try:
                    embed.add_field(name=f"[{i+1}] - {tags[str(ctx.author.id)][i]}",value=f"Most recent Trophies: {bsdict[tags[str(ctx.author.id)][i]]['history'][-1]['value']:,} / Best TSR: {tsrbest[tags[str(ctx.author.id)][i]]:,}")
                except:
                    embed.add_field(name=f"[{i+1}] - {tags[str(ctx.author.id)][i]}",value="*No records*")
    embed.set_footer(text="Shenzhia",
                    icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
    await ctx.send(embed=embed)

@interactions.slash_command(name="bling", description="Look for a player's projected Bling gain and Trophy Reset.")
@interactions.slash_option(name="tag", description="Requested Profile (empty: your own)", required=False, opt_type=interactions.OptionType.STRING)
async def bling(ctx: interactions.SlashContext, tag: str = ""):
    with open("bs_data.json") as f:
        bsdict = json.load(f)    
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    tag = tag.upper()
    multi = False
    try:
        if tag == "":
            multi = True if len(tags[str(ctx.author.id)]) > 1 else False
            tag = tags[str(ctx.author.id)]
        else:
            tag = [tag]
    except:
        await ctx.send(f"{emojidict['Warning']} No tag is saved to your account.\n-# Use '/profilelink' to set one.")
        return
    for i in tag:
        try:
            x = bsdict[i]
        except:
            bsdict[i] = {"history":[],"updates":False}
    embeds = []
    for element in tag:
        url = f"https://api.brawlstars.com/v1/players/{urllib.parse.quote(element)}/"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
        try:
            print(data["reason"])
            await ctx.send(send_api_error(data["reason"]))
            return
        except:
            try:
                if data["message"] == "API at maximum capacity, request throttled.":
                    await ctx.send(f"{emojidict['Error']} API is overloaded.\n-# Try again later.")
            except:
                pass
        cutoffs = {501:4,525:6,550:8,575:10,600:12,625:14,650:16,675:18,700:20,725:22,750:24,775:26,800:28,825:30,850:32,875:34,900:36,925:38,950:40,975:42,1000:44,1050:46,1100:48,1150:50,1200:52,1250:54,1300:56,1350:58,1400:60,1450:62,1500:64}
        totaltrophies = data["trophies"]
        tlist = []
        for i in data["brawlers"]:
            tlist.append(i["trophies"])
        tlist.sort(reverse=True)
        xtlist = tlist[0:10]
        templist = []
        for i in range(len(xtlist)):
            if xtlist[i] < 501:
                templist.append(i)
        templist.reverse()
        for i in templist:
            xtlist.pop(i)
        bling = 0
        deduction = 0
        for i in xtlist:
            for k in range(len(cutoffs)):
                if i < list(cutoffs.keys())[k]:
                    deduction += i - (list(cutoffs.keys())[k-1]-1)
                    bling += cutoffs[list(cutoffs.keys())[k-1]]
                    break


        embed = interactions.Embed(title=f"{data['name']} ({element})",
                        color=0x6f07b4,
                        timestamp=datetime.datetime.now())

        embed.add_field(name=f"{emojidict['Trophy']}",value=f"{totaltrophies:,} \u27A1 {totaltrophies-deduction:,} (-{deduction})",inline=False)
        embed.add_field(name={emojidict['Bling']},value="+"+str(bling),inline=False)
        embed.set_footer(text="Shenzhia",
                        icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
        embeds.append(embed)
    pg = Paginator.create_from_embeds(bot, *embeds)
    await pg.send(ctx)
    with open("bs_data.json","w") as f:
        json.dump(bsdict,f)

@interactions.slash_command(name="performance", description="Get a player's performance report, containing Trophy/Ranked info and TSR - a custom skill metric.", integration_types=[interactions.IntegrationType.GUILD_INSTALL, interactions.IntegrationType.USER_INSTALL])
@interactions.slash_option(name="tag", description="Requested Profile (empty: your own)", required=False, opt_type=interactions.OptionType.STRING)
@interactions.slash_option(name="extend", description="Show 18 instead of 12 brawlers", required=False, opt_type=interactions.OptionType.BOOLEAN)
async def performance(ctx: interactions.SlashContext, tag: str = "", extend: bool = False):
    await ctx.defer()
    if "fuckyou" in tag.lower().replace(" ",""):
        await ctx.send("https://i.imgur.com/6nfTFiR.png",ephemeral=True)
        return
    with open("bs_data.json") as f:
        bsdict = json.load(f)
    with open("tsr_best.json") as f:
        tsrbest = json.load(f)
    if tag != "":
        if tag[0] != "#":
            await ctx.send(f"{emojidict['Warning']} '#' missing from tag",ephemeral=True)
            return
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    try:
        if tag == "":
            tag = tags[str(ctx.author.id)]
        else:
            tag = [tag]
    except:
        await ctx.send(f"{emojidict['Warning']} No tag is saved to your account.\n-# Use '/profilelink' to set it.",ephemeral=True)
        return
    embeds = []
    for tag_element in tag:
        try:
            x = bsdict[tag_element]
        except:
            bsdict[tag_element] = {"history":[],"updates":False}
        url = f"https://api.brawlstars.com/v1/players/{urllib.parse.quote(tag_element)}/"
        url2 = f"https://api.hpdevfox.ru/profile/{tag_element.replace('#','')}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
            del headers["Authorization"]
            try:
                async with session.get(url2, headers=headers,timeout=5) as response:
                    su_data = await response.json()
            except:
                su_data = 0
        try:
            print(data["reason"])
            await ctx.send(send_api_error(data["reason"]),ephemeral=True)
            if bsdict[tag_element]["history"] == []:
                del bsdict[tag_element]
            return
        except:
            try:
                if data["message"] == "API at maximum capacity, request throttled.":
                    await ctx.send(f"{emojidict['Error']} API is overloaded.\n-# Try again later.",ephemeral=True)
                if bsdict[tag_element]["history"] == []:
                    del bsdict[tag_element]            
                return
            except:
                pass
        # Mastery
        mastery_dict = {}
        if su_data != 0:
            for i in su_data["response"]["Heroes"]:
                mastery_dict[brawlerIDs[i["Character"]]] = i["Mastery"]
        # Ranked
        load_from_archive = False
        try:
            i = su_data["response"]["Stats"]
            ranked_dict = {"rank_current":i["23"],"rank_best":i["22"],"score_current":i["24"],"score_best":i["25"]}
        except:
            load_from_archive = True
        brawlerlist = data["brawlers"]
        def brawlersort(a):
            return a["trophies"]
        brawlerlist.sort(reverse=True,key=brawlersort)
        gadgetcount = starpowercount = gearcount = 0
        pplist = []
        for i in brawlerlist:
            gadgetcount += len(i["gadgets"])
            starpowercount += len(i["starPowers"])
            gearcount += len(i["gears"])
        spice = 0
        with open("bs_spicyness.json") as f:
            spdict = json.load(f)
        ex_certified = True
        excludeSF = False
        for i in range(9):
            try:
                pplist.append(brawlerlist[i]["trophies"]-500 if brawlerlist[i]["trophies"]-500 > 0 else 0)
                try:
                    spice += spdict[brawlerlist[i]["name"]] / [2,2,2,1,1,1,0.5,0.5,0.5][i]
                except:
                    excludeSF = True
            except:
                excludeSF = True
        if len(pplist) == 9 and min(pplist) < 750:
            ex_certified = False
        ppscore = 0
        pplist_b = []
        index2 = 0
        for i in pplist:
            ppscore += int(round(1.7777777*((i if i < 750 else 750)**2),0) / [4,8,8,8,8,16,16,16,16][index2])
            ppscore += (i - 750) if i > 750 else 0
            pplist_b.append(int(round(1.7777777*((i if i < 750 else 750)**2),0) / [4,8,8,8,8,16,16,16,16][index2]))
            pplist_b[index2] += ((i - 750) if i > 750 else 0)
            index2 += 1
        if ppscore >= 1000000 and not ex_certified:
            ppscore = 999999
        ssdv = data["soloVictories"]
        dsdv = data["duoVictories"]
        v3v = data["3vs3Victories"]
        try:
            if tag_element in tags[str(ctx.author.id)]:
                if len(bsdict[tag_element]["history"]) > 3:
                    if not(data["trophies"] == bsdict[tag_element]["history"][-1]["value"]):
                        bsdict[tag_element]["history"].append({"value":data['trophies'],"time":int(time.time()),"tsr":ppscore,"relevancy":True})
                        print(f"[{tag_element}] Appended '"+str({"value":data['trophies'],"time":int(time.time()),"tsr":ppscore,"relevancy":True})+"'")
                    else:
                        bsdict[tag_element]["history"][-1] = {"value":data['trophies'],"time":int(time.time()),"tsr":ppscore,"relevancy":True}
                        print(f"[{tag_element}] Rebuilt last list entry for next bsp")
                else:
                    bsdict[tag_element]["history"].append({"value":data['trophies'],"time":int(time.time()),"tsr":ppscore,"relevancy":True})
                    print(f"[{tag_element}] Appended '"+str({"value":data['trophies'],"time":int(time.time()),"tsr":ppscore,"relevancy":True})+"'")
                print(bsdict[tag_element]["history"][-1])
            else:
                if bsdict[tag]["history"] == []:
                    del bsdict[tag]
        except:
            pass
        try:
            if int((ssdv+dsdv)/(ssdv+dsdv+v3v)*100) > 40:
                showdownwarning = True
            else:
                showdownwarning = False
        except:
            showdownwarning = False
        embed = interactions.Embed(title=f"{data['name']} ({tag_element})",
                        color=0x6f07b4,
                        timestamp=datetime.datetime.now())
        embed.add_field(name=f"{emojidict['Trophy']} {data['trophies']:,}",value=f"Best: {data['highestTrophies']:,}",inline=True)
        
        if len(brawlerlist) >= 10:
            performancelist = []
            for i in range(len(brawlerlist)):
                performancelist.append(brawlerlist[i]['trophies'])
            averagetrophies = 0
            for i in performancelist:
                averagetrophies += i
            try:
                averagetrophies /= len(performancelist)
            except:
                pass
        else:
            averagetrophies = "N/A"
        if len(brawlerlist) >= 10:
            powerlist = []
            for i in range(len(brawlerlist)):
                powerlist.append(brawlerlist[i]['power'])
            averagepower = 0
            for i in powerlist:
                averagepower += i
            try:
                averagepower /= len(powerlist)
            except:
                pass
        else:
            averagepower = "N/A"
        # for win rate
        url = f"https://api.brawlstars.com/v1/players/{urllib.parse.quote(tag_element)}/battlelog"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
        wins = 0
        total = 0
        flukes = 0
        isPowerLeague = False
        streak = 0
        streak_active = True
        nolog = False
        try:
            for i in data["items"]:
                #win rate
                try:
                    if i["battle"]["result"] == "victory":
                        wins += 1
                    if i["battle"]["result"] != "draw":
                        total += 1
                    if i["battle"]["result"] == "defeat" and tag == i["battle"]["starPlayer"]["tag"]:
                        flukes += 1
                    #Streaking
                    if i["battle"]["result"] == "victory" and streak_active:
                        if streak < 0:
                            streak_active = False
                        else:
                            streak += 1
                    if i["battle"]["result"] == "defeat" and streak_active:
                        if streak > 0:
                            streak_active = False
                        else:
                            streak -= 1
                except:
                    pass
                #PL background scanning
                if i["battle"]["type"].upper() in ["TEAMRANKED","SOLORANKED"] and not isPowerLeague:
                    isPowerLeague = True
                    with open("bs_powerleague.json", "r") as f:
                        pl_saves = json.load(f)
                    for j in [0,1]:
                        for k in range(3):
                            if i['battle']['teams'][j][k]['tag'] not in pl_saves:
                                pl_saves[i['battle']['teams'][j][k]['tag']] = {"best":0,"current":0}
                            pl_saves[i['battle']['teams'][j][k]['tag']]["current"] = i['battle']['teams'][j][k]['brawler']['trophies']
                            if pl_saves[i['battle']['teams'][j][k]['tag']]["current"] > pl_saves[i['battle']['teams'][j][k]['tag']]["best"]:
                                pl_saves[i['battle']['teams'][j][k]['tag']]["best"] = pl_saves[i['battle']['teams'][j][k]['tag']]["current"]
                            if i['battle']['teams'][j][k]['tag'] == tag_element:
                                print(f"[{i['battle']['teams'][j][k]['tag']}] - value found {pl_saves[i['battle']['teams'][j][k]['tag']]['current']}={pl_saves[i['battle']['teams'][j][k]['tag']]['best']}")
                    with open("bs_powerleague.json", "w") as f:
                        pl_saves = json.dump(pl_saves,f)
        except:
            nolog = True
        if not showdownwarning:
            rank = emojidict['RankNone']
            rlist = list({"E":emojidict['RankE'],"D":emojidict['RankD'],"D+":emojidict['RankD+'],"C-":emojidict['RankC-'],"C":emojidict['RankC'],"C+":emojidict['RankC+'],"B-":emojidict['RankB-'],"B":emojidict['RankB'],"B+":emojidict['RankB+'],"A-":emojidict['RankA-'],"A":emojidict['RankA'],"A+":emojidict['RankA+'],"S-":emojidict['RankS-'],"S":emojidict['RankS'],"S+":emojidict['RankS+'],"SS":emojidict['RankSS'],"X":emojidict['RankEX']}.values())
            index2 = 0
            for i in tsr_rank_thresholds:
                if ppscore < i:
                    break
                else:
                    rank = rlist[index2]
                    index2 += 1
            with open("tsr_best.json") as f:
                try:
                    besttsrdict = json.load(f)
                    besttsr = besttsrdict[tag_element]
                except Exception as e:
                    besttsr = 0
            with open("tsr_best.json") as f:
                besttsrdict = json.load(f)
            if besttsr < ppscore:
                besttsr = ppscore
                besttsrdict[tag_element] = besttsr
                with open("tsr_best.json","w") as f:
                    json.dump(besttsrdict,f)
            with open("bs_ar_supplementary.json","r") as f:
                ars = json.load(f)
                ars[tag_element] = {"sdr":int((ssdv+dsdv)/(ssdv+dsdv+v3v)*100),"abt":int(round(averagetrophies,0)) if averagetrophies != 'N/A' else -1}
            with open("bs_ar_supplementary.json","w") as f:
                json.dump(ars,f)
            try:
                with open("bs_powerleague.json") as f:
                    ranked = json.load(f)
                with open("bs_ar_supplementary.json") as f:
                    extra = json.load(f)
                with open("tsr_best.json") as f:
                    tsr = json.load(f)
                arscore = 0
                #ranked
                if tag_element in ranked:
                    arscore += ranked[tag_element]["best"]
                else:
                    pass
                #tsr
                if tag_element in tsr:
                    tsrscore = 0
                    for i in tsr_rank_thresholds:
                        if tsr[tag_element] < i:
                            break
                        else:
                            tsrscore += 1
                    arscore += tsrscore
                else:
                    pass
                #sdr
                if tag_element in extra:
                    arscore += int(abs(extra[tag_element]["sdr"]-100)/10)
                else:
                    pass
                #abt
                if tag_element in extra:
                    if extra[tag_element]["abt"] != -1:
                        j = extra[tag_element]["abt"] - 500
                        if j < 0:
                            j = 0
                        abt_tsr = int(round(1.7777777*((j if j < 750 else 750)**2),0))
                        tsrscore = 0
                        for i in tsr_rank_thresholds:
                            if abt_tsr < i:
                                break
                            else:
                                tsrscore += 1
                        arscore += int(tsrscore / 2)
                    else:
                        pass
                else:
                    pass
            except Exception as e:
                arscore = "---"
                print(traceback.format_exc())
            embed.add_field(name=f"{rank} | {ppscore:,} TSR (Best: {besttsr:,})",value=f"AR: {arscore}",inline=True)
        if showdownwarning:
            embed.add_field(name=f"{emojidict['Warning']} High SD/3v3 Win-Ratio",value=f"No Advanced Stats calculated.",inline=True)
        try:
            if tag[0] in ["#8VGY00G9"]:
                if tag[0] == "#8VGY00G9":
                    embed.add_field(name=f"{emojidict['Gold']} SHENZHIA DEVELOPER",value=f" ",inline=False)
            elif tag[0] in bs_leaderboard_data:
                if bs_leaderboard_data.index(tag[0])+1 < 11:
                    icon = f"{emojidict['Gold']} "
                elif bs_leaderboard_data.index(tag[0])+1 < 51:
                    icon = f"{emojidict['Silver']} "
                else:
                    icon = f"{emojidict['Bronze']} "
                embed.add_field(name=f"{icon}#{bs_leaderboard_data.index(tag[0])+1} GLOBAL PLAYER",value=f" ",inline=False)
            elif tag[0] in bs_local_leaderboard_data[:9]:
                if bs_local_leaderboard_data.index(tag[0])+1 == 1:
                    icon = f"{emojidict['Gold']} "
                elif bs_local_leaderboard_data.index(tag[0])+1 == 2:
                    icon = f"{emojidict['Silver']} "
                elif bs_local_leaderboard_data.index(tag[0])+1 == 3:
                    icon = f"{emojidict['Bronze']} "
                else:
                    icon = ""
                embed.add_field(name=f"{icon}#{bs_local_leaderboard_data.index(tag[0])+1} SHENZHIA USER",value=f" ",inline=False)
            else:
                embed.add_field(name=f"---",value=f" ",inline=False)
        except:
            embed.add_field(name=f"---",value=f" ",inline=False)
        while len(pplist_b) < (12 if not extend else 18):
            pplist_b.append("-")
        for i in range(9 if not extend else 18):
            if not showdownwarning:
                tsr_display = f"{pplist_b[i]:,} tsr ({round(pplist_b[i]/(10000/[4,8,8,8,8,16,16,16,16,1,1,1,1,1,1,1,1,1][i]),2) if pplist_b[i]/(10000/[4,8,8,8,8,16,16,16,16,1,1,1,1,1,1,1,1,1][i]) < 100 else 100}%)" if pplist_b[i] != "-" else "-"
                try:
                    tsr_val = round(pplist_b[i]/(10000/[4,8,8,8,8,16,16,16,16,1,1,1,1,1,1,1,1,1][i]),2) if pplist_b[i]/(10000/[4,8,8,8,8,16,16,16,16,1,1,1,1,1,1,1,1,1][i]) < 100 else 100
                except:
                    tsr_val = 0
            else:
                tsr_display = ""
                tsr_val = -1
            nl = "\n"
            lock_brawler_overview = False
            try:
                bname = brawlerlist[i]['name'].upper()
            except:
                bname = "Unknown"
                lock_brawler_overview = True
            if not lock_brawler_overview:
                try:
                    try:
                        masterypoints = mastery_dict[bname]
                    except:
                        masterypoints = 0
                    m_index = 0
                    for j in [300,800,1500,2600,4000,5800,10300,16800,24800]:
                        if masterypoints >= j:
                            m_index += 1
                        else:
                            break
                    if m_index not in [0,9]:
                        multiplier = m_index%3 if m_index%3 != 0 else 3
                        mastery_display = f"{[emojidict['Bronze'],emojidict['Silver'],emojidict['Gold']][(m_index-1)//3]}" * multiplier
                    elif m_index == 9:
                        mastery_display = f"{emojidict['Gold']*3} + {masterypoints - 24800}"
                    else:
                        mastery_display = f""
                    gadgetindicator = emojidict['Gadget_OK'] if len(brawlerlist[i]["gadgets"]) > 0 else emojidict['Slot_Empty']
                    spindicator = emojidict['SP_OK'] if len(brawlerlist[i]["starPowers"]) > 0 else emojidict['Slot_Empty']
                    gearindicator1 = emojidict['Gear_OK'] if len(brawlerlist[i]["gears"]) > 0 else emojidict['Slot_Empty']
                    gearindicator2 = emojidict['Gear_OK'] if len(brawlerlist[i]["gears"]) > 1 else emojidict['Slot_Empty']
                    embed.add_field(name=f"[#{i+1}] {bname}\n{powericonlist[brawlerlist[i]['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}",value=f"{emojidict['Trophy']} {brawlerlist[i]['trophies']} / {brawlerlist[i]['highestTrophies']} [T{brawlerlist[i]['rank']}]{nl}{tsr_display}{nl if su_data != 0 else ''}{mastery_display}",inline=True)
                except Exception as e:
                    embed.add_field(name=f"[#-] ---",value=f"{emojidict['Trophy']} {0} / {0}{nl}{tsr_display}",inline=True)
                    print(f"{e} : {str(e)}")
        if lock_brawler_overview:
            embed.add_field(name=f"API DEFUNCT",value=f"{emojidict['Warning']} Invalid data recieved. Can't display brawler data. ;-;",inline=False)
        
        fluc_list = []
        try:
            for i in bsdict[tag_element]["history"]:
                if i["relevancy"] == True:
                    fluc_list.append(i)
            rev_list = list(reversed(bsdict[tag_element]["history"]))
        except:
            pass
        if len(fluc_list) > 1:
            sessionstr = f"{fluc_list[-1]['value'] - fluc_list[-2]['value']:,} {emojidict['Trophy']}"
            try:
                tsrstr = f"{fluc_list[-1]['tsr'] - fluc_list[-2]['tsr']:,} tsr"
            except:
                tsrstr = f"---"
            if fluc_list[-1]['value'] - fluc_list[-2]['value'] >= 0:
                sessionstr = "+" + sessionstr
            if not tsrstr == f"---":
                if fluc_list[-1]['tsr'] - fluc_list[-2]['tsr'] >= 0:
                    tsrstr = "+" + tsrstr
            embed.add_field(name=f"FLUCTUATION",value=f"<t:{fluc_list[-2]['time']}:R>\n{sessionstr} / {tsrstr}",inline=True)
        #Power League
        rlist = [emojidict['RankNone'],emojidict['RankE'],emojidict['RankE'],emojidict['RankE'],emojidict['RankD'],emojidict['RankD+'],emojidict['RankC-'],emojidict['RankC'],emojidict['RankC+'],emojidict['RankB-'],emojidict['RankB'],emojidict['RankB+'],emojidict['RankA-'],emojidict['RankA'],emojidict['RankA+'],emojidict['RankS-'],emojidict['RankS'],emojidict['RankS+'],emojidict['RankSS'],emojidict['RankEX']]
        if load_from_archive:
            with open("bs_powerleague.json","r") as f:
                pl_saves = json.load(f)
            if tag_element in pl_saves.keys():
                pl_index_best = pl_saves[tag_element]["best"]
                pl_index_current = pl_saves[tag_element]["current"]
                embed.add_field(name=f"RANKED DIVISION",value=f"Approximated Current:\n{rlist[pl_index_current]} | {['N/A','BRONZE 1','BRONZE 2','BRONZE 3','SILVER 1','SILVER 2','SILVER 3','GOLD 1','GOLD 2','GOLD 3','DIAMOND 1','DIAMOND 2','DIAMOND 3','MYTHIC 1','MYTHIC 2','MYTHIC 3','LEGENDARY 1','LEGENDARY 2','LEGENDARY 3','MASTER'][pl_index_current]}",inline=True)
            else:
                embed.add_field(name=f"RANKED DIVISION",value=f"{emojidict['RankNone']}\n*Unknown*",inline=True)
        else:
            embed.add_field(name=f"RANKED DIVISION",value=f"Current: {rlist[ranked_dict['rank_current']]} | {['N/A','B1','B2','B3','S1','S2','S3','G1','G2','G3','D1','D2','D3','M1','M2','M3','L1','L2','L3','MASTER'][ranked_dict['rank_current']]} ({ranked_dict['score_current']})\nBest: {rlist[ranked_dict['rank_best']]} | {['N/A','B1','B2','B3','S1','S2','S3','G1','G2','G3','D1','D2','D3','M1','M2','M3','L1','L2','L3','MASTER'][ranked_dict['rank_best']]} ({ranked_dict['score_best']})",inline=True)
        #Win Rate
        if nolog:
            embed.add_field(name=f"RECENT WIN-RATE",value=f"{emojidict['Warning']} Unavailable...",inline=True)
        else: 
            if total != 0:
                streak_display = ""
                while streak >= 11:
                    streak_display += "<:glittering_sparkles:1138150631811596320>"
                    streak -= 10
                streak_display += '✨'*abs(streak) if streak > 0 else '❌'*abs(streak)
                embed.add_field(name=f"RECENT WIN-RATE",value=f"{round((wins/total)*100,2)}%{' ('+str(round((wins/(total-flukes))*100,2))+'%)' if flukes > 0 else ''}\n{streak_display}",inline=True)
        #Finishing
        try:
            if tag_element == tags[str(ctx.author.id)][0]:
                asyc = 'ON' if bsdict[tags[str(ctx.author.id)][0]]['updates'] else 'OFF'
            else:
                raise Exception()
        except:
            asyc = "---"
        embed.add_field(name=f" ",value=f"ASYC: {asyc} / ABT: {int(round(averagetrophies,0)) if averagetrophies != 'N/A' else averagetrophies} / ABP: {round(averagepower,2) if averagepower != 'N/A' else averagepower} / SDR: {int((ssdv+dsdv)/(ssdv+dsdv+v3v)*100)} / WD: {wins:,}>{total:,}-{flukes:,} / SF: {round(spice,2) if not excludeSF else '---'}%",inline=False)
        if su_data == 0:
            embed.add_field(name=f"{emojidict['Warning']}", value="Extension-API is down. Certain data is currently unavailable.")
        if str(ctx.author_id) not in tags:
            embed.add_field(name=f"{emojidict['Info']}", value="Is this profile yours? Link it with /profilelink to get more utility!")
        embeds.append(embed)
    if len(embeds) == 1 and not str(ctx.author_id) in tags:
        await ctx.send(embed=embed)
    else:
        pg = Paginator.create_from_embeds(bot, *embeds)
        await pg.send(ctx)
    with open("bs_data.json","w") as f:
        json.dump(bsdict,f)

@interactions.slash_command(name="progression", description="Get a player's progression estimate, including brawler Util and Hypercharges.")
@interactions.slash_option(name="tag", description="Requested Profile (empty: your own)", required=False, opt_type=interactions.OptionType.STRING)
@interactions.slash_option(name="advanced", description="Calculate with 2 Gadgets, 2 SPs and 6 Gears instead", required=False, opt_type=interactions.OptionType.BOOLEAN)
async def progression(ctx: interactions.SlashContext, tag: str = "", advanced: bool = False):
    if maxHypercharges == 0:
        await ctx.send(f"{emojidict['Error']} Bad data in database. Please wait until intrenat errors have been fixed.",ephemeral=True)
    await ctx.defer()
    with open("bs_data.json") as f:
        bsdict = json.load(f)
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_hc_info.json","r") as f:
        hcinfo = json.load(f)
    try:
        if tag == "":
            tag = tags[str(ctx.author.id)]
        else:
            tag = [tag]
    except:
        await ctx.send(f"{emojidict['Warning']} No tag is saved to your account.\n-# Use '/profilelink' to set it.",ephemeral=True)
        return
    embeds = []
    for tag_element in tag:
        try:
            x = bsdict[tag_element]
        except:
            bsdict[tag_element] = {"history":[],"updates":False}
        #personal data req
        url = f"https://api.brawlstars.com/v1/players/%23{urllib.parse.quote(tag_element[1:])}/"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
        
        try:
            print(data["reason"])
            await ctx.send(send_api_error(data["reason"]), ephemeral=True)
            return
        except:
            try:
                if data["message"] == "API at maximum capacity, request throttled.":
                    await ctx.send(f"{emojidict['Error']} API is overloaded.\n-# Try again later.",ephemeral=True)
                    return
            except:
                pass
        hcInfoWarning = False
        try:
            infotext = "Hypercharge info not set! Use '/hyperchargecount' to set it." if tag_element in tags[str(ctx.author.id)] else "Hypercharge info for this tag is unknown."
        except:
            infotext = "Hypercharge info for this tag is unknown."
        if tag_element not in hcinfo.keys():
            hcInfoWarning = True
            hcinfo = {tag_element:{"value":0,"time":-1}}
        else:
            if time.time() - hcinfo[tag_element]["time"] > 3600*24*30 and not hcinfo[tag_element]["value"] == maxHypercharges:
                infotext = "Your HC-Config may be outdated."
                hcInfoWarning = True
        powerlevellist = []
        gadgetcount = starpowercount = gearcount = neededCoins = neededPP = neededCurrency = maxed =  0
        maxcredits = 0
        creditvalues = {}
        outdatedlist = False
        for i in range(5):
            for j in [['NITA', 'COLT', 'BULL', 'BROCK', 'EL PRIMO', 'BARLEY', 'POCO', 'ROSA'],['JESSIE', 'DYNAMIKE', 'TICK', '8-BIT', 'RICO', 'DARRYL', 'PENNY', 'CARL', 'JACKY', 'GUS'],['BO', 'EMZ', 'STU', 'PIPER', 'PAM', 'FRANK', 'BIBI', 'BEA', 'NANI', 'EDGAR', 'GRIFF', 'GROM', 'BONNIE', 'GALE', 'COLETTE', 'BELLE', 'ASH', 'LOLA', 'SAM', 'MANDY', 'MAISIE', 'HANK', 'PEARL', 'LARRY & LAWRIE', 'ANGELO', 'BERRY'],['MORTIS', 'TARA', 'GENE', 'MAX', 'MR. P', 'SPROUT', 'BYRON', 'SQUEAK', 'LOU', 'RUFFS', 'BUZZ', 'FANG', 'EVE', 'JANET', 'OTIS', 'BUSTER', 'GRAY', 'R-T', 'WILLOW', 'DOUG', 'CHUCK', 'CHARLIE', 'MICO', 'MELODIE', 'LILY', 'CLANCY', 'MOE'],['SPIKE', 'CROW', 'LEON', 'SANDY', 'AMBER', 'MEG', 'SURGE', 'CHESTER', 'CORDELIUS', 'KIT', 'DRACO', 'KENJI']][i]:
                maxcredits += [160,430,925,1900,3800][i]
                creditvalues[j] = [160,430,925,1900,3800][i]
        for i in data["brawlers"]:
            if i["name"] != "SHELLY":
                try:
                    maxcredits -= creditvalues[i["name"]]
                except:
                    outdatedlist = True
            powerlevellist.append(i["power"])
            gadgetcount += len(i["gadgets"])
            starpowercount += len(i["starPowers"])
            gearcount += len(i["gears"])
            neededCoins += [7765,7745,7710,7635,7495,7205,6725,5925,4675,2800,0][i["power"]-1]
            neededPP += [3740,3720,3690,3640,3560,3430,3220,2880,2330,1440,0][i["power"]-1]
            utilindex = [2,6] if advanced else [1,2]
            neededCoins += 1000*((len(i["gadgets"])-utilindex[0])*-1) if 1000*((len(i["gadgets"])-utilindex[0])*-1) > 0 else 0
            neededCoins += 2000*((len(i["starPowers"])-utilindex[0])*-1) if 2000*((len(i["starPowers"])-utilindex[0])*-1) > 0 else 0
            neededCoins += 1000*((len(i["gears"])-utilindex[1])*-1) if 1000*((len(i["gears"])-utilindex[1])*-1) > 0 else 0
            if not advanced:
                if len(i["gadgets"]) > 0 and len(i["starPowers"]) > 0 and len(i["gears"]) >= 2 and i["power"] == 11:
                    maxed += 1
            else:
                if len(i["gadgets"]) > 1 and len(i["starPowers"]) > 1 and len(i["gears"]) >= 6 and i["power"] == 11:
                    maxed += 1
        if not maxBrawlers == len(data["brawlers"]):
            for i in range(maxBrawlers - len(data["brawlers"])-1):
                neededCoins += 7765
                neededCoins += 5000 if not advanced else (2000+4000+5000)
                neededPP += 3740
        neededCoins += (maxHypercharges - hcinfo[tag_element]["value"])*5000
        neededCurrency = neededCoins + (neededPP * 2)

        embed = interactions.Embed(title=f"{data['name']} ({tag_element}) {'// EXTRA' if advanced else ''}",
                        color=0x6f07b4,
                        timestamp=datetime.datetime.now())
        newline = "\n"
        warning = emojidict['Warning']
        embed.add_field(name=f"BRAWLER GEAR COMPLETION",value=f"{emojidict['GadgetIcon']} `{gadgetcount}/{maxGadgets}`\n{emojidict['SPIcon']} `{starpowercount}/{maxStarpower}`\n{emojidict['GearIcon']} `{gearcount}`\n{emojidict['HChargeIcon']} `{hcinfo[tag_element]['value']}/{maxHypercharges}`{'' if not hcInfoWarning else newline+warning+' '+infotext}",inline=True)
        embed.add_field(name=f"BRAWLER POWER COMPLETION",value=f"`P11     : {powerlevellist.count(11)}`\n`P10     : {powerlevellist.count(10)}`\n`P 9     : {powerlevellist.count(9)}`\n`Below P9: {len(data['brawlers']) - (powerlevellist.count(11)+powerlevellist.count(10)+powerlevellist.count(9))}`",inline=True)
        embed.add_field(name=f"RESCOURCE DEFECIT",value=f"{emojidict['PPoint']} {neededPP:,}\n{emojidict['Coin']} {neededCoins:,}\n{emojidict['Credit']} {maxcredits:,}\nIncludes P11, {2 if advanced else 1} SP, {2 if advanced else 1} Gadget and {6 if advanced else 2} Gears per brawler,\nas well as all available Hypercharges\n{'Does not include saved up rescources'}{'' if not outdatedlist else newline+warning+' Credit requirements outdated.'}",inline=False)
        if not advanced:
            embed.add_field(name=f"TOTAL PROGRESSION",value=f"{maxed} / {len(data['brawlers'])} maxed brawlers\nCompletion% : {round(((maxCurrency-neededCurrency)/maxCurrency)*100,2)}%",inline=False)
        else:
            embed.add_field(name=f"TOTAL PROGRESSION",value=f"{maxed} / {len(data['brawlers'])} maxed brawlers\nCompletion% : {round(((maxCurrencyAdv-neededCurrency)/maxCurrencyAdv)*100,2)}%",inline=False)
        if str(ctx.author_id) not in tags:
            embed.add_field(name=f"{emojidict['Info']}", value="Is this profile yours? Link it with /profilelink to get more utility!")
        embed.set_footer(text="Shenzhia",
                        icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
        embeds.append(embed)
    pg = Paginator.create_from_embeds(bot, *embeds)
    await pg.send(ctx)

@interactions.slash_command(name="hyperchargecount", description="Set the amount of Hypercharges you own. (Requires profile-linking)")
@interactions.slash_option(name="mode", description="Whether to set an amount or increase an already existing one", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Set",value="set"),interactions.SlashCommandChoice(name="Increase",value="inc")])
@interactions.slash_option(name="amount", description="Either Amount of Hypercharges you own or amount of Hypercharges to add", required=True, opt_type=interactions.OptionType.INTEGER, min_value=0)
@interactions.slash_option(name="tagid", description="If multiple accounts are linked, index of target account. Defaults to first linked profile.", required=False, opt_type=interactions.OptionType.INTEGER, min_value=1, max_value=3)
async def hyperchargecount(ctx: interactions.SlashContext, mode: str, amount: int, tagid: int = 1):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_hc_info.json","r") as f:
        hcinfo = json.load(f)
    if str(ctx.author.id) not in tags.keys():
        await ctx.send(f"{emojidict['Warning']} Link your BS-Account with '/profilelink' first.",ephemeral=True)
        return
    if tagid > len(tags[str(ctx.author.id)]):
        await ctx.send(f"{emojidict['Warning']} Provided Tag-ID is out of range.",ephemeral=True)
        return
    tagid -= 1
    try:
        prevhc = hcinfo[tags[str(ctx.author.id)][tagid]]["value"]
    except:
        prevhc = -1
    try:
        if mode == "set":
            if amount > maxHypercharges:
                raise Exception()
        else:
            if prevhc == -1:
                await ctx.send(f"{emojidict['Warning']} No Hypercharge record.",ephemeral=True)
                return
            else:
                prevhc += amount
    except:
        await ctx.send(f"{emojidict['Warning']} This exceeds the maximum amount of Hypercharges obtainable.",ephemeral=True)
        return
    hcinfo[tags[str(ctx.author.id)][tagid]] = {"value":amount if mode == 'set' else prevhc,"time":time.time()}
    await ctx.send(f"Hypercharge count of [{tags[str(ctx.author.id)][tagid]}] updated to {hcinfo[tags[str(ctx.author.id)][tagid]]['value']}.")
    with open("bs_hc_info.json","w") as f:
        json.dump(hcinfo,f)

@interactions.slash_command(name="matchanalysis", description="Look for a player's recently player game and analyze all participants. 3v3 only.")
@interactions.slash_option(name="tag", description="Target Player (empty: self)", required=False, opt_type=interactions.OptionType.STRING)
@interactions.slash_option(name="offset", description="Search for a less recent game (range: 0 - 24)", required=False, opt_type=interactions.OptionType.INTEGER, max_value=24, min_value=0)
@interactions.slash_option(name="show_tags", description="Show scanned players tags along with thier name.", required=False, opt_type=interactions.OptionType.BOOLEAN)
@interactions.slash_option(name="tagid", description="[Only on self] If multiple accounts are linked, index of target account. Defaults to first profile.", required=False, opt_type=interactions.OptionType.INTEGER, min_value=1, max_value=3)
async def matchanalysis(ctx: interactions.SlashContext, tag: str = "", offset: int = 0, show_tags: bool = False, tagid: int = 1):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    if str(ctx.author.id) not in tags:
        await ctx.send(f"{emojidict['Warning']} No tag is saved to your account.\n-# Use '/profilelink' to set it.",ephemeral=True)
        return
    tag = tag.upper()
    if tag == "":
        tagid -= 1
        override = False
        try:
            tag = tags[str(ctx.author.id)][tagid]
        except:
            await ctx.send(f"{emojidict['Warning']} Tag under ID {tagid+1} is not set.",ephemeral=True)
            return
    else:
        override = False
    targettag = tag
    url = f"https://api.brawlstars.com/v1/players/{urllib.parse.quote(tag)}/battlelog"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bs_api_token}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
    try:
        print(data["reason"])
        await ctx.send(send_api_error(data["reason"]))
        return
    except:
        pass
    try:
        if data["message"] == "API at maximum capacity, request throttled.":
            await ctx.send(f"{emojidict['Error']} API is overloaded.\n-# Try again later.",ephemeral=True)
            return
    except:
        pass
    data = data['items'][offset]
    if 1:
        with open("output.json","w") as f:
            json.dump(data,f)
    if data["event"]["mode"] == "soloShowdown":
        ssd_mode = True
    else:
        ssd_mode = False
        if data["event"]["mode"] == "duels":
            duel_mode = True
        else:
            duel_mode = False
            if "teams" not in data["battle"].keys():
                await ctx.send(f"{emojidict['Warning']} Unsupported Mode")
                return
            if len(data["battle"]["teams"]) != 2:
                await ctx.send(f"{emojidict['Warning']} Unsupported Mode\n-# Allowed: 3v3, 5v5, Solo SD")
                return
            if len(data["battle"]["teams"][0]) != len(data["battle"]["teams"][1]):
                await ctx.send(f"{emojidict['Warning']} Unsupported Mode\n-# Friendly battles are excluded.")
                return
            if len(data["battle"]["teams"][0]) not in [3,5]:
                await ctx.send(f"{emojidict['Warning']} Unsupported Mode\n-# Friendly battles are excluded.")
                return
            else:
                mode5v5 = len(data["battle"]["teams"][1]) == 5

    if ssd_mode:
        drumrollplacements = ["FRANK","TARA","DARRLY","BULL","NITA","MORTIS","JESSIE"]
        result = data["battle"]["rank"]
        battletype = data["battle"]["mode"].upper()
        taglist = []
        trophylist = []
        for i in data["battle"]["players"]:
            taglist.append(i["tag"])
            trophylist.append(i["brawler"]["trophies"])
        extensionlist = []
        for i, j in zip(taglist, trophylist):
            tag = urllib.parse.quote(i)
            url = f"https://api.brawlstars.com/v1/players/{tag}/"

            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {bs_api_token}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    exdata = await response.json()

            ssdv = exdata["soloVictories"]
            dsdv = exdata["duoVictories"]
            v3v = exdata["3vs3Victories"]
            sdr = int((ssdv+dsdv)/(ssdv+dsdv+v3v)*100)

            brawlerlist = exdata["brawlers"]
            def brawlersort(a):
                return a["trophies"]
            brawlerlist.sort(reverse=True,key=brawlersort)
            pplist = []
            ex_certified = True
            for k in range(9):
                try:
                    pplist.append(brawlerlist[k]["trophies"]-500 if brawlerlist[k]["trophies"]-500 > 0 else 0)
                except:
                    pass
            
            if len(pplist) == 9 and min(pplist) < 750:
                ex_certified = False
            ppscore = 0
            index2 = 0
            for k in pplist:
                ppscore += int(round(1.7777777*((k if k < 750 else 750)**2),0) / [4,8,8,8,8,16,16,16,16][index2])
                ppscore += (k - 750) if k > 750 else 0
                index2 += 1
            if ppscore >= 1000000 and not ex_certified:
                ppscore = 999999
            rank = emojidict['RankNone']
            rankiconlist = list({"E":emojidict['RankE'],"D":emojidict['RankD'],"D+":emojidict['RankD+'],"C-":emojidict['RankC-'],"C":emojidict['RankC'],"C+":emojidict['RankC+'],"B-":emojidict['RankB-'],"B":emojidict['RankB'],"B+":emojidict['RankB+'],"A-":emojidict['RankA-'],"A":emojidict['RankA'],"A+":emojidict['RankA+'],"S-":emojidict['RankS-'],"S":emojidict['RankS'],"S+":emojidict['RankS+'],"SS":emojidict['RankSS'],"X":emojidict['RankEX']}.values())
            index2 = 0
            for k in tsr_rank_thresholds:
                if ppscore < k:
                    break
                else:
                    rank = rankiconlist[index2]
                    index2 += 1
            extensionlist.append({"trophies":exdata["trophies"],"tsr":ppscore,"rank":rank,"indivTrophies":j,"sdr":sdr})
        embed = interactions.Embed(title="RANK #"+str(result),
            color=0x6f06ee,
            timestamp=datetime.datetime.now())
        if data['event']['map'] is None:
            matchmap = "MAP MAKER"
        else:
            matchmap = data['event']['map'].upper()
        botmatch = False
        embed.set_author(name=f"Scanned Battle // {battletype} on '{matchmap}'")
        tsrt = 0
        tbtc = 0
        tttc = 0
        for i in range(10):
            tag_vis = "\n" + data['battle']['players'][i]['tag'] if show_tags else ""
            brawler_vis = data['battle']['players'][i]['brawler']['name']
            try:
                starhighlight = [emojidict['Gold'],emojidict['Silver'],emojidict['Bronze']][i]
            except:
                starhighlight = ""
            embed.add_field(name=f"#{i+1} | "+data['battle']['players'][i]['name']+" "+starhighlight,
                                value=f"{brawler_vis}\n{powericonlist[data['battle']['players'][i]['brawler']['power']-1]}\n[{data['battle']['players'][i]['brawler']['trophies']}]\n\n{extensionlist[i]['trophies']:,} Trophies\n{extensionlist[i]['tsr']:,} tsr\n{extensionlist[i]['rank']}",
                                inline=True)
            tsrt += extensionlist[i]['tsr']
            tbtc += extensionlist[i]['indivTrophies']
            tttc += extensionlist[i]['trophies']
            if extensionlist[i]['indivTrophies'] > extensionlist[i]['trophies']:
                botmatch = True
            if data['battle']['players'][i]['tag'] == targettag:
                targettsr = extensionlist[i]['tsr']
                targetbt = extensionlist[i]['indivTrophies']
                targettt = extensionlist[i]['trophies']
        if botmatch:
            del embed
            await ctx.send(f"{emojidict['Warning']} The scanned match is a bot-match and therefore can't get evaluated.")
            return
        #enable after fixes!
        x = 1
        embed.add_field(name="---",value=" ",inline=False)
        result = targetbt-int(tbtc/10)
        embed.add_field(name=f"Average Brawler Deviation",
                        value=f"{'+' if result > 0 else ''}{result:,}",
                        inline=True)
        result = targettt-int(tttc/10)
        embed.add_field(name="Average Total Trophy-Deviation",
                        value=f"{'+' if result > 0 else ''}{result:,}",
                        inline=True)
        result = targettsr-int(tsrt/10)
        embed.add_field(name="Average TSR-Deviation",
                        value=f"{'+' if result > 0 else ''}{result:,}",
                        inline=True)
        embed.set_footer(text="Shenzhia", icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
    else:
        if duel_mode:
            result = data["battle"]["result"].upper()
            battletype = data["battle"]["mode"].upper()
            taglist = []
            trophylist = []
            namelist = []
            for j in data["battle"]["players"]:
                taglist.append(j["tag"])
                trophylist.append(j["brawlers"][0]["trophies"])
                namelist.append(j["brawlers"][0]["name"])
            secondTeam = True if taglist.index(tag) > 2 else False
            extensionlist = []
            for i, j, k in zip(taglist, trophylist, namelist):
                tag = urllib.parse.quote(i)
                url = f"https://api.brawlstars.com/v1/players/{tag}/"

                headers = {
                    "Accept": "application/json",
                    "Authorization": f"Bearer {bs_api_token}"
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        exdata = await response.json()

                ssdv = exdata["soloVictories"]
                dsdv = exdata["duoVictories"]
                v3v = exdata["3vs3Victories"]
                sdr = int((ssdv+dsdv)/(ssdv+dsdv+v3v)*100)
                
                brawlerlist = exdata["brawlers"]
                gadgetcount = {}
                spcount = {}
                gearcount = {}
                for l in brawlerlist:
                    gadgetcount[l["name"]] = len(l["gadgets"])
                    spcount[l["name"]] = len(l["starPowers"])
                    gearcount[l["name"]] = len(l["gears"])
                def brawlersort(a):
                    return a["trophies"]
                brawlerlist.sort(reverse=True,key=brawlersort)
                pplist = []
                for l in range(9):
                    try:
                        pplist.append(brawlerlist[l]["trophies"]-500 if brawlerlist[l]["trophies"]-500 > 0 else 0)
                    except:
                        pass
                ppscore = 0
                index2 = 0
                for l in pplist:
                    ppscore += int(round(1.7777777*((l if l < 750 else 750)**2),0) / [4,8,8,8,8,16,16,16,16][index2])
                    ppscore += (l - 750) if l > 750 else 0
                    index2 += 1
                rank = emojidict['RankNone']
                rankiconlist = list({"E":emojidict['RankE'],"D":emojidict['RankD'],"D+":emojidict['RankD+'],"C-":emojidict['RankC-'],"C":emojidict['RankC'],"C+":emojidict['RankC+'],"B-":emojidict['RankB-'],"B":emojidict['RankB'],"B+":emojidict['RankB+'],"A-":emojidict['RankA-'],"A":emojidict['RankA'],"A+":emojidict['RankA+'],"S-":emojidict['RankS-'],"S":emojidict['RankS'],"S+":emojidict['RankS+'],"SS":emojidict['RankSS'],"X":emojidict['RankEX']}.values())
                index2 = 0
                for l in tsr_rank_thresholds:
                    if ppscore < l:
                        break
                    else:
                        rank = rankiconlist[index2]
                        index2 += 1
                extensionlist.append({"trophies":exdata["trophies"],"tsr":ppscore,"rank":rank,"sdr":sdr,"gadgets":gadgetcount,"sp":spcount,"gears":gearcount})
            embed = interactions.Embed(title=result,
                color=0x6f06ee,
                timestamp=datetime.datetime.now())
            if data['event']['map'] is None:
                matchmap = "MAP MAKER"
            else:
                matchmap = data['event']['map'].upper()
            botmatch = False
            embed.set_author(name=f"Scanned Battle // {battletype} on '{matchmap}'")
            tag_vis = "\n" + data['battle']['players'][0]['tag'] if show_tags else ""
            warning = emojidict['Warning']
            embed.add_field(name=data['battle']['players'][0]['name']+tag_vis,
                                value=f"{extensionlist[0]['trophies']:,} Trophies | {extensionlist[0]['tsr']:,} tsr {extensionlist[0]['rank']}{f' / {warning} SDR '+str(extensionlist[0]['sdr']) if extensionlist[0]['sdr'] > 40 else ''}",
                                inline=False)
            for i in range(3):
                gadgetindicator = emojidict['Gadget_OK'] if extensionlist[0]["gadgets"][data['battle']['players'][0]['brawlers'][i]['name']] > 0 else emojidict['Slot_Empty']
                spindicator = emojidict['SP_OK'] if extensionlist[0]["sp"][data['battle']['players'][0]['brawlers'][i]['name']] > 0 else emojidict['Slot_Empty']
                gearindicator1 = emojidict['Gear_OK'] if extensionlist[0]["gears"][data['battle']['players'][0]['brawlers'][i]['name']] > 0 else emojidict['Slot_Empty']
                gearindicator2 = emojidict['Gear_OK'] if extensionlist[0]["gears"][data['battle']['players'][0]['brawlers'][i]['name']] > 1 else emojidict['Slot_Empty']
                embed.add_field(name=data['battle']['players'][0]['brawlers'][i]['name'],
                                value=f"{powericonlist[data['battle']['players'][0]['brawlers'][i]['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}\n[{data['battle']['players'][0]['brawlers'][i]['trophies']:,}]",
                                inline=True)
            embed.add_field(name="----------",
                            value=" ",
                            inline=True)
            embed.add_field(name="VERSUS",
                            value=" ",
                            inline=True)
            embed.add_field(name="----------",
                            value=" ",
                            inline=True)
            tag_vis = "\n" + data['battle']['players'][1]['tag'] if show_tags else ""
            warning = emojidict['Warning']
            embed.add_field(name=data['battle']['players'][1]['name']+tag_vis,
                                value=f"{extensionlist[1]['trophies']:,} Trophies | {extensionlist[1]['tsr']:,} tsr {extensionlist[1]['rank']}{f' / {warning} SDR '+str(extensionlist[1]['sdr']) if extensionlist[1]['sdr'] > 40 else ''}",
                                inline=False)
            for i in range(3):
                gadgetindicator = emojidict['Gadget_OK'] if extensionlist[1]["gadgets"][data['battle']['players'][1]['brawlers'][i]['name']] > 0 else emojidict['Slot_Empty']
                spindicator = emojidict['SP_OK'] if extensionlist[1]["sp"][data['battle']['players'][1]['brawlers'][i]['name']] > 0 else emojidict['Slot_Empty']
                gearindicator1 = emojidict['Gear_OK'] if extensionlist[1]["gears"][data['battle']['players'][1]['brawlers'][i]['name']] > 0 else emojidict['Slot_Empty']
                gearindicator2 = emojidict['Gear_OK'] if extensionlist[1]["gears"][data['battle']['players'][1]['brawlers'][i]['name']] > 1 else emojidict['Slot_Empty']
                embed.add_field(name=data['battle']['players'][1]['brawlers'][i]['name'],
                                value=f"{powericonlist[data['battle']['players'][1]['brawlers'][i]['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}\n[{data['battle']['players'][1]['brawlers'][i]['trophies']:,}]",
                                inline=True)
            embed.add_field(name="-----",value=" ",inline=False)
            result = -1 * (int(extensionlist[0]['trophies'])-int(extensionlist[1]['trophies']) if not secondTeam else int(extensionlist[1]['trophies'])-int(extensionlist[0]['trophies']))
            embed.add_field(name="Average Total Trophy-Deviation",
                            value=f"{'+' if result > 0 else ''}{result:,}",
                            inline=True)
            result = -1 * (int(extensionlist[0]['tsr'])-int(extensionlist[1]['tsr']) if not secondTeam else int(extensionlist[1]['tsr'])-int(extensionlist[0]['tsr']))
            embed.add_field(name="Average TSR-Deviation",
                            value=f"{'+' if result > 0 else ''}{result:,}",
                            inline=True)
            embed.set_footer(text="Shenzhia", icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
        else:
            result = data["battle"]["result"].upper()
            battletype = data["battle"]["mode"].upper()
            try:
                starplayertag = data["battle"]["starPlayer"]["tag"]
            except:
                starplayertag = ""
            isRankedDiv = True if data["battle"]["type"].upper() in ["TEAMRANKED","SOLORANKED"] else False
            if isRankedDiv:
                with open("bs_powerleague.json", "r") as f:
                    pl_saves = json.load(f)
            taglist = []
            trophylist = []
            namelist = []
            for i in data["battle"]["teams"]:
                for j in i:
                    taglist.append(j["tag"])
                    trophylist.append(j["brawler"]["trophies"])
                    namelist.append(j["brawler"]["name"])
            secondTeam = True if taglist.index(tag) > 2 else False
            extensionlist = []
            if mode5v5:
                await ctx.send(f"{emojidict['Warning']} 5v5 `/matchanalysis` is in development.\n-# Please check back later")
            else:
                for i, j, k in zip(taglist, trophylist, namelist):
                    tag = urllib.parse.quote(i)
                    url = f"https://api.brawlstars.com/v1/players/{tag}/"

                    headers = {
                        "Accept": "application/json",
                        "Authorization": f"Bearer {bs_api_token}"
                    }

                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            exdata = await response.json()

                    ssdv = exdata["soloVictories"]
                    dsdv = exdata["duoVictories"]
                    v3v = exdata["3vs3Victories"]
                    sdr = int((ssdv+dsdv)/(ssdv+dsdv+v3v)*100)
                    
                    brawlerlist = exdata["brawlers"]
                    for l in brawlerlist:
                        if l["name"] == k:
                            gadgetcount = len(l["gadgets"])
                            spcount = len(l["starPowers"])
                            gearcount = len(l["gears"])
                            break
                    def brawlersort(a):
                        return a["trophies"]
                    brawlerlist.sort(reverse=True,key=brawlersort)
                    pplist = []
                    for l in range(9):
                        try:
                            pplist.append(brawlerlist[l]["trophies"]-500 if brawlerlist[l]["trophies"]-500 > 0 else 0)
                        except:
                            pass
                    ppscore = 0
                    index2 = 0
                    for l in pplist:
                        ppscore += int(round(1.7777777*((l if l < 750 else 750)**2),0) / [4,8,8,8,8,16,16,16,16][index2])
                        ppscore += (l - 750) if l > 750 else 0
                        index2 += 1
                    rank = emojidict['RankNone']
                    rankiconlist = list({"E":emojidict['RankE'],"D":emojidict['RankD'],"D+":emojidict['RankD+'],"C-":emojidict['RankC-'],"C":emojidict['RankC'],"C+":emojidict['RankC+'],"B-":emojidict['RankB-'],"B":emojidict['RankB'],"B+":emojidict['RankB+'],"A-":emojidict['RankA-'],"A":emojidict['RankA'],"A+":emojidict['RankA+'],"S-":emojidict['RankS-'],"S":emojidict['RankS'],"S+":emojidict['RankS+'],"SS":emojidict['RankSS'],"X":emojidict['RankEX']}.values())
                    index2 = 0
                    for l in tsr_rank_thresholds:
                        if ppscore < l:
                            break
                        else:
                            rank = rankiconlist[index2]
                            index2 += 1
                    extensionlist.append({"trophies":exdata["trophies"],"tsr":ppscore,"rank":rank,"indivTrophies":j,"sdr":sdr,"gadgets":gadgetcount,"sp":spcount,"gears":gearcount})
                embed = interactions.Embed(title=result,
                    color=0x6f06ee,
                    timestamp=datetime.datetime.now())
                if data['event']['map'] is None:
                    matchmap = "MAP MAKER"
                else:
                    matchmap = data['event']['map'].upper()
                botmatch = False
                for i in [data['battle']['teams'][1][x]['brawler']['trophies'] for x in [0,1,2]]:
                    pass
                embed.set_author(name=f"Scanned Battle // {battletype} on '{matchmap}'{' // RANKED' if isRankedDiv else ''}")
                tsrt1 = 0
                tbtc1 = 0
                tttc1 = 0
                for i in range(3):
                    tag_vis = "\n" + data['battle']['teams'][0][i]['tag'] if show_tags else ""
                    gadgetindicator = emojidict['Gadget_OK'] if extensionlist[i]["gadgets"] > 0 else emojidict['Slot_Empty']
                    spindicator = emojidict['SP_OK'] if extensionlist[i]["sp"] > 0 else emojidict['Slot_Empty']
                    gearindicator1 = emojidict['Gear_OK'] if extensionlist[i]["gears"] > 0 else emojidict['Slot_Empty']
                    gearindicator2 = emojidict['Gear_OK'] if extensionlist[i]["gears"] > 1 else emojidict['Slot_Empty']
                    if not isRankedDiv:
                        warning = emojidict['Warning']
                        embed.add_field(name=data['battle']['teams'][0][i]['name']+f"{emojidict['Gold']}"+tag_vis if starplayertag == data['battle']['teams'][0][i]['tag'] else data['battle']['teams'][0][i]['name']+tag_vis,
                                        value=f"{data['battle']['teams'][0][i]['brawler']['name']}\n{powericonlist[data['battle']['teams'][0][i]['brawler']['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}\n[{data['battle']['teams'][0][i]['brawler']['trophies']:,}]\n\n{extensionlist[i]['trophies']:,} Trophies\n{extensionlist[i]['tsr']:,} tsr\n{extensionlist[i]['rank']}{f' / {warning} SDR '+str(extensionlist[i]['sdr']) if extensionlist[i]['sdr'] > 40 else ''}",
                                        inline=True)
                    else:
                        embed.add_field(name=data['battle']['teams'][0][i]['name']+f"{emojidict['Gold']}"+tag_vis if starplayertag == data['battle']['teams'][0][i]['tag'] else data['battle']['teams'][0][i]['name']+tag_vis,
                                        value=f"{data['battle']['teams'][0][i]['brawler']['name']}\n{powericonlist[data['battle']['teams'][0][i]['brawler']['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}\n[{['','BRONZE 1','BRONZE 2','BRONZE 3','SILVER 1','SILVER 2','SILVER 3','GOLD 1','GOLD 2','GOLD 3','DIAMOND 1','DIAMOND 2','DIAMOND 3','MYTHIC 1','MYTHIC 2','MYTHIC 3','LEGENDARY 1','LEGENDARY 2','LEGENDARY 3','MASTER'][data['battle']['teams'][0][i]['brawler']['trophies']]}]\n\n{extensionlist[i]['trophies']:,} Trophies\n{extensionlist[i]['tsr']:,} tsr\n{extensionlist[i]['rank']}",
                                        inline=True)
                        if data['battle']['teams'][0][i]['tag'] not in pl_saves:
                            pl_saves[data['battle']['teams'][0][i]['tag']] = {"best":0,"current":0}
                        pl_saves[data['battle']['teams'][0][i]['tag']]["current"] = data['battle']['teams'][0][i]['brawler']['trophies']
                        if pl_saves[data['battle']['teams'][0][i]['tag']]["current"] > pl_saves[data['battle']['teams'][0][i]['tag']]["best"]:
                            pl_saves[data['battle']['teams'][0][i]['tag']]["best"] = pl_saves[data['battle']['teams'][0][i]['tag']]["current"]
                    tsrt1 += extensionlist[i]['tsr']
                    tbtc1 += extensionlist[i]['indivTrophies']
                    tttc1 += extensionlist[i]['trophies']
                    if extensionlist[i]['indivTrophies'] > extensionlist[i]['trophies']:
                        botmatch = True
                embed.add_field(name="----------",
                                value=" ",
                                inline=True)
                embed.add_field(name="VERSUS",
                                value=" ",
                                inline=True)
                embed.add_field(name="----------",
                                value=" ",
                                inline=True)
                tsrt2 = 0
                tbtc2 = 0
                tttc2 = 0
                for i in range(3):
                    tag_vis = "\n" + data['battle']['teams'][1][i]['tag'] if show_tags else ""
                    gadgetindicator = emojidict['Gadget_OK'] if extensionlist[3+i]["gadgets"] > 0 else emojidict['Slot_Empty']
                    spindicator = emojidict['SP_OK'] if extensionlist[3+i]["sp"] > 0 else emojidict['Slot_Empty']
                    gearindicator1 = emojidict['Gear_OK'] if extensionlist[3+i]["gears"] > 0 else emojidict['Slot_Empty']
                    gearindicator2 = emojidict['Gear_OK'] if extensionlist[3+i]["gears"] > 1 else emojidict['Slot_Empty']
                    if not isRankedDiv:
                        warning = emojidict['Warning']
                        embed.add_field(name=data['battle']['teams'][1][i]['name']+f"{emojidict['Gold']}"+tag_vis if starplayertag == data['battle']['teams'][1][i]['tag'] else data['battle']['teams'][1][i]['name']+tag_vis,
                                value=f"{data['battle']['teams'][1][i]['brawler']['name']}\n{powericonlist[data['battle']['teams'][1][i]['brawler']['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}\n[{data['battle']['teams'][1][i]['brawler']['trophies']:,}]\n\n{extensionlist[3+i]['trophies']:,} Trophies\n{extensionlist[3+i]['tsr']:,} tsr\n{extensionlist[3+i]['rank']}{f' / {warning} SDR '+str(extensionlist[3+i]['sdr']) if extensionlist[3+i]['sdr'] > 40 else ''}",
                                inline=True)
                    else:
                        embed.add_field(name=data['battle']['teams'][1][i]['name']+f"{emojidict['Gold']}"+tag_vis if starplayertag == data['battle']['teams'][1][i]['tag'] else data['battle']['teams'][1][i]['name']+tag_vis,
                                        value=f"{data['battle']['teams'][1][i]['brawler']['name']}\n{powericonlist[data['battle']['teams'][1][i]['brawler']['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}\n[{['','BRONZE 1','BRONZE 2','BRONZE 3','SILVER 1','SILVER 2','SILVER 3','GOLD 1','GOLD 2','GOLD 3','DIAMOND 1','DIAMOND 2','DIAMOND 3','MYTHIC 1','MYTHIC 2','MYTHIC 3','LEGENDARY 1','LEGENDARY 2','LEGENDARY 3','MASTER'][data['battle']['teams'][1][i]['brawler']['trophies']]}]\n\n{extensionlist[3+i]['trophies']:,} Trophies\n{extensionlist[3+i]['tsr']:,} tsr\n{extensionlist[3+i]['rank']}",
                                        inline=True)
                        if data['battle']['teams'][1][i]['tag'] not in pl_saves:
                            pl_saves[data['battle']['teams'][1][i]['tag']] = {"current":0,"best":0}
                        pl_saves[data['battle']['teams'][1][i]['tag']]["current"] = data['battle']['teams'][1][i]['brawler']['trophies']
                        if pl_saves[data['battle']['teams'][1][i]['tag']]["current"] > pl_saves[data['battle']['teams'][1][i]['tag']]["best"]:
                            pl_saves[data['battle']['teams'][1][i]['tag']]["best"] = pl_saves[data['battle']['teams'][1][i]['tag']]["current"]
                    tsrt2 += extensionlist[3+i]['tsr']
                    tbtc2 += extensionlist[3+i]['indivTrophies']
                    tttc2 += extensionlist[3+i]['trophies']
                    if extensionlist[3+i]['indivTrophies'] > extensionlist[3+i]['trophies']:
                        botmatch = True
                if botmatch:
                    del embed
                    await ctx.send(f"{emojidict['Warning']} The scanned match is a bot-match and thus can't get evaluated.")
                    return
                embed.add_field(name="-----",value=" ",inline=False)
                if not isRankedDiv:
                    result = int(tbtc1/3)-int(tbtc2/3) if not secondTeam else int(tbtc2/3)-int(tbtc1/3)
                else:
                    result = int(tbtc1)-int(tbtc2) if not secondTeam else int(tbtc2)-int(tbtc1)
                embed.add_field(name=f"{'Average Brawler' if not isRankedDiv else 'Ranked-Division'} Deviation",
                                value=f"{'+' if result > 0 else ''}{result:,}",
                                inline=True)
                result = int(tttc1/3)-int(tttc2/3) if not secondTeam else int(tttc2/3)-int(tttc1/3)
                embed.add_field(name="Average Total Trophy-Deviation",
                                value=f"{'+' if result > 0 else ''}{result:,}",
                                inline=True)
                result = int(tsrt1/3)-int(tsrt2/3) if not secondTeam else int(tsrt2/3)-int(tsrt1/3)
                embed.add_field(name="Average TSR-Deviation",
                                value=f"{'+' if result > 0 else ''}{result:,}",
                                inline=True)
                embed.set_footer(text="Shenzhia", icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
                if isRankedDiv:
                    with open("bs_powerleague.json", "w") as f:
                        json.dump(pl_saves,f)
    await ctx.send(embed=embed)

@interactions.slash_command(name="history", description="View a recorded graph of your stat development. (Requires linked profile)")
@interactions.slash_option(name="timespan", description="How far back the graph should go", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Last 30 days",value="30"),interactions.SlashCommandChoice(name="Last 90 days",value="90"),interactions.SlashCommandChoice(name="All Time",value="full")])
@interactions.slash_option(name="dataset", description="What dataset to use.", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Trophies",value="value"),interactions.SlashCommandChoice(name="TSR",value="tsr")])
@interactions.slash_option(name="graphcolor", description="Set the color of the graph. Use Hex-codes for this (#xxxxxx).", required=False, opt_type=interactions.OptionType.STRING, min_length=7, max_length=7)
@interactions.slash_option(name="tagid", description="If multiple accounts are linked, index of target account. Defaults to first linked profile.", required=False, opt_type=interactions.OptionType.INTEGER, min_value=1, max_value=5)
async def history(ctx: interactions.SlashContext, timespan: str, dataset: str, graphcolor: str = "", tagid: int = 1):
    await ctx.defer()
    limiter = timespan != "full"
    try:
        with open("bs_data.json") as f:
            savedata = json.load(f)
        with open("dc_id_rel.json") as f:
            translatenames = json.load(f)
        with open("bs_tags.json") as f:
            x = json.load(f)
            if str(ctx.author_id) not in x.keys():
                await ctx.send(f"{emojidict['Warning']} No tags linked.\n-# You have yet to use this bot. Go for it!",ephemeral=True)
                return
            if tagid > len(x[str(ctx.author_id)]):
                await ctx.send(f"{emojidict['Warning']} Selected slot empty.\n-# Filled slots: {len(x[str(ctx.author_id)])}",ephemeral=True)
                return
            i = x[str(ctx.author_id)][tagid-1]

        def calculate_brightness(hex_color):
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return (r * 299 + g * 587 + b * 114) / 1000

        z = 1
        if len(savedata[i]["history"]) > 3:
            if graphcolor == "" or (not bool(re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', graphcolor))):
                colorcode = f"#{random.randint(0,999999):06}"
            else:
                colorcode = graphcolor.upper().strip()
            xlist = []
            ylist = []
            xOrigin = savedata[i]['history'][0]["time"]
            for k in savedata[i]['history']:
                if dataset in k.keys():
                    if dataset == "value":
                        xlist.append((k["time"] - xOrigin)/86400)
                        ylist.append(k[dataset])
                    elif dataset == "tsr" and k[dataset] != -1:
                        xlist.append((k["time"] - xOrigin)/86400)
                        ylist.append(k[dataset])
            brightness = calculate_brightness(colorcode)
            br_threshold = 128
            if brightness < br_threshold:
                plt.style.use('default')
            else:
                plt.style.use('dark_background')
            plt.rcParams['axes.axisbelow'] = True
            plt.rcParams["font.family"] = "Torus"
            #plt.rcParams["font.weight"] = "bold"
            plt.step(xlist,ylist,color=colorcode,where="post")
            plt.xlabel(f"DAYS SINCE FIRST RECORDING\n({datetime.datetime.utcfromtimestamp(savedata[i]['history'][0]['time']).strftime('%d.%m.%Y')})")
            plt.ylabel({"value":"TROPHIES","tsr":"TSR"}[dataset])
            subject = {'value':'Trophy','tsr':'TSR'}[dataset]
            try:
                plt.title(f"{subject}-Progression for '{translatenames[str(ctx.author_id)]}'/{i}")
            except:
                plt.title(f"{subject}-Progression for {i}")
            if brightness > br_threshold:
                plt.grid(which="major", color='gray')
                plt.grid(which="minor", color='#222222', linestyle="dashed")
            else:
                plt.grid(which="major", color='gray')
                plt.grid(which="minor", color='#DDDDDD', linestyle="dashed")
            plt.minorticks_on()
            plt.ylim(int(min(ylist)/500)*500,(int(max(ylist)/500)+2)*500)
            if max(xlist) <= 15:
                margin_negative = 0.9
            else:
                margin_negative = int(max(xlist)/15)
            stepunit = 500
            markers = int(max(ylist)/stepunit)+2 - int(min(ylist)/stepunit)
            while markers > 15:
                stepunit *= 2
                markers = int(max(ylist)/stepunit)+2 - int(min(ylist)/stepunit)
            if not limiter:
                if dataset == "value":
                    plt.xlim(0-margin_negative,round(max(xlist))+1+int(max(xlist)/10))
                else:
                    plt.xlim(int(min(xlist))-margin_negative,round(max(xlist))+1+int(max(xlist)/10))
                plt.yticks(np.arange(int(min(ylist)/500)*500, (int(max(ylist)/500)+2)*500+1, stepunit))
                adjusted_lim = min(ylist)
            else:
                timespan = int(timespan)
                plt.xlim(left=max(xlist)-timespan if max(xlist) > timespan else 0-margin_negative)
                #plt.xlim(max(xlist)-timespan if max(xlist) > timespan else 0-margin_negative,round(max(xlist))+1+int(max(xlist)/10))
                plt.yticks(np.arange(int(min(ylist)/500)*500, (int(max(ylist)/500)+2)*500+1, stepunit))
                if max(xlist) > timespan:
                    for k in reversed(xlist):
                        if max(xlist) - timespan > k:
                            break
                    adjusted_lim = ylist[xlist.index(k)]
                    plt.ylim(int(adjusted_lim/500)*500,(int(max(ylist)/500)+2)*500)
                    stepunit = 500
                    markers = int(max(ylist)/stepunit)+2 - int(adjusted_lim/stepunit)
                    while markers > 15:
                        stepunit *= 2
                        markers = int(max(ylist)/stepunit)+2 - int(adjusted_lim/stepunit)
                    plt.yticks(np.arange(int(adjusted_lim/500)*500, (int(max(ylist)/500)+2)*500+1, stepunit))
            prev = (999999,999999)
            xmin, xmax, ymin, ymax = plt.axis()
            minimun_distance = np.sqrt((xmax - xmin)**2 + (ymax - ymin)**2) * 0.1
            for x,y in zip(xlist,ylist):
                distance = np.sqrt((x - prev[0])**2 + (y - prev[1])**2)
                if distance >= minimun_distance or xlist.index(x) == len(xlist)-1:
                    if not((xlist.index(x) == len(xlist)-1)):
                        plt.annotate(str(y), # annotation text
                                    (x,y), # these are the coordinates to position the label
                                    textcoords="offset points", # how to position the text
                                    color=colorcode,
                                    xytext=(0,10), # distance from text to points (x,y)
                                    ha='center') # horizontal alignment can be left, right or center
                        prev = (x,y)
                    else:
                        plt.annotate(str(y), # annotation text
                                    (x,y), # these are the coordinates to position the label
                                    textcoords="offset points", # how to position the text
                                    xytext=(5,0), # distance from text to points (x,y)
                                    ha='left', # horizontal alignment can be left, right or center
                                    va='center',
                                    color=colorcode,
                                    bbox=dict(boxstyle="square,pad=0.3",fc="black" if brightness > br_threshold else "white", ec=colorcode, lw=1)) 
            plt.savefig(f"graphs/{i}_{timespan}_{dataset}.png", bbox_inches="tight")
            plt.close()
        else:
            await ctx.send(f"{emojidict['Warning']} No data available yet.\n-# Use the bot more!",ephemeral=True)
            return
        file = interactions.File(f"graphs/{i}_{timespan}_{dataset}.png")
        await ctx.send(f"-# Activate AutoSync via `/autosync` to get more data automatically.",file=file)
    except Exception as e:
        await ctx.send(f"{emojidict['Warning']} An error occured.\n```{e}\n{str(e)}```",ephemeral=True)

@interactions.slash_command(name="status", description="Check if the bot (and it's services) are functional.")
async def status(ctx: interactions.SlashContext):
    await ctx.defer()
    tag = urllib.parse.quote("#8VGY00G9")
    url_d = f"https://api.hpdevfox.ru/profile/8VGY00G9"
    url_c = "https://api.brawlstars.com/v1/brawlers"
    url_b = f"https://api.brawlstars.com/v1/players/{tag}/battlelog"
    url = f"https://api.brawlstars.com/v1/players/{tag}/"
    headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {bs_api_token}"
            }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                response_d = response.status
        except:
            response_d = "Not reachable"
        try:
            async with session.get(url_b, headers=headers) as response:
                response_b = response.status
        except:
            response_b = "Not reachable"
        try:
            async with session.get(url_c, headers=headers) as response:
                response_c = response.status
        except:
            response_c = "Not reachable"
        try:
            async with session.get(url_d, headers=headers, timeout=5) as response:
                response_e = await response.json()
                response_e = response_e["state"]
        except:
            response_e = "Not reachable"
        data_ok = maxHypercharges != 0 and (not bs_leaderboard_data is None)
    embed = interactions.Embed(title="STATUS + DIAGNOSTICS",
                        color=0x6f07b4,
                        timestamp=datetime.datetime.now())
    embed.add_field(name="Uptime",value=f"Started <t:{startuptime}:R>",inline=True)
    embed.add_field(name="Internal Data Integrity",value=f"{emojidict['Error']} [{response_d}]" if data_ok != True else f"{emojidict['Connected']} [OK]",inline=True)
    embed.add_field(name="-----",value=" ",inline=False)
    embed.add_field(name="API-Node [Profile]",value=f"{emojidict['Error']} [{response_d}]" if response_d != 200 else f"{emojidict['Connected']} [{response_d}]",inline=True)
    embed.add_field(name="API-Node [Battle-History]",value=f"{emojidict['Error']} [{response_b}]" if response_b != 200 else f"{emojidict['Connected']} [{response_b}]",inline=True)
    embed.add_field(name="API-Node [Brawlers]",value=f"{emojidict['Error']} [{response_c}]" if response_c != 200 else f"{emojidict['Connected']} [{response_c}]",inline=True)
    embed.add_field(name="-----",value=" ",inline=False)
    embed.add_field(name="Extension API",value=f"{emojidict['Error']} [{response_e}]" if response_e != 0 else f"{emojidict['Connected']} [{response_e}]",inline=True)
    embed.add_field(name="-----",value=" ",inline=False)
    embed.add_field(name="Status Code Glossary",value=f"200: OK\n400: Incorrect request template\n403: API Key expired/wrong\n429: Client overloaded\n500: Unknown API-Server issue\n503: Maintenance",inline=True)
    embed.set_footer(text="Shenzhia",
                        icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/044c7ebfc9aca45e4a3224e756a670dd.webp?size=160")
    await ctx.send(embed=embed)

@interactions.slash_command(name="randomimg", description="Get a randomly chosen image from imgur.")
@interactions.slash_option(name="hidden", description="Hide the response from everyone but you.", required=False, opt_type=interactions.OptionType.BOOLEAN)
async def randomimg(ctx: interactions.SlashContext, hidden: bool = False):
    client_id = "8b47ca7b21ed9f1"
    url = "https://api.imgur.com/3/gallery/random/random/"
    headers = {"Authorization": f"Client-ID {client_id}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
    if "data" in data:
        output = data["data"][random.randint(0,59)]["link"]
    else:
        output = f"{emojidict['Error']} Access to imgur-API was denied."
    await ctx.send(output,ephemeral=hidden)

@interactions.slash_command(name="gallery", description="View art of Shenzhia.")
async def gallery(ctx: interactions.SlashContext):
    await ctx.defer(ephemeral=True)
    embeds = []
    for i in range(6,-1,-1):
        embed = interactions.Embed(title=["Artsgui: '0x00000'","Sebixo: 'Dual Boot'","Sebixo: 'Unexpected Exception'","VIPKiddo: 'http://'","Inji: 'Trirumvirate'","Inji: 'FTP-Share'","Inji: 'Websocket-Hardreset :: 500'"][i],
                      url=["https://x.com/GuilhermeArtz","https://x.com/Sebixo3priv","https://x.com/Sebixo3priv","https://x.com/VIPKiddo29","https://x.com/Inji_arts","https://x.com/Inji_arts","https://x.com/Inji_arts"][i],
                      color=0x6f07b4,
                      timestamp=datetime.datetime.now())
        if i not in [0,1,4,6]:
            embed.set_author(name="VIEW POST",url=["","","https://x.com/Sebixo3priv/status/1800572051377541314","https://x.com/VIPKiddo29/status/1806194763181232262","","https://x.com/Inji_arts/status/1821997546018857384",""][i])
        embed.set_image(url=["https://i.imgur.com/WNS8kvk.png","https://i.imgur.com/CYoynim.png","https://pbs.twimg.com/media/GPzqvHlWkAAkMil?format=jpg&name=medium","https://pbs.twimg.com/media/GRDkj6JXIAAYg9M?format=jpg&name=900x900","https://i.imgur.com/yxQw2Is.png","https://pbs.twimg.com/media/GUkJHJtXwAA3-gF?format=jpg&name=large","https://i.imgur.com/Kig9Ewj.png"][i])
        embeds.append(embed)
    pg = Paginator.create_from_embeds(bot, *embeds)
    await pg.send(ctx)
    
@interactions.slash_command(name="help", description="View the documentation.")
async def help(ctx: interactions.SlashContext):
    embed = interactions.Embed(title="Get started (beta)",
                      color=0x6f07b4,
                      timestamp=datetime.datetime.now())
    embed.add_field(name="View repository",value="- [Main page](<https://github.com/SweetPinkMilkTea/shenzhia>)", inline=True)
    embed.add_field(name="View wiki",value="- [Commands](<https://github.com/SweetPinkMilkTea/shenzhia/wiki/Commands-and-Usage>)\n- [Terms](<https://github.com/SweetPinkMilkTea/shenzhia/wiki/Terms>)", inline=True)
    embed.add_field(name="Report problems or suggest additions",value="- [Issue Page](<https://github.com/SweetPinkMilkTea/shenzhia/issues>)", inline=True)
    await ctx.send(embed=embed)

# -------------------
# CALLBACKS
# -------------------

@interactions.modal_callback("shuffle")
async def modal_shuffle(ctx: interactions.ModalContext, userinput: str):
    await ctx.defer()
    try:
        await ctx.send(f"Rolled: {random.choice(userinput.split(sep=','))}")
    except:
        await ctx.send(f"{emojidict['Error']}: Something went wrong.")

bot.start(discord_bot_token[login])