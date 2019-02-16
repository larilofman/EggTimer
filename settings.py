import json


def save_settings(json_entry):

    with open('settings.json') as f:
        data = json.load(f)

    with open('settings.json', 'w') as f:
        data.update(json_entry)
        json.dump(data, f, indent=2)


def load_settings(json_key):
    with open('settings.json') as f:
        data = json.load(f)
        return data[json_key]
