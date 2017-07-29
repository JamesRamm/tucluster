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
    CASCADE
)
from tucluster.fmdb.serializers import id_from_path, path_from_id

class Model(Document):
    '''Metadata for a single Model.

    Conceptually a model is a region or project which has a set of
    input data files relating to that project. It may have
    have multiple individual flood models (ModelRuns), but typically
    would designate a single of these runs as the definitive or baseline
    flood model.
    '''
    name = StringField(required=True, unique=True, help_text='Name of the model')
    email = EmailField(help_text='Email of a person who is responsible for this model')
    description = StringField(help_text="Optional, short description of the model")
    date_created = DateTimeField(default=datetime.datetime.now)
    folder = StringField(help_text="Path to folder containing model data")
    entry_points = ListField(
        StringField(),
        help_text=(
            'List of entry points for the model.'
            ' These may be tuflow control files or anuga python scripts')
    )

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
                name for name in os.listdir(self.folder) if name.endswith(('.tcf', '.py'))
            ]
            self.entry_points = fnames
            # Ensure folder is a base64 id rather than a path
            self.folder = id_from_path(self.folder)


    def resolve_folder(self):
        return path_from_id(self.folder)

ENGINES = (
    ('tuflow', 'Tuflow'),
    ('anuga', 'Anuga'),
)

class ModelRun(Document):

    entry_point = StringField(
        required=True,
        help_text="File to be used as the entry point for Anuga/Tuflow"
    )
    time_started = DateTimeField()
    task_id = StringField()

    engine = StringField(
        max_length=6,
        choices=ENGINES,
        help_text="The flood modelling engine used for this run",
        required=True
    )

    # Is this run the baseline/reference model?
    is_baseline = BooleanField(help_text="If true, designates this run as the baseline model")
    # The model area is defined by the GIS file referred to in the
    # control file for this run
    # 'Read GIS Location' is the command
    model_area = PolygonField()
    model = ReferenceField(Model, reverse_delete_rule=CASCADE)

    meta = {
        'strict': False
    }
