import json

def parse_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        items = []
        for item_key, item_value in data[0]['Rows'].items():
            # Extract the item name after 'ITEM_NAME_'
            item_name = item_key.split('_', 2)[-1]  # Adjusted to correctly split the string
            description = item_value['TextData']['SourceString']
            items.append((item_name, description))
        return items
