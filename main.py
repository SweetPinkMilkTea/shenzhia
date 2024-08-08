import os, sys
import random
import asyncio

# THIS DISABLES ALL PRINTING - DISABLE IN DEBUGGING
# sys.stdout = open(os.devnull, 'w')

#print(os.getcwd())
if os.getcwd()[0] == "/":
    instance = "rasp"
    os.chdir("/mnt/NikitaSyn/shenzhia")
    sys.path.append('/home/admin/.local/lib/python3.10/site-packages')
else:
    if "shenzhitek" in os.getcwd():
        instance = "pt-tek"
    else:
        instance = "desk"

class ManualRaisedException(Exception):
    pass
class APIConnectionException(Exception):
    pass

import sys
import interactions
from interactions.ext.paginators import Paginator
import json
import time, datetime
import aiohttp
import sentry_sdk
import traceback
from interactions.api.events import CommandError

with open("bs_api_token.json") as f:
    bs_api_token = json.load(f)["main" if instance != "pt-tek" else "alt"]
with open("dc_bot_tokens.json") as f:
    discord_bot_token = json.load(f)["main" if instance != "pt-tek" else "alt"]
with open("sentry_dsn.json") as f:
    dsn = json.load(f)["main" if instance != "pt-tek" else "alt"]
with open("verbose_silence.json") as f:
    silence = json.load(f)["dur"]
with open("polling.json") as f:
    polling = json.load(f)
ranklist = [1,17778,36111,54444,73333,92222,111111,127407,143703,160000,201481,242962,284444,364444,444444,751111,1000000,999999999]

while True:
    url = f"https://api.brawlstars.com/v1/brawlers/"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bs_api_token}"
    }       
    response = requests.get(url, headers=headers)
    data = response.json()
    outdatedIP = False
    try:
        backup = False
        try:
            if data["message"] == "API at maximum capacity, request throttled.":
                raise APIConnectionException("Overload!")
        except:
            pass
        try:
            if data["reason"] == "unknownException":
                print("API ERROR")
                backup = True
        except:
            pass

    except APIConnectionException:
        raise Exception()
    try:
        if backup:
            raise Exception()
        print(data["reason"])
        print(urllib.request.urlopen('https://api4.ipify.org').read().decode('utf8'))
        bs_api_token = input("REPLACE TOKEN > ")
        with open("bs_api_token.json", "r") as f:
            bs_api_dict = json.load(f)
        bs_api_dict["main" if instance != "pt-tek" else "alt"] = bs_api_token
        with open("bs_api_token.json", "w") as f:
            json.dump(bs_api_dict,f)
    except:
        maxGadgets = maxStarpower = maxGear = maxCurrency = maxCurrencyAdv = 0
        if not backup:
            maxBrawlers = len(data["items"])
            for i in data["items"]:
                maxGadgets += len(i["gadgets"])
                maxStarpower += len(i["starPowers"])
                maxCurrency += 20245
                maxCurrencyAdv += 20245 + 6000
        else:
            maxBrawlers = 80
            for i in range(maxBrawlers):
                maxGadgets += 2
                maxStarpower += 2
                maxCurrency += 20245
                maxCurrencyAdv += 20245 + 6000
        break
maxHypercharges = 37
maxCurrency += maxHypercharges * 5000
maxCurrencyAdv += maxHypercharges * 5000
powericonlist = ["<:1:1228965645262258207>","<:2:1228965679122743379>","<:3:1228965688677236737>","<:4:1228965697045135442>","<:5:1228965704988889149>","<:6:1228965713058730125>","<:7:1228965722068226098>","<:8:1228965730750435368>","<:9_:1228965740116180992>","<:10:1228965748064387182>","<:11:1228965756092285011>"]

def send_api_error(reason):
    if "accessDenied" in reason:
        return f"<:qito_error:1137124869713166416> The current API tag for the BS-API is outdated. This will likely be fixed in up to a few hours."
    elif reason == "inMaintenance":
        return"<:qito_error:1137124869713166416> BS API under Maintenance. Please wait until it's over, this often only takes a few minutes."
    elif reason == "notFound":
        return "<:warning:1229332347086704661> This profile doesn't exist."
    else:
        return f"<:qito_error:1137124869713166416> BS API couldn't respond. Check '/status'?"


startuptime = int(time.time())
bot = interactions.Client(intents=interactions.Intents.DEFAULT, delete_unused_application_cmds=True, send_command_tracebacks=False if not instance == "pt-tek" else True)
if instance != "pt-tek":
    bot.load_extension('interactions.ext.sentry', token=dsn)

@interactions.listen(CommandError, disable_default_listeners=False)
async def on_command_error(event: CommandError):
    traceback.print_exception(event.error)
    embed = interactions.Embed(title=random.choice(["Yikes!","Ouch...","Aw...","Oops."]),
                        color=0xff0000,
                        timestamp=datetime.datetime.now(),
                        description=f"An unexpected error occured.\nAn error log was generated and sent to Qi.")
    if not event.ctx.responded:
        await event.ctx.send(embed=embed)

@interactions.listen()
async def on_startup():
    global exitcode, activity
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
        check_trophies.start()
        check_club.start()
        bs_player_leaderboard.start()
        ar_refresh.start()
        await check_club()
        await bs_player_leaderboard()
        if exitcode == 0:
            await check_trophies()
            await ar_refresh()
    except:
        print("Task error!")
    channel = bot.get_channel(1028719425035178016)
    if silence <= time.time():
        await channel.send(f"<:qito_connected:1140550294313373766> Bot has started/resumed.")
    exitcode = 0
    with open("quick_restart.txt","w") as f:
        f.write(str(exitcode))
    with open("datadump.txt","w") as f:
        f.write(str([v for v in dir() if not v.startswith('_')]))
    return

@interactions.Task.create(interactions.IntervalTrigger(hours=12))
async def check_trophies():
    global bsdict
    with open("bs_data.json") as f:
        bsdict = json.load(f)
    channel = bot.get_channel(1028719425035178016)
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
                                channel = bot.get_channel(1028719425035178016)
                                await channel.send(f"<:qito_error:1137124869713166416> Auto-Request failed! Task was abandoned.\n\nReason: {data['reason']}")
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
    channel = bot.get_channel(1028719425035178016)
    if silence <= time.time():
        await channel.send(f"Auto-Request completed. {'' if not errors else str(errors)+' errors encountered.'}", silent=True)

@interactions.Task.create(interactions.IntervalTrigger(hours=1))
async def check_club():
    global clubmembercount
    if instance != "pt-tek":
        with open("bs_club_member_cache.json","r") as f:
            clubmembercount = json.load(f)
        tag = "#2JVV90YQ0"
        tag = urllib.parse.quote(tag)
        url = f"https://api.brawlstars.com/v1/clubs/{tag}/members"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                channel = await bot.fetch_channel(1059810979204051005)
                if response.status != 200:
                    print(f"Error with Club-Scan: err {response.status}")
                    return
                data = await response.json()
                if len(data['items']) < 30 and len(data['items']) != clubmembercount["amount"]:
                    await channel.send(f"<:warning:1229332347086704661> <@411823919436136458> Club not full: {len(data['items'])} members")
                    print(f"Club-scan done with result [{True} - {len(data['items'])}].")
                    clubmembercount = {"amount":len(data['items'])}
                    with open("bs_club_member_cache.json","w") as f:
                        json.dump(clubmembercount,f)
                else:
                    print(f"Club-scan done with result [{False} - {len(data['items'])}].")
    else:
        print("Development Instance - Club check skipped")

@interactions.Task.create(interactions.IntervalTrigger(hours=3))
async def bs_player_leaderboard():
    global bs_leaderboard_data, bs_guild_leaderboard_data, bsdict
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
        #Send error to dev channel and stop task
        channel = bot.get_channel(1028719425035178016)
        await channel.send(f"<:qito_error:1137124869713166416> Leaderboard data request failed! Task was abandoned.\n\nReason: {data['message']}")
        return
    except:
        pass
    bs_leaderboard_data = []
    for i in data["items"]:
        bs_leaderboard_data.append(i["tag"])
    channel = bot.get_channel(1028719425035178016)
    # guild
    bs_guild_leaderboard_data_temp = []
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("tsr_best.json") as f:
        tsrbest = json.load(f)
    for i in tags.values():
        try:
            bs_guild_leaderboard_data_temp.append([tsrbest[i[0]],i[0]])
        except:
            pass
    bs_guild_leaderboard_data_temp.sort(reverse=True)
    bs_guild_leaderboard_data = []
    for i in bs_guild_leaderboard_data_temp:
        try:
            if len(bsdict[i[1]]['history']) != 0:
                bs_guild_leaderboard_data.append(i[1])
        except:
            pass
    # finish
    with open("bs_guild_leaderboard_data.json","w") as f:
        json.dump(bs_guild_leaderboard_data,f)
    if silence <= time.time():
        await channel.send(f"Global Leaderboard data updated.", silent=True)
    print("Global Leaderboard data updated.")

@interactions.Task.create(interactions.IntervalTrigger(hours=3))
async def ar_refresh():
    # >>> About AR
    # TSR    : Every Rank Div - +1 AR
    # Ranked : Every Rank Div - +1 AR
    # SDR    : int(abs(SDR-100)/10) AR
    # ABT    : -> TSR / 2

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
            for i in ranklist:
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
                for i in ranklist:
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
    channel = bot.get_channel(1028719425035178016)
    await channel.send(f"AR compiled.")
    print("AR updated.")

# ------------------------
# COMMANDS BELOW THIS LINE
# LOCAL SCOPE ONLY 
# ------------------------

@interactions.slash_command(name="say", description="Send a message somewhere as Shen", scopes=[647539435117740043])
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

