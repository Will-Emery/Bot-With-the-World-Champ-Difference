import os
import openai
import preload_database as pdb
import query_database as qdb
import animations as ani

import bot as main_bot

class TeamBuilderBot:
    def __init__(self, openai_client, collection, chatbot_context=None):
        self.openai_client = openai_client
        self.pokemon_collection = collection
        self.team = []
        self.chatbot_context = chatbot_context


    def get_pokemon_list(self):
        print("Please supply up to 6 Pokemon that you would like to use on your team. If you do not have a full team, I can provide suggestions for the remaining Pokemon.")
        
        pokemon_list = []
        
        user_input_pokemon = input(f"(If you are done, just press [Enter]). Please enter Pokemon {len(pokemon_list) + 1}: ")

        while (len(pokemon_list) < 6) and user_input_pokemon != '':
            response = qdb.filter_single_property(self.pokemon_collection, 'name', user_input_pokemon)

            try:
                response_name = response.objects[0].properties.get('name')
            except IndexError:
                response_name = None

            while response_name != user_input_pokemon or response_name is None:
                print(f'{user_input_pokemon} is not in the database. Please enter a valid Pokemon. (Your spelling may be off)')
                user_input_pokemon = input(f"Please enter Pokemon {len(pokemon_list) + 1}: ")

                response = qdb.filter_single_property(self.pokemon_collection, 'name', user_input_pokemon)

                try:
                    response_name = response.objects[0].properties.get('name')
                except IndexError:
                    response_name = None

            pokemon_list.append(response)
            user_input_pokemon = input(f"Press [Enter] if you are done. Otherwise enter Pokemon {len(pokemon_list) + 1}:")

        pokemon_string = ', '.join([pokemon.objects[0].properties.get('name') for pokemon in pokemon_list])
        print(f'You have entered: {pokemon_string}')

        return pokemon_list
    

    def bot_query(self, query_from_bot):
        """This function will query the database for the bot. It will return the result of the query to the bot.
        The bot will then use this information to make a suggestion to the user.
        
        Args:
            query_from_bot -- str: the query from the bot
            
        Returns:
            query_result -- str: the result of the query to the bot"""
        
        query_response = query_from_bot.split(',')
        query_response.pop(0)
        query_response = [x.strip() for x in query_response]

        query_result = qdb.filter_single_property(self.pokemon_collection, query_response[0], query_response[1])

        query_context = f"""Here is the result from your Query: 
        '''
        {query_result}
        '''
        
        Please synthesize this information to help the user build a team.
        Include details about why you think this would be a good fit for the user's team."""

        self.chatbot_context.append({'role': 'system', 'content': query_context})

        return main_bot.get_llm_response(self.openai_client, self.chatbot_context, temperature=0).choices[0].message.content
    

    def add_pokemon_to_team(self, bot_add_command):
        if len(self.team) >= 6:
            print("You already have a full team. You cannot add any more Pokemon.")
            return
        
        add_command = bot_add_command.split(',')
        add_command.pop(0)
        add_command = [x.strip() for x in add_command]

        query_response = qdb.filter_single_property(self.pokemon_collection, 'name', add_command[0])
        query_response_name = query_response.objects[0].properties.get('name')

        self.team.append(query_response)
        print(f'You have added {query_response_name} to the team.')

        if (len(self.team) < 6):
            add_chatbot_context = f"""The user has added {query_response_name} to their team. They now have {len(self.team)} Pokemon on their team.
            Their team is now {self.team}. Looking at this team, help the user pick the next Pokemon to add to their team."""
            self.chatbot_context.append({'role': 'system', 'content': add_chatbot_context})

            return main_bot.get_llm_response(self.openai_client, self.chatbot_context, temperature=0).choices[0].message.content

        else:
            self.add_chatbot_context = f"""The user has added {query_response_name} to their team. They now have a full team. Their team is now :::{self.team}:::.
            Please provide suggestions for improvements to the team."""
            self.chatbot_context.append({'role': 'system', 'content': add_chatbot_context})

            return main_bot.get_llm_response(self.openai_client, self.chatbot_context, temperature=0).choices[0].message.content
        

    def team_builder_bot(self):
        self.team = self.get_pokemon_list()

        if len(self.team) < 6:
            team_length_context_string = f"The user has not provided a full team. You will need to provide suggestions for the {6 - len(self.team)} remaining Pokemon."
        else:
            team_length_context_string = "The user has provided a full team, your job is to point out potential flaws with the team and suggest improvements."

        chatbot_context_team_builder_start = f"""The user has chosen to focus on building a whole team. For this, you need to focus on building a well-rounded team.
            To start with, the user will provide you with a list of up to 6 Pokemon they are interested in using. The list of Pokemon will be delimited by ::: and will be 
            in the following format. Here is the example for Bulbasaur: 

            {qdb.filter_single_property(self.pokemon_collection, 'name', 'Bulbasaur')}

            If the list is not a full 6 Pokemon, you will need to provide suggestions for the remaining Pokemon. You will need to provide the user with a well-rounded team that can handle a variety of threats. 
            To help with this, you have access to a database of Pokemon, their moves, and abilities. You can use this information to help the user build a team that can handle a variety of threats. You should only
            provide one suggestion at a time. 

            If the user likes your suggestion, they will tell you so. If you get a response to a recommendation that indicates they want you to add it to their team, 
            you will need to respond with ONLY the string ```add, pokemon_name```. This will add the Pokemon to the team. If the user does not like your suggestion, you will need to provide another suggestion.

            To query the database, simply respond with the string 'query', the property that you want to query for, and finally the value that you want to query for. 
            You can query any property in the database found in the example above for Bulbasaur. The query response will look like ```query, category, value```. 
            Your queries MUST be formatted as ```query, category, value```. You can only perform one query at a time. If you are going to make a 
            suggestion about adding a Pokemon to the team, you MUST make sure that Pokemon exists via a query. 
            If it does not, you will get a response that looks like the following:

            {qdb.filter_single_property(self.pokemon_collection, 'name', 'Thunder Butt')}

            If you get a query response that matches the above one, you should respond with another query to find a Pokemon that does exist.

            {team_length_context_string}
            User Input Team: :::{self.team}:::

            IMPORTANT NOTE: You should not recomend a Pokemon that is already on the user's team.
            IMPORTANT NOTE: queries MUST be formatted as 'query, category, value'. If you want to query the database, 
            you MUST format your query as such and it should be the ONLY item in your response. For example, if you 
            want to query for an electric type Pokemon, you would respond with ONLY the text 'query, type1, Electric'.
            IMPORTANT NOTE: If you are going to add a Pokemon to the team, you MUST format your response as 'add, pokemon_name'.
            You MUST format it as such and it should be the ONLY thing in your response.

            Finally, here is some information about the current metagame to inform the input you provide the user with.
            This information is delimitated with --- on either side of the information.
            ---{main_bot.create_metagame_context_string()}---
        """
                
        self.chatbot_context.append({'role': 'system', 'content': chatbot_context_team_builder_start})

        response = main_bot.get_llm_response(self.openai_client, self.chatbot_context, temperature=0).choices[0].message.content
        print(f"Bot with the World Champ Difference> {response}")

        prompt = 'None'
        i = 0

        while prompt != '':
            response, query = main_bot.trim_query_from_response(response)

            # Special cases when talking to the bot
            if query:
                response = self.bot_query(query)
            if response.startswith('query'):
                response = self.bot_query(response)
            if response.startswith('add'):
                response = self.add_pokemon_to_team(response)

            if i != 0:
                print(f"Bot with the World Champ Difference> {response}")

            response, prompt = main_bot.collect_messages(self.openai_client, self.chatbot_context)

            i = i + 1
