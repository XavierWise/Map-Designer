import sbs

import simulation
from Terrain import TerrainHandling


def MapSelection(clientObj):
    sbs.send_gui_image(clientObj.clientID, "", f"system-menu-background", "image: ../missions/TSN Cosmos/Images/GMSystembackground; color: white", 0, 0, 100, 100)
    for name, datalist in TerrainHandling.allsystems.items():
        if name == simulation.startSystem:
            colour = "#00FF2A"
        elif datalist[1] == "USFP":
            colour = "#33DDFF"
        else:
            colour = "red"
        coordinate = datalist[0]
        x = 47.5 + coordinate[0]
        y = 47.5 + coordinate[2]
        sbs.send_gui_rawiconbutton(clientObj.clientID, "", f"selsyst-{name}", f"icon_index: 01; color: {colour}", x, y, x + 5, y + 5)
        sbs.send_gui_text(clientObj.clientID, "", f"system-label-{name}", f"text: {name}; font: smallest; justify: center", x, y + 5, x + 5, y + 8)
    sbs.send_gui_button(clientObj.clientID, "", "load-system", "text: Load; font: gui-1", 92, 5, 100, 8)
    sbs.send_gui_button(clientObj.clientID, "", "save-system", "text: Save; font: gui-1", 92, 10, 100, 13)


def NewSystemCreation(clientObj):
    pass


#thie menuData is the dictionary of all the main menus and related submenus
menuData = {
    "Map Selection": {
        "subMenus": {
            "New": {"subMenuState": "off",
                       "render": NewSystemCreation},
            "Edit": {"subMenuState": "on",
                       "render": MapSelection}
        }
    }
}
