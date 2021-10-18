import serial
import time
from ..util.color import color

"""
     0, conexão ok
    -1, porta ocupada
    -2, conexão inexistente
    -3, conexão perdida durante a comunicação

"""



class new_connection(object):
    def __init__(self, name, port, baudrate, **codes):
        self.name = name
        self.port = port
        self.baudrate = baudrate
        self.code = -1
        self.serial = None

        self.codes = {
            0: ["conexão ok.", 'S'],
            -1: [f"porta [{self.port}] está ocupada!",'W'],
            -2: ["conexão inexistente!", 'E'],
            -3: ["conexão perdida durante a comunicação!", 'W'],
        }
        
        self.open(self.port, self.baudrate, 3)


    def open(self, port, baudrate, timeout):
        print(color(f"{self.name} está conectando...", 'I'))
        try:
            self.serial = serial.Serial(port, baudrate, timeout=timeout)
        except serial.serialutil.SerialException as exp:
            if "FileNotFoundError" in str(exp):
                self.code = -2
            elif 'Acesso negado.' in str(exp):
                self.code = -1
        else:
            print(color(f"{self.name} está confirmando a conexão...", 'I'))
            t0 = time.monotonic() + timeout
            while time.monotonic() < t0 and not self.isAlive():
                pass
            self.code = 0
        self.codePrint(self.code)
    def isAlive(self):
        try:
            return self.serial.isOpen()
        except AttributeError:
            return False

    def codePrint(self,code):
        print(color(self.name+" >> "+self.codes[code][0],self.codes[code][1]))

    def statusCode(self):
        return self.code

    def close(self):
        self.serial.close()

    def clear(self):
        self.serial.flush()
        self.serial.flushInput()
        self.serial.flushOutput()

    def send(self, command, **kargs):
        # Verifica se é possivel enviar dados através da conexão informada.
        if self.isAlive():

            self.clear()

            # Verifica se é um unico comando
            if isinstance(command, str):
                self.serial.write(
                    str(command + '{0}'.format('\n')).encode('ascii'))
            # Verifica se é uma lista de comandos
            if isinstance(command, list):
                for linha in command:
                    self.serial.write(
                        str(linha + '{0}'.format('\n')).encode('ascii'))

            # Verifica se é uma lista de comandos do tipo "dicionário".
            if isinstance(command, dict):
                for linha in command:
                    self.serial.write(
                        str(command[linha] + '{0}'.format('\n')).encode('ascii'))

            strr = []

            # Lê, decodifica e processa enquanto houver informação no buffer de entrada.
            while True:
                b = self.serial.readline()
                string_n = b.decode()
                strr.append(string_n.rstrip())

                if b == b'':
                    print("b:", b, type(b))
                    print("string_n:", string_n, type(string_n))
                    print("string_n.rstrip():", string_n.rstrip(),
                          type(string_n.rstrip()))
                    break

                if self.serial.inWaiting() == 0:
                    break

            if b == b'' or b == None or b is None:
                self.code = -3
                self.close()

            # Limpa o buffer.
            self.clear()

            # Se requisitado, retorna aquilo que foi recebido após o envio dos comandos.
            if kargs.get('echo'):
                return strr

            return True
        # Avisa que o comando não pode ser enviado, pois a conexão não existe.
        else:
            return False
        #     return ["Comando não enviado, falha na conexão com a serial."]

# if __name__ == '__main__':
#     ardu = new_connection("nome", "com4", 9600)