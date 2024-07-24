"""Module: file_conversion.py

This file contains functions for converting files to different formats."""

import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    data = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            # Convert specific fields to integers
            row['Number'] = int(row['Number'])
            row['Total'] = int(row['Total'])
            row['Attack'] = int(row['Attack'])
            row['Defense'] = int(row['Defense'])
            row['SP Attack'] = int(row['SP Attack'])
            row['SP Defense'] = int(row['SP Defense'])
            row['Speed'] = int(row['Speed'])
            
            
            # Convert empty strings to None for optional fields
            row['Type2'] = row['Type2'] if row['Type2'] else None
            row['Ability2'] = row['Ability2'] if row['Ability2'] else None
            row['AbilityHA'] = row['AbilityHA'] if row['AbilityHA'] else None
            
            data.append(row)
    
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)



if __name__ == '__main__':
    csv_file_path = 'pokemon_data.csv'
    json_file_path = 'pokemon_data.json'
    csv_to_json(csv_file_path, json_file_path)