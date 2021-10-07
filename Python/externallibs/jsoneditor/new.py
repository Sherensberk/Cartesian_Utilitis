# pylint: disable=no-member

import json as js
import os
from pathlib import Path

class json(object):
    def __init__(self, path, name, script_dir, **args):
        self.name = name+".json"
        self.dir = os.path.join(script_dir, path)
        self.data = args.get("data")
        self.this = self.open(self.dir) if not self.data else self.data

    def self(self):
        return self.this

    def add(self, key, value):
        self.this[key] = value

    def pop(self, key):
        self.this.pop(key, None)
        
    # Abre e lê um json no caminho solicitado.
    def open(self, path):
        if isinstance(path, str):
            with open(f"{path}", 'r', encoding='utf8') as json_file:
                return js.load(json_file)
        elif isinstance(path, dict):
            return path


    # Abre e grava um json no caminho solicitado.
    def save(self, **args):
        json_data = args.get("data")
        if json_data:
            self.this  = json_data
        with open(f"{self.dir}", "w", encoding='utf8') as jsonFile:
            js.dump(self.this, jsonFile, indent=4, ensure_ascii=False)