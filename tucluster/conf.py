'''Get the tucluster configuration.

The default configuration is suitable for development and may
be overriden by specifying an environment variable - ``TUCLUSTER_CONFIG``
which points to a JSON file.
'''
import json
import os


__DEFAULTS = {
    "MONGODB": {
        "db": "tucluster",
        "host": "127.0.0.1",
        "port": 27017
    },
    "MODEL_DATA_DIR": os.path.join(os.path.dirname(__file__), 'data'),
    "TUFLOW_PATH": "tuflow",
    "ANUGA_ENV": "anuga"
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
