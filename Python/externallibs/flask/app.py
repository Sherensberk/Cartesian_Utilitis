from threading import Thread

from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO, send
from waitress import serve

#from ..camera.device import new_camera as camera


class Server(Thread):
    def __init__(self, app_ip, app_port, buildfolder, **kwargs):
        Thread.__init__(self)
        self.app = Flask(__name__, static_folder = f"{buildfolder}/static",
                                template_folder = buildfolder)
        self.socketio = SocketIO(self.app)
        self.ip = app_ip
        self.port = app_port
        self.mode = kwargs.get("debug")
        self.cameras = {}

    def run(self):
        self.defineRoutes()
        print("rodando....")
        if self.mode:
            self.socketio.run(self.app)
            # self.app.run(host=self.ip, port=self.port, debug=True,
            #         threaded=True, use_reloader=False)
        else:
            serve(self.app, host=self.ip, port=self.port)
        print("parou!")

    def addCamera(self, nome, valor):
        self.cameras[nome] = valor
    
    def removeCamera(self, nome):
        self.cameras.pop(nome)

    def stop(self):
        serve.graceful_shutdown()

    def stopped(self):
        return self._stop_event.is_set()

    def shutdown_server(self):
        shutdown_function = request.environ.get('werkzeug.server.shutdown')
        if shutdown_function is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        shutdown_function()

    def defineRoutes(self):
        app = self.app
        socketio = self.socketio
        @app.route('/')
        def index():
            """Video streaming home page."""
            return render_template('index.html')

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

            if self.mode:
                self.shutdown_server()
                return "Kill successfully"
            else:
                return "Cannot kill"

        @socketio.on('message')
        def handleMessage(msg):
            print('Message: ' + msg)
            send(msg, broadcast=True)



