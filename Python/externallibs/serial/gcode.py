
class gcode():
    def __init__(self, serial):
        self.serial = serial

    def M114(self,where=[("X:", " Y:"), ("Y:", " Z:"), ("Z:", " E:"), ("E:", " Count")]):
        if self.serial.isAlive():
            for _ in range(2):
                Echo = (self.serial.send("M114", echo=True))[0]
            try:
                Pos = []
                for get in where:
                    left, right = get[0], get[1]
                    Pos.append(float(Echo[Echo.index(left)+len(left):Echo.index(right)]))
                return dict(zip(['X', 'Y', 'Z', 'E'], Pos))
            except ValueError:
                print("Recebi:", Echo)
                return Echo


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
