import sbs, os


def PrintEvents(event):
    print("Event Time: " + str(event.event_time))
    print("Main Tag: " + event.tag + " Sub Tag: " + event.sub_tag)
    print("Client: " + str(event.client_id))
    print("Sub Float: " + str(event.sub_float) + " Value Tag: " + str(event.value_tag))
    print("Selected ID: " + str(event.selected_id) + " Origin ID: " + str(event.origin_id))
    print("Source Point: " + str(event.source_point) + " Parent ID: " + str(event.parent_id))
    print(event.source_point.x, event.source_point.y, event.source_point.z)
    print("Extra Tag: " + str(event.extra_tag))
    print("Extra-Extra Tag: " + str(event.extra_extra_tag))


def resCon(percentagesize, standardisedres, currentres):
    decimal = percentagesize/100
    newpercentage = ((standardisedres * decimal)/currentres) * 100
    return newpercentage


def AddNavPoint(sim, name, position, **kwargs):
    if "colour" in kwargs:
        colour = kwargs.get("colour")
    else:
        colour = "Green"
    if "offset" in kwargs:
        offset = kwargs.get("offset")
    else:
        offset = (0, 0, 0)
    navpointID = sim.add_navpoint(position[0] + offset[0], position[1], position[2] + offset[2], name, colour)
    navpoint = sim.get_navpoint_by_id(navpointID)
    if "side" in kwargs:
        navpoint.visibleToSide = kwargs.get("side")
    elif "objectID" in kwargs:
        navpoint.visibleToShip = kwargs.get("objectID")
    return navpointID


class timer:
    def __init__(self, time):
        self.time = time
        self.timer = False
        self.end = 0

    def countdownSecs(self, cur_tick):
        if self.timer == False:
            self.end = cur_tick + 30 * self.time
            self.timer = True
        if self.timer and cur_tick <= self.end:
            pass
        else:
            self.timer = "Done"
        return self.timer

    def countdownMins(self, cur_tick):
        if self.timer == False:
            self.end = cur_tick + 60 * self.time
            self.timer = True
        if self.timer and cur_tick <= self.end:
            pass
        else:
            self.timer = "Done"
        return self.timer

    def deletetimerobj(self):
        del self


def crender(clientObj, tag):
    sbs.send_gui_clear(clientObj.clientID, tag)
    clientObj.myConsoles.consoleRender()
    sbs.send_gui_complete(clientObj.clientID, tag)


def crenderID(clientID, clientDict, tag):
    sbs.send_gui_clear(clientID, tag)
    clientObj = clientDict.get(clientID, tag)
    clientObj.myConsoles.consoleRender()
    sbs.send_gui_complete(clientID, tag)


def mrender(clientObj, tag):
    sbs.send_gui_clear(clientObj.clientID, tag)
    clientObj.myMenu.menuRender()
    sbs.send_gui_complete(clientObj.clientID, tag)


def mrenderID(clientID, clientDict, tag):
    sbs.send_gui_clear(clientID, tag)
    clientObj = clientDict.get(clientID, tag)
    clientObj.myMenu.menuRender()
    sbs.send_gui_complete(clientID, tag)


def clearComms(ship):
    sbs.send_comms_selection_info(ship, "", "#00FFFF", "")


def tagrender(clientObj, tag):
    pass


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


testData = {"TH30": {
                "NavPoint": True,
                "Signature": "Tharium Radiation",
                "Strength": 250,
                "Analysis": "Emissions indicative of Kralien technology. "
                "Consistent wave strength and pattern suggests thrust output from engine exhausts."},
            "DBR51": {
                "NavPoint": True,
                "Signature": "Debris field",
                "Strength": 250,
                "Analysis": "Composite signature indicative of Torgoth hull plating."},
            "TRA90": {
                "NavPoint": True,
                "Signature": "Gredian Signature",
                "Strength": 943,
                "Analysis": "Asteroid sweep indicates trace elements of gredian compounds."},
            "TRN11": {
                "NavPoint": True,
                "Signature": "Filum gas compunds",
                "Strength": 250,
                "Analysis": "Gaseous particles, indicating Filum nebula. Highly volitile and disruptive "
                            "to shield systems and warp bubble stability."},
            "JP43": {
                "NavPoint": True,
                "Signature": "Omega Jump point",
                "Strength": 250,
                "Analysis": "Class Omega jump point. Drift radius estimated at 10000. Origin unknown. "
                            "Records indicate no known plotting within USFP databases."},
            }
