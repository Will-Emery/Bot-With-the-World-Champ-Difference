### Bot with the Wolrd Champ Difference

Recently, in my free time, which I have very little of, I've been enjoying playing some competitive Pokemon. Competitive Pokemon sounds silly, but it is one of the most complex strategy games out there and it takes a lot of game knowledge to be remotely decent at. Because of the high barrier to entry, I figured that this would be a fun project to work on because its a passion of mine and could potentially be useful to others.

#### Data Gathering

The biggest hurdle to overcome with this project is that ChatGPT knows little to nothing about the current metagame of Pokemon Scarlet and Violet as it's last training data is from 2021. This means that I will have to manually input all of the data for the Pokemon, moves, abilities, and items that have been released since then. This was done using a script that scrapes data from a website called PokemonDB.

The contents of this script and the result of the scraping can be found in the folder `data_collection`. The script is called `pokemon_scraper.py`. The data from this script is stored in the file `pokemon_data.csv`. This data was then put into a JSON file called `pokemon_data.json` for easier access with Weaviate. This JSON data is then uploaded into Weaviate using the `preload_database.py` script. Because of the sheer amount of data in this file, the Weaviate collection containg this data is not created every time the bot is run. Instead, the collection is created once and then the bot is run with the collection already in place.

#### The main Bot

The main way to run the bot can be found in the `bot.py` file located in the root of the Project 3 directory. This file contains a lot of big helper functions for what I have decided to call the sub-bots of which there are currently 4. The sub-bots are as follows and can be found in the `bot_categories` folder:

- `format_bot.py`- this is a general bot used for disucssing strategies within certain battle formats. The only format currently supported is the doubles format where each player has 2 Pokemon on the field at once. The focus on only a single format for now is that so that the bot can be more specialized in its responses.
- `individual_builder.py` - This bot is used for building out strategies surrounding a single Pokemon. This bot is used for discussing the best moves, abilities, and items for a single Pokemon as well as good partners for said Pokemon. The functionality of this bot is very similar to the format bot because it is less restrictive and less focused on a specific task.
- `team_builder.py` - This bot is used for building out strategies surrounding a team of Pokemon. This bot is used for discussing the best moves, abilities, and items for a team of Pokemon as well as good partners for the team. This bot is more focused on the team as a whole rather than the individual Pokemon. This is a really well fleshed out bot that is honestly really helpful for team building.
- `play_by_play_bot.py` - This is a bot that is used for discussing the best moves to make in a given situation as a battle plays out. The player starts by giving the bot a "pokepaste" of the team that they want to use, and then either a pokepaste of their opponent's team or the opponent's team in a more readable format, if the battle format is closed team sheets. The bot then gives the player the best moves to make in the given situation. This bot is the most complex of the bots and is the most useful for players who are already familiar with the game. If you want to try this, the best way to do so is to go to a website called Pokemon Showdown and play a game with the bot as your coach. I have supplied a pokepaste of a team that I have used in the past in the `test_prompts` folder. For testing I played against an agent on the website. The team I gave said agent can also be found in the `pokepaste_for_pbp.txt` file in the `test_prompts` folder.

#### Test Prompts

A lot of my testing can be found in the folder labled `test_prompts`. This folder contains a lot of the prompts that I used to test the bot. The prompts are organized by the bot that they are used for. The prompts are also organized by the type of prompt that they are.
