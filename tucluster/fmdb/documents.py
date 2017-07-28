# -*- coding: utf-8 -*-

'''
    fmdb - flood meta database
    Copyright (C) 2017  James Ramm

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import datetime
import os

from mongoengine import (
    Document,
    StringField,
    ListField,
    DateTimeField,
    BooleanField,
    ReferenceField,
    PolygonField,
    EmailField,
    DoesNotExist,
    CASCADE
)
from tucluster.fmdb.serializers import id_from_path, path_from_id

class Model(Document):
    '''
    Meta data about a task given to tuflow
    '''
    name = StringField(required=True, unique=True)
    email = EmailField()
    description = StringField()
    date_created = DateTimeField(default=datetime.datetime.now)
    folder = StringField()
    control_files = ListField(StringField())
    tuflow_exe = StringField()

    meta = {
        'indexes': [
            'date_created'
        ],
        'strict': False
    }

    def clean(self):
        if self.folder:
            # Gather all the files which have been uploaded to provide
            # record of initial state of the model folder
            fnames = [
                name for name in os.listdir(self.folder) if name.endswith('.tcf')
            ]

            # Ensure folder is a base64 id rather than a path
            self.folder = id_from_path(self.folder)
            self.control_files = fnames

    def resolve_folder(self):
        return path_from_id(self.folder)


class ModelRun(Document):

    control_file = StringField(required=True)
    time_started = DateTimeField()
    task_id = StringField()
    # Is this run the baseline/reference model?
    is_baseline = BooleanField()
    # The model area is defined by the GIS file referred to in the
    # control file for this run
    # 'Read GIS Location' is the command
    model_area = PolygonField()
    model = ReferenceField(Model, reverse_delete_rule=CASCADE)

    meta = {
        'strict': False
    }
