import os
import openai
import preload_database as pdb
import query_database as qdb
import animations as ani

import bot as main_bot

class IndividualBuilderBot:
    def __init__(self, openai_client, collection, chatbot_context=[]):
        self.openai_client = openai_client
        self.pokemon_collection = collection
        self.interest_pokemon = None
        self.chatbot_context = chatbot_context
    

    def get_pokemon(self):
        """This function will prompt the user to enter a Pokemon that they would like to learn more about.
        
        Returns:
            db_query -- str: the result of the query to the database for the user's Pokemon of choice"""
        print("Please supply a Pokemon that you would like to learn more about and build a strategy around.")

        user_input_pokemon = input("Please enter a Pokemon: ")
        db_query = qdb.filter_single_property(self.pokemon_collection, 'name', user_input_pokemon)

        print(f"\n{db_query}\n")

        return db_query
    

    def IndividualBuilderBot(self):
        """This function will start the conversation with the user and prompt them to enter a Pokemon that they would like to learn more about."""
        self.interest_pokemon = self.get_pokemon()

        chatbot_context_individual_builder_start = f"""The user has chosen to focus on building a strategy or having a conversation around {self.interest_pokemon.objects[0].properties.get('name')}. 
        You should begin by asking the user what they would like to do with this Pokémon.

        Here is some more information about {self.interest_pokemon.objects[0].properties.get('name')}:
        self.interest_pokemon

        Throughout this conversation, you have access to a database of Pokémon, their moves, and abilities. You can use this information to help the user with their strategy.
        
        To query the database, simply respond with the string 'query', the property that you want to query for, and finally the value that you want to query for. 
        You can query any property in the database found in the example above for Bulbasaur. The query response will look like ```query, category, value```. 
        Your queries MUST be formatted as ```query, category, value```. You can only perform one query at a time. 

        If you are going to mention or suggest a Pokémon, you MUST make sure that Pokémon exists via a query. 
        If it does not, you will get a response that looks like the following:

        {qdb.filter_single_property(self.pokemon_collection, 'name', 'Thunder Butt')}

        If you get a query response that matches the above one, you should respond with another query to find a Pokémon that does exist.

        IMPORTANT NOTE: Queries MUST be formatted as 'query, category, value'. If you want to query the database, 
        you MUST format your query as such and it should be the ONLY item in your response. For example, if you 
        want to query for an electric type Pokémon, you would respond with ONLY the text 'query, type1, Electric'.
        VALID PROPERTIES: number, name, type1, type2, total, attack, defense, sp_attack, sp_defense, speed, weight, ability1, ability2, ability_ha, possible_moves

        You can only perform a query on one of the above VALID PROPERTIES.

        You have already been given information on {self.interest_pokemon.objects[0].properties.get('name')}, so you should just use past chat context to refer back to that information.
        """

        self.chatbot_context.append({'role': 'system', 'content': chatbot_context_individual_builder_start})
        response = main_bot.get_llm_response(self.openai_client, self.chatbot_context, temperature=0).choices[0].message.content

        prompt = 'None'

        while prompt != '':
            response, query = main_bot.trim_query_from_response(response)

            # Special cases when talking to the bot
            if query:
                response = main_bot.bot_query(query, self.pokemon_collection, self.chatbot_context, self.openai_client)
            if response.startswith('query'):
                response = main_bot.bot_query(response, self.pokemon_collection, self.chatbot_context, self.openai_client)

            print(f"\nBot with the World Champ Difference> {response}")

            response, prompt = main_bot.collect_messages(self.openai_client, self.chatbot_context)