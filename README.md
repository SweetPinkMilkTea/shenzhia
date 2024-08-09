> [!CAUTION]
> This bot is unfinished and in active development. Anything might be broken and be changed without notice.

# About
This is Shenzhia, a python discord bot.

It's use is communicating with the Brawl Stars API and displaying data to the requester in an appropriate format.

Additionally, it can save and work with received data to further utilize API data.

# Additional Requirements
Shenzhia needs additional resources outside of python related to you. These consist of:
- A Discord Bot Token via [Discords Developer Platform](https://discord.com/developers)
- A Brawl Stars API Token via their [Webpage](https://developer.brawlstars.com/#/)
> [!NOTE]
> The API requires your IP. If your IP changes, you have to regenerate your key. 
>
> Shenzhia will notify you either when starting the bot or if a request fails because of this.

- A Sentry DSN for capturing any exceptions that may occur. Create a new project [on their site](https://sentry.io) and select *Python*. Skip the Framework selection and just copy the string shown after `dsn=`.

> [!WARNING]
> You can use the bot without Sentry's service, this however requires editing Shenzhia's code.

# Set-up
- Clone the repo into the directory of your choice
- `cd` into the directory
- Create a venv with `python -m venv .venv` and activate it with `.venv\Scripts\activate.bat` / `source .venv/bin/activate`
- Install the requirements via `pip install -r requirements.txt`
- Start `main.py` and follow any instructions that may occur
