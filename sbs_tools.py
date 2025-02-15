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


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
