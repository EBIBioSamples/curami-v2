import json


class SetEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        return json.JSONEncoder.default(self, o)