@interactions.slash_command(name="close", description="Quit the current session.", scopes=[647539435117740043])
@interactions.slash_option(name="quick_restart", description="Whether to skip autosync - Only use this when debugging.", required=False, opt_type=interactions.OptionType.BOOLEAN)
async def close(ctx: interactions.SlashContext, quick_restart: bool = False):
    exitcode = 0 if not quick_restart else 1
    with open("quick_restart.txt","w") as f:
        f.write(str(exitcode))
    await ctx.defer()
    await ctx.send("Session closing.")
    await bot.stop()

@interactions.slash_command(name="tokenswitch", description="Overwrite the API-Key used to communicate with the Supercell API.", scopes=[647539435117740043])
@interactions.slash_option(name="new_key", description="The new API key received by the developer portal", required=True, opt_type=interactions.OptionType.STRING)
async def tokenswitch(ctx: interactions.SlashContext, new_key: str):
    await ctx.defer()
    global bs_api_token
    bs_api_token = new_key
    with open("bs_api_token.json","r") as f:
        tokendict = json.load(f)
        tokendict["alt" if instance == "pt-tek" else "main"] = bs_api_token
    with open("bs_api_token.json","w") as f:
        json.dump(tokendict,f) 
    await ctx.send("API Token overwritten.")

@interactions.slash_command(name="ip", description="Get the current IPv4-Address used by the current instance host device.", scopes=[647539435117740043])
async def ip(ctx: interactions.SlashContext):
    await ctx.send(urllib.request.urlopen('https://api4.ipify.org').read().decode('utf8'))

@interactions.slash_command(name="clubcount", description="Show vacant slots of the club.", scopes=[647539435117740043,1059810441074856048])
async def clubcount(ctx: interactions.SlashContext):
    await ctx.defer()
    tag = "#2JVV90YQ0"
    tag = urllib.parse.quote(tag)
    url = f"https://api.brawlstars.com/v1/clubs/{tag}/members"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bs_api_token}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
    await ctx.send(f"{-1*(len(data['items'])-30)} open spot(s)",ephemeral=True)

@interactions.slash_command(name="linknames", description="Save username-id relations to archive", scopes=[647539435117740043])
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

@interactions.slash_command(name="reset_ranked_elo", description="Set EVERYONE'S saved elo under 'current' to 0. Only use on season switch.", scopes=[647539435117740043])
async def reset_ranked_elo(ctx: interactions.SlashContext):
    await ctx.defer()
    with open("bs_powerleague.json") as f:
        pl_saves = json.load(f)
    for i in pl_saves:
        pl_saves[i]["current"] = 0
    with open("bs_powerleague.json","w") as f:
        json.dump(pl_saves,f)
    ctx.send("Completed.")

@interactions.slash_command(name="export", description="Search for a resource in the bot directory and send it", scopes=[647539435117740043])
@interactions.slash_option(name="query", description="(!listdir) : Query of file | (listdir) : subdirectory", required=False, opt_type=interactions.OptionType.STRING)
@interactions.slash_option(name="listdir", description="Instead of sending a resource, list items in subdirectory", required=False, opt_type=interactions.OptionType.BOOLEAN)
async def export(ctx: interactions.SlashContext, listdir: bool = False, query: str = ""):
    if listdir:
        try:
            await ctx.send(f"```\n{os.listdir((query) if query != '' else None)}\n```")
            return
        except:
            await ctx.defer(ephemeral=True)
            await ctx.send("<:warning:1229332347086704661> Subdirectory does not exist. Typo?")
            return
    else:
        try:
            file = interactions.File(query)
            await ctx.send(file=file)
            return
        except:
            await ctx.defer(ephemeral=True)
            await ctx.send("<:warning:1229332347086704661> Resource does not exist. Typo?")
            return

@interactions.slash_command(name="raiseerror", description="Force an error for tracking purposes", scopes=[647539435117740043])
async def raiseerror(ctx: interactions.SlashContext):
    raise ManualRaisedException("This Exception was forced manually.")

@interactions.slash_command(name="silenceverbose", description="Mute the periodic task output for a set amount to time", scopes=[647539435117740043])
@interactions.slash_option(name="duration", description="Amount of minutes to mute for. Set to 0 to remove any currently active silence.", required=True, opt_type=interactions.OptionType.INTEGER, min_value=0)
async def silenceverbose(ctx: interactions.SlashContext, duration: int):
    global silence
    await ctx.defer()
    with open("verbose_silence.json") as f:
        silence = json.load(f)
    if duration == 0:
        silence["dur"] = 0
        await ctx.send(f"<:info:1229350084299194388> Logging silence at 0")
    else:
        silence["dur"] = int(time.time()) + duration*60
        await ctx.send(f"<:info:1229350084299194388> Logging disabled until <t:{silence['dur']}:f> | <t:{silence['dur']}:R>")
    with open("verbose_silence.json","w") as f:
        json.dump(silence,f)
    silence = silence["dur"]
    
@interactions.slash_command(name="forcerefresh", description="Instantly rerun a task.", scopes=[647539435117740043])
@interactions.slash_option(name="subject", description="Task to push", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="AutoSync",value="AS"),interactions.SlashCommandChoice(name="Leaderboard (Player)",value="LBp"),interactions.SlashCommandChoice(name="AR Compilation",value="AR")])
async def forcerefresh(ctx: interactions.SlashContext, subject: str):
    await ctx.defer()
    await ctx.send(f"<{subject}> initiated.")
    if subject == "AS":
        await check_trophies()
    elif subject == "LBp":
        await bs_player_leaderboard()
    elif subject == "AR":
        await ar_refresh()

@interactions.slash_command(name="reloadjson", description="Reload all .json files loaded on startup", scopes=[647539435117740043])
async def reloadjson(ctx: interactions.SlashContext):
    await ctx.defer()
    with open("bs_api_token.json") as f:
        bs_api_token = json.load(f)["main" if instance != "pt-tek" else "alt"]
    with open("dc_bot_tokens.json") as f:
        discord_bot_token = json.load(f)["main" if instance != "pt-tek" else "alt"]
    with open("sentry_dsn.json") as f:
        dsn = json.load(f)["main" if instance != "pt-tek" else "alt"]
    with open("verbose_silence.json") as f:
        silence = json.load(f)["dur"]
    with open("polling.json") as f:
        polling = json.load(f)
    await ctx.send("Done.")

@interactions.slash_command(name="paginator_test", description="Testing callbacks over pages", scopes=[647539435117740043])
async def paginatortest(ctx: interactions.SlashContext):
    embeds = []
    for i in range(5):
        embeds.append(interactions.Embed(title=f"EMBED {i}",
            color=0x6f07b4))
    paginator = Paginator.create_from_embeds(bot, *embeds,)
    paginator.callback = test()
    await paginator.send(ctx)

@interactions.slash_command(name="asyncdelay", description="Testing async", scopes=[647539435117740043])
async def asyncdelay(ctx: interactions.SlashContext):
    await ctx.send("Delaying...")
    await asyncio.sleep(10)
    await ctx.send("Released delay.")

def test():
    print("!!!")

#---------------------------
# GLOBAL COMMANDS BELOW
#---------------------------

