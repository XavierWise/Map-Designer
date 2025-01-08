import sbs
import simulation
import tsn_databases as data
from Objects import SpaceObjects

#below are all the GM specific consoles


def GMControls(clientObj):
    name = "GMControls"
    widgets = "science_2d_view^"
    layoutdata = {"science_2d_view": [0, 0, 100, 98, 0, 0, 100, 98]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    for widget in widgets.split("^"):
        if layoutdata.get(widget):
            pos = layoutdata.get(widget)
            sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    menus = clientObj.myShip.shipSystems.get("Menus")
    menus.iconbar.displayBar()
    for panel in menus.panelDatabase:
        panel.displayPanel()


def GMComms(clientObj):
    name = "GMNavigation"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    CiCDisplayMessages(clientObj)


def CiCDisplayMessages(clientObj):
    CiCScrollButtons(clientObj)
    ciccomms = clientObj.myShip.shipSystems.get("Comms")
    ypos = ciccomms.CiCScroll
    for key, message in ciccomms.CiCMessageList.items():
        if ypos < 18:
            ypos += 4
        elif ypos < 40:
            text = message.get("Message")
            sbs.send_gui_text(clientObj.clientID, "", f"disp-mess-{key}", f"text: {key}) {text[0:20]}; font:gui-1", 10, ypos, 60, ypos + 10)
            sendlist = message.get("SendTo")
            xpos = 10
            for s in sendlist:
                receiver = clientObj.myShip.sim.get_space_object(int(s))
                receiverdata = receiver.data_set
                name = receiverdata.get("name_tag", 0)
                sbs.send_gui_text(clientObj.clientID, "", f"disp-messlist-{key}-{s}", f"text:{name}; font:smallest", xpos, ypos + 2, xpos + 10, ypos + 4)
                xpos += 10
            if ciccomms.CiCMessageID == 0:
                sbs.send_gui_button(clientObj.clientID, "", f"send-mess-{key}", "text: Send; font:gui-1", 60, ypos, 70, ypos + 3)
                sbs.send_gui_button(clientObj.clientID, "", f"select-mess-{key}", "text: Options; font:gui-1", 70, ypos, 80, ypos + 3)
                sbs.send_gui_button(clientObj.clientID, "", f"delete-mess-{key}", "text: Delete; font:gui-1", 80, ypos, 90, ypos + 3)
            ypos += 4
    sbs.send_gui_button(clientObj.clientID, "", "create-mess-new", "text: NEW; font:gui-1", 70, 45, 80, 48)
    if ciccomms.CiCMessageID != 0:
        CiCEditMessage(ciccomms.CiCMessageID, clientObj)


def CiCEditMessage(key, clientObj):
    ciccomms = clientObj.myShip.shipSystems.get("Comms")
    sbs.send_gui_button(clientObj.clientID, "", f"save-mess-{key}", f"text: Save; font:gui-1", 60, 10, 70, 14)
    sbs.send_gui_typein(clientObj.clientID, "", f"input-mess-{key}", f"text:{ciccomms.CiCMessageInput}", 10, 10, 60, 14)
    xpos = 10
    for ship in SpaceObjects.activeShips.values():
        if ship.ObjectID in ciccomms.CiCSendTolist:
            sbs.send_gui_checkbox(clientObj.clientID, "", f"sendto-mess-{key}-{ship.ObjectID}", f"text:{ship.ObjectName[0:10]}; font:gui-1; state:on", xpos, 15, xpos + 15, 19)
        else:
            sbs.send_gui_checkbox(clientObj.clientID, "", f"sendto-mess-{key}-{ship.ObjectID}", f"text:{ship.ObjectName[0:10]}; font:gui-1; state:off", xpos, 15, xpos + 15, 19)
        xpos += 16


def CiCScrollButtons(clientObj):
    ciccomms = clientObj.myShip.shipSystems.get("Comms")
    if len(ciccomms.CiCMessageList.keys()) > 6:
        sbs.send_gui_button(clientObj.clientID, "", "scroll-mess-list-up", "text:up", 8, 20, 9, 30)
        sbs.send_gui_button(clientObj.clientID, "", "scroll-mess-list-down", "text:down", 8, 30, 9, 40)
