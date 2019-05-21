# **Albion Minimap Overlay Tool**
This tool automatically gathers the information about your current map at https://www.albiononline2d.com and displays the pointed nodes over your minimap.<br />
Doesn't interfers with the game and doesn't violate the user agreement since it only displays the on-screen overlay over the albion window and gets the current map name making screenshots.

## How it works:
1. Makes screenshot of the Albion map name region
2. Recognizes the name of the current map via the Google Tesseract OCR engine (needs to be installed)
3. Gets the map id at [albion.thisgame.ru](https://albion.thisgame.ru/)
4. Gets the map information at [www.albiononline2d.com](https://www.albiononline2d.com)
5. Filters the information based on the ./config file
6. Renders the nodes over the Albion minimap region

## First launch:
1. Download and unpack the [latest release](https://github.com/ph5x5/albion-minimap-overlay/releases)
2. Download the latest [Google Tesseract OCR Engine](https://github.com/tesseract-ocr/tesseract/wiki/Downloads)
3. Go the executable folder and edit the config.json file updating the Tesseract "tesseract_path" installation location
4. Fill the filters you want to view in the "filters" section according to [Configuration Nodes] section
5. Launch the albion-minimap-tool executable
6. Switch Albion to the windowed full screen mode
6. Play and enjoy!

## Configuration nodes:
General section:
- screenshot_file   - place to store screenshots
- tesseract_path    - path to the installed Google Tesseract OCR engine
- update_interval   - map update interval
- retries           - retries on web request errors number

Filters sections:
Resource filters are pointed as this: <RESOURCE>_<TIER>_NODE, where
- <RESOURCE> - is the resource name (FIBER, HIDE, ORE, ROCK WOOD)
- <TIER> - is the relative resource on the map (HIGH, MEDIUM, LOW)
For example the ORE_HIGH_NODE pointed will display the T6 ore points on a T5 map.

## Planned features:
1. Tray icon and menu
2. Random dungeons and fishing

## Contact information:
E-mail: [phoenixus87@gmail.com](mailto:phoenixus87@gmail.com)<br />
Skype: fenyanyaa<br />
Donates are appreciated: https://www.patreon.com/ph5x5

## Thanks to:
1. [Albion Online Team](https://albiononline.com)
2. [albion.thisgame.ru](https://albion.thisgame.ru/)
3. [www.albiononline2d.com](https://www.albiononline2d.com)
4. [Pelfusion](http://www.pelfusion.com/) for icon
5. Google