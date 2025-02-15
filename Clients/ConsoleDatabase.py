import sbs

import simulation


def MainMapControls(clientObj):
    name = "GMControls"
    widgets = "science_2d_view^"
    layoutdata = {"science_2d_view": [0, 0, 100, 98, 0, 0, 100, 98]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    for widget in widgets.split("^"):
        if layoutdata.get(widget):
            pos = layoutdata.get(widget)
            sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    sbs.send_gui_text(clientObj.clientID, "",  f"SystemName", f"text:{simulation.startSystem}; color: #ccffff; font: gui-2; justify: center", 0, 3, 100, 5)
    menus = clientObj.myShip.shipSystems.get("Menus")
    menus.iconbar.displayBar()
    for panel in menus.panelDatabase:
        panel.displayPanel()



consoleData = {
    "GM Controls": {
        "subConsoles": {
            "Controls": {"subConsoleState": "on",
                         "render": MainMapControls},
            },
        "mainConsoleState": "on"
        },
}
