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

> [!CAUTION]
> All of these tokens are needed later. Store them securely.
> 
> **Do not share them with anyone!**
> For example, your Discord Token allows anyone in possession of it to have full access to the bot.

## Installing
> [!NOTE]
> Python v3.11.9 has been used for this project.
> v3.12 and above had issues with installing requirements.
- Clone the repo into the directory of your choice
- `cd` into the directory
- Create a venv with `python -m venv .venv` and activate it with `.venv\Scripts\activate.bat` (Windows) / `source .venv/bin/activate` (Mac/Linux)
- Install the requirements via `pip install -r requirements.txt`
- Start `main.py` and follow any instructions that may occur (see next section)

## First Run
> [!WARNING]
> On the bot's first run, important files will be generated.
> Avoid modifying code until the bot has successfully run once to avoid any unexpected behaviour.

Upon running `main.py` for the first time, you will be asked of all the information listed in the prerequisites section.

You can assign a name to your Discord bot token.
In later steps, you can save multiple bot tokens to switch between them (for example when testing while a stable version is already running).

You will also be asked for a logging channel and an "Admin-Server". Paste their respective IDs to assign them.

> [!TIP]
> Get Channel/Server IDs by enabling developer mode in Discord, then right-clicking your server/channel of choice and selecting "Copy [...] ID".
>
> Your logging channel should ideally be inside your "Admin-Server".

After pasting everything, your first-run-setup is done!

