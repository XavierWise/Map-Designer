import sbs, math


def TabletButton(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    # creates a shaped button that can be click and selected once.
    text = ""
    colour1 = "orange"
    colour2 = "#006600"
    font = "gui-1"
    subtext = ""

    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("highlightcolour"):
        colour1 = kwargs.get("highlightcolour")
    if kwargs.get("font"):
        font = kwargs.get("font")
    if kwargs.get("subtext"):
        subtext = kwargs.get("subtext")
    if kwargs.get("buttoncolour"):
        colour2 = kwargs.get("buttoncolour")

    sbs.send_gui_text(clientID, GUITag, f"{reference}-text", f"text:{text}; color: #ccffff; font: {font}; justify: center", posx, posy, posx + w, posy + h)
    if kwargs.get("subtext"):
        sbs.send_gui_text(clientID, GUITag, f"{reference}-subtext", f"text:{subtext}; color: #ccffff; font: smallest; justify: center", posx, posy + 3, posx + w, posy + h)
    sbs.send_gui_clickregion(clientID, GUITag, reference, f"text:{text}; color: {colour1}; font: {font}", posx, posy, posx + w, posy + h)
    sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {colour2}", posx, posy, posx + w, posy + h)


def IconTabletButton(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    # creates a shaped button that can be click and selected once.
    text = ""
    subtext = ""
    colour1 = "orange"
    colour2 = "#ccffff"
    colour3 = "#006600"
    font = "gui-1"
    justify = "center"
    icon = "101"

    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("colour"):
        colour1 = kwargs.get("colour")
    if kwargs.get("font"):
        font = kwargs.get("font")
    if kwargs.get("justify"):
        justify = kwargs.get("justify")
    if kwargs.get("icon"):
        icon = str(kwargs.get("icon"))
    if kwargs.get("iconcolour"):
        colour2 = kwargs.get("iconcolour")
    if kwargs.get("highlightcolour"):
        colour1 = kwargs.get("highlightcolour")
    if kwargs.get("buttoncolour"):
        colour3 = kwargs.get("buttoncolour")
    if kwargs.get("subtext"):
        subtext = kwargs.get("subtext")

    sbs.send_gui_text(clientID, GUITag, f"{reference}-text", f"text:{text}; color: #ccffff; font: {font}; justify: {justify}", posx + 5, posy, posx + w, posy + 5)
    sbs.send_gui_clickregion(clientID, GUITag, reference, f"text:{text}; color: {colour1}; font: {font}", posx + 5, posy, posx + w, posy + 5)
    if kwargs.get("subtext"):
        sbs.send_gui_text(clientID, GUITag, f"{reference}-subtext", f"text:{subtext}; color: #ccffff; font: smallest; justify: center", posx + 5, posy + 3, posx + w,  posy + h)

    sbs.send_gui_rawiconbutton(clientID, GUITag, f"icon{reference}", f"icon_index: {icon}; color: {colour2}", posx, posy, posx + 5, posy + 5)
    sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {colour3}", posx, posy, posx + w, posy + h)


def IconButton(clientID, GUITag, reference, posx, posy, **kwargs):
    text = ""
    colour1 = "#ccffff"
    colour2 = "#ccffff"
    font = "smallest"
    icon = "101"
    size = 5
    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("colour"):
        colour1 = kwargs.get("colour")
    if kwargs.get("font"):
        font = kwargs.get("font")
    if kwargs.get("icon"):
        icon = kwargs.get("icon")
    if kwargs.get("iconcolour"):
        colour2 = kwargs.get("iconcolour")
    if kwargs.get("iconsize"):
        size = kwargs.get("iconsize")

    sbs.send_gui_text(clientID, GUITag, f"{reference}-name", f"text: {text}; color: {colour1}; font: {font}; justify: center", posx, posy - 3, posx + 5, posy)
    sbs.send_gui_rawiconbutton(clientID, GUITag, f"{reference}", f"icon_index: {icon}; color: {colour2}", posx, posy, posx + size, posy + size)


def ToggleButton(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    # creates a shaped button that can be click and selected once.
    text = ""
    colour1 = "#ccffff"
    colour2 = "#ff3300"
    colour3 = "orange"
    font = "gui-1"
    justify = "center"

    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("textcolour"):
        colour1 = kwargs.get("colour")
    if kwargs.get("togglecolour"):
        colour2 = kwargs.get("togglecolour")
    if kwargs.get("highlightcolour"):
        colour3 = kwargs.get("highlightcolour")
    if kwargs.get("font"):
        font = kwargs.get("font")
    if kwargs.get("justify"):
        justify = kwargs.get("justify")

    sbs.send_gui_text(clientID, GUITag, f"{reference}-text", f"text:{text}; color: {colour1}; font: {font}; justify: {justify}", posx, posy, posx + w, posy + h)
    sbs.send_gui_clickregion(clientID, GUITag, reference, f"text:{text}; color: {colour3}; font: {font}", posx, posy, posx + w, posy + h)
    sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {colour2}", posx, posy, posx + w, posy + h)


def IconToggleButton(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    # creates a shaped button that can be click and selected once.
    text = ""
    colour1 = "orange"
    colour2 = "#ccffff"
    colour3 = "#006600"
    font = "gui-1"
    justify = "center"
    icon = "101"
    iconsize = (5, 5)

    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("colour"):
        colour1 = kwargs.get("colour")
    if kwargs.get("font"):
        font = kwargs.get("font")
    if kwargs.get("justify"):
        justify = kwargs.get("justify")
    if kwargs.get("icon"):
        icon = kwargs.get("icon")
    if kwargs.get("iconcolour"):
        colour2 = kwargs.get("iconcolour")
    if kwargs.get("highlightcolour"):
        colour1 = kwargs.get("highlightcolour")
    if kwargs.get("buttoncolour"):
        colour3 = kwargs.get("buttoncolour")
    if kwargs.get("iconsize"):
        iconsize = kwargs.get("iconsize")

    sbs.send_gui_text(clientID, GUITag, f"{reference}-text", f"text:{text}; color: #ccffff; font: {font}; justify: {justify}", posx + iconsize[0], posy, posx + w, posy + h)
    sbs.send_gui_clickregion(clientID, GUITag, reference, f"text:{text}; color: {colour1}; font: {font}", posx + iconsize[0], posy, posx + w, posy + h)
    sbs.send_gui_rawiconbutton(clientID, GUITag, f"icon{reference}", f"icon_index: {icon}; color: {colour2}", posx, posy, posx + iconsize[0], posy + iconsize[1])
    sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {colour3}", posx, posy, posx + w, posy + h)


def menuBackground(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    # creates a background box with a title
    text = ""
    colour1 = "#ccffff"
    font = "gui-1"
    justify = "left"
    spacing = 3
    background = True

    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("colour"):
        colour1 = kwargs.get("colour")
    if kwargs.get("font"):
        font = kwargs.get("font")
        if font == "smallest":
            spacing = 2
    if kwargs.get("justify"):
        justify = kwargs.get("justify")
    if "background" in kwargs:
        background = kwargs.get("background")

    sbs.send_gui_text(clientID, GUITag, f"{reference}-heading", f"text: {text}; color: #ccffff; font: {font}; justify: {justify}", posx, posy - spacing, posx + w, posy + h)
    if background:
        sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {colour1}", posx, posy, posx + w, posy + h)
    if kwargs.get("scrollbar") and kwargs.get('maxLength') > 0:
        sbs.send_gui_slider(clientID, GUITag, f"{reference}-scroll", 0-kwargs.get('currentPos'), f"high: 0; low: {0-kwargs.get('maxLength')}", posx-1, posy, posx, posy+h)


def IncDecDisplay(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    # creates a box with a number in the middle, and a + and - either side
    displayVal = kwargs.get("value")
    name = kwargs.get("name")
    sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: white", posx - 10, posy - 0.2, posx + w + 5, posy + h)
    sbs.send_gui_text(clientID, GUITag, f"{reference}-name", f"text: {name}; color: #ccffff; font: gui-1; justify: center", posx - 10, posy - 5, posx + w + 5, posy + h)
    sbs.send_gui_rawiconbutton(clientID, GUITag, f"icon{reference}-increase", f"icon_index: 156; color: green", posx + w, posy, posx + w + 5, posy + h)
    sbs.send_gui_rawiconbutton(clientID, GUITag, f"icon{reference}-decrease", f"icon_index: 157; color: red", posx - 10, posy, posx - 5, posy + h)
    sbs.send_gui_text(clientID, GUITag, f"{reference}-value", f"text: {displayVal}; color: #ccffff; font: gui-1; justify: center", posx - 10, posy, posx + w + 5, posy + h)


def holotextDisplay(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    # creates a textbox with a background
    text = ""
    colour1 = "#ccffff"
    font = "gui-1"
    justify = "center"
    subtext = ""
    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("colour"):
        colour1 = kwargs.get("colour")
    if kwargs.get("font"):
        font = kwargs.get("font")
    if kwargs.get("justify"):
        justify = kwargs.get("justify")
    if kwargs.get("subtext"):
        subtext = kwargs.get("subtext")
    sbs.send_gui_text(clientID, GUITag, f"{reference}-heading", f"text: {text}; color: #ccffff; font: {font}; justify: {justify}", posx, posy, posx + w, posy + h)
    sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {colour1}", posx, posy, posx + w, posy + h)
    if kwargs.get("subtext"):
        sbs.send_gui_text(clientID, GUITag, f"{reference}-subtext", f"text:{subtext}; color: #ccffff; font: smallest; justify: center", posx + 5, posy + 3, posx + w,  posy + h)


def holotextBox(clientID, GUITag, reference, posx, posy, w, **kwargs):
    # creates a textbox with a background
    text = ""
    backgroundcolour = "#ccffff"
    font = "gui-1"
    justify = "left"
    textcolour = "#ccffff"
    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("textColour"):
        textcolour = kwargs.get("textColour")
    if kwargs.get("colour"):
        backgroundcolour = kwargs.get("colour")
    if kwargs.get("font"):
        font = kwargs.get("font")
    if kwargs.get("justify"):
        justify = kwargs.get("justify")
    screen = sbs.get_screen_size()
    width = int((screen.y / 100) * w)
    textBlockH = sbs.get_text_block_height(font, text, width)
    textHPercent = (textBlockH / screen.y) * 100
    sbs.send_gui_text(clientID, GUITag, f"{reference}-text", f"text: {text}; color: {textcolour}; font: {font}; justify: {justify}", posx, posy, posx + w, posy + textHPercent)
    if kwargs.get("background"):
        sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {backgroundcolour}", posx, posy, posx + w, posy + textHPercent)
    return textHPercent


def scrollList(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    pass


def spaceobjectviewer(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    colour1 = "#ccffff"
    objName = ""
    objType = ""
    objHull = "unknown"
    if kwargs.get("colour"):
        colour1 = kwargs.get("colour")
    if kwargs.get('name'):
        objName = kwargs.get("name")
    if kwargs.get("hull"):
        objHull = kwargs.get("hull")
        objType = objHull.replace("_", " ")
    sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {colour1}", posx, posy, posx + w, posy + h)
    sbs.send_gui_text(clientID, GUITag, f"{reference}-objname", f"text: {objName}; font: gui-1; justify: center", posx, posy, posx + w, posy + h)
    sbs.send_gui_text(clientID, GUITag, f"{reference}-objtype", f"text: {objType.upper()}; font: smallest; justify: center", posx, posy, posx + w, posy + h)
    sbs.send_gui_3dship(clientID, GUITag, f"{reference}-objhull", f"hull_tag: {objHull}", posx, posy, posx + w, posy + h)


def textBox(clientID, GUITag, reference, posx, posy, w, h, **kwargs):
    w = int(w)
    h = int(h)
    text = ""
    header = ""
    hfont = "gui-1"
    tfont = "gui-1"
    hjustify = "left"
    tjustify = "left"
    hcolour = "#ccffff"
    tcolour = "#ccffff"
    bcolour = "#ccffff"
    spacing = 4
    background = False

    if kwargs.get("font"):
        font = kwargs.get("font")
        if font == "smallest":
            spacing = 3
    if "background" in kwargs:
        background = kwargs.get("background")
    if kwargs.get("text"):
        text = kwargs.get("text")
    if kwargs.get("header"):
        header = kwargs.get("header")
    if kwargs.get("font"):
        tfont = kwargs.get("font")
    if kwargs.get("headingfont"):
        hfont = kwargs.get("headingfont")
    if kwargs.get("headingjust"):
        hjustify = kwargs.get("headingjust")
    if kwargs.get("textjust"):
        tjustify = kwargs.get("textjust")
    if kwargs.get("headingcol"):
        hcolour = kwargs.get("headingcol")
    if kwargs.get("textcol"):
        tcolour = kwargs.get("textcol")
    if kwargs.get("backgroundcol"):
        bcolour = kwargs.get("backgroundcol")

    textBlockH = sbs.get_text_block_height(tfont, text, w)
    textHPercent = (textBlockH/1080) * 100

    textLineH = sbs.get_text_line_height(tfont, text)
    textLineHPercent = (textLineH/1080) * 100

    lines = text.split("^")
    lineCount = 0
    for line in lines:
        textLineW = sbs.get_text_line_width(tfont, line)
        textWPercent = (textLineW/1920) * 100
        if textWPercent/w > 1:
            lineCount += math.ceil(textWPercent/w)
        else:
            lineCount += 1

    textTotalH = textLineHPercent * lineCount

    sbs.send_gui_text(clientID, GUITag, f"{reference}-header", f"text: {header}; color: {hcolour}; font{hfont}; justify:{hjustify}", posx, posy - spacing, posx + w, posy + h)
    sbs.send_gui_text(clientID, GUITag, f"{reference}-body", f"text: {text}; color: {tcolour}; font{tfont}; justify:{tjustify}", posx, posy, posx + w, posy + h)

    if background:
        sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {bcolour}", posx, posy, posx + w, posy + h)
    if textHPercent < textTotalH:
        sbs.send_gui_button(clientID, GUITag, f"{reference}-scrollUp", "text:", posx-1, posy, posx, posy + (h/2))
        sbs.send_gui_button(clientID, GUITag, f"{reference}-scrollDown", "text:", posx-1, posy + (h/2), posx, posy + h)


class ProgressBar:
    def __init__(self, **kwargs):
        self.increment = 0
        self.timeend = 0
        self.timestart = 0
        self.cumulation = 0
        self.iconW = 2
        self.iconH = 3

        if "barW" in kwargs.keys():
            self.iconW = kwargs.get("barW")
        if "barH" in kwargs.keys():
            self.iconH = kwargs.get("barH")

        self.curPoint = 0
        self.Timer = False

    def StartTrigger(self, length):
        self.curPoint = 0
        self.timeend = sbs.app_seconds() + length
        self.timestart = sbs.app_seconds()
        self.increment = length/10
        self.cumulation = self.increment
        self.Timer = True

    def TickMonitor(self, updateClients):
        if self.Timer:
            if self.timeend < sbs.app_seconds():
                self.curPoint = 10
                self.Timer = False
            elif sbs.app_seconds() >= self.timestart + self.cumulation:
                self.cumulation += self.increment
                self.curPoint += 1
                updateClients()

    def send_gui_progressbar(self, clientID, GUITag, reference, position):
        posx = position[0]
        posy = position[1]
        posx1 = position[0]
        sbs.send_gui_image(clientID, GUITag, f"{reference}-background", f"image: ../missions/TSN Cosmos/Images/Box-50; color: white", posx1 - 0.1, posy - 0.1, posx1 + (self.iconW * 10) + 1, posy + self.iconH + 0.1)
        for point in range(self.curPoint):
            sbs.send_gui_image(clientID, GUITag, f"{reference}{point}", f"image: ../missions/TSN Cosmos/Images/Box-100; color: green", posx, posy, posx + self.iconW, posy + self.iconH)
            posx += self.iconW + 0.1
