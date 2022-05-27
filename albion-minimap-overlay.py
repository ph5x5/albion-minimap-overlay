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
from win32gui import GetWindowText, GetForegroundWindow
import logging
from pathlib import Path
import cv2
import numpy
import psutil
import sys
from PyQt6 import QtGui, QtWidgets, QtCore, uic
import threading
import os



# CLASSES
class Configuration():
    __display = {
        "width": None,
        "height": None,
        "scale_factor": None
    }
    __data_source_online = {
        "name": "AlbionOnline2D",
        "uri": "https://www.albiononline2d.com",
        "list_maps": "/en/map",
        "api_map": "/en/map/api/nodes/"
    }
    __text_capture_zone = {
        "x0": None,
        "y0": None,
        "x1": None,
        "y1": None
    }
    __user = None
    __version = None
    __file_paths = {
        "user_configuration": Path('.\config.json'),
        "version": Path('.\\version.json'),
        "region_logo": Path('.\\misc\\region_logo.jpg'),
        "maps_cache": Path('.\\cache\\maps.json'),
        "icon": Path('.\\misc\\map.ico'),
        "form_configuration": Path('.\\ui\\configuration.ui')
    }
    __game = {
        "window_name": "Albion Online Client",
        "process_name": "Albion-Online.exe"
    }
    __application = {
        "name": "Albion Minimap Overlay"
    }

    def get_resolution(self):
        try:
            monitors = get_monitors()
            monitor_primary = next((x for x in monitors if x.is_primary == True), None)
        except Exception as e:
            logging.error(f"Can't get the display resolution: {e}")
        return monitor_primary.width, monitor_primary.height

    def load_configuration_file(self, configuration_file_path):
        with open(configuration_file_path) as json_file:  
            configuration = json.load(json_file)
        return configuration

    def get_version(self, version_file_path):
        with open(version_file_path) as json_file:  
            version = json.load(json_file)['version']
        return version

    def __init__(self):
        self.__display['width'], self.__display['height'] = self.get_resolution()
        self.__display['scale_factor'] = self.__display['height'] / 1080
        self.__user = self.load_configuration_file(self.__file_paths['user_configuration'])
        self.__version = self.get_version(self.__file_paths['version'])
        self.__text_capture_zone['x0'] = (
            self.__display['width'] -
            self.__user['recognition']['x0'] *
            self.__display['scale_factor']
        )
        self.__text_capture_zone['y0'] = (
            self.__display['height'] -
            self.__user['recognition']['y0'] *
            self.__display['scale_factor']
        )
        self.__text_capture_zone['x1'] = (
            self.__display['width'] -
            self.__user['recognition']['x1'] *
            self.__display['scale_factor']
        )
        self.__text_capture_zone['y1'] = (
            self.__display['height'] -
            self.__user['recognition']['y1'] *
            self.__display['scale_factor']
        )

    @property
    def display(self):
        return self.__display

    @property
    def user(self):
        return self.__user

    @property
    def version(self):
        return self.__version

    @property
    def data_source_online(self):
        return self.__data_source_online

    @property
    def file_paths(self):
        return self.__file_paths

    @property
    def text_capture_zone(self):
        return self.__text_capture_zone

    @property
    def game(self):
        return self.__game

    @property
    def application(self):
        return self.__application

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def exit_application(self):
        overlayThread.do_run = False
        exit()

    def configuration_save(self):
        user_configuration = json.loads(configuration_window.whatsThis())
        for attribute_window in dir(configuration_form):
            element = eval(f"configuration_form.{attribute_window}")
            if (
                isinstance(element, QtWidgets.QLineEdit) or 
                isinstance(element, QtWidgets.QCheckBox) or 
                isinstance(element, QtWidgets.QSpinBox)
            ):
                for attribute_config_upper in user_configuration:
                    if attribute_config_upper != 'filters':
                        for attribute_config_lower in configuration.user[attribute_config_upper]:
                            if attribute_config_lower == attribute_window:
                                if isinstance(element, QtWidgets.QLineEdit):
                                    value = None
                                    if json.loads(element.whatsThis())['type'] == "integer":
                                        value = int(element.text())
                                    elif json.loads(element.whatsThis())['type'] == "string":
                                        value = element.text()
                                    user_configuration[attribute_config_upper][attribute_config_lower] = value
                                elif isinstance(element, QtWidgets.QSpinBox):
                                    user_configuration[attribute_config_upper][attribute_config_lower] = element.value()
                                elif isinstance(element, QtWidgets.QCheckBox):
                                    if element.checkState().name == "Checked":
                                        value = True
                                    else:
                                        value = False
                                    user_configuration[attribute_config_upper][attribute_config_lower] = value
                if hasattr(element, "parent"):
                    if hasattr(element.parent(), "parent"):
                        if element.parent().parent().objectName() == 'filters':
                            if hasattr(element, 'checkState'):
                                if element.checkState().name == "Checked":
                                    user_configuration['filters'].append(element.objectName())
        with configuration.file_paths['user_configuration'].open('w', encoding ='utf8') as json_file:
            json.dump(
                user_configuration,
                json_file,
                indent = 4,
                sort_keys = True
            )
        logging.info("Reloading after configuration change...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    def configure_application(self):
        for attribute_window in dir(configuration_form):
            element = eval(f"configuration_form.{attribute_window}")
            for attribute_config_upper in list(configuration.user):
                if attribute_config_upper != 'filters':
                    for attribute_config_lower in list(configuration.user[attribute_config_upper]):
                        value_config_lower = configuration.user[attribute_config_upper][attribute_config_lower]
                        if attribute_window == attribute_config_lower:
                            if isinstance(element, QtWidgets.QLineEdit):
                                element.setText(str(value_config_lower))
                            elif isinstance(element, QtWidgets.QSpinBox):
                                element.setValue(value_config_lower)
                            elif isinstance(element, QtWidgets.QCheckBox):
                                element.setChecked(value_config_lower)
                else:
                    for map_filter in configuration.user['filters']:
                        if attribute_window == map_filter:
                            element.setChecked(True)
        configuration_form.buttonBox.accepted.connect(self.configuration_save)
        configuration_window.show()

    def __init__(self, icon, parent = None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)   
        
        action_configure = QtGui.QAction('&Configure', self)
        menu.addAction(action_configure)
        action_configure.triggered.connect(self.configure_application)

        action_exit = QtGui.QAction('&Exit', self)
        menu.addAction(action_exit)
        action_exit.triggered.connect(self.exit_application)

        self.setContextMenu(menu)
        self.setToolTip(configuration.application['name'])

class Printer():
    @property
    def information(self):
        logging.info("Albion minimap extension")
        logging.info("Doesn't interfers with the game and doesn't violate the user agreement")
        logging.info("By ph5x5 (phoenixus87@gmail.com)")
        logging.info("Donate: https://www.patreon.com/ph5x5")
        logging.info(f"Version: {configuration.version}")
        logging.info("----------------------------------------------------")

class ImageProcessor():
    def get_map_name_image(self):
        screenshot_file = Path(configuration.user['paths']['screenshot_file'])
        logging.info(f"Saving map name screenshot to {screenshot_file}..")
        try:
            screenshot = ImageGrab.grab(bbox = (
                configuration.text_capture_zone['x0'],
                configuration.text_capture_zone['y0'],
                configuration.text_capture_zone['x1'],
                configuration.text_capture_zone['y1']
            ))
            screenshot.save(screenshot_file)
        except Exception as e:
            logging.error(f"Can't capture screenshot to file {screenshot_file}: {e}")
        return screenshot_file

    def extract_region_logo(self, image_file_path):
        output_file_path = None
        try:
            black_screen = False
            output_file_path = f"{image_file_path.stem}_extracted.jpg"
            image = cv2.imread(str(image_file_path), 0)
            region_logo = cv2.imread(str(configuration.file_paths['region_logo']), 0)
            region_logo_width, region_logo_height = region_logo.shape[::-1]
            match = cv2.matchTemplate(image, region_logo, cv2.TM_CCOEFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
            image_cropped = image[0:24, 0:max_loc[0]]
            if image_cropped.size:
                cv2.imwrite(str(output_file_path), image_cropped)
        except Exception as e:
            logging.warning(f"Cant extract logo: {e}")
        return output_file_path

    def recognize_map_name(self, text_image_file_path):
        logging.info("Recognizing the captured screenshot..")
        pytesseract.pytesseract.tesseract_cmd = configuration.user['paths']['tesseract_path']
        recognized_text = None
        try:
            recognized_text = pytesseract.image_to_string(
                Image.open(str(text_image_file_path)),
                lang = 'eng',
                config = '''
                    --psm 13
                    --oem 1
                    -c tessedit_char_whitelist='ABCDEFGHIJKLMNOPRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
                    -c tessedit_char_blacklist='0123456789'
                '''
            )
        except Exception as e:
            logging.warning(f"Can't recognize the map name. Set the game to windowed FullScreen: {e}")
        return recognized_text

class MapDataSource():
    def get_map_id_from_cache(self, map_name):
        map_id = None
        try:
            with configuration.file_paths['maps_cache'].open('r', encoding ='utf8') as json_file:
                map_cache = json.load(json_file)
            map_cache_entry = next((x for x in map_cache['maps'] if x['name'] == map_name), None)
            if map_cache_entry:
                map_id = map_cache_entry['id']
        except Exception as e:
            logging.warning(f"Can't get id information from cache: {e}")
        return map_id, "cache"

    def get_map_id_online(self, map_name):
        logging.info(f"Map is not cached, loading information from {configuration.data_source_online['name']}...")
        retries = configuration.user['general']['retries']
        error_counter = 0
        map_id = None
        while not map_id:
            if error_counter < retries:
                try:
                    r = requests.get(configuration.data_source_online['uri'] + configuration.data_source_online['list_maps'])
                    map_json = json.loads(r.text.split('var config = ')[1].split(';</script>')[0])
                    for node in map_json["nodes"]:
                        if node["_attr"]["displayname"] == map_name:
                            map_id = node["_attr"]["id"]
                        if not map_id:
                            error_counter += 1
                except Exception as e:
                    error_counter += 1
                    logging.warning(f"Can't get id, retrying: {e}")
            else:
                break
        return map_id, format(configuration.data_source_online['name'])

    def get_map_id(self, map_name):
        map_id, source = self.get_map_id_from_cache(map_name)
        if not map_id:
            map_id, source = self.get_map_id_online(map_name)
        return map_id, source

    def get_map_nodes_from_cache(self, map_id):
        map_nodes = None
        try:
            with configuration.file_paths['maps_cache'].open('r', encoding ='utf8') as json_file:
                map_cache = json.load(json_file)
            map_cache_entry = next((x for x in map_cache['maps'] if x['id'] == map_id), None)
            if map_cache_entry:
                if map_cache_entry['nodes']:
                    map_nodes = map_cache_entry['nodes']
        except Exception as e:
            logging.warning(f"Can't get nodes information from cache: {e}")
        if map_nodes:
            logging.info(f"Successfully loaded map nodes for {map_id} from cache")
        return map_nodes, "cache"

    def get_map_nodes_online(self, map_id):
        logging.info(f"Map nodes are not cached, loading information from {configuration.data_source_online['name']}...")
        retries = configuration.user['general']['retries']
        error_counter = 0
        map_nodes = None
        while not map_nodes:
            if error_counter < retries:
                try:
                    r = requests.get(configuration.data_source_online['uri'] + configuration.data_source_online['api_map'] + map_id)
                    map_nodes = json.loads(r.content)
                    if not map_nodes:
                        error_counter += 1
                except Exception as e:
                    error_counter += 1
                    logging.warning(f"Can't get nodes, retrying: {e}")
            else:
                break
        return map_nodes, configuration.data_source_online['name']

    def get_map_nodes(self, map_id):
        map_nodes, source = self.get_map_nodes_from_cache(map_id)
        if not map_nodes:
            map_nodes, source = self.get_map_nodes_online(map_id)
        return map_nodes, source

    def cache_map(self, map_id, map_name, map_nodes):
        try:
            with configuration.file_paths['maps_cache'].open('r', encoding ='utf8') as json_file:
                map_cache = json.load(json_file)
        except Exception as e:
            logging.warning(f"Cache is missing: {e}")
            map_cache = { "maps": [] }
        map_cache_entry = next((x for x in map_cache['maps'] if x['id'] == map_id), None)
        if not map_cache_entry:
            map_cache['maps'].append({
                "name": map_name,
                "id": map_id,
                "nodes": map_nodes
            })
            configuration.file_paths['maps_cache'].parents[0].mkdir(parents = True, exist_ok = True)
            with configuration.file_paths['maps_cache'].open('w', encoding ='utf8') as json_file:
                json.dump(map_cache, json_file)

    @property
    def nodes(self):
        return self.__nodes

class MapFilter():
    def filter_nodes(self, nodes):
        logging.info("Applying the filters..")
        nodes_filtered = []
        error = False
        try:
            filters = configuration.user["filters"]
            if nodes['resourceNodes']:
                for node in nodes['resourceNodes']:
                    if node["name"] in filters:
                        nodes_filtered.append(node)
            if "RANDOM_DUNGEONS" in filters:
                if nodes["randomDungeonNodes"]:
                    for node in nodes["randomDungeonNodes"]:
                        nodes_filtered.append(node)
            if "FISHING_NODE" in filters:
                if nodes["fishingNodes"]:
                    for node in nodes["fishingNodes"]:
                        nodes_filtered.append(node)
        except Exception as e:
            error = True
            logging.error(f"Can't apply the filters, please check their syntax in {str(configuration.file_paths['user_configuration'])}: {e}")
        return nodes_filtered, error

class GameMap():
    __name = None
    __name_previous = None
    __id = None
    __nodes = None
    __nodes_filtered = None

    def get_map_name(self):
        map_name = None
        image_file_path = image_processor.get_map_name_image()
        text_image_file_path = image_processor.extract_region_logo(image_file_path)
        if text_image_file_path:
            map_name_unstripped = image_processor.recognize_map_name(text_image_file_path)
            if map_name_unstripped:
                map_name = map_name_unstripped.strip()
        return map_name

    def update(self):
        update_interval = configuration.user['general']['update_interval']
        logging.info("Updating map data..")
        handler = self.get_map_name()
        if handler:
            self.__name = handler
            logging.info(f"Recognized map name: {self.__name}")
            if self.__name != self.__name_previous:
                self.__nodes = []
                self.__id, source = map_data_source.get_map_id(self.__name)
                if self.__id:
                    logging.info(f"Successfully loaded map {self.__name} id {self.__id} from {source}")
                    self.__nodes, source = map_data_source.get_map_nodes(self.__id)
                    if self.__nodes:
                        logging.info(f"Successfully loaded nodes for map {self.__name} with id {self.__id} from {source}")
                        map_data_source.cache_map(self.__id, self.__name, self.__nodes)
                        self.__nodes_filtered, filter_error = map_filter.filter_nodes(self.__nodes)
                        if self.__nodes_filtered:
                            self.__name_previous = self.__name
                        elif filter_error:
                            logging.warning("Failed to get filtered nodes!")
                        else:
                            logging.info("All nodes are filtered out.")
                    else:
                        logging.warning("Failed to get map nodes!")
                else:
                    logging.warning("Failed to get map id!")
            else:
                logging.info("Map hasn't changed")
        else:
            logging.warning("Hasn't recognized the map")

    @property
    def nodes_filtered(self):
        return self.__nodes_filtered

class Overlay():
    def create_circle(self, x, y, r, color, canvasName):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return canvasName.create_oval(x0, y0, x1, y1, fill = color)

    def draw_text_capture_zone(self, canvasName):
        x0 = configuration.text_capture_zone['x0']
        y0 = configuration.text_capture_zone['y0']
        x1 = configuration.text_capture_zone['x1']
        y1 = configuration.text_capture_zone['y1']
        return canvasName.create_rectangle(x0, y0, x1, y1, width = 2, outline = "red")

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-disabled", True)
        self.canvas = tkinter.Canvas(self.root, width = configuration.display['width'], height = configuration.display['height'], bg = "white", highlightthickness = 0)     
        self.canvas.pack()
        self.launch()

    def launch(self):
        self.redraw_canvas()
        self.root.mainloop()
        pass

    def redraw_canvas(self):
        thread = threading.current_thread()
        if getattr(thread, "do_run", True):
            if configuration.game['process_name'] in (p.name() for p in psutil.process_iter()):
                if GetWindowText(GetForegroundWindow()) == configuration.game['window_name']:
                    self.canvas.delete("all")
                    if configuration.user['recognition']['draw_text_capture_zone']:
                        self.draw_text_capture_zone(self.canvas)
                    game_map.update()
                    if game_map.nodes_filtered:
                        nodes = game_map.nodes_filtered
                        logging.info("Updating the nodes on minimap..")                        
                        for node in nodes:
                            if node["name"] == "RandomExitPositionMarker_10x10_EXIT_RND-DNG":
                                color = "deep sky blue"
                                radius = 4
                            elif "FishingZone" in node["name"]:
                                color = "SlateBlue1"
                                radius = 2
                            else:
                                if node["resourcetype"] == "mobcamp":
                                    color = "DarkOrange3"
                                    radius = 3
                                else:
                                    if node["nodetype"] == "high":
                                        color = "red"
                                        radius = 2
                                    elif node["nodetype"] == "medium":
                                        color = "orange"
                                        radius = 1
                                    elif node["nodetype"] == "low":
                                        color = "yellow"
                                        radius = 1
                            self.create_circle(configuration.display['width'] - 340 * configuration.display['scale_factor'] + (node["x"] + 1000 * configuration.display['scale_factor']) * 0.172, configuration.display['height'] - 250 * configuration.display['scale_factor'] + (-node["y"] + 1000 * configuration.display['scale_factor']) * 0.115, radius, color, self.canvas)
                    else:
                        logging.warning("No filtered map data yet!")
                else:
                    self.canvas.delete("all")
                    logging.warning("Game window is not active, please switch into the game!")
            else:
                self.canvas.delete("all")
                logging.warning("Game is not running, please start the game!")
            logging.info(f"Waiting for {configuration.user['general']['update_interval']} seconds..")
            self.canvas.after(configuration.user['general']['update_interval'] * 1000, self.redraw_canvas)
        else:
            self.root.destroy()

class Creator():
    def create_overlay(self):
        overlay = Overlay()



# MAIN
def main():
    global configuration
    global map_data_source
    global game_map
    global image_processor
    global map_filter
    global overlayThread
    global configuration_window
    global configuration_form

    configuration = Configuration()
    logging.basicConfig(level = logging.INFO)

    printer = Printer()
    printer.information
    map_data_source = MapDataSource()
    image_processor = ImageProcessor()
    map_filter = MapFilter()
    game_map = GameMap()
    creator = Creator()

    overlayThread = threading.Thread(
        target = creator.create_overlay
    )
    overlayThread.start()

    application = QtWidgets.QApplication(sys.argv)
    application.setQuitOnLastWindowClosed(False)
    tray_widget = QtWidgets.QWidget()
    ConfigurationForm, ConfigurationWindow = uic.loadUiType(configuration.file_paths['form_configuration'])
    configuration_window = ConfigurationWindow()
    configuration_form = ConfigurationForm()
    configuration_form.setupUi(configuration_window)
    tray = SystemTrayIcon(QtGui.QIcon(str(configuration.file_paths['icon'])), tray_widget)
    tray.show()
    sys.exit(application.exec())



# BODY
if __name__ == "__main__":
    main()
