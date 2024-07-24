"""Module: pokemonscraper.py
This file contains functions for scraping data from pokemondb.net. This includes scraping the Pokemon data and the additional information for each Pokemon."""

import time
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd


def make_data_frame():
    """Make a dataframe for the Pokemon
    
    Args: 
        None
    Returns:
        A dataframe for the Pokemon"""
    #list of Pokemon formatted with name, type, damage type, Power, Accuracy, PP
    return pd.DataFrame(columns = ['Number', 'Name', 'Type1', 'Type2', 'Total', 'Attack', 'Defense',
                                   'SP Attack', 'SP Defense', 'Speed'])


def scrape_pokemon_data():
    """Scrape the Pokemon data from the 
    
    Args:
        None
    Returns:
        A dataframe containing the Pokemon data"""
    
    pokemon_df = make_data_frame()

    link = "https://pokemondb.net/pokedex/all"
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all table rows (<tr>) within the desired table
    table_rows = soup.find_all("tr")

    # Extract data from each table row
    for row in table_rows:
        # Find the columns within the row (<td>) and extract relevant data
        columns = row.find_all("td")
        if len(columns) >= 9:
            number = columns[0].find("span", class_="infocard-cell-data").text.strip()
            name = columns[1].find("a").text.strip()

            #processing the types
            soup2 = BeautifulSoup(str(columns[2]), "html.parser")
            types = soup2.get_text(separator=' ')
            #sepearate the types
            type1 = types.split()[0]
            type2 = types.split()[1] if len(types.split()) > 1 else None

            #processing the stats
            total = columns[3].text.strip()
            attack = columns[4].text.strip()
            defense = columns[5].text.strip()
            sp_attack = columns[6].text.strip()
            sp_defense = columns[7].text.strip()
            speed = columns[8].text.strip()

            pokemon_df = pokemon_df._append({'Number': number, 'Name': name, 'Type1': type1, 'Type2': type2, 
                                            'Total': total, 'Attack': attack, 'Defense': defense, 
                                            'SP Attack': sp_attack, 'SP Defense': sp_defense, 'Speed': speed}, 
                                            ignore_index=True)
    
    return pokemon_df


def add_additional_info(dataframe):
    """This function will add additional information to the dataframe
    
    Args:
        dataframe: The dataframe containing the pokemon data ie Weight, Abilities, Possible Moves
    
    Returns:
        The dataframe with the additional information added"""
    #add columns to the dataframe
    dataframe["Weight"] = None
    dataframe["Ability1"] = None
    dataframe["Ability2"] = None
    dataframe["AbilityHA"] = None

    #iterate through the dataframe and add the additional info
    for index, row in dataframe.iterrows():
        info = get_additional_info_pokemon(row["Name"])
        print(row["Name"])
        dataframe.loc[index, "Weight"] = info[0]
        dataframe.loc[index, "Ability1"] = info[1][0]
        dataframe.loc[index, "Ability2"] = info[1][1]
        dataframe.loc[index, "AbilityHA"] = info[1][2]
        list_str = ', '.join(info[2])
        dataframe.loc[index, "Possible Moves"] = list_str

    return dataframe


def get_additional_info_pokemon(pokemon_name):
    """This function will go to the pokemon's page in pokemon db and get 
    needed additional information such as weight, abilities, and possible moves
    
    Args:
        pokemon_name: The name of the pokemon
    
    Returns:
        A list containing the weight, abilities, and possible moves of the pokemon"""
    if " " in pokemon_name:
        pokemon_name = pokemon_name.replace(" ", "-")

    link = "https://pokemondb.net/pokedex/" + pokemon_name
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")

    if len(soup.find_all("tr")) == 0:
        #case to handel a bug with regional forms, this will be added later manually
        return [None, [None, None, None], ["None", "None"]]
    
    weight = soup.find_all("tr")[4].find("td").text.strip()

    abilities = get_abilities(pokemon_name, soup)
    
    levelup_moves = get_levelup_moves(pokemon_name, soup)
    evolution_moves = get_evolution_moves(pokemon_name, soup)
    egg_moves = get_egg_moves(pokemon_name, soup)
    tm_moves = get_tm_moves(pokemon_name, soup)
    possible_moves = levelup_moves + evolution_moves + egg_moves + tm_moves

    #remove duplicate moves
    possible_moves = list(dict.fromkeys(possible_moves))
    #put the moves in alphabetical order
    possible_moves.sort()
    #put them back into a list without duplicates
    possible_moves = list(dict.fromkeys(possible_moves))

    return [weight, abilities, possible_moves]


