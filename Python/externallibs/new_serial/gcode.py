import logging.config
from ..util.customException import *

class gcode():
    def __init__(self, serial):
        self.serial = serial

    def M114(self, type='', where=[("X:", " Y:"), ("Y:", " Z:"), ("Z:", " A:"), ("A:", " Count")]):
        if self.serial.isAlive():
            for _ in range(2):
                Echo = (self.serial.send(f"M114 {type}", echo=True))[0]
            try:
                Pos = []
                for get in where:
                    left, right = get[0], get[1]
                    Pos.append(float(Echo[Echo.index(left)+len(left):Echo.index(right)]))
                return dict(zip(['X', 'Y', 'Z', 'A'], Pos))
            except ValueError:
                raise M114unpackFail(self.serial.name, Echo)


    def M119(self, cut=": "):
        if self.serial.isAlive():
            pos=[]
            key=[]
            for _ in range(2):
                Echo = (self.serial.send("M119", echo=True))[1:-1]
            for info in Echo:
                try:
                    pos.append(info[info.index(cut)+len(cut):len(info)])
                    key.append(info[0:info.index(cut)])
                except ValueError:
                    print("ERRO:", info)
            return dict(zip(key, pos))


    def G28(self,axis='E', endStop='filament', status='open',offset=-23, steps=5, speed=50000):
        if self.serial.isAlive():
            self.serial.send("G91")
            while True:
                try:
                    if self.M119()[endStop] != status:
                        self.serial.send(f"G0 E{offset * -1} F{speed}")
                    break
                except KeyError:
                    pass

            while True:
                try:
                    while self.M119()[endStop] == status:
                        self.serial.send(f"G0 {axis}{steps} F{speed}")

                    self.serial.send("G91")
                    self.serial.send(f"G0 E-{10} F{speed}")

                    while self.M119()[endStop] == status:
                        self.serial.send(f"G0 {axis}{1} F{speed}")

                    self.serial.send("G91")
                    self.serial.send(f"G0 E{offset} F{speed}")
                    self.serial.send("G90")
                    break
                except KeyError:
                    pass

                                            
    def M_G0(self, *args, **kargs):
        cords = ""
        for pos in args:
            axis = pos[0].upper()
            pp = pos[1]
            cords+=f"{axis}{pp} "
        self.serial.send(f"G0 {cords}")
        if kargs.get("nonSync"):
            return
        futuro = self.M114()
        real = self.M114('R')
        #while True:
        a = [v for v in futuro.values()]
        b = [v for v in real.values()]
        while not all((a[i] - 0.5 <= b[i] <= a[i] + 0.5) == True for i in range(len(b))):
            real = self.M114('R')
            b = [v for v in real.values()]
            #print(a, b)
            
        real = self.M114('R')
        #print(real, futuro)
        pass

    def callPin(self, name, state, json):
        value = json[name]["command"]+(json[name]["values"].replace("_pin_", str(json[name]["pin"]))).replace("_state_", str(json[name][state]))
        print(value)
        self.serial.send(value)