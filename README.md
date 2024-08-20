> [!IMPORTANT]
> Hello world! This readme is not complete yet.

> [!CAUTION]
> This bot is unfinished and in active development. Anything might be broken and be changed without notice.
> 
> This bot has not been tested against large numbers of users/servers. Be aware that performance problems might arise under such circumstances.
>
> *I am by no means a experienced developer. I'm always open for suggestions and feedback, provided it's constructive and remains civil.*

# About
This is Shenzhia, a python discord bot.

It's use is communicating with the Brawl Stars API and displaying data to the requester in an engaging format.

Additionally, it can save and work with received data to further utilize API data.

Shenzhia uses [`discord-interactions-py`](https://github.com/interactions-py/interactions.py) as it's Discord API wrapper. 

# Setup
## Prerequisites
### Software

`Python >= 3.10` is required for certain packages.

> [!NOTE]
> v3.12 and above had issues with installing requirements.
### API-Keys
Shenzhia needs additional resources outside of python related to you. These consist of:
- A Discord Bot Token via [Discords Developer Platform](https://discord.com/developers)
- A Brawl Stars API Token via their [Webpage](https://developer.brawlstars.com/#/)
> [!NOTE]
> The API requires your bot host's IP. If it's IP changes, you have to regenerate your key. 
>
> Shenzhia will notify you either when starting the bot or if a request fails because of this.

- A Sentry DSN for capturing any exceptions that may occur. Create a new project [on their site](https://sentry.io) and select *Python*. Skip the Framework selection and just copy the string shown after `dsn=`.

> [!WARNING]
> You can use the bot without Sentry's service, this however requires editing Shenzhia's code.

## Installing
- Clone the repo into the directory of your choice
- `cd` into the directory
- Create a venv with `python -m venv .venv`
- Activate it
    - `.venv\Scripts\activate.bat` (Windows)
    - `source .venv/bin/activate` (Mac/Linux)
- Install the requirements via `pip install -r requirements.txt`
- Start `main.py` and follow any instructions that may occur (see next section)

## First Run

> [!IMPORTANT]
> Add your bot to a server and get it's and one of it's channels ID before starting `main.py`.
>
> This server will be an "Admin-Server" with additional privileged commands. Make sure only trusted users are inside this server.

> [!WARNING]
> On the bot's first run, important files will be generated.
> Avoid modifying code until the bot has successfully run once to avoid any unexpected behaviour.

Upon running `main.py` for the first time, you will be asked of all the information listed in the prerequisites section.

You can assign a name to your Discord bot token.
When starting the bot after the setup has concluded, you can save multiple bot tokens to switch between them (for example when testing while a stable version is already running).

You will also be asked for a logging channel and an "Admin-Server". Paste their respective IDs to assign them.

After entering everything, your first-run-setup is done!

# Usage

Shenzhia has many different commands. This section explains what every command does.

## Regular Commands

### `/autosync`
Autosync automatically requests profile data for you. Once the command is passed by a user, the `update` key in their data is set to `True`.

This command can only be used, if a user:
- has linked at least one profile
- has successfully executed a `/performance` command while their tag was linked

> [!TIP]
> Behaviour of Autosync itself can be found/adjusted under the `autosync()` coroutine.

### `/bling`
Get information on how much bling you will get next trophy reset. Also displays how much trophies you will lose as well.

### `/gallery`
Shows all Shenzhia-Artwork that has been done by artists.

### `/history`
> [!NOTE]
> This command is incomplete but functional. It will be expanded upon in the future.

Displays your Trophy/TSR-Progression in a graph.
You can choose if the graph shows the last 30 days or all available data with the `timespan` argument.

All generated graphs are saved in `./graphs` until they are overwritten. Graphs are saved per user and display mode.

### `/hyperchargecount`
> [!NOTE]
> - This command is sadly necessary, as the Brawl Stars API does not transmit any data containing Hypercharges.
> - This command can only be executed by uses who have linked at least one profile.

Set how many Hypercharges you currently have. Either set explicitly or add onto an existing record.

### `/leaderboard`
> [!NOTE]
> This command is incomplete but functional. It will be expanded upon in the future.

Shows the 9 best users of Shenzhia by their highest achieved TSR.

Updates to the leaderboard occur when the `bs_player_leaderboard()` coroutine runs (every 3 hours).

### `/listing`
Use this command to add/remove yourself to/from a server wide list.

This list can be used for many reasons - like giveaways, participation checks or anything else.

As a list admin, additional configurations can be made:
- `clear` - Completely wipe the list clean.
- `lock` - No further changes can be made to the list.
- `restrict` - Only users with at least 1 profile link can join the list.

> [!TIP]
> To access the admin commands, enter your Discord username in the `listadmins` symbol. This will likely however be moved to an external file.

### `/matchanalysis`
> [!NOTE]
> Description to be added...

### `/performance`
> [!NOTE]
> Description to be added...

### `/poll`
> [!IMPORTANT]
> This command is broken. It will get fixed in the future.

### `/profilelink`
> [!NOTE]
> Description to be added...

### `/progression`
Shows how much resources you have to collect to be able to max out.
Additionally, a percentage value is given out as well, telling you how far along the way you already are. The status of your brawler power, as well as your battle items is displayed too.

With the `advanced` argument, more stricter requirements for brawlers to be considered "maxed" can be enabled.

> [!TIP]
>
> The requirements for "maxing out" per brawler are as follows: 
> | Standard | Advanced |
> | --- | --- |
> | Power 11 | Power 11 |
> | 1 Gadget | 2 Gadgets |
> | 1 Star Power | 2 Star Powers |
> | 2 Gears | 5 Gears |

### `/randomimg`
Sends a random image from imgur. Enabling `hidden` makes you able to spam this without regrets (probably)

### `/roll`
Roll virtual dice. The number of sides and amount of dice can be set within limits.
- `maximum` : 1 - 9,999,999
- `multiplier` : 1 - 10 (1 implied)

### `/shuffle`
Randomly chooses between different options in a passed list.

Seperate arguments with `,`.

> [!INFO]
> Avoid using leading or trailing commas, as well as commas inside arguments to prevent unexpected results.

### `/status`
Tests the connection to the Brawl Stars API (and by extension if the bot is alive).

If any issues 

### `/whois`
Returns all Brawl Stars Profiles that are linked to the specified Discord User-ID.

## "Admin-Server"-specific Commands
> [!NOTE]
> Any commands not explained here are only for testing purposes and do not have any utility.

### `/close`
Ends the program. Useful if you don't have access to the host at the time.

Setting `quick_restart` to `True` will skip Autosync on Startup.

### `/export`
Get any file within the `shenzhia` directory. To get a file in a subdirectory, use a pattern like this: `subdirectory/file`

Setting `listdir` to `True` will instead list everything inside the directory specified in `query`.

### `/forcerefresh`
Rerun a task ahead of scedule. This doesn't affect the regular excutions of the task.

### `/ip`
Show the IPv4 Address currently in use by the host running the bot.

### `/linknames`
Fetch the Discord-Usernames of every user that has linked at least one profile. Names are linked to User-IDs.

If a username cannot be fetched (e.g. the user is not sharing a server with the bot anymore), the ID is used as the name instead.

### `/reloadjson`
Overwrite the variables manually that are set at the beginning of the program.

### `/reset_ranked_elo`
Sets the `current` key for everyone's saved ranked data to 0 (Effectively showing "Unranked").

This action is irreversible, unless a backup was made.

### `/say`
Let the bot say anything wherever you want.

Use a Channel ID to point to the correct place.

### `/silenceverbose`
Mute the status information posted in the logging channel.

The amount given in `duration` is equal to the amount of minutes logging will be suppressed. If 0 is passed, logging will be enabled unconditionally.

### `/tokenswitch`
Replace the Brawl Stars API token with another one.

> [!INFO]
> Your input is not checked, be sure you copied the the token correctly.

# Additional Information
The following sections are not necessary for operation on the bot, but can give very helpful insight.

## About the Brawl Stars API

The Brawl Stars API gives out a good amount of data, but sadly, has not been updated to keep up with the updates the actual game has gotten.

The following list describes the data you can expect to get from it (and expected data unfortunately missing).

> [!INFO]
> Time of writing: 20th Aug 2024

| *Data* | *Availablity* |
| ---- | ----------- |
| **Main Profile**  |  |
| Current total Trophies    | ✅ |
| Highest total Trophies    | ✅ |
| Win counts for 3v3 and SD | ✅ |
| Fame | ❌ |
| Win Streaks | ❌ |
| Ranked | see later |
| **Brawlers**  |  |
| Current Trophies      | ✅ |
| Highest Trophies      | ✅ |
| Highest achieved Tier | ✅ |
| Power Level | ✅ |
| Gadgets, Star Powers and Gears | ✅ |
| Hypercharges | ❌ |
| Equipped skin | ❌ |
| Mastery | ❌ |
| **Ranked**  |  |
| Current Ranked Rank                | ⚠️ |
| Highest Ranked Rank                | ❌ |
| Current Ranked Elo                 | ❌ |
| Highest Ranked Elo                 | ❌ |
| **Battle Log**  |  |
| Played Brawlers                    | ✅ |
| Total Trophies of Players          | ✅ |
| Brawler Trophies of Players        | ✅ |
| K/D                                | ❌ |
| Damage dealt / Healing done        | ❌ |

## Glossary

> [!INFO]
> This section is not written yet...
