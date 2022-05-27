# **Albion Minimap Overlay Tool**
This tool automatically gathers the information about your current map at https://www.albiononline2d.com and displays the pointed nodes over your minimap.<br />
Doesn't interfers with the game and doesn't violate the user agreement since it only displays the on-screen overlay over the albion window and gets the current map name making screenshots.
Easily configurable and convinient

## **Download**:
[Releases link](https://github.com/ph5x5/albion-minimap-overlay/releases)

## Screenshot:
![Screenshot](https://raw.githubusercontent.com/ph5x5/albion-minimap-overlay/master/misc/image.png)

## How does it work:
1. Makes screenshot of the Albion map name region
2. Recognizes the name of the current map via the Google Tesseract OCR engine (needs to be installed)
3. Gets the map information at [www.albiononline2d.com](https://www.albiononline2d.com)
4. Filters the information based on the ./config.json file
5. Renders the nodes over the Albion minimap region

## Installation:
1. Download and unpack the [latest release](https://github.com/ph5x5/albion-minimap-overlay/releases)
2. Download the latest [Google Tesseract OCR Engine](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.1.0.20220510.exe)
3. Run the Albion Minimap Overlay, right click on the tray icon and press "Configure"
4. Update the Tesseract "tesseract_path" installation location if needed
5. Fill the filters you want to view in the "filters" section according to [Configuration Nodes] section
5. Launch the albion-minimap-tool executable
6. Switch Albion to the windowed full screen mode
7. Set the ingame interface scaling to 80%
8. Play and enjoy!

## Configuration nodes:
General section:
- Update interval   - map update interval
- Retries number    - retries on web request errors number

Paths section:
- Screenshot location   - place to store screenshots
- Tesseract location    - path to the installed Google Tesseract OCR engine

Recognition coordinates:
- Draw text capture zone         - turn on if you want to fix your recognition zone
- coordinates (x0, y0, x1, y1)   - relative coordinates of the recognition rectangle, feel free to play with them if your recognition rectangle has wrong positioning by default

Filters sections:
Resource filters are pointed as this: {RESOURCE} -> {TIER}, where:
- {RESOURCE} - is the resource name (FIBER, HIDE, ORE, ROCK, WOOD)
- {TIER} - is the relative tier level of a resource on the map (HIGH, MEDIUM, LOW)
For example the high ore selected will display the T6 ore points on a T5 map.<br />
Random dungeons     - filter allows displaying of random dungeons.<br />
Fishing             - displays fishing nodes.<br />
Mob camp            - displays mob camps.<br />
Roaming mob         - displays roaming mobs.

## Troubleshooting:
1. The tool launches and exites immideately - Check the tesseract path, it can't find it. Try the p.2 if this didn't help.
2. The tool can't read the JSON configuration file - Try to validate your config's JSON syntax at [Online JSON Formatter and Validator](https://jsonformatter.curiousconcept.com/)
3. Map names aren't recognizing - tune your recognition coordinates

## Changelog:
- v0.5.1    Recognition improved much, added system tray icon and configuration menu, caching, code refactoring
- v0.4.3    Fixed minimap scaling for different resolutions, minor recognition fix
- v0.4.2    Renamed script/binary to "albion-minimap-overlay", readme fixes, minor recognition fixes, resolution fixes
- v0.4.1    Improved node coordinates, added scaling for different resolutions, improved map name recognition
- v0.4      Added fishing zones and mob camps
- v0.3.2    Misc updates
- v0.3.1    Improved map name recognition
- v0.3      Improved map name recognition removed dependency on albion.thisgame.ru
- v0.2      Fixed map name recognition and added random dungeon markers
- v0.1      Initial Release

## Planned features:
1. Chat log recognition, parsing and alerts based on it, will make if I will see interest from community and will have time to do it of course :)
2. Full map cache as an additional archive

## Contact information:
E-mail: [phoenixus87@gmail.com](mailto:phoenixus87@gmail.com)<br />
Skype: fenyanyaa<br />
Reddit: https://www.reddit.com/user/ph5x5
Donate: https://www.patreon.com/ph5x5

## Thanks to:
1. [Albion Online Team](https://albiononline.com)
2. [www.albiononline2d.com](https://www.albiononline2d.com)
3. [Pelfusion](http://www.pelfusion.com/) for icon
4. [SkinnyZi](https://github.com/SkinnyZi) for code review and ideas
5. Google
