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
> [!TIP]
> Terms specific to Shenzhia are used here. Use the [Glossary](#glossary) to search them up.

Gets a match from your (or the specified profiles) battle log and analyses all of its participants like in `/performance`.

The following is displayed when running the command:
- Every participating players:
  - Picked brawler and their trophies, power, gadget/star power/gear status
  - Current total trophies
  - Current TSR and associated rank
- Differences in your and the opposing teams:
  - Average brawler trophy count
  - Average total trophy count
  - Average TSR

> [!NOTE]
> Evaluation is only available for 3v3 or Solo Showdown matches with all player slots filled. 

### `/performance`
> [!TIP]
> Terms specific to Shenzhia are used here. Use the [Glossary](#glossary) to search them up.

Evaluates your profile on the basis of your Trophies and Ranked data ([within limits](##About-the-Brawl-Stars-API)).

The following is displayed when running the command:
- Profiles current and highest Trophies
- Profiles current and highest recorded TSR
- If the Discord User which the profile is linked to is in the TSR Leaderboard
- The profiles 9 highest brawlers in Trophy League which also have:
  - Current and highest achieved trophies
  - The Brawlers tier
  - Whether the brawler has a Gadget, a Star Power and/or up to 2 gears equipped
  - The brawlers individually calculated TSR
- If not the first request, the difference of Trophies (and TSR, if applicable) to the previous request
- Your last and highest scanned Ranked rank.
> [!NOTE]
> Ranked data is unreliable to get and will differ from expected results. View more info [here](##About-the-Brawl-Stars-API).
- Your win rate and current win/loss streak
- Autosync status (Available for linked profiles in Slot 1 of a user)
- ABT, ABP, SDR, WD and SF (Read more about them in the [Glossary](#glossary))

Certain information may not be shown under certain circumstances, either if they are not available or if certain conditions are (not) met.

If multiple profiles are linked, all of them are requested simultaneously. Switch viewing profiles with the arrow buttons available under the sent embed.


### `/poll`
> [!IMPORTANT]
> This command is broken. It will get fixed in the future.

### `/profilelink`
Adds or removes a tag to your linked profiles or lists all of your current linked profiles (depending on what is passed in `mode`).

A total of 5 profiles can be linked at once.

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

> [!NOTE]
> Avoid using leading or trailing commas, as well as commas inside arguments to prevent unexpected results.

### `/status`
Tests the connection to the Brawl Stars API (and by extension if the bot is alive).

Displays errors when they occur.

### `/whois`
Returns all Brawl Stars Profiles that are linked to the specified Discord User-ID.

## "Admin-Server"-specific Commands
> [!NOTE]
> Any commands not explained here are only for testing purposes and do not have any utility.

> [!CAUTION]
> Most of the commands in this section have a major (indirect) impact on the operation of the bot. Take precautions to not let malicious actors access these commands!

### `/close`
Ends the program. Useful if you don't have access to the host at the time.

Setting `quick_restart` to `True` will skip Autosync on the next Startup.

### `/export`
Get any file within the `shenzhia` directory. To get a file in a subdirectory, use a pattern like this: `subdirectory/file`

Setting `listdir` to `True` will instead list everything inside the directory specified in `query`.

### `/forcerefresh`
Rerun a task ahead of scedule. This doesn't affect the regular excutions of the task.

### `/ip`
Show the IPv4 Address currently in use by the host device running the bot.

### `/linknames`
Fetch the Discord-Usernames of every user that has linked at least one profile. Names are linked to User-IDs.

If a username cannot be fetched (e.g. the user is not sharing a server with the bot anymore), the ID is used as the name instead.

> [!TIP]
> Normally, a link is established when a user links the profile. This command can be used to correct faulty links or renew them to update the names.

### `/reloadjson`
Rewrites the constants that are set at the beginning of the program.

> [!TIP]
> For devs: If any additional constants are added, adding the load process within the coroutine is a good idea.

### `/reset_ranked_elo`
> [!NOTE]
> This command will be removed once accurate ranked data is used.

Sets the `current` key for everyone's saved ranked data to 0 (Effectively showing "Unranked").

This action is irreversible unless a backup was made.

### `/say`
Let the bot say anything wherever you want.

Use a Channel ID to point to the correct place.

### `/silenceverbose`
Mute the status information posted in the logging channel.

The amount given in `duration` is equal to the amount of minutes logging will be suppressed. If 0 is passed, logging will be enabled unconditionally.

### `/tokenswitch`
Replace the Brawl Stars API token with another one.

> [!NOTE]
> Your input will not be checked for validity, be sure you copied the the token correctly.

# Additional Information
The following sections are not necessary for operation on the bot, but can give very helpful insight.

## About the Brawl Stars API

The Brawl Stars API gives out a good amount of data, but sadly, has not been updated to keep up with the updates the actual game has gotten.

The following list describes the data you can expect to get from it (and expected data unfortunately missing).

> [!NOTE]
> Time of writing: 25th Aug 2024
>
> ✅: Available
> ⚠️: Supplemented by 3rd party API
> ❌: Unavialable

| *Data* | *Availablity* |
| ---- | ----------- |
| **Main Profile**  |  |
| Current total Trophies    | ✅ |
| Highest total Trophies    | ✅ |
| Win counts for 3v3 and SD | ✅ |
| Fame | ⚠️ |
| Win Streaks | ⚠️ |
| Ranked | see below |
| **Brawlers**  |  |
| Current Trophies      | ✅ |
| Highest Trophies      | ✅ |
| Highest achieved Tier | ✅ |
| Power Level | ✅ |
| Gadgets, Star Powers and Gears | ✅ |
| Hypercharges | ❌ |
| Equipped skin | ❌ |
| Mastery | ⚠️ |
| **Ranked**  |  |
| Current Ranked Rank                | ⚠️ |
| Highest Ranked Rank                | ⚠️ |
| Current Ranked Elo                 | ⚠️ |
| Highest Ranked Elo                 | ⚠️ |
| **Battle Log**  |  |
| Max amount of Battles              | 25 |
| Played Brawlers                    | ✅ |
| Total Trophies of Players          | ✅ |
| Brawler Trophies of Players        | ✅ |
| K/D                                | ❌ |
| Damage dealt / Healing done        | ❌ |

## Glossary

### TSR
TSR stands for **Trophy Skill Rating**. It's an attempt at making the trophy system at least express a little bit on how a players skill can be expected.

TSR factors the Top 9 brawlers of a profile into account. The trophies of those brawlers are then subtracted `500`.

Next, all values are calculated using this formula (`x` representing the modified trophy values):

$y = 1.\overline{7}*(x^2)$

Resulting values under `0` are set to `0`. Values exceeding `1,000,000` are set to `1,000,000` plus $x-750$

> [!TIP]
> Effectively, 0 points are awarded at 500 Trophies (Tier 20) and 1M at 1250 (Tier 35)
> Any trophies over 1250 are added on top of the max TSR at a 1:1 ratio (Example: 1300 -> 1M + 50)

The now 9 (probably different) scores are then weighted by calculating $y = \frac{x}{a}$, with `x` being the score and `a` being the divisor derived as follows:

| Position | Divisor |
| --- | --- |
| #1 | 4 (25%) |
| #2 | 8 (12.5%) |
| #3 | 8 |
| #4 | 8 |
| #5 | 8 |
| #6 | 16 (6.25% ) |
| #7 | 16 |
| #8 | 16 |
| #9 | 16 |

All calculated and weighted scores are now added together and result in a players TSR. Additionally, a rank is displayed representing it.

| Rank | TSR-Requirements |
| --- | --- |
| E | ≥ 1 |
| D | ≥ 17,778 |
| D+ | ≥ 36,111 |
| C | ≥ 54,444 |
| C | ≥ 73,333 |
| C | ≥ 92,222 |
| B | ≥ 111,111 |
| B | ≥ 127,407 |
| B | ≥ 143,703 |
| A | ≥ 160,000 |
| A | ≥ 201,481 |
| A | ≥ 242,962 |
| S | ≥ 284,444 |
| S | ≥ 364,444 |
| S | ≥ 444,444 |
| SS | ≥ 751,111 |
| EX | ≥ 1,000,000 |

> [!TIP]
> The highest rank (EX) can only be obtained if all 9 brawlers are ≥1250 trophies - regardless of TSR.

### SDR

SDR stands for **Showdown-Ratio**, which displays the percentage of Showdown (Solo and Duo) wins compared to all wins.

The calculation is as follows:

$\frac{DuoShowdownWins + SoloShowdownWins}{DuoShowdownWins + SoloShowdownWins + 3v3Wins}*100$

> [!TIP]
> Commands like `/performance` and `/matchanalysis` behave differently with accounts on high SDR.

### ABT/ABP

ABT and ABP mean **Average Brawler Trophies** and **Average Brawler Power** respectively.

*(The name should be pretty self-explanatory)*

> [!NOTE]
> ABT/ABP do not get calculated for players with less than 10 brawlers.

### AR

AR stands for **Account Rating**. It is intended to build upon TSR to additionally indicate dedication and skill.

An account can have 54 AR at most. AR is awarded as follows:

| Area | AR | Max AR |
| --- | --- | --- |
| TSR | 1 per rank passed | 17
| Ranked | 1 per rank passed | 19
| SDR | $AR = \frac{\|SDR-100\|}{10}$ | 10
| ABT | 1 AR per 2 ranks passed | 8

> [!NOTE]
> The ABT value is translated into a TSR Rank for AR evaluation.
>
> All AR-values are rounded down. 

### WD

WD stands for **Win Distribution**. It's used in the `/performance` to explain the calculated Winrate.

It's displayed like this: `t > w - f`
- `t` : 3v3 games in Battle-Log
- `w` : Wins in Battle-Log
- `f` : Games qualifying as "flukes" (Defeats with the target player as Star Player)

> [!TIP]
> Flukes are treated as ties. If any are present, the winrate shown will be adjusted, with the original one in parentheses.

### SF

> [!WARNING]
> To set up SF, run `bs_spiciness.py` in `/extras`. There are currently no safeguards preventing the `/performance` command from failing if SF isn't set up.
>
> The data used for SF had to be manually entered by hand (unless any automated process concerning Brawl Stars Tier Lists is found), preferably every time the game balance changes.

SF stands for **Spiciness Factor**. It's uses as a representation on how "meta" a player is playing by evaluating their top brawlers. It is by no means a measure of skill.

It's calculated by the bot-owner assigning tiers to every brawler. The more "meta" a brawler is, the lower the score.

For SF, the top 9 brawlers of a players are used, while higher positions are weighted more.