def get_levelup_moves(pokemon_name, soup):
    """This function will go to a pokemon's page in pokemon db and get the levelup moves and return it as a list
    
    Args:
        pokemon_name: The name of the pokemon
        soup: The soup object of the pokemon's page
    
    Returns:
        A list containing the levelup moves of the pokemon"""

    #levelup moves will be in the sixth table
    levelup_moves_table = soup.find("table", class_="data-table")

    levelup_moves = []

    tbody = levelup_moves_table.find("tbody")
    levelup_moves_raw = tbody.find_all(class_ = "ent-name")
    for move in levelup_moves_raw:
        levelup_moves.append(move.text.strip())
        
    return levelup_moves


def get_evolution_moves(pokemon_name, soup):
    """This function will go to the pokemon's page in pokemon db and will return the egg moves as a list
    
    Args:
        pokemon_name: The name of the pokemon
        soup: The soup object of the pokemon's page
        
    Returns:
        A list containing the evolution moves of the pokemon"""

    #egg moves will be in the 7th table
    egg_moves_table = soup.find_all("table", class_="data-table")[1]
    
    egg_moves = []

    tbody = egg_moves_table.find("tbody")
    egg_moves_raw = tbody.find_all(class_ = "ent-name")
    for move in egg_moves_raw:
        egg_moves.append(move.text.strip())

    return egg_moves


def get_egg_moves(pokemon_name, soup):
    """This function will go to the pokemon's page in pokemon db and will return the egg moves as a list
    
    Args:
        pokemon_name: The name of the pokemon
        soup: The soup object of the pokemon's page
        
    Returns:
        A list containing the egg moves of the pokemon"""

    #egg moves will be in the 8th table
    egg_moves_table = soup.find_all("table", class_="data-table")[2]
    
    egg_moves = []

    tbody = egg_moves_table.find("tbody")
    egg_moves_raw = tbody.find_all(class_ = "ent-name")
    for move in egg_moves_raw:
        egg_moves.append(move.text.strip())

    return egg_moves


def get_tm_moves(pokemon_name, soup):
    """This function will go to the pokemon's page in pokemon db and will return the tm moves as a list
    
    Args:
        pokemon_name: The name of the pokemon
        soup: The soup object of the pokemon's page
        
    Returns:
        A list containing the tm moves of the pokemon"""

    if len(soup.find_all("table", class_="data-table")) < 4:
        return []

    #tm moves will be in the 9th table
    tm_moves_table = soup.find_all("table", class_="data-table")[3]

    tm_moves = []

    tbody = tm_moves_table.find("tbody")
    tm_moves_raw = tbody.find_all(class_ = "ent-name")
    for move in tm_moves_raw:
        tm_moves.append(move.text.strip())

    return tm_moves
    

def get_abilities(pokemon_name, soup):
    """This function will go to the pokemon's page in pokemon db and will return the abilities as a list
    
    Args:
        pokemon_name: The name of the pokemon
        soup: The soup object of the pokemon's page
        
    Returns:
        A list containing the abilities of the pokemon"""
    
    #setting up local Variables
    ability1 = None
    ability2 = None
    abilityHA = None

    abilities = soup.find_all("tr")[5].find("td").text.strip()

    #check to see if the text "hidden ability" is in the string
    if "hidden ability" in abilities:
        # Split the string on capitals not followed by a space
        matches = re.split(r'(?<!\s)(?=[A-Z])', abilities)

        if len(matches) > 1:
            abilityHA = matches[1]
            #remove the text "(hidden ability)" from the string and trim
            abilityHA = abilityHA.replace("(hidden ability)", "").strip()

            #now remove split the information in matches[0] by the numbers follwed by a '.'
            text = matches[0]

            #the contents of text will be the remaining abilities.
            #they will be formatted as 1.ability textFirst2.ability textSecond
            #split the string into "ability textFirst" and "ability textSecond"
            matches = re.split(r'(?<!\s)(?=[0-9])', text)
            #now remove the number and '.' from the strings
            if len(matches) > 2:
                ability1 = matches[1].replace("1.", "").strip()
                ability2 = matches[2].replace("2.", "").strip()
            else:
                ability1 = matches[1].replace("1.", "").strip()

    else:
        ability1 = abilities.replace("1.", "").strip()
    
    return[ability1, ability2, abilityHA]


if __name__ == "__main__":
    df = scrape_pokemon_data()
    df = add_additional_info(df)
    df.to_csv("pokemon.csv", index=False)
