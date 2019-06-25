# discord-quest-bot
Discord bot for the Discord Hackweek.

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