import os
import json
import base64

def id_from_path(path):
    ''' Converts a filepath string to a URL safe encoding
    '''
    return base64.urlsafe_b64encode(path.encode('utf-8')).decode('utf-8')

def path_from_id(path_id):
    ''' Decode a filepath from its URL safe base64 representation
    '''
    return base64.urlsafe_b64decode(path_id).decode('utf-8')


def directory_tree_serializer(path):
    '''Output a directory tree as a json representation

    Args:

        fid (str): base64 encoding of root directory path (see ``path_from_id``)

    Returns:
        str: JSON representation of the directory tree. Each object has the following attributes:
            'type': file or folder
            'name': The base name of the file/folder
            'path': Absolute path to the object.
            'id': The URL-safe base64 encoding of the ``path``

            If 'type' is 'folder', then a 'children' attribute is also present. This is a list
            containing all sub-folders/files
    '''
    hierarchy = {
        'type': 'folder',
        'name': os.path.basename(path),
        'path': path,
        'id': id_from_path(path)
    }
    try:
        hierarchy['children'] = [
            directory_tree_serializer(os.path.join(path, contents))
            for contents in os.listdir(path)
        ]
    except NotADirectoryError:
        hierarchy['type'] = 'file'
    return json.dumps(hierarchy)
