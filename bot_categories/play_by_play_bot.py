import os
import openai
import preload_database as pdb
import query_database as qdb

import bot as main_bot

class PlayByPlayBot():
    def __init__(self, openai_client, collection, chatbot_context=[]):
        self.openai_client = openai_client
        self.pokemon_collection = collection
        self.chatbot_context = chatbot_context
        self.player_team = []
        self.opponent_team = []

    def get_pokemon_pokepaste(self, player='user'):
        """This function will prompt the user to input pokemon on either their team or their opponent's team
        in the form of a PokePaste. The PokePaste will be split into a list of pokemon that can be used for analysis.

        This is what a PokePaste looks like:
        ```
        Cinderace @ Heavy-Duty Boots
        Ability: Libero
        EVs: 252 Atk / 4 SpD / 252 Spe
        Jolly Nature
        - Pyro Ball
        - High Jump Kick
        - U-turn
        - Gunk Shot

        Dragapult @ Choice Specs
        Ability: Infiltrator
        EVs: 252 SpA / 4 SpD / 252 Spe
        Timid Nature
        - Draco Meteor
        - Fire Blast
        - Thunderbolt
        - Shadow Ball
        ```
        
        Returns:
            team -- list: a list of the pokemon that can be given to the bot for analysis"""
        
        if player == 'user':
            print("Please supply a PokePaste of the pokemon that you currently have on your team.")
        else:
            print("Please supply a PokePaste of the pokemon that your opponent currently has on their team.")

        print('Enter your PokePaste (end with "END OF TEAM"):')

        user_input_team = []
        while True:
            line = input()
            if line.strip() == "END OF TEAM":
                break
            user_input_team.append(line)

        user_input_team = "\n".join(user_input_team)
        team = user_input_team.split('\n\n')

        return team


    def get_low_information(self, player='opponent'):
        """This function retrieves the names of pokemon one by one.

        Args:
            player -- str: the player that the pokemon belong to, either 'user' or 'opponent'

        Returns:
            team -- list: a list of the 6 pokemon names provided by the user
        """

        team = []
        message = ("Please supply the names of the pokemon that you currently have on your team."
                    if player == 'user' else
                    "Please supply the names of the pokemon that your opponent currently has on their team.")
        print(message)
        print("Enter one Pokemon name at a time. Press 'Enter' when finished.")

        while len(team) < 6:
            name = input("Enter Pokemon name: ")
            # Check if name is empty before database query
            if name:
                db_query = qdb.filter_single_property(self.pokemon_collection, 'name', name)
                if db_query.objects.count == 0:
                    print(f"{name} is not a valid Pokemon name.")
                else:
                    team.append(name)
            else:
                print("Please enter a Pokemon name.")

        print("Thank you for providing the team information.")
        return team
    
    def generate_format_context_string(self, battle_format):
        if battle_format == 'singles':
            return f"""The user is playing in the Singles format. In this format, each player sends out one Pokémon at a time.
            the user can bring up to 6 Pokémon to the battle, but only 3 can be used in the battle. The battle ends when all of one player's Pokémon faint."""
        
        else:
            return f"""The user is playing in the Doubles format. In this format, each player sends out two Pokémon at a time. The user can bring up to 6 Pokémon to the battle, 
            but only 4 can be used in the battle. The battle ends when all of one player's Pokémon faint."""
        
    def generate_team_sheet_format_context_string(self, sheet_format):
        if sheet_format == 'open':
            return f"""The user is using an open team sheet. This means that the user can see the opponent's team before the battle begins. 
            This allows the user to make more informed decisions about their team composition and strategy."""
        
        else:
            return f"""The user is using a closed team sheet. This means that the user cannot see the opponent's team before the battle begins. 
            This requires the user to make more general decisions about their team composition and strategy. Because of this your input will 
            need to make more general assumptions about the opponent's team. Some useful information about the current metagame will be provided to help with this."""

        
    
    def PlayByPlayBot(self):
        """This is the main function that will start the conversation with the user and prompt them to input 
        the pokemon that they currently have on their team. The next step will be to prompt the user for what 
        format they are  playing in and what their opponent's team is. This will allow the bot to provide a
        play-by-play analysis of the battle, with assistance for the user"""

        format = input("Please enter the format that you are playing in. Currently supported formats are Singles and Doubles: ")

        while format.lower() not in ['singles', 'doubles']:
            print("Please enter a valid format.")
            format = input("Please enter the format that you are playing in. Currently supported formats are Singles and Doubles: ")
        
        sheet_format = input("Please enter the format of the teamsheet that you are using. Currently supported formats are Open and Closed: ")

        while sheet_format.lower() not in ['open', 'closed']:
            print("Please enter a valid format.")
            sheet_format = input("Please enter the format of the teamsheet that you are using. Currently supported formats are Open and Closed: ")

        
        opponent_team_information = " "
        if sheet_format.lower() == 'open':
            self.player_team = self.get_pokemon_pokepaste('user')
            self.opponent_team = self.get_pokemon_pokepaste('opponent')
        else:
            self.player_team = self.get_pokemon_pokepaste('user')
            self.opponent_team = self.get_low_information('opponent')

            opponent_team_information_list = []
            for pokemon in self.opponent_team:
                db_query = qdb.filter_single_property(self.pokemon_collection, 'name', pokemon)
                opponent_team_information_list.append(db_query)
            
            opponent_team_information = f"""The opponent's team consists of the above pokemon. Below  you can find more, unspecific information
             because the format is closed team sheet. You should use this infomation and the metagame information in order to inform
              how you help the user through their match. :::{opponent_team_information_list}:::"""
            

        print(f"\nYour team: {self.player_team}")
        print(f"Opponent's team: {self.opponent_team}")

        meta_information = main_bot.create_metagame_context_string()

        chatbot_context_play_by_play_start = f"""The user has chosen to focus on a play-by-play analysis of the battle.
        {self.generate_format_context_string(format)} {self.generate_team_sheet_format_context_string(sheet_format)}

        Here is some general information about the current metagame to inform the input you provide the user with. 
        This information is delimitated with --- on either side of the information.
        ---{meta_information}---

        Here is the user's team deliminated by ::: on either side of the team.
        :::{self.player_team}:::

        Here is the opponent's team deliminated by ::: on either side of the team.   
        :::{self.opponent_team}:::

        {opponent_team_information}

        Here are some steps that you should follow to provide a play-by-play analysis of the battle:
        1. Suggest a lead/leads for the user based on the opponent team.
        2. From here the user will provide you with information turn by turn about what is happening in the battle. 
        3. Based on this information you should provide the user with the best course of action for the next turn. 
            This can include switching or choosing a move from their active pokemon.
            3a. You should justtify your decisions based on the information provided and the general metagame information. 
            This justification should include some sort of prediction about what the opponent will do.
        4. Repeat steps 2 and 3 until the battle is over.
        """

        self.chatbot_context.append({'role': 'system', 'content': chatbot_context_play_by_play_start})
        response = main_bot.get_llm_response(self.openai_client, self.chatbot_context, temperature=0).choices[0].message.content

        prompt = 'None'


        while prompt != '':
            print(f"\nBot with the World Champ Difference> {response}")

            response, prompt = main_bot.collect_messages(self.openai_client, self.chatbot_context)