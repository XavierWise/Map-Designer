import sbs, simulation, sbs_tools
from Clients import MenuDatabase


class MapDesignerMenu:
    def __init__(self, clientObj):
        self.clientObj = clientObj
        self.menuData = {}
        self.subMenus = {}
        self.text = ""
        self.setupMenu()
        self.setupSubMenus()

    def setupMenu(self):
        defaultMenu = self.constructMenuData("Map Selection")
        self.menuData = ({"Map Selection": defaultMenu})

    def setupSubMenus(self):
        for key, value in self.menuData.items():
            if value.get("mainMenuState") == "on":
                self.subMenus = value.get("subMenus")

    def constructMenuData(self, choice):
        # this ensures an copy of the menuData is created to avoid conflicts with shared dictionaries.
        newMenuData = {}
        newsubmenus = {}
        menuChoice = MenuDatabase.menuData.get(choice)
        mainstate = "on"
        submenus = menuChoice.get("subMenus")
        for submenus, data in submenus.items():
            newsubdata = {}
            state = data.get("subMenuState")
            render = data.get("render")
            newsubdata.update({"subMenuState": state})
            newsubdata.update({"render": render})
            newsubmenus.update({submenus: newsubdata.copy()})
        newMenuData.update({"subMenus": newsubmenus.copy()})
        newMenuData.update({"mainMenuState": mainstate})
        return newMenuData.copy()

    def menuTriggers(self, event):
        if event.sub_tag in self.menuData.keys():
            # this check is to change between different main menu options
            for data in self.menuData.values():
                data.update({"mainMenuState": "off"})
            data = self.menuData.get(event.sub_tag)
            data.update({"mainMenuState": "on"})
            self.subMenus = data.get("subMenus")
            sbs_tools.mrender(self.clientObj, "")

        if event.sub_tag in self.subMenus.keys():
            # this check is to change between different sub menu options
            for subConsole in self.subMenus.values():
                subConsole.update({"subMenuState": "off"})
            subConsole = self.subMenus.get(event.sub_tag)
            subConsole.update({"subMenuState": "on"})
            sbs_tools.mrender(self.clientObj, "")

        if "selsyst-" in event.sub_tag:
            systemname = event.sub_tag.split("-")[1]
            simulation.startSystem = systemname
            sbs_tools.mrender(self.clientObj, "")



    def menuRender(self):
        self.menuMainOptions()
        #send the footer displaying the available submenus
        self.menuSubOptions()
        #render the selected submenu on the screen
        self.menuSubRender()

    def menuMainOptions(self):
        xpos = 20
        ypos = 0
        for menu, data in self.menuData.items():
            sbs.send_gui_checkbox(self.clientObj.clientID, "", menu, f"text:{menu};state:{data.get('mainMenuState')}", xpos, ypos, xpos + 14, ypos + 3)
            xpos += 15

    def menuSubOptions(self):
        xpos = 0.5
        ypos = 96
        for menu, data in self.menuData.items():
            if data.get("mainMenuState") == "on":
                for subMenu, subData in data.get("subMenus").items():
                    sbs.send_gui_checkbox(self.clientObj.clientID, "", subMenu, f"text:{subMenu};state:{subData.get('subMenuState')}", xpos, ypos, xpos + 24, ypos + 4)
                    xpos += 25

    def menuSubRender(self):
        for menu, data in self.menuData.items():
            if data.get("mainMenuState") == "on":
                subMenu = data.get("subMenus")
                for subMenu, subData in subMenu.items():
                    if subData.get("subMenuState") == 'on':
                        subData.get("render")(self.clientObj)
