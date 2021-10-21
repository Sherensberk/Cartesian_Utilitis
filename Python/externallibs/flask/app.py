from threading import Thread

from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO, send
from waitress import serve

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
#from ..camera.device import new_camera as camera
from engineio.payload import Payload
import json
Payload.max_decode_packets = 500

# from time import sleep
# class process(Thread):
#     def __init__(self, *args, **kargs):
#             Thread.__init__(self)

#     def run():
#         print("run")

# def FuncA():
#     for _ in range(10):
#         print('A')
#         sleep(1)

# def FuncB():
#     for _ in range(5):
#         print('B')

# def FuncN(**kargs):
#     for _ in range(kargs.get("range")):
#         print(kargs.get("char"))
#         sleep(kargs.get("time"))



# # t1 = taskProcess(treadMount(args=('a','b',), kargs={"1":0, "2":1, "model":"k"}))

# """
# Recebi nome da função quero executar...

#     t = tread (func, args)
#     parar {
#             if not func.stop()?
#                 run...
#                 para sozinha, como não esta em um loop permanente, não precisa de um stop esterno

#         como requistar stop externo?
#     }

# """
# Processo = {
# }

# def updateProcesso(Nome, status, valor, **kargs):
#     global Processo
#     print(kargs.get("op"), Nome, status, valor)
#     if kargs.get("op") == "edit":
#         Processo[Nome][status] = valor
#     if kargs.get("op") == 'remove':
#         Processo.remove(Nome)
#     if kargs.get("op") == "add":
#         Processo[Nome] = {"st": False, "rn":False, "stp":False, "fn":False}
#     for p in Processo:
#         print(p, Processo[p])
# lk = Lock()

# import string
# from random import choice
# def randomString(tamanho=20, pattern=''):
#     valores = string.ascii_letters + string.digits
#     word = ''
#     for i in range(tamanho):
#         word += choice(valores)
#     return pattern+word

# def taskInput(lock, nome, status, valor, processo):
#     for _ in range(500):
#         lock.acquire()
#         updateProcesso(nome, status,valor, op=processo)
#         lock.release()

# nomes = [randomString(5) for _ in range(5)]
# for n in nomes:
#     updateProcesso(n, '','',op='add')
# t1 = Thread(target=taskInput, args=(lk, choice(nomes), choice(("st", "rn", "stp", "fn")), choice((False, True, True, True, True)), "edit"))
# t2 = Thread(target=taskInput, args=(lk, choice(nomes), choice(("st", "rn", "stp", "fn")), choice((False, True, True)), "edit"))
# t1.start()
# t2.start()
# t1.join()
# t2.join()
# exit()
# """

# Recebe nome da função que deve acionar,
#     Inicia função função atraves de uma nova thread.
#     Uma segnda thread, monitora os eventos dessa nova, e ajusta o objeto de status deacordo com isso, (background task?).

#     Thread(função, parametros.)

#     ThreadMonitor(monitora, listaStatus)

# """

class Server(object):
    def __init__(self, app_ip, app_port, report_time, **kargs):
        #Thread.__init__(self)
        # self.app = Flask(__name__, static_folder = f"{buildfolder}/static",
        #                         template_folder = buildfolder)

        self.ip = app_ip
        self.port = app_port
        self.report_time = report_time

        self.thread = None
        self.thread_lock = Lock()
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, async_mode=None, async_handlers=True)
        self.functions = kargs.get("functions")
        self.cameras = {}
        self.process = {}

    def start(self):
        self.defineRoutes()
        print("rodando....")
        self.socketio.run(self.app, host=self.ip, port=self.port)
        print("parou!")

    def addCamera(self, nome, valor):
        self.cameras[nome] = valor
    
    def removeCamera(self, nome):
        self.cameras.pop(nome)

    def addFunction(self, name, function):
        self.functions[name] = function

    def removeFunction(self, name):
        self.functions.remove(name)

    def stop(self):
        serve.graceful_shutdown()

    def stopped(self):
        return self._stop_event.is_set()

    def shutdown_server(self):
        self.socketio.stop()
        return "Server stopped"

    def defineRoutes(self):
        app = self.app
        socketio = self.socketio
        def background_thread():
            """Example of how to send server generated events to clients."""
            while True:
                update = {}
                for k, v in self.process.items():
                    update[k] = {"alive": v.is_alive()}
                socketio.sleep(self.report_time)
                socketio.emit('my_response',
                            {'data': json.dumps(update, indent=2, ensure_ascii=False)})


        @app.route('/')
        def index():
            return render_template('index.html', async_mode=socketio.async_mode)


        @socketio.event
        def my_event(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': message['data'], 'count': session['receive_count']})


        @socketio.event
        def my_broadcast_event(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': message['data'], 'count': session['receive_count']},
                broadcast=True)
        
        @socketio.event
        def trigger_this(message):
            print(message)
            function = self.functions[message["command"]]
            thread = Thread(target=function, args=(), kwargs={})
            self.process[message["command"]] = thread
            thread.start()
            
            emit('my_response',
                {'data': "ok", 'count': session['receive_count']})


        @socketio.event
        def join(message):
            join_room(message['room'])
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': 'In rooms: ' + ', '.join(rooms()),
                'count': session['receive_count']})


        @socketio.event
        def leave(message):
            leave_room(message['room'])
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': 'In rooms: ' + ', '.join(rooms()),
                'count': session['receive_count']})


        @socketio.on('close_room')
        def on_close_room(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                                'count': session['receive_count']},
                to=message['room'])
            close_room(message['room'])


        @socketio.event
        def my_room_event(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': message['data'], 'count': session['receive_count']},
                to=message['room'])


        @socketio.event
        def disconnect_request():
            @copy_current_request_context
            def can_disconnect():
                disconnect()

            session['receive_count'] = session.get('receive_count', 0) + 1
            # for this emit we use a callback function
            # when the callback function is invoked we know that the message has been
            # received and it is safe to disconnect
            emit('my_response',
                {'data': 'Disconnected!', 'count': session['receive_count']},
                callback=can_disconnect)


        @socketio.event
        def my_ping():
            emit('my_pong')


        @socketio.event
        def connect():
            global thread
            with self.thread_lock:
                if self.thread is None:
                    thread = socketio.start_background_task(background_thread)
            emit('my_response', {'data': 'Connected', 'count': 0})


        @socketio.on('disconnect')
        def test_disconnect():
            print('Client disconnected', request.sid)

        # @app.route('/')
        # def index():
        #     """Video streaming home page."""
        #     return render_template('index.html')

        @app.route('/video_feed/<camera>')
        def video_feed(camera):
            try:
                return Response(getattr(self.cameras[camera], "stream")(),
                                mimetype='multipart/x-mixed-replace; boundary=frame')
            except KeyError:
                return f"{camera} is offline or disabled"

        @app.route('/kill_<camera>')
        def kill_camera(camera):
            try:
                getattr(self.cameras[camera], "stop")()
                self.removeCamera(camera)
            except KeyError:
                return f"{camera} is offline or disabled"
            return "Kill successfully"
        
        @app.route('/kill_server')
        def kill_server():
            for camera in self.cameras.values():
                camera.stop()
                #self.removeCamera(nome)
            return self.shutdown_server()
            



