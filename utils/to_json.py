import csv
import json

def make_json(csvFilePath, jsonFilePath):
    # create a list to hold the documents
    data = []
    
    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        
        # Convert each row into a dictionary 
        # and add it to data
        for rows in csvReader:
            data.append(rows)

    # Open a json writer, and use the json.dumps() 
    # function to dump data
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))
        
# Driver Code

# Decide the two file paths according to your 
# computer system
csvFilePath = r'covid_dataset_preprocessed.csv'
jsonFilePath = r'cord-19.json'

# Call the make_json function
make_json(csvFilePath, jsonFilePath)
