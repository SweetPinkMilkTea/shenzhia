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

### Custom Emojis
Many custom Emojis are used with Shenzhia. On the first run setup, you set emojis so they can be displayed.

To be able to set emojis, [follow the instructions here.](https://github.com/SweetPinkMilkTea/shenzhia/wiki/Setting-Emojis)

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

Finally, set all needed Emojis.

After entering everything, your first-run-setup is done!

> [!TIP]
> Searching for bot usage documentation? Find information on using the bot on the wiki section of the repo.