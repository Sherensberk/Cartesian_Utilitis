import cv2
import numpy as np
import math
import colorsys
from ..util import color
"""
filterconfig ={

    "mode":"RETR_TREE",
    "method":"CHAIN_APPROX_SIMPLE",

    "areaMin":100,
    "areaMax":00,

    "kerenelA":(3, 3),
    "kerenelB":(2, 2),
    "Color":{
        "mode":"hsv",

        "hex":{
            "lower":"#999999",
            "upper":"#FFFFFF",
        },
        "rgb":{
            "lower":(255,255,255),
            "upper":(255,255,255)
            },
        "hsv":{
            "lower":(0,0,0),
            "upper":(360,255,255)
        }
    }
}
"""
def findContour(image, config):
    contours, hierarchy = cv2.findContours(image, mode=getattr(cv2, config["mode"]), method=getattr(cv2, config["method"]))
    data = [False]
    try:
        hierarchy = hierarchy[0]
    except TypeError:
        return data
    for component in zip(contours, hierarchy):
        currentContour = component[0]
        area = cv2.contourArea(currentContour)
        #currentHierarchy = component[1]
        if config["areaMin"] < area < config["areaMax"]:
            data[0] = True
            xA, yA, wA, hA = cv2.boundingRect(currentContour)
            boxA = np.int0(cv2.boxPoints(cv2.minAreaRect(currentContour)))
            boxOrded = order_points(np.array(boxA, dtype="float32"))
            bxA = boxOrded[2][0] - boxOrded[1][0]
            axA = boxOrded[1][1] - boxOrded[2][1]
            byA = boxOrded[0][0] - boxOrded[1][0]
            ayA = boxOrded[1][1] - boxOrded[0][1]
            alturaA = math.sqrt(pow(axA, 2) + pow(bxA, 2))
            larguraA = math.sqrt(pow(ayA, 2) + pow(byA, 2))
            momentsA = cv2.moments(currentContour)
            cxA = int(momentsA["m10"] / momentsA["m00"])
            cyA = int(momentsA["m01"] / momentsA["m00"])
            centro_momentsA = (cxA, cyA)
            centro_boxA = (larguraA / 2 + xA, alturaA / 2 + yA)
            data.append(
                {"boundRect": [(xA, yA), (wA, hA)], "dimension": [alturaA, larguraA], "contours":contours, "box": boxA, "centers": [centro_momentsA, centro_boxA], "area":area})
    return data 

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

# Cria uma mascara HSV apartir de um range pré-determinado.
def HSVMask(img, config):
    if config["Color"]["mode"] == "hex":
        l = colorsys.rgb_to_hsv(color.hex_to_rgb(config["Color"][config["Color"]["mode"]]["lower"]))
        u = colorsys.rgb_to_hsv(color.hex_to_rgb(config["Color"][config["Color"]["mode"]]["upper"]))
    else:
        l = config["Color"][config["Color"]["mode"]]["lower"]
        u = config["Color"][config["Color"]["mode"]]["upper"]
    return cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL), np.array(l), np.array(u))


# Reduz ruídos os ruidos da mascara.
def refineMask(maskToRefine, config):
    return cv2.morphologyEx(cv2.morphologyEx(maskToRefine, cv2.MORPH_CLOSE, (np.ones(config["kerenelA"], np.uint8))),
                            cv2.MORPH_OPEN,
                            (np.ones(config["kerenelB"], np.uint8)))

def apply(img, config, **kwargs):
    data = {}
    hsvmask = HSVMask(img, config)
    bettermask = refineMask(hsvmask, config)
    cnts = findContour(bettermask, config)
    # for k in kwargs.keys():
    #     try:
    #         data[str(k): locals()[k]]
    #     except KeyError:
    #         print(k, "não é um valor valido.")
    return cnts, bettermask