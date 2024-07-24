"""Module: bot.py
Author: Will Emery
Date: May 15th 2024
This file contains the code to run the chatbot for project3"""

import os
import openai
import logging
import warnings

import preload_database as pdb
import query_database as qdb


import bot_categories.team_builder_bot as tbb
import bot_categories.individual_builder as ibot
import bot_categories.format_bot as fbot
import bot_categories.play_by_play_bot as pbpbot

openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore", category=DeprecationWarning)


def database_setup():
    """This function will set up the database for the chatbot to use"""
    try: 
        wv_client = pdb.create_client()
        collection_name = 'pokemon_collection'

        if pdb.collection_exists(wv_client, collection_name):
            print(f'The collection {collection_name} already exists')
        
        else:
            print(f'The collection {collection_name} does not exist')
            print(f"Collection '{collection_name}' does not exist.")
            file_path = 'data_collection/pokemon_data.json'

            # dropping the collection, setting it up and adding data to it
            pdb.drop_collections(wv_client, collection_name)
            pdb.create_collection(wv_client, collection_name)
            pdb.add_data_to_collection(wv_client, collection_name, file_path)


    except Exception as error:
        print(error)

    finally:
        print('Database setup complete')
        return wv_client.collections.get(collection_name), wv_client
 

def trim_query_from_response(response: str):
    '''This function will trim queries from the bot from the response. 
    Querey is defined as a block of text that the bot will respond with formatted as 
    ??? query, property, value ???

    ###NOTE: This function is not working with ??? as the split character. It is currently working with ``` as the split character.
    # This is due to the way that ChatGPT is choosing to respond.###
    
    Args:
        response -- str: the response from the chatbot
        
    Returns:
        response -- str: the response from the chatbot with the query trimmed
        
        query -- str: the query that was trimmed from the response'''
    
    # Initialize query to an empty string
    query = ''

    # print(f'Response: {response}')

    # Check if the response contains a query block
    if '```query,' in response:
        # Split the response to extract the query
        parts = response.split('```query,')
        if len(parts) > 1:
            # Extract the query part and remove surrounding backticks
            query = 'query,' + parts[1].split('```')[0].strip()
            # Remove the query part from the response
            response = parts[0].strip() + ' ' + ' '.join(parts[1].split('```')[1:]).strip()
    
    return response, query


def get_llm_response(client : openai.OpenAI, messages, temperature: float = 0, model : str = 'gpt-3.5-turbo') -> str:
    """Get an OpenAI chat completion that will return a response based on the messages provided.
    
    Args:
        client -- OpenAI: the OpenAI client
        messages -- list[dict]: a list of dictionaries with the role and content of the message
        temperature -- float: the randomness of the response
        model -- str: the model to use
    
    Returns:
        response -- str: the response from the chat completion
    """

    response = client.chat.completions.create(
        model = model,
        messages = messages,
        temperature=temperature
    )

    return response


def collect_messages(client: openai.OpenAI, chatbot_context: list) -> str:
    """Collects messages from the user and the chatbot, returning the messages to the user
    
    Args:
        client -- OpenAI: the open AI client
        
    Returns
        response -- str: the response from the chatbot
        prompt -- str: the prompt from the user"""


    prompt = input('\nUser> ')

    # check for prompt injection and apply moderation
    check_for_injection(prompt)
    apply_moderation(prompt, client)

    chatbot_context.append({'role': 'user', 'content' : prompt})
    response = get_llm_response(client, chatbot_context).choices[0].message.content
    
    # print(f'Bot with the World Champ Difference> {response}')
    chatbot_context.append({'role' : 'system', 'content' : response})

    return response, prompt


def check_for_injection(prompt: str):
    """Check for any sort of prompt injection that could be harmful to the system
    
    Args:
        prompt -- str: the prompt to check
    
    Throws an error if the prompt is harmful"""
    
    # check to make sure the prompt is a string
    if not isinstance(prompt, str):
        raise ValueError('Prompt must be a string')
    
    # check for any harmful characters
    for char in prompt:
        if char in [';', '>', '<', '|', '&']:
            raise ValueError('Prompt contains harmful characters')
    
    for word in prompt.split():
        if word in ['rm', 'ls', 'cd', 'pwd', 'cat', 'touch', 'mv', 'cp']:
            raise ValueError('Prompt contains potentially harmful commands')
    
    return prompt
        
    
def apply_moderation(prompt: str, client: openai.OpenAI):
    """
    Calls OpenAI's Moderations endpoint to check whether text is potentially harmful.
    
    Args:
        prompt (str): The prompt to moderate
        client: The OpenAI client object
    
    Returns:
        str: The original prompt if it passes moderation
    
    Raises:
        ValueError: If the prompt is rejected by OpenAI's moderation
    """
    response = client.moderations.create(input=prompt)
    # print(response)
    
    if response.results[0].flagged:
        flagged_categories = response.results[0].categories

        flagged_category = None
        for category, flagged in flagged_categories.__dict__.items():
            if flagged:
                flagged_category = category.replace('_', ' ')
                break
        
        raise ValueError(f'User input most likely contained: {flagged_category}. Ending conversation.')
    else:
        return prompt
    

