import json
import os


__DEFAULTS = {
    "MONGODB": {
        "db": "tucluster",
        "host": "127.0.0.1",
        "port": 27017
    },
    "TUFLOW_DATA": os.path.join(os.path.dirname(__file__), 'data'),
    "TUFLOW_EXES": {
        'Tuflow Classic': 'tuflow',
    }
}


def __get_config():
    config_path = os.environ.get('TUCLUSTER_CONFIG', None)
    config = __DEFAULTS
    if config_path:
        with open(config_path) as fin:
            user_config = json.load(fin)
        config.update(user_config)
    return config


settings = __get_config()
