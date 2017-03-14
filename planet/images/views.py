# -*- coding: utf-8 -*-

import os
from flask import send_from_directory
from planet.extensions import storage
from planet.images import image_view

rule = os.path.join('/', storage.base_dir, '<path:path>')

@image_view.route(rule, methods=['GET'])
def show(path):
    return send_from_directory(
        os.path.join(storage.base_path, storage.base_dir), path)
