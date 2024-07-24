'''
Module: query_database.py
'''
from weaviate.classes.query import Filter
import preload_database as pdb


def filter_single_property(collection, property, property_value):
    '''
    Using a filter, return only one property from the first 10 objects.

    Args:
        collection -- weaviate.Collection: the collection to query
        property -- str: the property to filter on
        property_value -- str: the value to filter on
    
    Returns:
        response -- weaviate.Response: the response from the query
    '''
    response = collection.query.fetch_objects(
        filters = Filter.by_property(property).equal(property_value),
        limit = 10
    )
    
    # print(''.join(['-'] * 100))
    # print('Using a filter, return only one property from the first 3 objects:')
    # print(f'\tby_property: {property} \n\tequal to: {property_value}')

    # for o in response.objects:
        # print(o.properties)

        # print(o.properties.get('name'))

    return response


def filter_search_values_below(collection, property, threshold_value):
    '''
    Using a filter, search for values that are below some specific value.
    '''
    response = collection.query.fetch_objects(
        filters = Filter.by_property(property).less_than(threshold_value),
    )
    
    print(''.join(['-'] * 100))
    print('Using a filter, search for values that are below some specific value:')
    print(f'\tby_property: {property} \n\tless_than: {threshold_value}')

    for o in response.objects:
        print(o.properties)

        # print(o.properties.get('name'))
    
    print()
    return response


def filter_boolean_or(collection, prop1, prop2, value1, value2):
    '''
    Using a filter that uses boolean OR.
    '''
    response = collection.query.fetch_objects(
        filters = Filter.by_property(prop1).equal(value1) |
        Filter.by_property(prop2).less_than(value2)
    )
    
    print(''.join(['-'] * 100))
    print('Using a filter that uses boolean OR:')
    print(f'\tby_property: {prop1} \n\tequal: {value1}')
    print('\t\tOR')
    print(f'\tby_property: {prop2} \n\tless_than: {value2}')

    for o in response.objects:
        print(o.properties)

        print(o.properties.get('name'))


    print()
    return response


def main():
    """
    Main function to run and test the code
    """
    try:
        wv_client = pdb.create_client()

        collection_name = 'pokemon_collection'

        # check to see if the collection already exists
        # Making sure that it is empty before adding data because otherwise it takes a long time to add data
        if (pdb.collection_exists(wv_client, collection_name)):
            print(f"Collection '{collection_name}' already exists.")
            collection = wv_client.collections.get(collection_name)
            
        else:
            print(f"Collection '{collection_name}' does not exist.")

            file_path = 'data_collection/pokemon_data.json'
            pdb.drop_collections(wv_client, collection_name)

            pdb.create_collection(wv_client, collection_name)

            pdb.add_data_to_collection(wv_client, collection_name, file_path)


        print(filter_single_property(collection, 'name', 'Bulbasaur'))
        print(filter_single_property(collection, 'name', 'Glimmora'))
        print(filter_single_property(collection, 'name', 'Thunder Butt'))
        filter_search_values_below(collection, 'total', 500)
        filter_boolean_or(collection,
                          prop1='name', value1='Rayquaza',
                          prop2='total', value2=500)


        
    except Exception as error:
      print(error)
    
    finally:
        wv_client.close()
        print("\nWeaviate client closed cleanly.\n")


if __name__ == "__main__":
    main()