def bot_query(query_from_bot, pokemon_collection, chatbot_context, openai_client):
    """This function will query the database for the bot. It will return the result of the query to the bot.
    The bot will then use this information to make a suggestion to the user.
    
    Args:
        query_from_bot -- str: the query from the bot
        pokemon_collection -- the collection of Pokemon data
        chatbot_context -- list: the context of the chatbot
        openai_client -- the openai client
        
    Returns:
        query_result -- str: the result of the query to the bot"""
    
    query_response = query_from_bot.split(',')
    query_response.pop(0)
    query_response = [x.strip() for x in query_response]

    query_result = qdb.filter_single_property(pokemon_collection, query_response[0], query_response[1])

    # print(f"Query: {query_result}")

    query_context = f"""Here is the result from your Query: 
    '''
    {query_result}
    '''
    
    Please synthesize this information to help the user build a team.
    Include details about why you think this would be a good fit for the user's team."""

    chatbot_context.append({'role': 'system', 'content': query_context})

    return get_llm_response(openai_client, chatbot_context, temperature=0).choices[0].message.content

def create_metagame_context_string():
    """This function will read the metagame context from a file and return it as a string
    
    Returns:
        context -- str: the metagame context as a string"""
    
    with open('data_collection/metagame_info.txt', 'r') as file:
        context = file.read()

    return context
    

def main():
    client = openai.OpenAI()

    chatbot_context = [
    {'role' : 'system', 'content' : """
    Your role is a as a Competitve Pokemon tutor. Your purpose is to help trainers in their effors to get better at 
     playing competitive Pokemon. Your focus is on gen 9 competitive Pokemon. You are a AI tutor who is very knowledgeable.
     You will stay on subject no matter what the user says.


     Here is information about the gimick of generation 9 as Dynamax has been phased out in favor of a new mechanic called Terastallization:
     When your Pokémon Terastallizes, it changes its entire type to a single pure type Pokémon matching its Tera Type. With this, its moves get a 
     Tera Boost. If the Pokémon is no longer of its original types, those types still get the STAB of *1.5, and the new Tera Type also gets the STAB of *1.5.
     
     If however, the Pokémon Terastallizes into a type which is the same as one of its original types, then the boost on moves of that type is *2 instead. 
     If the Pokémon also has Adaptability as its Ability, then the STAB is *2.25

     Now you will recieve some information from the user about what the user is interested in. Keep in mind that you are a tutor and your purpose is to help the user.
     Stay on this specific topic and provide the user with the information they need to know.
    """}
]

    # Setting up the database
    collection, wv_client = database_setup()

    print("""Hello! I am your AI assistant with the World Champ Difference. I am here to help you with your competitive Pokemon needs. 
          Do you have a category that you would like my help with? If not simply reply 'other' and we will enter into a general 
          discussion about competitive Pokemon.""")
    
    # Setting up data from the user
    user_preference = input('What category would you like help with? [Whole Team Builder, Individual Pokemon Discussion, Doubles, Play by Play Assistance, Other]> ')

    while (user_preference not in ["Whole Team Builder", "Individual Pokemon Discussion", "Doubles", "Play by Play Assistance"]):
        print('Please enter a valid preference to proceed.')
        user_preference = input('User Topic prefrence: [Whole Team Builder, Individual Pokemon Discussion, Doubles, Play by Play Assistance] > ')

    user_data = f"User Topic prefrence: {user_preference}"

    # adding the user data to the chatbot context
    chatbot_context.append({'role' : 'user', 'content' : user_data})

    # If blocks for the different user preferences
    if user_preference == 'Whole Team Builder':
        team_bot = tbb.TeamBuilderBot(client, collection, chatbot_context)
        team_bot.team_builder_bot()
    if user_preference == 'Individual Pokemon Discussion':
        individual_bot = ibot.IndividualBuilderBot(client, collection, chatbot_context)
        individual_bot.IndividualBuilderBot()
    if user_preference == 'Doubles':
        doubles_bot = fbot.DiscussFormatsBot(client, collection, chatbot_context)
        doubles_bot.doubles_discussion()
    if user_preference == 'Singles': # TODO add singles bot
        print('Singles')
    if user_preference == 'Play by Play Assistance':
        play_bot = pbpbot.PlayByPlayBot(client, collection, chatbot_context)
        play_bot.PlayByPlayBot()

    

if __name__ == '__main__':
    main()