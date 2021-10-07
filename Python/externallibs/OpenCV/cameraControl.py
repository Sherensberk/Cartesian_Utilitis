from threading import Thread, Event
import cv2

class camera(Thread):
    def __init__(self, nome, id, config):
        Thread.__init__(self)
        self.name = nome
        self.id = id
        self.config = {"heigth":720, "width":1280,"usbID":0,"properties":{}}#config
        self.frame = None
        self.frameHeigth = self.config["heigth"]
        self.frameWidth = self.config["width"]
        self.usbID = self.config["usbID"]
        self.cam = cv2.VideoCapture(self.usbID)        
        cv2.imshow("frame0", self.cam.read()[1])
        cv2.waitKey(1)
        self._stop_event = Event()
        self.runnig = Event()
        
    
    def stop(self):
        self.runnig.clear()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def isRunning(self):
        return self.runnig.is_set()
    
    def RR(self):
        self.runnig.set()

    def setProperties(self, width, heigth):
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, heigth)
        self.cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
        
        for k, v in self.config["properties"].items():
            self.cam.set(getattr(cv2, 'CAP_PROP_' + k), v)

    def run(self):
        return self.camera()
    
    def getFrame(self):
        return self.frame

    def camera(self):
        self.setProperties(self.frameHeigth, self.frameWidth)
        while self.cam.isOpened() and not self.stopped():
            status, self.frame = self.cam.read()
            if not status:
                self.stop()            
            if not self.isRunning():
                self.RR()

cam = camera("validar", 0, "a")
cam.start()
while not cam.isRunning():
    pass
else:
    while cam.isRunning():
        cv2.imshow("frame", cam.getFrame())
        cv2.waitKey(1)
# print("ok")

# class CamThread(threading.Thread):
#     def __init__(self, previewName, camID):
#         threading.Thread.__init__(self)
#         self.previewName = previewName
#         self.camID = camI
#         self._running = True

#         self.Procs = {"hole": False,
#                       "screw": False, "normal": False}

#         self.Processos = ['screw']
#         self.pFA = (50, 50)
#         self.pFB = (100, 60)
#         self.fixPoiint = (self.pFB[0], int(
#             self.pFA[1] + ((self.pFB[1] - self.pFA[1]) / 2)))

#         self._stop_event = threading.Event()
#         self.get_data = threading.Event()

#     def stop(self):
#         self._stop_event.set()

#     def stopped(self):
#         return self._stop_event.is_set()

#     def run(self):
#         print("Starting " + self.previewName)
#         return self.camPreview(self.previewName, self.camID)

#     async def report(self, item):
#         item["description"] = item["description"].replace("_id_", str(self.camID['Settings']['id']))
#         await sendWsMessage("error", item)

#     def camPreview(self, previewName, cam_json):
#         # Abre a camera com o id passado.
#         camID = cam_json["Settings"]["id"]
#         cw = cam_json["Settings"]["frame_width"]
#         ch = cam_json["Settings"]["frame_height"]
#         print(cw,'x', ch)
#         cam = cv2.VideoCapture(camID)
#         cam.set(cv2.CAP_PROP_FRAME_WIDTH, int(cw))
#         cam.set(cv2.CAP_PROP_FRAME_HEIGHT, int(ch))
#         cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
        
#         # for k, v in cam_json["Properties"].items():
#         #     cam.set(getattr(cv2, 'CAP_PROP_' + k), v)

#         if cam.isOpened():                            # Verifica se foi aberta
#             rval, frame = cam.read()                  # Lê o Status e uma imagem
#             # if frame.shape[1] != cw or frame.shape[0] != ch:
#             #     sendWsMessage('erro', {'codigo': "Wronge image size", 'menssagem': f'A imagem deveria ter:{cw} x {ch}, mas tem {frame.shape[1]} x {frame.shape[0]}' })
#         else:
#             globals()[f'frame{previewName}'] = cv2.imread(f"../engine_H/Images/{camID}.jpg")
#             rval = False

#         while rval and not self.stopped():                                   # Verifica e camera ta 'ok'

#             rval, frame = cam.read()                  # Atualiza
#             frame = cv2.blur(frame, (3,3))
#             globals()[f'frame{previewName}'] = frame
#             if cv2.waitKey(1) == 27:
#                 break
#         try:    
#             cv2.destroyWindow(previewName)
#         except cv2.error:
#             pass
#         cam.release()
#         print("Saindo da thread", self.previewName)
#         infoCode = 6
#         for item in stopReasons:
#             if infoCode == item['code']:
#                 asyncio.run(self.report(item))
#         return False


#     def ViewCam(self):
#         while not self.stopped():
#             if self.Procs['screw']:
                
#                 frame, _ = Process_Imagew_Scew(
#                                     globals()['frame'+self.previewName],
#                                     Op.extractHSValue(mainParamters['Filtros']['HSV']['screw']["Valores"], 'lower' ),
#                                     Op.extractHSValue(mainParamters['Filtros']['HSV']['screw']["Valores"], 'upper' ),
#                                     mainParamters['Mask_Parameters']['screw']['areaMin'],
#                                     mainParamters['Mask_Parameters']['screw']['areaMax']
#                                     )
#                 # _, frame = findScrew(globals()[
#                 #                      'frame'+self.previewName], mainParamters['Filtros']['HSV'], mainParamters, self.Processos)
#                 yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'
#                        + cv2.imencode('.JPEG', frame,
#                                       [cv2.IMWRITE_JPEG_QUALITY, 100])[1].tobytes()
#                        + b'\r\n')
#             if self.Procs['hole']:
#                 _, _, _, frame = Process_Image_Hole(
#                     globals()['frame' + self.previewName],
#                     mainParamters['Mask_Parameters']['hole']['areaMin'],
#                     mainParamters['Mask_Parameters']['hole']['areaMax'],
#                     mainParamters['Mask_Parameters']['hole']['perimeter'],
#                     mainParamters['Filtros']['HSV']['hole']['Valores']
#                     )
#                 yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'
#                        + cv2.imencode('.JPEG', frame,
#                                       [cv2.IMWRITE_JPEG_QUALITY, 100])[1].tobytes()
#                        + b'\r\n')
#             if self.Procs['normal']:
#                 # print("normal")
#                 frame = globals()['frame'+self.previewName].copy()
#                 cv2.drawMarker(frame, (int(frame.shape[1]/2), int(frame.shape[0]/2)),(255,50,0),0,1000, 5)
#                 yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'
#                        + cv2.imencode('.JPEG', frame,
#                                       [cv2.IMWRITE_JPEG_QUALITY, 100])[1].tobytes()
#                        + b'\r\n')
#         print("Fechando Vizualizção")
