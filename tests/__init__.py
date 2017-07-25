# -*- coding: utf-8 -*-

"""Unit test package for tucluster."""
import os
from tucluster.conf import settings

# Before importing the tucluster app we must override the settings
# for testing
settings['MODEL_DATA_DIR'] = os.path.join(os.path.dirname(__file__), 'data')
settings['MONGODB'] = {
    "db": "mongoenginetest",
    "host": "mongomock://localhost"
}