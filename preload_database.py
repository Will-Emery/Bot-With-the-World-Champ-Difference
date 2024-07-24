'''
Module: preload_database.py

This file contains functions for creating a Weaviate client, creating a collection, and adding data to the collection.
'''

import json
import os
import weaviate
import weaviate.classes as wvc


def create_client(weaviate_version="1.24.10") -> weaviate.WeaviateClient:
    open_ai_key = os.getenv("OPENAI_API_KEY")
    
    os.environ["LOG_LEVEL"] = "error"
    
    client = weaviate.connect_to_embedded(
        version=weaviate_version,
        headers={"X-OpenAI-Api-Key": open_ai_key}
    ) 

    print('\nWeaviate client created.\n')

    return client


def drop_collections(client: weaviate.WeaviateClient, collection_name: str):
    """
    Function whose only purpose is to kill previous collections
    """
    
    if client.collections.exists(collection_name):
        client.collections.delete(collection_name)
        print('\nOld collection dropped.\n')
    
    return None


def create_collection(client: weaviate.Client, 
                      collection_name: str,
                      embedding_model: str = 'text-embedding-3-small',
                      model_dimensions: int = 512):
    """
    Create a collection in Weaviate with a schema based on the provided JSON object.
    {
        "Number": "0001",
        "Name": "Bulbasaur",
        "Type1": "Grass",
        "Type2": "Poison",
        "Total": "318",
        "Attack": "45",
        "Defense": "49",
        "SP Attack": "49",
        "SP Defense": "65",
        "Speed": "65",
        "Weight": "6.9\u00a0kg (15.2\u00a0lbs)",
        "Ability1": "Overgrow",
        "Ability2": "",
        "AbilityHA": "Chlorophyll",
        "Possible Moves": "Acid Spray, Body Slam, Bullet Seed, Charm, Curse, Double-Edge, Endure, Energy Ball, Facade, False Swipe, Giga Drain, Grass Knot, Grass Pledge, Grassy Glide, Grassy Terrain, Growl, Growth, Helping Hand, Ingrain, Knock Off, Leaf Storm, Leech Seed, Magical Leaf, Petal Dance, Poison Powder, Power Whip, Protect, Razor Leaf, Rest, Seed Bomb, Sleep Powder, Sleep Talk, Sludge Bomb, Solar Beam, Substitute, Sunny Day, Sweet Scent, Swords Dance, Synthesis, Tackle, Take Down, Tera Blast, Toxic, Trailblaze, Venoshock, Vine Whip, Weather Ball, Worry Seed"
    },  

    """
    try:
        collection = client.collections.create(
            name=collection_name,
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(
                model=embedding_model,
                dimensions=model_dimensions
            ),
            properties=[wvc.config.Property(name="number",data_type=wvc.config.DataType.INT),
                        wvc.config.Property(name="name",data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="type1",data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="type2",data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="total",data_type=wvc.config.DataType.INT),
                        wvc.config.Property(name="attack",data_type=wvc.config.DataType.INT),
                        wvc.config.Property(name="defense",data_type=wvc.config.DataType.INT),
                        wvc.config.Property(name="sp_attack",data_type=wvc.config.DataType.INT),
                        wvc.config.Property(name="sp_defense",data_type=wvc.config.DataType.INT),
                        wvc.config.Property(name="speed",data_type=wvc.config.DataType.INT),
                        wvc.config.Property(name="weight",data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="ability1",data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="ability2",data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="ability_ha",data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="possible_moves",data_type=wvc.config.DataType.TEXT)
            ]
        )
        # print(f"\nCollection '{collection_name}' created.\n")
        return collection
    
    except Exception as e:
        print(f"Error creating collection: {e}")
        return None


def add_data_to_collection(collection: weaviate.Collection, 
                           data: dict):
    try:
        for item in data:
            try:
                collection.data.insert({
                    "number": int(item["Number"]),
                    "name": item["Name"],
                    "type1": item["Type1"],
                    "type2": item["Type2"],
                    "total": item["Total"],
                    "attack": int(item["Attack"]),
                    "defense": int(item["Defense"]),
                    "sp_attack": int(item["SP Attack"]),
                    "sp_defense": int(item["SP Defense"]),
                    "speed": int(item["Speed"]),
                    "weight": item["Weight"],
                    "ability1": item["Ability1"],
                    "ability2": item["Ability2"],
                    "ability_ha": item["AbilityHA"],
                    "possible_moves": item["Possible Moves"]
                })
                print(f"Added item {item['Name']} to collection.")
            except weaviate.UnexpectedStatusCodeException as e:
                print(f"Failed to add item to collection: {e}")

    except FileNotFoundError:
        print("Data file not found.")


def collection_exists(client, collection_name):
    """
    Check if a collection exists in Weaviate
    """
    return client.collections.exists(collection_name)



def main():
    """Main function used for testing"""
    
    try:
        client = create_client()
        collection_name = 'pokemon_collection'

        drop_collections(client, collection_name)

        print('DEBUG: going to create collection')
        collection = create_collection(client, collection_name)
        print('DEBUG: collection created')

        file_path = "data_collection/pokemon_data.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
            add_data_to_collection(collection, data)
    
    except Exception as error:
        print(error)

    finally:
        client.close()
        print("\nWeaviate client closed cleanly.\n")


if __name__ == "__main__":
    main()
