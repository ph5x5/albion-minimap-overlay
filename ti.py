# IMPORTS
from screeninfo import get_monitors
import pytesseract
import time
import tkinter
from PIL import Image
from PIL import ImageGrab
import requests
import json
import win32api, win32con, pywintypes
import logging



# CONFIGURATION
CONFIGURATION_FILE = '.\config.json'
with open(CONFIGURATION_FILE) as json_file:  
    configuration = json.load(json_file)
SCREENSHOT_FILE = configuration['general']['screenshot_file']
UPDATE_INTERVAL = configuration['general']['update_interval']
RETRIES = configuration['general']['retries']
pytesseract.pytesseract.tesseract_cmd = configuration['general']['tesseract_path']
MAP_PREVIOUS = ""
MAP_INFO_PREVIOUS = {}
RESOLUTION = "", ""
VERSION = "0.1beta"

logging.basicConfig(level = logging.INFO)



# CLASSES
class CriticalError:
    def __init__(self, text):
        logging.error(text)
        exit(1)


class GetResolution:
    def __init__(self):
        logging.info("Getting screen resolution...")
        found = False
        for monitor in get_monitors():
            if str(monitor).split('+')[1] == '0':
                resolution_string = str(monitor).split('+')[0].split('(')[1]
                self.width = resolution_string.split('x')[0]
                self.height = resolution_string.split('x')[1]
                found = True
        if found == False:
            CriticalError('Can\'t find display resolution!')

    @property
    def resolution(self):
        logging.info("Resolution is {}x{}".format(self.width, self.height))
        return int(self.width), int(self.height)


class GetScreenshot:
    def __init__(self, width, height):
        logging.info("Saving map name screenshot to {}..".format(SCREENSHOT_FILE))
        try:
            screenshot = ImageGrab.grab(bbox = (width - 265, height - 44, width - 80, height - 20))
            screenshot.save(SCREENSHOT_FILE)
        except:
            CriticalError("Can\'t capture screenshot to file {}!".format(SCREENSHOT_FILE))


class RecognizeMap:
    def __init__(self):
        logging.info("Recognizing the captured screenshot..")
        try:            
            temp_text = pytesseract.image_to_string(Image.open(SCREENSHOT_FILE))
            if '<' in temp_text:
                temp_text = temp_text.split('<')[0]
            if temp_text.endswith(' '):
                temp_text = temp_text[:-1]
            self.text = temp_text.replace(' ', '-')
        except:
            CriticalError('Can\'t recognize the map name. Set the game to windowed FullScreen!')
        
    @property
    def name(self):
        logging.info("Recognized: {}".format(self.text))
        return self.text


class GetMapId:
    def __init__(self, name):
        self.map_id = ""
        self.flag = False
        error_counter = 0
        logging.info("Getting map id from \"albion.thisgame.ru\"..")
        while self.map_id == "":
            if error_counter < RETRIES:
                try:
                    r = requests.get('https://albion.thisgame.ru/en/map/' + name)
                    name = name.replace('-', ' ')
                    map_json = json.loads(str(r.content).split("\"{}\":".format(name))[1].split('},')[0] + "}")
                    self.map_id = map_json["id"].split('_')[0]
                    self.flag = True
                    break
                except:
                    logging.warning("Can't get id, retrying..")
                    error_counter += 1
            else:
                self.flag = False
                break

    @property
    def mapid(self):
        if self.flag != False:
            logging.info("Map ID: {}".format(self.map_id))
            return self.map_id
        else:
            logging.warning("Error receiving map id. Please open Albion in FullScreen mode")
            return self.flag


class GetMapInfo:
    def __init__(self, map_id):
        logging.info("Receiving the map data from \"albiononline2d.com\"..")
        error_counter = 0
        self.flag = False
        while 'self.data_json' not in locals():
            if error_counter < RETRIES:
                try:
                    r = requests.get('https://www.albiononline2d.com/en/map/api/nodes/' + map_id)
                    self.data_json = json.loads(r.content)
                    self.flag = True
                    break
                except:
                    logging.warning("Can't get data, retrying..")
                    error_counter += 1
            else:
                self.flag = False
                self.data_json = {}
                break

    @property
    def data(self):
        if self.flag != False:
            logging.info("Successfully received map data")
            return self.data_json
        else:
            logging.warning("Error receiving map data")
            return self.flag


class FilterMapInfo:
    def __init__(self, map_info):
        logging.info("Applying the filters..")
        try:
            with open(CONFIGURATION_FILE) as json_file:  
                filters = json.load(json_file)["filters"]
            self.filtered_info = []
            for resource in map_info["resourceNodes"]:
                if resource["name"] in filters:
                    self.filtered_info.append(resource)
        except:
            logging.error("Can't apply the filters, please check their syntax in {}".format(CONFIGURATION_FILE))
        
    @property
    def data_filtered(self):
        logging.info("Filters applied successfully")
        return self.filtered_info


class InitOverlay():
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-disabled", True)
        self.canvas = tkinter.Canvas(self.root, width = RESOLUTION[0], height = RESOLUTION[1], bg = "white", highlightthickness = 0)     
        self.canvas.pack()
        self.launch()

    def launch(self):
        self.redraw_canvas()
        self.root.mainloop()

    def redraw_canvas(self):
        map_info_filtered = GetData().data
        self.canvas.delete("all")
        logging.info("Updating the nodes on minimap..")
        for resource in map_info_filtered:
            if resource["nodetype"] == "high":
                color = "red"
                radius = 2
            elif resource["nodetype"] == "medium":
                color = "orange"
                radius = 1
            elif resource["nodetype"] == "low":
                color = "yellow"
                radius = 1
            self.create_circle(RESOLUTION[0] - 340 + (resource["x"] + 1000) * 0.175, RESOLUTION[1] - 240 + (-resource["y"] + 1000) * 0.108, radius, color, self.canvas)
        logging.info("Sleeping for {} seconds..".format(UPDATE_INTERVAL))
        self.canvas.after(5000, self.redraw_canvas)


    def create_circle(self, x, y, r, color, canvasName):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return canvasName.create_oval(x0, y0, x1, y1, fill = color)


class GetData():
    def __init__(self):
        global MAP_PREVIOUS
        global MAP_INFO_PREVIOUS
        global RESOLUTION

        logging.info("Updating map data..")
        GetScreenshot(RESOLUTION[0], RESOLUTION[1])
        map_name = RecognizeMap().name
        if map_name != MAP_PREVIOUS:
            map_id = GetMapId(map_name).mapid
            if map_id != "False":
                map_info = GetMapInfo(map_id).data
                if map_info != "False":
                    self.map_info_filtered = FilterMapInfo(map_info).data_filtered
                    MAP_PREVIOUS = map_name
                else:
                    time.sleep(UPDATE_INTERVAL)
            else:
                time.sleep(UPDATE_INTERVAL)
        else:
            self.map_info_filtered = MAP_INFO_PREVIOUS
        MAP_INFO_PREVIOUS = self.map_info_filtered


    @property
    def data(self):
        return self.map_info_filtered



# MAIN
def main():
    global RESOLUTION

    logging.info("Albion minimap extension")
    logging.info("Doesn't interfers with the game and doesn't violate the user agreement")
    logging.info("By ph5x5 (phoenixus87@gmail.com)")
    logging.info("Version: {}".format(VERSION))

    RESOLUTION = GetResolution().resolution
    InitOverlay()



# BODY
if __name__ == "__main__":
    main()
