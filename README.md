# discord-quest-bot
Discord bot for the Discord Hackweek. Will probably be released publicly later. For now, please use the support server below to play.

# Support Server

Please join in order to report bugs, seek help with the bot, or just to play.
**[Click here to join!](https://discordapp.com/invite/HMakTvr)**

# Running

Requires python 3 and a database.

Copy `.env.example` to `.env` and change appropriate variables. If you use a database other than mysql, you may need additional dependencies: See [here](https://tortoise-orm.readthedocs.io/en/latest/databases.html#databases)

It's recommended to create a virtualenv for consistency:

```
 $ virtualenv .venv
 $ source .venv/bin/activate

 $ pip install -r requirements.txt
```

Then, to run the bot:

```
 $ python run.py
```

# Developing

Set up pre-commit hook (for linting):

```
  $ pip install black
  $ ln ./scripts/pre_commit .git/hooks/pre-commit 
```

# Attribution

Placeholder art:

	- Zombie - CharlesGabriel (opengameart.org, CC-BY 3.0)
	- Chest - Blarumyrran (opengameart.org, CC 0)
	- Tiles - https://opengameart.org/content/lpc-tile-atlas (GPL 3.0)