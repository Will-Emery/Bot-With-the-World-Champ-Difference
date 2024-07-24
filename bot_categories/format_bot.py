import openai
import preload_database as pdb
import query_database as qdb
import bot as main_bot


class DiscussFormatsBot:
    def __init__(self, openai_client, collection, chatbot_context=[]):
        self.openai_client = openai_client
        self.pokemon_collection = collection
        self.interest_pokemon = None
        self.chatbot_context = chatbot_context

    def doubles_discussion(self):
        chatbot_context_doubles_discussion_start = f"""The user has chosen to focus on having a conversation around doubles battles. 
        You should begin by asking the user if they have any questions about doubles battles or if they would like to learn more about them.

        Throughout this conversation, you have access to a database of Pokémon, their moves, and abilities. You can use this information to help the user with their strategy.

        To query the database, simply respond with the string 'query', the property that you want to query for, and finally the value that you want to query for. 
        You can query any property in the database found in the example below for Bulbasaur. The query response will look like ```query, category, value```. 
        Your queries MUST be formatted as ```query, category, value```. You can only perform one query at a time.

        VALID PROPERTIES: number, name, type1, type2, total, attack, defense, sp_attack, sp_defense, speed, weight, ability1, ability2, ability_ha, possible_moves
        You can only perform a query on one of the above VALID PROPERTIES.

        If you are going to mention or suggest a Pokémon, you MUST make sure that Pokémon exists via a query. 
        If it does not, you will get a response that looks like the following:

        {qdb.filter_single_property(self.pokemon_collection, 'name', 'Thunder Butt')}

        If you get a query response that matches the above one, you should respond with another query to find a Pokémon that does exist.

        Here is an example of how Pokémon data will be provided to you:
        {qdb.filter_single_property(self.pokemon_collection, 'name', 'Bulbasaur')}

        You have already been given information on {self.interest_pokemon.objects[0].properties.get('name')}, so you should just use past chat context to refer back to that information.

        IMPORTANT NOTE: Queries MUST be formatted as 'query, category, value'. If you want to query the database, 
        you MUST format your query as such and it should be the ONLY item in your response. For example, if you 
        want to query for an electric type Pokémon, you would respond with ONLY the text 'query, type1, Electric'.
        VALID PROPERTIES: number, name, type1, type2, total, attack, defense, sp_attack, sp_defense, speed, weight, ability1, ability2, ability_ha, possible_moves

        You can only perform a query on one of the above VALID PROPERTIES.
        """


        self.chatbot_context.append({'role': 'system', 'content': chatbot_context_doubles_discussion_start})
        response = main_bot.get_llm_response(self.openai_client, self.chatbot_context, temperature=0).choices[0].message.content

        prompt = 'None'

        while prompt != '':
            response, query = main_bot.trim_query_from_response(response)

            # Special cases when talking to the bot
            if query:
                print(f"Query: {query}")
                response = main_bot.bot_query(query, self.pokemon_collection, self.chatbot_context, self.openai_client)
            if response.startswith('query'):
                response = main_bot.bot_query(response, self.pokemon_collection, self.chatbot_context, self.openai_client)
            print(f"Bot with the World Champ Difference> {response}")

            response, prompt = main_bot.collect_messages(self.openai_client, self.chatbot_context)            