@interactions.slash_command(name="leaderboard", description="Find the best Shenzhia users for brawlers or overall!")
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
    for i in bs_guild_leaderboard_data[:9]:
        userelement = await bot.fetch_user(tag_dict[i])
        rank = "<:tranknone:1134890614635372675>"
        rlist = list({"E":"<:rank_e:1262541950561812601>","D":"<:rank_d:1262542011576356915>","D+":"<:rank_d_plus:1262542055326879858>","C-":"<:rank_c_minus:1262542122469294121>","C":"<:rank_c:1262542167440756847>","C+":"<:rank_c_plus:1262542219714494484>","B-":"<:rank_b_minus:1262542285644501095>","B":"<:rank_b:1262543019417014333>","B+":"<:rank_b_plus:1262543136291426394>","A-":"<:rank_a_minus:1262543188908839022>","A":"<:rank_a:1262543236518383616>","A+":"<:rank_a_plus:1262543274506457089>","S-":"<:rank_s_minus:1263948719577894922> ","S":"<:rank_s:1263948731167015013>","S+":"<:rank_s_plus:1263948744286802021>","SS":"<:rank_ss:1263953646245384274>","X":"<:trankx:1133686283093426256>"}.values())
        index2 = 0
        #         E   D     D+    C-    C     C+    B-     B      B+     A-     A      A+     S-      S     S+    S++      X         max
        #         -  600         675                750                 800                  900           1000   1150    1250
        for j in ranklist:
            if tsrbest[i] < j:
                break
            else:
                rank = rlist[index2]
                index2 += 1
        l_value = bsdict[i]['history'][-1]['value']
        l_indicator = ['<:goldstar:1153418516205162577> ','<:silverstar:1153418444486758513> ','<:bronzestar:1153418350970536007> ',''][index]
        embed.add_field(name=f"{l_indicator}#{placement} {userelement.username}",value=f"{rank} | {tsrbest[i]:,} tsr\n<:qito_trophy:1137140150065954816> {l_value}",inline=True)
        if index != 3:
            index += 1
        placement += 1
    embed.set_footer(text="Shenzhia",
                icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/74d23eaed7713a6d474dfbbf225bd40c?size=256")
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
@interactions.slash_option(name="id", description="Identifier of a list. Keep empty to make your own.", required=False, opt_type=interactions.OptionType.STRING)
async def shuffle(ctx: interactions.SlashContext, id: str = ""):
    list_modal = interactions.Modal(interactions.ShortText(label="List to shuffle", placeholder="Seperate items with ','!", custom_id="userinput"), title="List-Shuffle", custom_id="shuffle")
    await ctx.send_modal(modal=list_modal)

@interactions.slash_command(name="autosync", description="Enable automatic trophy saving for your primary linked tag. (Requires linked profile)")
async def autosync(ctx: interactions.SlashContext):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_data.json","r") as f:
        bsdict = json.load(f)
    if not str(ctx.author.id) in tags.keys():
        await ctx.send(f"<:warning:1229332347086704661> You are not linked to a BS-Account to sync.")
        return
    for i in tags[str(ctx.author.id)]:
        if not i in bsdict.keys():
            await ctx.send(f"<:warning:1229332347086704661> You have yet to use '/performance' {'at at least one of your linked accounts ' if len(tags[str(ctx.author.id)]) > 1 else ''}to initiate a save.")
            return
    for i in tags[str(ctx.author.id)]:
        bsdict[i]["updates"] = True
    await ctx.send(f"<:info:1229350084299194388> AutoSync is turned on.")
    with open("bs_data.json","w") as f:
        json.dump(bsdict,f)

@interactions.slash_command(name="profilelink", description="Set your own tag, so you can quickly use commands and access other special utility.")
@interactions.slash_option(name="method", description="Add/Remove a tag or view currently linked ones", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Add",value="1"),interactions.SlashCommandChoice(name="Remove",value=""),interactions.SlashCommandChoice(name="View",value="A")])
@interactions.slash_option(name="tag", description="Your tag, with '#' in front. (Reqired on add/remove)", required=False, opt_type=interactions.OptionType.STRING)
async def profilelink(ctx: interactions.SlashContext,method: str ,tag: str = ""):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_data.json","r") as f:
        bsdict = json.load(f)
    with open("tsr_best.json","r") as f:
        tsrbest = json.load(f)
    if method == "A":
        if str(ctx.author.id) not in tags:
            await ctx.send(f"<:warning:1229332347086704661> No profiles linked yet.",ephemeral=True)
            return
        embed = interactions.Embed(title=f"LINKED PROFILES",
                        color=0x6f07b4,
                        timestamp=datetime.datetime.now())
        for i in range(5):
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
                        icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/74d23eaed7713a6d474dfbbf225bd40c?size=256")
        await ctx.send(embed=embed)
        return
    if tag == "":
        await ctx.send(f"<:warning:1229332347086704661> 'tag' is required.",ephemeral=True)
        return
    if method:
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
            if len(tags[str(ctx.author.id)]) >= 5:
                await ctx.send(f"<:warning:1229332347086704661> Max # of links created.",ephemeral=True)
                return
            if tag.upper() in tags[str(ctx.author.id)]:
                await ctx.send(f"<:warning:1229332347086704661> You already linked this tag to yourself.",ephemeral=True)
                return
            saved_tags = []
            for i in tags:
                saved_tags += tags[i] if i != str(ctx.author.id) else []
            if tag.upper() in saved_tags:
                await ctx.send(f"<:warning:1229332347086704661> This tag has been blocked for linking as it has been linked to somebody else.",ephemeral=True)
                return
        url = f"https://api.brawlstars.com/v1/players/{urllib.parse.quote(tag)}/"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    await ctx.send(f"<:warning:1229332347086704661> '#' missing, Tag incorrect and/or API unavailable.\n-# Use '/status' to check for connectivity.")
                    return
        try:
            tags[str(ctx.author.id)].append(tag.upper())
        except:
            tags[str(ctx.author.id)] = [tag.upper()]
        await ctx.send("<:info:1229350084299194388> Your profile was linked.")
    else:
        if str(ctx.author.id) not in tags:
            await ctx.send(f"<:warning:1229332347086704661> No profiles linked yet.")
            return
        if tag.upper() not in tags[str(ctx.author.id)]:
            await ctx.send(f"<:warning:1229332347086704661> This tag is not linked to your account.")
            return
        tags[str(ctx.author.id)].remove(tag.upper())
        await ctx.send(f"<:info:1229350084299194388> Removed successfully.")
    with open("bs_tags.json","w") as f:
        json.dump(tags,f)

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
        await ctx.send("<:warning:1229332347086704661> No tag is saved to your account.\n-# Use '/bslink' to set one.")
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
                    await ctx.send("<:qito_error:1137124869713166416> API is overloaded.\n-# Try again later.")
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

        embed.add_field(name="<:qito_trophy:1137140150065954816>",value=f"{totaltrophies:,} \u27A1 {totaltrophies-deduction:,} (-{deduction})",inline=False)
        embed.add_field(name="<:qito_bling:1137121684449677322>",value="+"+str(bling),inline=False)
        embed.set_footer(text="Shenzhia",
                        icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/74d23eaed7713a6d474dfbbf225bd40c?size=256")
        embeds.append(embed)
    pg = Paginator.create_from_embeds(bot, *embeds)
    await pg.send(ctx)
    with open("bs_data.json","w") as f:
        json.dump(bsdict,f)

@interactions.slash_command(name="performance", description="Get a player's performance report, containing Trophy/Ranked info and TSR - a custom skill metric.")
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
            await ctx.send(f"<:warning:1229332347086704661> '#' missing from tag",ephemeral=True)
            return
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    try:
        if tag == "":
            tag = tags[str(ctx.author.id)]
        else:
            tag = [tag]
    except:
        await ctx.send("<:warning:1229332347086704661> No tag is saved to your account.\n-# Use '/bslink' to set it.",ephemeral=True)
        return
    embeds = []
    for tag_element in tag:
        try:
            x = bsdict[tag_element]
        except:
            bsdict[tag_element] = {"history":[],"updates":False}
        url = f"https://api.brawlstars.com/v1/players/{urllib.parse.quote(tag_element)}/"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {bs_api_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
        try:
            print(data["reason"])
            await ctx.send(send_api_error(data["reason"]),ephemeral=True)
            if bsdict[tag_element]["history"] == []:
                del bsdict[tag_element]
            return
        except:
            try:
                if data["message"] == "API at maximum capacity, request throttled.":
                    await ctx.send("<:qito_error:1137124869713166416> API is overloaded.\n-# Try again later.",ephemeral=True)
                if bsdict[tag_element]["history"] == []:
                    del bsdict[tag_element]            
                return
            except:
                pass
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
        for i in range(9):
            try:
                pplist.append(brawlerlist[i]["trophies"]-500 if brawlerlist[i]["trophies"]-500 > 0 else 0)
                spice += spdict[brawlerlist[i]["name"]] / [2,2,2,1,1,1,0.5,0.5,0.5][i]
            except:
                pass
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
        embed.add_field(name=f"<:qito_trophy:1137140150065954816> {data['trophies']:,}",value=f"Best: {data['highestTrophies']:,}",inline=True)
        if not showdownwarning:
            rank = "<:tranknone:1134890614635372675>"
            rlist = list({"E":"<:rank_e:1262541950561812601>","D":"<:rank_d:1262542011576356915>","D+":"<:rank_d_plus:1262542055326879858>","C-":"<:rank_c_minus:1262542122469294121>","C":"<:rank_c:1262542167440756847>","C+":"<:rank_c_plus:1262542219714494484>","B-":"<:rank_b_minus:1262542285644501095>","B":"<:rank_b:1262543019417014333>","B+":"<:rank_b_plus:1262543136291426394>","A-":"<:rank_a_minus:1262543188908839022>","A":"<:rank_a:1262543236518383616>","A+":"<:rank_a_plus:1262543274506457089>","S-":"<:rank_s_minus:1263948719577894922> ","S":"<:rank_s:1263948731167015013>","S+":"<:rank_s_plus:1263948744286802021>","SS":"<:rank_ss:1263953646245384274>","X":"<:trankx:1133686283093426256>"}.values())
            index2 = 0
            #         E   D     D+    C-    C     C+    B-     B      B+     A-     A      A+     S-      S     S+    S++      X         max
            #         -  600         675                750                 800                  900           1000   1150    1250
            for i in ranklist:
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
            with open("bs_ar.json") as f:
                try:
                    ar = json.load(f)[tag_element.upper()]
                except:
                    ar = "---"
            embed.add_field(name=f"{rank} | {ppscore:,} TSR (Best: {besttsr:,})",value=f"AR: {ar}",inline=True)
        if showdownwarning:
            embed.add_field(name=f"<:warning:1229332347086704661> High SD/3v3 Win-Ratio",value=f"No Advanced Stats calculated.",inline=True)
        if tag[0] in ["#8VGY00G9"]:
            if tag[0] == "#8VGY00G9":
                embed.add_field(name=f"<:goldstar:1153418516205162577> SHENZHIA DEVELOPER",value=f" ",inline=False)
        elif tag[0] in bs_leaderboard_data:
            if bs_leaderboard_data.index(tag[0])+1 < 11:
                icon = "<:goldstar:1153418516205162577> "
            elif bs_leaderboard_data.index(tag[0])+1 < 51:
                icon = "<:silverstar:1153418444486758513> "
            else:
                icon = "<:bronzestar:1153418350970536007> "
            embed.add_field(name=f"{icon}#{bs_leaderboard_data.index(tag[0])+1} GLOBAL PLAYER",value=f" ",inline=False)
        elif tag[0] in bs_guild_leaderboard_data[:9]:
            if bs_guild_leaderboard_data.index(tag[0])+1 == 1:
                icon = "<:goldstar:1153418516205162577> "
            elif bs_guild_leaderboard_data.index(tag[0])+1 == 2:
                icon = "<:silverstar:1153418444486758513> "
            elif bs_guild_leaderboard_data.index(tag[0])+1 == 3:
                icon = "<:bronzestar:1153418350970536007> "
            else:
                icon = ""
            embed.add_field(name=f"{icon}#{bs_guild_leaderboard_data.index(tag[0])+1} SHENZHIA USER",value=f" ",inline=False)
        else:
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
            debug_ext = ""
            lock_brawler_overview = False
            try:
                bname = brawlerlist[i]['name'].upper()
            except:
                bname = "Unknown"
                lock_brawler_overview = True
            if not lock_brawler_overview:
                try:
                    gadgetindicator = "<:gadget:1228965764631892069>" if len(brawlerlist[i]["gadgets"]) > 0 else "<:no_util:1228965782390702201>"
                    spindicator = "<:sp:1228965791639277659>" if len(brawlerlist[i]["starPowers"]) > 0 else "<:no_util:1228965782390702201>"
                    gearindicator1 = "<:gear:1228965774199230474>" if len(brawlerlist[i]["gears"]) > 0 else "<:no_util:1228965782390702201>"
                    gearindicator2 = "<:gear:1228965774199230474>" if len(brawlerlist[i]["gears"]) > 1 else "<:no_util:1228965782390702201>"
                    embed.add_field(name=f"[#{i+1}] {bname}\n{powericonlist[brawlerlist[i]['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}",value=f"<:qito_trophy:1137140150065954816> {brawlerlist[i]['trophies']} / {brawlerlist[i]['highestTrophies']} [T{brawlerlist[i]['rank']}]{nl}{tsr_display}{debug_ext}",inline=True)
                except Exception as e:
                    embed.add_field(name=f"[#-] ---",value=f"<:qito_trophy:1137140150065954816> {0} / {0}{nl}{tsr_display}",inline=True)
                    print(f"{e} : {str(e)}")
        if lock_brawler_overview:
            embed.add_field(name=f"API DEFUNCT",value=f"<:warning:1229332347086704661> Invalid data recieved. Can't display brawler data. ;-;",inline=False)
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
        fluc_list = []
        try:
            for i in bsdict[tag_element]["history"]:
                if i["relevancy"] == True:
                    fluc_list.append(i)
            rev_list = list(reversed(bsdict[tag_element]["history"]))
        except:
            pass
        if len(fluc_list) > 1:
            sessionstr = f"{fluc_list[-1]['value'] - fluc_list[-2]['value']:,} <:qito_trophy:1137140150065954816>"
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
        with open("bs_powerleague.json","r") as f:
            pl_saves = json.load(f)
        if tag_element in pl_saves.keys():
            pl_index_best = pl_saves[tag_element]["best"]
            pl_index_current = pl_saves[tag_element]["current"]
            rlist = ["<:tranknone:1134890614635372675>","<:rank_e:1262541950561812601>","<:rank_e:1262541950561812601>","<:rank_e:1262541950561812601>","<:rank_d:1262542011576356915>","<:rank_d_plus:1262542055326879858>","<:rank_c_minus:1262542122469294121>","<:rank_c:1262542167440756847>","<:rank_c_plus:1262542219714494484>","<:rank_b_minus:1262542285644501095>","<:rank_b:1262543019417014333>","<:rank_b_plus:1262543136291426394>","<:rank_a_minus:1262543188908839022>","<:rank_a:1262543236518383616>","<:rank_a_plus:1262543274506457089>","<:rank_s_minus:1263948719577894922> ","<:rank_s:1263948731167015013>","<:rank_s_plus:1263948744286802021>","<:rank_ss:1263953646245384274>","<:trankx:1133686283093426256>"]
            embed.add_field(name=f"RANKED DIVISION",value=f"Current: {rlist[pl_index_current]} | {['N/A','BRONZE 1','BRONZE 2','BRONZE 3','SILVER 1','SILVER 2','SILVER 3','GOLD 1','GOLD 2','GOLD 3','DIAMOND 1','DIAMOND 2','DIAMOND 3','MYTHIC 1','MYTHIC 2','MYTHIC 3','LEGENDARY 1','LEGENDARY 2','LEGENDARY 3','MASTER'][pl_index_current]}\nBest: {rlist[pl_index_best]} | {['N/A','BRONZE 1','BRONZE 2','BRONZE 3','SILVER 1','SILVER 2','SILVER 3','GOLD 1','GOLD 2','GOLD 3','DIAMOND 1','DIAMOND 2','DIAMOND 3','MYTHIC 1','MYTHIC 2','MYTHIC 3','LEGENDARY 1','LEGENDARY 2','LEGENDARY 3','MASTER'][pl_index_best]}",inline=True)
        else:
            embed.add_field(name=f"RANKED DIVISION",value=f"<:tranknone:1134890614635372675>\n*Unknown*",inline=True)
        #Win Rate
        if nolog:
            embed.add_field(name=f"RECENT WIN-RATE",value=f"<:warning:1229332347086704661> Unavailable...",inline=True)
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
        embed.add_field(name=f" ",value=f"ASYC: {asyc} / ABT: {int(round(averagetrophies,0)) if averagetrophies != 'N/A' else averagetrophies} / ABP: {round(averagepower,2) if averagepower != 'N/A' else averagepower} / SDR: {int((ssdv+dsdv)/(ssdv+dsdv+v3v)*100)} / WD: {wins:,}>{total:,}-{flukes:,} / SF: {round(spice,2)}%",inline=False)
        with open("bs_ar_supplementary.json","r") as f:
            ars = json.load(f)
            ars[tag_element] = {"sdr":int((ssdv+dsdv)/(ssdv+dsdv+v3v)*100),"abt":int(round(averagetrophies,0)) if averagetrophies != 'N/A' else -1}
        with open("bs_ar_supplementary.json","w") as f:
            json.dump(ars,f)
        if str(ctx.author_id) not in tags:
            embed.add_field(name="<:info:1229350084299194388>", value="Is this profile yours? Link it with /profilelink to get more utility!")
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
    #await ctx.send("<:warning:1229332347086704661> This function is unavailable due to a defunct in the Brawl Stars API.\n-# Maybe check back later. :(",ephemeral=True)
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
        await ctx.send("<:warning:1229332347086704661> No tag is saved to your account.\n-# Use '/profilelink' to set it.",ephemeral=True)
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
                    await ctx.send("<:qito_error:1137124869713166416> API is overloaded.\n-# Try again later.",ephemeral=True)
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
        for i in data["brawlers"]:
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
        embed.add_field(name=f"BRAWLER GEAR COMPLETION",value=f"<:qito_gadget:1147201313810157629> `{gadgetcount}/{maxGadgets}`\n<:qito_starpower:1147201382420590663> `{starpowercount}/{maxStarpower}`\n<:qito_gear:1147201448191459328> `{gearcount}`\n<:qito_hypercharge:1147552215435849832> `{hcinfo[tag_element]['value']}/{maxHypercharges}`{'' if not hcInfoWarning else newline+'<:warning:1229332347086704661> '+infotext}",inline=True)
        embed.add_field(name=f"BRAWLER POWER COMPLETION",value=f"`P11     : {powerlevellist.count(11)}`\n`P10     : {powerlevellist.count(10)}`\n`P 9     : {powerlevellist.count(9)}`\n`Below P9: {len(data['brawlers']) - (powerlevellist.count(11)+powerlevellist.count(10)+powerlevellist.count(9))}`",inline=True)
        embed.add_field(name=f"RESCOURCE DEFECIT",value=f"<:qito_pp:1147162040352374918> {neededPP:,}\n<:qito_coins:1147624181337432135> {neededCoins:,}\nIncludes P11, {2 if advanced else 1} SP, {2 if advanced else 1} Gadget and {6 if advanced else 2} Gears per brawler,\nas well as all available Hypercharges\n{'Does not include saved up rescources'}",inline=False)
        if not advanced:
            embed.add_field(name=f"TOTAL PROGRESSION",value=f"{maxed} / {len(data['brawlers'])} maxed brawlers\nCompletion% : {round(((maxCurrency-neededCurrency)/maxCurrency)*100,2)}%",inline=False)
        else:
            embed.add_field(name=f"TOTAL PROGRESSION",value=f"{maxed} / {len(data['brawlers'])} maxed brawlers\nCompletion% : {round(((maxCurrencyAdv-neededCurrency)/maxCurrencyAdv)*100,2)}%",inline=False)
        if str(ctx.author_id) not in tags:
            embed.add_field(name="<:info:1229350084299194388>", value="Is this profile yours? Link it with /profilelink to get more utility!")
        embed.set_footer(text="Shenzhia",
                        icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/74d23eaed7713a6d474dfbbf225bd40c?size=256")
        embeds.append(embed)
    pg = Paginator.create_from_embeds(bot, *embeds)
    await pg.send(ctx)

@interactions.slash_command(name="hyperchargecount", description="Set the amount of Hypercharges you own. (Requires profile-linking)")
@interactions.slash_option(name="mode", description="Whether to set an amount or increase an already existing one", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Set",value="set"),interactions.SlashCommandChoice(name="Increase",value="inc")])
@interactions.slash_option(name="amount", description="Either Amount of Hypercharges you own or amount of Hypercharges to add", required=True, opt_type=interactions.OptionType.INTEGER, min_value=0, max_value=maxHypercharges)
@interactions.slash_option(name="tagid", description="If multiple accounts are linked, index of target account. Defaults to first linked profile.", required=False, opt_type=interactions.OptionType.INTEGER, min_value=1, max_value=5)
async def hyperchargecount(ctx: interactions.SlashContext, mode: str, amount: int, tagid: int = 1):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    with open("bs_hc_info.json","r") as f:
        hcinfo = json.load(f)
    if str(ctx.author.id) not in tags.keys():
        await ctx.send(f"<:warning:1229332347086704661> Link your BS-Account with '/bslink' first.",ephemeral=True)
        return
    if tagid > len(tags[str(ctx.author.id)]):
        await ctx.send(f"<:warning:1229332347086704661> Provided Tag-ID is out of range.",ephemeral=True)
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
                await ctx.send(f"<:warning:1229332347086704661> No Hypercharge record.",ephemeral=True)
                return
            else:
                prevhc += amount
    except:
        await ctx.send(f"<:warning:1229332347086704661> This exceeds the maximum amount of Hypercharges obtainable.",ephemeral=True)
        return
    hcinfo[tags[str(ctx.author.id)][tagid]] = {"value":amount if mode == 'set' else prevhc,"time":time.time()}
    await ctx.send(f"Hypercharge count of [{tags[str(ctx.author.id)][tagid]}] updated to {hcinfo[tags[str(ctx.author.id)][tagid]]['value']}.")
    with open("bs_hc_info.json","w") as f:
        json.dump(hcinfo,f)

@interactions.slash_command(name="matchanalysis", description="Look for a player's recently player game and analyze all participants. 3v3 only.")
@interactions.slash_option(name="tag", description="Target Player (empty: self)", required=False, opt_type=interactions.OptionType.STRING)
@interactions.slash_option(name="offset", description="Search for a less recent game (range: 0 - 24)", required=False, opt_type=interactions.OptionType.INTEGER, max_value=24, min_value=0)
@interactions.slash_option(name="show_tags", description="Show scanned players tags along with thier name.", required=False, opt_type=interactions.OptionType.BOOLEAN)
@interactions.slash_option(name="tagid", description="[Only on self] If multiple accounts are linked, index of target account. Defaults to first profile.", required=False, opt_type=interactions.OptionType.INTEGER, min_value=1, max_value=5)
async def matchanalysis(ctx: interactions.SlashContext, tag: str = "", offset: int = 0, show_tags: bool = False, tagid: int = 1):
    await ctx.defer()
    with open("bs_tags.json","r") as f:
        tags = json.load(f)
    if str(ctx.author.id) not in tags:
        await ctx.send("<:warning:1229332347086704661> No tag is saved to your account.\n-# Use '/bslink' to set it.",ephemeral=True)
        return
    tag = tag.upper()
    if tag == "":
        tagid -= 1
        override = False
        try:
            tag = tags[str(ctx.author.id)][tagid]
        except:
            await ctx.send(f"<:warning:1229332347086704661> Tag under ID {tagid+1} is not set.",ephemeral=True)
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
            await ctx.send("<:qito_error:1137124869713166416> API is overloaded.\n-# Try again later.",ephemeral=True)
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
                await ctx.send("<:warning:1229332347086704661> Unsupported Mode")
                return
            if len(data["battle"]["teams"]) < 2:
                await ctx.send("<:warning:1229332347086704661> Unsupported Mode\n-# PvP only!")
                return
            if len(data["battle"]["teams"][0]) != len(data["battle"]["teams"][1]):
                await ctx.send("<:warning:1229332347086704661> Unsupported Mode\n-# Friendly batteles are excluded.")
                return
            if len(data["battle"]["teams"][0]) not in [3,5]:
                await ctx.send("<:warning:1229332347086704661> Unsupported Mode\n-# Friendly batteles are excluded.")
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
            rank = "<:tranknone:1134890614635372675>"
            rankiconlist = list({"E":"<:rank_e:1262541950561812601>","D":"<:rank_d:1262542011576356915>","D+":"<:rank_d_plus:1262542055326879858>","C-":"<:rank_c_minus:1262542122469294121>","C":"<:rank_c:1262542167440756847>","C+":"<:rank_c_plus:1262542219714494484>","B-":"<:rank_b_minus:1262542285644501095>","B":"<:rank_b:1262543019417014333>","B+":"<:rank_b_plus:1262543136291426394>","A-":"<:rank_a_minus:1262543188908839022>","A":"<:rank_a:1262543236518383616>","A+":"<:rank_a_plus:1262543274506457089>","S-":"<:rank_s_minus:1263948719577894922> ","S":"<:rank_s:1263948731167015013>","S+":"<:rank_s_plus:1263948744286802021>","SS":"<:rank_ss:1263953646245384274>","X":"<:trankx:1133686283093426256>"}.values())
            index2 = 0
            for k in ranklist:
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
                starhighlight = ['<:goldstar:1153418516205162577>','<:silverstar:1153418444486758513>','<:bronzestar:1153418350970536007>'][i]
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
            await ctx.send(f"<:warning:1229332347086704661> The scanned match is a bot-match and therefore can't get evaluated.")
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
        embed.set_footer(text="Shenzhia", icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/74d23eaed7713a6d474dfbbf225bd40c?size=256")
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
            if False:
                await ctx.send("<:warning:1229332347086704661> 5v5 `/matchanalysis` is in development.\n-# Please check back later")
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
                    rank = "<:tranknone:1134890614635372675>"
                    rankiconlist = list({"E":"<:rank_e:1262541950561812601>","D":"<:rank_d:1262542011576356915>","D+":"<:rank_d_plus:1262542055326879858>","C-":"<:rank_c_minus:1262542122469294121>","C":"<:rank_c:1262542167440756847>","C+":"<:rank_c_plus:1262542219714494484>","B-":"<:rank_b_minus:1262542285644501095>","B":"<:rank_b:1262543019417014333>","B+":"<:rank_b_plus:1262543136291426394>","A-":"<:rank_a_minus:1262543188908839022>","A":"<:rank_a:1262543236518383616>","A+":"<:rank_a_plus:1262543274506457089>","S-":"<:rank_s_minus:1263948719577894922> ","S":"<:rank_s:1263948731167015013>","S+":"<:rank_s_plus:1263948744286802021>","SS":"<:rank_ss:1263953646245384274>","X":"<:trankx:1133686283093426256>"}.values())
                    index2 = 0
                    for l in ranklist:
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
                embed.add_field(name=data['battle']['players'][0]['name']+tag_vis,
                                    value=f"{extensionlist[0]['trophies']:,} Trophies | {extensionlist[0]['tsr']:,} tsr {extensionlist[0]['rank']}{' / <:warning:1229332347086704661> SDR '+str(extensionlist[0]['sdr']) if extensionlist[0]['sdr'] > 40 else ''}",
                                    inline=False)
                for i in range(3):
                    gadgetindicator = "<:gadget:1228965764631892069>" if extensionlist[0]["gadgets"][data['battle']['players'][0]['brawlers'][i]['name']] > 0 else "<:no_util:1228965782390702201>"
                    spindicator = "<:sp:1228965791639277659>" if extensionlist[0]["sp"][data['battle']['players'][0]['brawlers'][i]['name']] > 0 else "<:no_util:1228965782390702201>"
                    gearindicator1 = "<:gear:1228965774199230474>" if extensionlist[0]["gears"][data['battle']['players'][0]['brawlers'][i]['name']] > 0 else "<:no_util:1228965782390702201>"
                    gearindicator2 = "<:gear:1228965774199230474>" if extensionlist[0]["gears"][data['battle']['players'][0]['brawlers'][i]['name']] > 1 else "<:no_util:1228965782390702201>"
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
                embed.add_field(name=data['battle']['players'][1]['name']+tag_vis,
                                    value=f"{extensionlist[1]['trophies']:,} Trophies | {extensionlist[1]['tsr']:,} tsr {extensionlist[1]['rank']}{' / <:warning:1229332347086704661> SDR '+str(extensionlist[1]['sdr']) if extensionlist[1]['sdr'] > 40 else ''}",
                                    inline=False)
                for i in range(3):
                    gadgetindicator = "<:gadget:1228965764631892069>" if extensionlist[1]["gadgets"][data['battle']['players'][1]['brawlers'][i]['name']] > 0 else "<:no_util:1228965782390702201>"
                    spindicator = "<:sp:1228965791639277659>" if extensionlist[1]["sp"][data['battle']['players'][1]['brawlers'][i]['name']] > 0 else "<:no_util:1228965782390702201>"
                    gearindicator1 = "<:gear:1228965774199230474>" if extensionlist[1]["gears"][data['battle']['players'][1]['brawlers'][i]['name']] > 0 else "<:no_util:1228965782390702201>"
                    gearindicator2 = "<:gear:1228965774199230474>" if extensionlist[1]["gears"][data['battle']['players'][1]['brawlers'][i]['name']] > 1 else "<:no_util:1228965782390702201>"
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
                embed.set_footer(text="Shenzhia", icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/74d23eaed7713a6d474dfbbf225bd40c?size=256")
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
                await ctx.send("<:warning:1229332347086704661> 5v5 `/matchanalysis` is in development.\n-# Please check back later")
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
                    rank = "<:tranknone:1134890614635372675>"
                    rankiconlist = list({"E":"<:rank_e:1262541950561812601>","D":"<:rank_d:1262542011576356915>","D+":"<:rank_d_plus:1262542055326879858>","C-":"<:rank_c_minus:1262542122469294121>","C":"<:rank_c:1262542167440756847>","C+":"<:rank_c_plus:1262542219714494484>","B-":"<:rank_b_minus:1262542285644501095>","B":"<:rank_b:1262543019417014333>","B+":"<:rank_b_plus:1262543136291426394>","A-":"<:rank_a_minus:1262543188908839022>","A":"<:rank_a:1262543236518383616>","A+":"<:rank_a_plus:1262543274506457089>","S-":"<:rank_s_minus:1263948719577894922> ","S":"<:rank_s:1263948731167015013>","S+":"<:rank_s_plus:1263948744286802021>","SS":"<:rank_ss:1263953646245384274>","X":"<:trankx:1133686283093426256>"}.values())
                    index2 = 0
                    for l in ranklist:
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
                    gadgetindicator = "<:gadget:1228965764631892069>" if extensionlist[i]["gadgets"] > 0 else "<:no_util:1228965782390702201>"
                    spindicator = "<:sp:1228965791639277659>" if extensionlist[i]["sp"] > 0 else "<:no_util:1228965782390702201>"
                    gearindicator1 = "<:gear:1228965774199230474>" if extensionlist[i]["gears"] > 0 else "<:no_util:1228965782390702201>"
                    gearindicator2 = "<:gear:1228965774199230474>" if extensionlist[i]["gears"] > 1 else "<:no_util:1228965782390702201>"
                    if not isRankedDiv:
                        embed.add_field(name=data['battle']['teams'][0][i]['name']+"<:goldstar:1153418516205162577>"+tag_vis if starplayertag == data['battle']['teams'][0][i]['tag'] else data['battle']['teams'][0][i]['name']+tag_vis,
                                        value=f"{data['battle']['teams'][0][i]['brawler']['name']}\n{powericonlist[data['battle']['teams'][0][i]['brawler']['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}\n[{data['battle']['teams'][0][i]['brawler']['trophies']:,}]\n\n{extensionlist[i]['trophies']:,} Trophies\n{extensionlist[i]['tsr']:,} tsr\n{extensionlist[i]['rank']}{' / <:warning:1229332347086704661> SDR '+str(extensionlist[i]['sdr']) if extensionlist[i]['sdr'] > 40 else ''}",
                                        inline=True)
                    else:
                        embed.add_field(name=data['battle']['teams'][0][i]['name']+"<:goldstar:1153418516205162577>"+tag_vis if starplayertag == data['battle']['teams'][0][i]['tag'] else data['battle']['teams'][0][i]['name']+tag_vis,
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
                    gadgetindicator = "<:gadget:1228965764631892069>" if extensionlist[3+i]["gadgets"] > 0 else "<:no_util:1228965782390702201>"
                    spindicator = "<:sp:1228965791639277659>" if extensionlist[3+i]["sp"] > 0 else "<:no_util:1228965782390702201>"
                    gearindicator1 = "<:gear:1228965774199230474>" if extensionlist[3+i]["gears"] > 0 else "<:no_util:1228965782390702201>"
                    gearindicator2 = "<:gear:1228965774199230474>" if extensionlist[3+i]["gears"] > 1 else "<:no_util:1228965782390702201>"
                    if not isRankedDiv:
                        embed.add_field(name=data['battle']['teams'][1][i]['name']+"<:goldstar:1153418516205162577>"+tag_vis if starplayertag == data['battle']['teams'][1][i]['tag'] else data['battle']['teams'][1][i]['name']+tag_vis,
                                value=f"{data['battle']['teams'][1][i]['brawler']['name']}\n{powericonlist[data['battle']['teams'][1][i]['brawler']['power']-1]} {gadgetindicator}{spindicator}{gearindicator1}{gearindicator2}\n[{data['battle']['teams'][1][i]['brawler']['trophies']:,}]\n\n{extensionlist[3+i]['trophies']:,} Trophies\n{extensionlist[3+i]['tsr']:,} tsr\n{extensionlist[3+i]['rank']}{' / <:warning:1229332347086704661> SDR '+str(extensionlist[3+i]['sdr']) if extensionlist[3+i]['sdr'] > 40 else ''}",
                                inline=True)
                    else:
                        embed.add_field(name=data['battle']['teams'][1][i]['name']+"<:goldstar:1153418516205162577>"+tag_vis if starplayertag == data['battle']['teams'][1][i]['tag'] else data['battle']['teams'][1][i]['name']+tag_vis,
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
                    await ctx.send(f"<:warning:1229332347086704661> The scanned match is a bot-match and thus can't get evaluated.")
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
                embed.set_footer(text="Shenzhia", icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/74d23eaed7713a6d474dfbbf225bd40c?size=256")
                if isRankedDiv:
                    with open("bs_powerleague.json", "w") as f:
                        json.dump(pl_saves,f)
    await ctx.send(embed=embed)

@interactions.slash_command(name="history", description="View a recorded graph of your stat development. (Requires linked profile, only primary profile)")
@interactions.slash_option(name="timespan", description="Whether to show the last 30 days or the complete graph if the full history is more than 30 days long", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Last 30 days",value=""),interactions.SlashCommandChoice(name="All Time",value="_full")])
@interactions.slash_option(name="dataset", description="What dataset to use.", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Trophies",value="t"),interactions.SlashCommandChoice(name="TSR",value="r")])
async def history(ctx: interactions.SlashContext, timespan: str, dataset: str):
    if dataset == "r":
        await ctx.send("<:warning:1229332347086704661> This feature is under development.")
        return
    try:
        print(os.getcwd())
        file = interactions.File(f"graphs/{str(ctx.author.id)}{timespan}_{dataset}.png")
        await ctx.send(f"Activate AutoSync via `/autosync` to get more data automatically.",file=file)
    except Exception as e:
        await ctx.defer(ephemeral=True)
        await ctx.send("<:warning:1229332347086704661> No graph available yet. Check back in a few days.\n*Hint: Turn on AutoSync to get your stats automatically saved!*")

@interactions.slash_command(name="status", description="Check if the bot (and it's services) are functional.")
async def status(ctx: interactions.SlashContext):
    await ctx.defer()
    tag = urllib.parse.quote("#8VGY00G9")
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
                response = response.status
        except:
            response = "Not reachable"
        try:
            async with session.get(url, headers=headers) as response:
                response_b = response.status
        except:
            response_b = "Not reachable"
        try:
            async with session.get(url, headers=headers) as response:
                response_c = response.status
        except:
            response_c = "Not reachable"

    embed = interactions.Embed(title="STATUS + DIAGNOSTICS",
                        color=0x6f07b4,
                        timestamp=datetime.datetime.now())
    embed.add_field(name="Instance",value=f"'{instance}'",inline=True)
    embed.add_field(name="Uptime",value=f"Started <t:{startuptime}:R>",inline=True)
    embed.add_field(name="-----",value=" ",inline=False)
    embed.add_field(name="API-Node [Profile]",value=f"<:qito_error:1137124869713166416> [{response}]" if response != 200 else f"<:qito_connected:1140550294313373766> [{response}]",inline=True)
    embed.add_field(name="API-Node [Battle-History]",value=f"<:qito_error:1137124869713166416> [{response_b}]" if response_b != 200 else f"<:qito_connected:1140550294313373766> [{response_b}]",inline=True)
    embed.add_field(name="API-Node [Brawlers]",value=f"<:qito_error:1137124869713166416> [{response_c}]" if response_c != 200 else f"<:qito_connected:1140550294313373766> [{response_c}]",inline=True)
    embed.add_field(name="-----",value=" ",inline=False)
    embed.add_field(name="Status Code Glossary",value=f"200: OK\n400: Incorrect request template\n403: API Key expired/wrong\n429: Client overloaded\n500: Unknown API-Server issue\n503: Maintenance",inline=True)
    embed.add_field(name="Note for Instances",value=f"Certain functions might only be available on 'desk'.",inline=True)
    embed.set_footer(text="Shenzhia",
                        icon_url="https://cdn.discordapp.com/avatars/1048344472171335680/74d23eaed7713a6d474dfbbf225bd40c?size=256")
    await ctx.send(embed=embed)

@interactions.slash_command(name="gpt", description="Make a prompt to a CHatGPT-Model. (Not always available)")
@interactions.slash_option(name="model", description="What model to use", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="GPT 3.5 Turbo",value="gpt-3.5-turbo"),interactions.SlashCommandChoice(name="GPT 4 Omni",value="gpt-4o")])
@interactions.slash_option(name="prompt", description="Your prompt. Be creative with it!", required=True, opt_type=interactions.OptionType.STRING)
@interactions.slash_option(name="temp", description="Temperature/Variance. High amounts (500+) might detoriate results.", required=False, opt_type=interactions.OptionType.INTEGER, min_value=0, max_value=2000)
@interactions.slash_option(name="export", description="Output the reponse in a .txt (Always when the response is too long.)", required=False, opt_type=interactions.OptionType.BOOLEAN)
async def gpt(ctx: interactions.SlashContext, prompt: str, model: str, export: bool = False, temp: int = 0):
    await ctx.send("<:warning:1229332347086704661> This feature is disabled. Sorry.",ephemeral=True)
    return
    await ctx.defer()
    if instance == "rasp":
        await ctx.send("<:warning:1229332347086704661> Unavailable for now. Try again later.",ephemeral=True)
        return
    with open("gpt_usage.json") as f:
        gptdata = json.load(f)
    try:
        tokenCurrency = gptdata[str(ctx.author.id)]
    except:
        gptdata[str(ctx.author.id)] = 500000
        tokenCurrency = gptdata[str(ctx.author.id)]
        with open("gpt_usage.json","w") as f:
            json.dump(gptdata,f)
    if tokenCurrency < 1:
        await ctx.send("<:warning:1229332347086704661> You reached your usage limit, wait until it's refreshed.",ephemeral=True)
        return
    #modal start
    try:
        with open("gpt_usage.json") as f:
            gptdata = json.load(f)
        try:
            tokenCurrency = gptdata[str(ctx.author.id)]
        except:
            tokenCurrency = 1000000
        if prompt == "info":
            if str(ctx.author) == "pink_milk_tea":
                await ctx.send(f"You have ∞ tokens left to use.")
            else:
                await ctx.send(f"You have {tokenCurrency} tokens left to use.\n(750 words are about 1k tokens)")
            return
        messages = [{"role": "user", "content": prompt}]
        try:
            response = client.chat.completions.create(model=model,messages=messages,temperature=temp,max_tokens=1024)
        except Exception as error:
            await ctx.send(f"<:qito_error:1137124869713166416> Request failed: {error}",ephemeral=True)
            return
        if export:
            output = f"*{prompt}*\n\n" + str(response.choices[0].message.content)
            if "@everyone" in output or "@here" in output or "<@" in output:
                export = True
            if str(ctx.author) != "pink_milk_tea":
                tokenCurrency -= int(response.usage.total_tokens)
            if tokenCurrency < 0:
                tokenCurrency = 0
            gptdata[str(ctx.author.id)] = tokenCurrency
            with open("gpt_usage.json","w") as f:
                json.dump(gptdata,f)
            appendstr = ""
            if tokenCurrency < 3000 and str(ctx.author) != "pink_milk_tea":
                appendstr = f"<:warning:1229332347086704661> **Approaching token limit.**"
            if tokenCurrency == 0:
                appendstr = f"<:warning:1229332347086704661> **Token limit reached!**"
            with open("gpt_result.txt", "w", encoding="utf-8") as f:
                f.write(output)
            with open("gpt_result.txt", "rb") as file:
                if appendstr == "":
                    await ctx.send(file=interactions.File(file, "gpt_result.txt"))
                else:
                    await ctx.send(f"{appendstr}",file=interactions.File(file, "gpt_result.txt"))
        else:
            output = str(response.choices[0].message.content)
            if "@everyone" in output or "@here" in output or "<@" in output:
                export = True
            if str(ctx.author) != "pink_milk_tea":
                tokenCurrency -= int(response.usage.total_tokens)
            if tokenCurrency < 0:
                tokenCurrency = 0
            gptdata[str(ctx.author.id)] = tokenCurrency
            with open("gpt_usage.json","w") as f:
                json.dump(gptdata,f)
            appendstr = ""
            if tokenCurrency < 3000 and str(ctx.author) != "pink_milk_tea":
                appendstr = f"<:warning:1229332347086704661> **Approaching token limit.**"
            if tokenCurrency == 0:
                appendstr = f"<:warning:1229332347086704661> **Token limit reached!**"
            try:
                if appendstr == "":
                    await ctx.send(output)
                else:
                    await ctx.send(appendstr+"\n\n"+output)
            except:
                with open("gpt_result.txt", "w", encoding="utf-8") as f:
                    f.write(output)
                with open("gpt_result.txt", "rb") as file:
                    if appendstr == "":
                        await ctx.send(file=interactions.File(file, "gpt_result.txt"))
                    else:
                        await ctx.send(f"{appendstr}",file=interactions.File(file, "gpt_result.txt"))
    except:
        await ctx.send("Something went wrong...")

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
        output = "<:qito_error:1137124869713166416> Access to imgur-API was denied. Ask Qi to look into it."
    await ctx.send(output,ephemeral=hidden)

@interactions.slash_command(name="listing", description="Join a listing for an event or similar.")
@interactions.slash_option(name="mode", description="What do you want to do?", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Join",value="+"),interactions.SlashCommandChoice(name="Leave",value="-"),interactions.SlashCommandChoice(name="View",value="/"),interactions.SlashCommandChoice(name="[ADM] Clear",value="*"),interactions.SlashCommandChoice(name="[ADM] Lock",value="**"),interactions.SlashCommandChoice(name="[ADM] Restrict",value="***")])
async def listing(ctx: interactions.SlashContext, mode: str):
    await ctx.defer()
    listadmins = ["@space.invader","@flyingline","@pink_milk_tea"]
    user = str(ctx.author)
    guildid = str(ctx.guild.id)
    with open("listing.json") as f:
        listing = json.load(f)
    with open("bs_tags.json") as f:
        tags = json.load(f)
    if guildid not in listing.keys():
        listing[guildid] = {"users":[],"state":True,"restrict":False}
    if mode == "+":
        if (datetime.datetime.now(datetime.timezone.utc) - ctx.author.created_at).days < 30:
            await ctx.send("<:warning:1229332347086704661> This account is too young to join a list.")
            return
        if listing[guildid]["state"] == False:
            await ctx.send("<:warning:1229332347086704661> List is closed.")
            return
        if listing[guildid]["restrict"] == True and str(ctx.author.id) not in tags.keys():
            await ctx.send("<:warning:1229332347086704661> List is restricted to linked BS-Accounts only. Connect yours first via `sh!bslink #TAG`.")
            return
        try:
            if user not in listing[guildid]["users"]:
                listing[guildid]["users"].append(user)
            else:
                await ctx.send("<:warning:1229332347086704661> Already in list.",ephemeral=True)
                return
        except:
            listing[guildid]["users"] = [user]
        await ctx.send("Added to list.")
    if mode == "-":
        try:
            listing[guildid]["users"].remove(user)
        except:
            await ctx.send("<:warning:1229332347086704661> User not in list.",ephemeral=True)
            return
        await ctx.send("Removed from list.")
    if mode == "/":
        try:
            guildlist = listing[guildid]["users"]
            if len(guildlist) == 0:
                raise Exception()
            await ctx.send(f"**Current list:**\n{guildlist}\n**Length:** {len(guildlist)}")
        except:
            await ctx.send(f"<:warning:1229332347086704661> No list available right now.")
    if mode == "*":
        if not user in listadmins:
            await ctx.send("<:warning:1229332347086704661> No permissions to use this command.",ephemeral=True)
            return
        listing[guildid]["users"] = []
        await ctx.send("List cleared.")
    if mode == "**":
        if not user in listadmins:
            await ctx.send("<:warning:1229332347086704661> No permissions to use this command.",ephemeral=True)
            return
        listing[guildid]["state"] = False if listing[guildid]["state"] == True else True
        await ctx.send(f"List state: {listing[guildid]['state']}.")
    with open("listing.json", "w") as f:
        json.dump(listing,f)
    if mode == "***":
        if not user in listadmins:
            await ctx.send("<:warning:1229332347086704661> No permissions to use this command.",ephemeral=True)
            return
        listing[guildid]["restrict"] = False if listing[guildid]["restrict"] == True else True
        await ctx.send(f"List restrict: {listing[guildid]['restrict']}.")
    with open("listing.json", "w") as f:
        json.dump(listing,f)

@interactions.slash_command(name="poll", description="Vote on topics set by admins.")
@interactions.slash_option(name="mode", description="What do you want to do?", required=True, opt_type=interactions.OptionType.STRING, choices=[interactions.SlashCommandChoice(name="Vote",value="+"),interactions.SlashCommandChoice(name="Info",value="*"),interactions.SlashCommandChoice(name="[ADM] Visibility",value="*+"),interactions.SlashCommandChoice(name="[ADM] Delete",value="-"),interactions.SlashCommandChoice(name="[ADM] Set",value="**")])
async def poll(ctx: interactions.SlashContext, mode: str):
    global polling
    await ctx.defer(ephemeral=True)
    listadmins = ["@space.invader","@flyingline","@pink_milk_tea"]
    user = str(ctx.author.id)
    guildid = str(ctx.guild.id)
    if str(guildid) not in polling.keys():
        polling[guildid] = {"voters":[],"options":{},"time":0,"vis":True}
    if (datetime.datetime.now(datetime.timezone.utc) - ctx.author.created_at).days < 30:
        await ctx.send("<:warning:1229332347086704661> This account is too young to use the poll feature.",ephemeral=True)
        return
    # vote
    if mode == "+":        
        if len(polling[guildid]["options"].keys()) == 0:
            await ctx.send("<:warning:1229332347086704661> No poll active.",ephemeral=True)
            return
        if time.mktime(ctx.author.joined_at.timetuple()) > polling[guildid]["time"]:
            await ctx.send("<:warning:1229332347086704661> This account is ineligible to vote.",ephemeral=True)
            return
        if user in polling[guildid]["voters"]:
            await ctx.send("<:warning:1229332347086704661> You have already voted.")
            return
        try:
            content = [x.lower().capitalize() for x in polling[guildid]['options'].keys()]
            components = interactions.StringSelectMenu(
                content,
                placeholder="Select:",
                min_values=1,
                max_values=1,
                custom_id="pollcallback"
            )
            await ctx.send("Options to vote for:", components=components,ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occured.\n{e} : {str(e)}")
    # info
    if mode in ["*"]:
        if len(polling[guildid]["options"].keys()) == 0:
            await ctx.send("<:warning:1229332347086704661> No poll active.")
            return
        if polling[guildid]["vis"] == False:
            await ctx.send("<:warning:1229332347086704661> Poll information hidden.")
            return
        output = "**CURRENT POLL**\n\n"
        for i in polling[guildid]["options"]:
            output += f"[{i.upper()}] - {polling[guildid]['options'][i]} votes\n"
        output += f"\n*Total participation: {len(polling[guildid]['voters'])}*"
        await ctx.send(output,ephemeral=True if mode == "*" else False)
    # visibility
    if mode == "*+":
        if str(ctx.author) in listadmins:
            polling[guildid]["vis"] = not polling[guildid]["vis"]
            await ctx.send(f"<:info:1229350084299194388> Poll visibility switched to {polling[guildid]['vis']}",ephemeral=True)
            with open("polling.json","w") as f:
                json.dump(polling, f)
        else:
            await ctx.send("<:warning:1229332347086704661> No permission to use this",ephemeral=True)
    # delete
    if mode == "-":
        if str(ctx.author) in listadmins:
            polling[guildid] = {"voters":[],"options":{},"time":0,"vis":True}
            with open("voting_log.txt","a") as f:
                f.write(f"A Poll was deleted on GID {guildid}\n")
            await ctx.send("Poll was successfully destroyed.")
        else:
            await ctx.send("<:warning:1229332347086704661> No permission to use this",ephemeral=True)
        with open("polling.json","w") as f:
            json.dump(polling, f)
    # set
    if mode == "**":
        await ctx.send("<:warning:1229332347086704661> Unavailable",ephemeral=True)
        return
        if str(ctx.author) in listadmins:
            if polling[guildid] != {"voters":[],"options":{},"time":0,"vis":True}:
                await ctx.send("<:warning:1229332347086704661> Poll already active. Destroy it first.")
                return
            my_modal = interactions.Modal(
            interactions.ShortText(label="Poll overwrite", custom_id="newpoll", placeholder="Input your poll options. Use this template: ['A','B','C',...]", required=True, min_length=4),
            interactions.ShortText(label="Guild ID", custom_id="guildid", placeholder="Destination Guild-ID", required=True),
            title="POLL // Create:",
            custom_id="poll_create",
            )
            await ctx.send_modal(modal=my_modal)
        else:
            await ctx.send("<:warning:1229332347086704661> No permission to use this",ephemeral=True)

@interactions.slash_command(name="gallery", description="View art of Shenzhia.")
async def gallery(ctx: interactions.SlashContext):
    await ctx.defer(ephemeral=True)
    embeds = []
    for i in range(4,-1,-1):
        embed = interactions.Embed(title=["ARTSGUI","SEBIXO","SEBIXO","VIPKIDDO","INJI"][i],
                      url=["https://x.com/GuilhermeArtz","https://x.com/Sebixo3priv","https://x.com/Sebixo3priv","https://x.com/VIPKiddo29","https://x.com/Inji_arts"][i],
                      color=0x6f07b4,
                      timestamp=datetime.datetime.now())
        if i not in [0,1,4]:
            embed.set_author(name="VIEW POST",url=["","","https://x.com/Sebixo3priv/status/1800572051377541314","https://x.com/VIPKiddo29/status/1806194763181232262",""][i])
        embed.set_image(url=["https://i.imgur.com/WNS8kvk.png","https://i.imgur.com/CYoynim.png","https://pbs.twimg.com/media/GPzqvHlWkAAkMil?format=jpg&name=medium","https://pbs.twimg.com/media/GRDkj6JXIAAYg9M?format=jpg&name=900x900","https://i.imgur.com/yxQw2Is.png"][i])
        embeds.append(embed)
    pg = Paginator.create_from_embeds(bot, *embeds)
    await pg.send(ctx)
    
# -------------------
# CALLBACKS
# -------------------
"""
@interactions.modal_callback("gpt")
async def modal_gpt(ctx: interactions.ModalContext, prompt: str, temp: str = "0"):
    await ctx.defer()
    try:
        temp = float(temp)
    except Exception as e:
        await ctx.send(f"<:warning:1229332347086704661> 'temp' was not a valid number between 0 and 2",ephemeral=True)
        print(e)
        return
    try:
        with open("gpt_usage.json") as f:
            gptdata = json.load(f)
        try:
            tokenCurrency = gptdata[str(ctx.author.id)]
        except:
            tokenCurrency = 1000000
        if prompt == "info":
            if str(ctx.author) == "pink_milk_tea":
                await ctx.send(f"You have ∞ tokens left to use.")
            else:
                await ctx.send(f"You have {tokenCurrency} tokens left to use.\n(750 words are about 1k tokens)")
            return
        messages = [{"role": "user", "content": prompt}]
        try:
            response = client.chat.completions.create(model="gpt-3.5-turbo",messages=messages,temperature=temp,max_tokens=1024)
        except Exception as error:
            await ctx.send(f"<:qito_error:1137124869713166416> Request failed: {error}",ephemeral=True)
            return
        output = f"*{prompt}*\n\n" + str(response.choices[0].message.content)
        if "@everyone" in output or "@here" in output or "<@" in output:
            export = True
        if str(ctx.author) != "pink_milk_tea":
            tokenCurrency -= int(response.usage.total_tokens)
        if tokenCurrency < 0:
            tokenCurrency = 0
        gptdata[str(ctx.author.id)] = tokenCurrency
        with open("gpt_usage.json","w") as f:
            json.dump(gptdata,f)
        appendstr = ""
        if tokenCurrency < 3000 and str(ctx.author) != "pink_milk_tea":
            appendstr = f"<:warning:1229332347086704661> **Approaching token limit.**"
        if tokenCurrency == 0:
            appendstr = f"<:warning:1229332347086704661> **Token limit reached!**"
        try:
            if appendstr == "":
                await ctx.send(output)
            else:
                await ctx.send(appendstr+"\n\n"+output)
        except:
            with open("gpt_result.txt", "w", encoding="utf-8") as f:
                f.write(output)
            with open("gpt_result.txt", "rb") as file:
                if appendstr == "":
                    await ctx.send(file=interactions.File(file, "gpt_result.txt"))
                else:
                    await ctx.send(f"{appendstr}",file=interactions.File(file, "gpt_result.txt"))
    except:
        await ctx.send("Something went wrong...")

@interactions.modal_callback("gpt-e")
async def modal_gpt_export(ctx: interactions.ModalContext, prompt: str, temp: str = "0"):
    await ctx.defer()
    try:
        temp = float(temp)
    except Exception as e:
        await ctx.send(f"<:warning:1229332347086704661> 'temp' was not a valid number between 0 and 2",ephemeral=True)
        print(e)
        return
    with open("gpt_usage.json") as f:
        gptdata = json.load(f)
    tokenCurrency = gptdata[str(ctx.author.id)]
    if prompt == "info":
        if str(ctx.author) == "pink_milk_tea":
            await ctx.send(f"You have ∞ tokens left to use.")
        else:
            await ctx.send(f"You have {tokenCurrency} tokens left to use.\n(750 words are about 1k tokens)")
        return
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",messages=messages,temperature=temp,max_tokens=1024)
    except Exception as error:
        await ctx.send(f"<:qito_error:1137124869713166416> Request failed: {error}",ephemeral=True)
        return
    output = f"*{prompt}*\n\n" + str(response.choices[0].message.content)
    if "@everyone" in output or "@here" in output or "<@" in output:
        export = True
    if str(ctx.author) != "pink_milk_tea":
        tokenCurrency -= int(response.usage.total_tokens)
    if tokenCurrency < 0:
        tokenCurrency = 0
    gptdata[str(ctx.author.id)] = tokenCurrency
    with open("gpt_usage.json","w") as f:
        json.dump(gptdata,f)
    appendstr = ""
    if tokenCurrency < 3000 and str(ctx.author) != "pink_milk_tea":
        appendstr = f"<:warning:1229332347086704661> **Approaching token limit.**"
    if tokenCurrency == 0:
        appendstr = f"<:warning:1229332347086704661> **Token limit reached!**"
    with open("gpt_result.txt", "w", encoding="utf-8") as f:
        f.write(output)
    with open("gpt_result.txt", "rb") as file:
        if appendstr == "":
            await ctx.send(file=interactions.File(file, "gpt_result.txt"))
        else:
            await ctx.send(f"{appendstr}",file=interactions.File(file, "gpt_result.txt"))
"""
@interactions.modal_callback("shuffle")
async def modal_shuffle(ctx: interactions.ModalContext, userinput: str):
    await ctx.defer()
    try:
        await ctx.send(f"Rolled: {random.choice(userinput.split(sep=','))}")
    except:
        await ctx.send(f"<:qito_error:1137124869713166416> Something went wrong.")
    
@interactions.modal_callback("poll_create")
async def modal_poll_create(ctx: interactions.ModalContext, newpoll: str, guildid: str):
    await ctx.defer()
    try:
        userinput = eval(newpoll.strip())  
    except:
        await ctx.send("<:warning:1229332347086704661> Invalid content.")
        return
    if len(userinput) < 2:
        await ctx.send("<:warning:1229332347086704661> Less than 2 options provided.")
        return
    comparision_list = []
    for i in userinput:
        if not isinstance(i, str):
            await ctx.send("<:warning:1229332347086704661> List contains non-string elements. Clear/Format them and try again.")
            return
        if i.upper() in comparision_list:
            await ctx.send("<:warning:1229332347086704661> Duplicate entires detected. (Reminder: Entries are case-**insensitive**)")
            return
        comparision_list.append(i.upper())
    with open("polling.json","r") as f:
        polling = json.load(f)
    polling[guildid.strip()]["options"] = {}
    polling[guildid.strip()]["time"] = time.time()
    for i in userinput:
        polling[guildid.strip()]["options"][i.upper()] = 0
    await ctx.send("Poll created!")
    with open("voting_log.txt","a") as f:
        f.write(f"A Poll was created on GID {guildid}\n")
    with open("polling.json","w") as f:
        json.dump(polling, f)

@interactions.component_callback("pollcallback")
async def pollcallback(ctx: interactions.ComponentContext):
    global polling
    await ctx.defer()
    user = str(ctx.author.id)
    guildid = str(ctx.guild.id)
    with open("polling.json","r") as f:
        polling = json.load(f)
    if str(user) in polling[guildid]["voters"]:
        await ctx.send(f"<:warning:1229332347086704661> Voted already.")
        return
    choice = ctx.values[0]
    polling[guildid]["voters"].append(user)
    polling[guildid]["options"][choice.upper()] += 1
    if polling[guildid]["vis"]:
        await ctx.send(f"Voting completed!\n*Voted for: `{choice}`*")
    else:
        await ctx.send(f"Vote has been cast.")
    with open("voting_log.txt","a") as f:
        f.write(f"{str(ctx.author)} voted {choice} on GID {guildid}\n")
    with open("polling.json","w") as f:
        json.dump(polling, f)


bot.start(discord_bot_token)