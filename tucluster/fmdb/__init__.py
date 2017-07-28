# -*- coding: utf-8 -*-

"""Top-level package for fmdb."""

__author__ = """James Ramm"""
__email__ = 'jamessramm@gmail.com'
__version__ = '0.1.0'

from mongoengine import connect as conn
from tucluster.fmdb.documents import Model, ModelRun, User
from tucluster.fmdb import serializers
from tucluster.fmdb.serializers import path_from_id, id_from_path

def connect(**kwargs):
    '''Encapsulates connecting to the configured mongodb instance
    '''
    return conn(**kwargs)
