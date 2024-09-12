> [!TIP]
> Searching for bot usage documentation? Find information on using the bot on the wiki section of the repo.

> [!CAUTION]
> This bot is unfinished and in active development. Anything might be broken and be changed without notice.
> 
> This bot has not been tested against large numbers of users/servers. Be aware that performance problems might arise under such circumstances.
>
> *I am by no means an experienced developer. I'm always open for suggestions and feedback, provided it's constructive and remains civil.*

# About
This is Shenzhia, a python discord bot.

Its use is communicating with the Brawl Stars API and displaying data to the requester in an engaging format.

Additionally, it can save and work with received data to further utilize API data.

Shenzhia uses [`discord-interactions-py`](https://github.com/interactions-py/interactions.py) as it's Discord API wrapper. 

# Setup
## Create and Invite your Bot
Visit [Discords Developer Platform](https://discord.com/developers) and create a bot.

For it to work correctly, visit the "Installation" section and select the `bot` scope under "Default Install Settings" (while enabling Guild Installation).

Next, check the following permissions:
- Attach Files
- Embed Links
- Send Messages
- Use external Emojis
- Use Slash Commands
- View Channels

Invite your Bot to your server after.

> [!IMPORTANT]>
> This server will be an "Admin-Server" with additional privileged commands. Make sure only trusted users are inside this server, or create a server just for the bot instead.

## Prerequisites
### Software

`Python >= 3.10` is required for certain packages.

### API

Shenzhia needs additional resources outside of python related to you. These consist of:
- A Discord Bot Token gotten while creating your bot in [Discords Developer Platform](https://discord.com/developers)
- A Brawl Stars API Token via their [Webpage](https://developer.brawlstars.com/#/)
> [!NOTE]
> The API requires your bot host's IP. If it's IP changes, you have to regenerate your key. 
>
> Shenzhia will notify you either when starting the bot or if a request fails because of this.

- A Sentry DSN for capturing any exceptions that may occur. Create a new project [on their site](https://sentry.io) and select *Python*. Skip the Framework selection and just copy the string shown after `dsn=`.

> [!WARNING]
> You can use the bot without Sentry's service, this however requires editing Shenzhia's code.

### Custom Emojis
Custom Emojis are an integral part of Shenzhia by visualizing a lot of data in a more digestible format than simply dumping text everywhere.
However, for them to function, they have to be set first.

A bot can use an emoji reference (e.g. `<:bingus:1228965645262258207>`) to display custom emojis.
To get Emoji references:

- Send a message with a Backslash in front of the emoji in a Server the App and Emoji is in.

or

- Press the "Copy Markdown" button of the Emoji in the Emoji Section of your Application

> [!NOTE]
> For a bot to use a custom emoji, the emoji has to be in the same server where the app is in, or has to get added to the application itself.
> If you are using multiple applications interchangeably, the second option will lead to only one app being able to use assigned Emojis.

On first run setup, every Emoji utilized is asked to be assigned by pasting in the references obtained during Emoji creation.

The list of Emojis (and Examples used) is as follows:
| Prompt | Description | Example |
| --- | --- | --- |
| Power1 - Power11 | Brawler Power Indicators | ![](https://cdn.discordapp.com/emojis/1228965756092285011.webp?size=44&quality=lossless) |
| Gadget_OK | Brawler has a Gadget | ![](https://cdn.discordapp.com/emojis/1228965764631892069.webp?size=44&quality=lossless) |
| SP_OK | Brawler has a Star Power | ![](https://cdn.discordapp.com/emojis/1228965791639277659.webp?size=44&quality=lossless) |
| Gear_OK | Brawler has a Gear | ![](https://cdn.discordapp.com/emojis/1228965774199230474.webp?size=44&quality=lossless) |
| Slot_Empty | Brawler does not have this item | ![](https://cdn.discordapp.com/emojis/1228965782390702201.webp?size=44&quality=lossless) |
| Bronze, Silver, Gold | Star Icons for Rankings and Star Player | ![](https://cdn.discordapp.com/emojis/1153418516205162577.webp?size=44&quality=lossless) |
| Trophy, Bling, PPoint, GadgetIcon, SPIcon, GearIcon, HChargeIcon | Represenation for the in game symbols | ![](https://cdn.discordapp.com/emojis/1137140150065954816.webp?size=44&quality=lossless) |
| Error, Warning, Info | Symbols for emphasizing process outcomes | ![](https://cdn.discordapp.com/emojis/1137124869713166416.webp?size=44&quality=lossless) ![](https://cdn.discordapp.com/emojis/1229332347086704661.webp?size=44&quality=lossless) ![](https://cdn.discordapp.com/emojis/1229350084299194388.webp?size=44&quality=lossless) |
| Connected | Indicates bot startup | ![](https://cdn.discordapp.com/emojis/1140550294313373766.webp?size=44&quality=lossless) |
| Rank<tier> | Rankings for certain functionality | See below |

Here are all rank icons. You can use them by copying their URLs.

| Rank | Icon |
| --- | --- |
| None | ![](https://cdn.discordapp.com/emojis/1134890614635372675.webp?size=44&quality=lossless) |
| E | ![](https://cdn.discordapp.com/emojis/1262541950561812601.webp?size=44&quality=lossless) |
| D | ![](https://cdn.discordapp.com/emojis/1262542011576356915.webp?size=44&quality=lossless) |
| D+ | ![](https://cdn.discordapp.com/emojis/1262542055326879858.webp?size=44&quality=lossless) |
| C- | ![](https://cdn.discordapp.com/emojis/1262542122469294121.webp?size=44&quality=lossless) |
| C | ![](https://cdn.discordapp.com/emojis/1262542167440756847.webp?size=44&quality=lossless) |
| C+ | ![](https://cdn.discordapp.com/emojis/1262542219714494484.webp?size=44&quality=lossless) |
| B- | ![](https://cdn.discordapp.com/emojis/1262542285644501095.webp?size=44&quality=lossless) |
| B | ![](https://cdn.discordapp.com/emojis/1262543019417014333.webp?size=44&quality=lossless) |
| B+ | ![](https://cdn.discordapp.com/emojis/1262543136291426394.webp?size=44&quality=lossless) |
| A- | ![](https://cdn.discordapp.com/emojis/1262543188908839022.webp?size=44&quality=lossless) |
| A | ![](https://cdn.discordapp.com/emojis/1262543236518383616.webp?size=44&quality=lossless) |
| A+ | ![](https://cdn.discordapp.com/emojis/1262543274506457089.webp?size=44&quality=lossless) |
| S- | ![](https://cdn.discordapp.com/emojis/1263948719577894922.webp?size=44&quality=lossless) |
| S | ![](https://cdn.discordapp.com/emojis/1263948731167015013.webp?size=44&quality=lossless) |
| S+ | ![](https://cdn.discordapp.com/emojis/1263948744286802021.webp?size=44&quality=lossless) |
| SS | ![](https://cdn.discordapp.com/emojis/1263953646245384274.webp?size=44&quality=lossless) | 
| EX | ![](https://cdn.discordapp.com/emojis/1133686283093426256.webp?size=44&quality=lossless) |

## Installing

- Clone the repo into the directory of your choice or download from the Releases
    - When downloading from Releases, unpack the archive.
- `cd` into the directory
- Create a venv with `python -m venv .venv`
- Activate it
    - `.venv\Scripts\activate.bat` (Windows)
    - `source .venv/bin/activate` (Mac/Linux)
- Install the requirements via `pip install -r requirements.txt`
- Start `main.py` and follow any instructions that may occur (see next section)

## First Run
> [!WARNING]
> On the bot's first run, important files will be generated.
> Avoid modifying code until the bot has successfully run once to avoid any unexpected behavior.

Upon running `main.py` for the first time, you will be asked of all the information listed in the prerequisites section.

You can assign a name to your Discord bot token.
When starting the bot after the setup has concluded, you can save multiple bot tokens to switch between them (for example when testing while a stable version is already running).

You will also be asked for a logging channel and an "Admin-Server". Paste their respective IDs to assign them.

Finally, set all needed Emojis.

After entering everything, your first-run-setup is done!