# pylint: disable=no-member

import json as js
import os
from pathlib import Path
from datetime import datetime
from numpy import average, around

class new(object):
    def __init__(self, path, name, script_dir, **args):
        self.name = name+".json"
        self.dir = os.path.join(script_dir, path)
        self.data = args.get("data")
        self.value = self.open(self.dir) if not self.data else self.data

    def self(self):
        return self.value

    def add(self, key, value):
        self.value[key] = value

    def pop(self, key):
        self.value.pop(key, None)
        
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
            self.value  = json_data
        with open(f"{self.dir}", "w", encoding='utf8') as jsonFile:
            js.dump(self.value, jsonFile, indent=4, ensure_ascii=False)

class production(object):
    def __init__(self, data_dir, modelo, script_dir, **kwargs):
        
        self.data_path = data_dir
        self.model = modelo
        self.total = new(f"{data_dir}/{modelo}/total.json", "total", script_dir)
        self.info = new(f"{data_dir}/{modelo}/info.json", "info", script_dir) 
        self.times = new(f"{data_dir}/{modelo}/times.json", "times", script_dir) 
        self.today = new(f"{data_dir}/{modelo}/today.json", "today", script_dir) 
        self.week = new(f"{data_dir}/{modelo}/week.json", "week", script_dir)
        self.kwargs = kwargs
    def is_another_day(self):
        return self.info.value["day"] != datetime.now().day

    def add(self, what, qtd, time):
        self.total.value[what] += qtd
        self.total.value["total"] += qtd
        if not self.is_another_day():
            self.today.value[what] += qtd
            self.today.value["total"] += qtd
            self.times.value[what].append(time)
            if what == "rigth":
                if self.today.value["fasttime"] > time:
                    self.today.value["fasttime"] = time
                elif self.today.value["lowertime"] < time:
                    self.today.value["lowertime"] = time
        else:
            self.week.value["week_total"].pop(0)
            self.week.value["week_rigth"].pop(0)
            self.week.value["week_wrong"].pop(0)
            self.week.value["week_total"].append(self.today.value["total"])
            self.week.value["week_rigth"].append(self.today.value["rigth"])
            self.week.value["week_wrong"].append(self.today.value["wrong"])
            self.avaragetimes("wrong")
            self.avaragetimes("rigth")
            self.reset_day(what, qtd, time)
        if self.kwargs.get("autoSave"):
            self.save()

    def avaragetimes(self, what):
        try:
            print(what, self.times.value[what])
            if self.times.value[what] != None:
                self.week.value[f"week_times_{what}"].pop(0)
                self.week.value[f"week_times_{what}"].append(around(average(self.times.value[what])))
            print(what, self.week.value[f"week_times_{what}"])
        except RuntimeWarning:
            pass 

    def reset_day(self, what, qtd, time):
        self.info.value["day"] = datetime.now().day
        self.today.value = {
                        "total": 0,
                        "rigth": 0,
                        "wrong": 0,
                        "fasttime": 0,
                        "lowertime": 0
                    }
        self.today.value[what] = qtd
        self.today.value["total"] = qtd
        self.times.value[what].append(time)

    def remove(self, what, qtd):
        self.total.value[what] -= qtd
        self.today.value[what] -= qtd
        self.total.value["total"] -= qtd
        self.today.value["total"] -= qtd
        self.times.value.pop(len(self.times.value)-1)
        if self.kwargs.get("autoSave"):
            self.save()

    def save(self):
        self.total.save()
        self.info.save()
        self.times.save()
        self.today.save()
        self.week.save()

