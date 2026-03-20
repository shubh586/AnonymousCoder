from json import load


def load_json(settings_path:str="user_space/settings.json"):
    with open(settings_path,"r")  as f:
        user_settings=load(f)
    return user_settings