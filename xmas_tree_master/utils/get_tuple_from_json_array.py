import json

def get_tuple_from_json_array(x):
    if x is not None:
        return tuple(json.loads(x))