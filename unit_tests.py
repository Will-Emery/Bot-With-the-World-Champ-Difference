
#################### bot.py ####################
import bot as bot

def test_trim_query_from_response():
    '''Function for testing the trim_query_from_response function in bot.py'''
    response = 'This is some body text from the LLM ``` query, property, value ```'
    response2, query = bot.trim_query_from_response(response)
    print(response2)
    print(query)
    assert bot.trim_query_from_response(response) ==  ('This is some body text from the LLM', ' query, property, value ')

def test_create_current_metadata():
    '''Function for testing the create_current_metadata function in bot.py'''
    print("here")
    metadata = bot.create_metagame_context_string()
    print(metadata)
    assert bot.create_metagame_context_string() == metadata


if __name__ == '__main__':
    test_trim_query_from_response()
    test_create_current_metadata()
