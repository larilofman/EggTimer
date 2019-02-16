import json


def save_setting(json_entry):

    with open('settings.json') as f:
        data = json.load(f)

    with open('settings.json', 'w') as f:
        data.update(json_entry)
        json.dump(data, f, indent=2)


def load_setting(json_key):
    try:
        with open('settings.json') as f:
            data = json.load(f)
            return data[json_key]
    except:
        return 1


def load_settings():

    with open('settings.json') as f:
        data = json.load(f)
        return data
