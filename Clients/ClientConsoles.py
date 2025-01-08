import sbs, sbs_tools
from Clients import ConsoleDatabase


class Consoles:
    def __init__(self, clientObj):
        self.clientObj = clientObj
        #this consoleData is built from the main consoleDatabase.
        #keys and values are copied, based upon the client's console selections in the main menu
        self.consoleData = {}
        self.subConsoles = {}
        self.storedConsoleData = {}
        self.setNavpoint = False
        self.AMCLibrarySel = "--"

    def setupConsole(self, choice):
        #when a client selects a console, the data is added to their myConsoles.consoleData dictionary
        if choice in self.consoleData.keys():
            #this clears a console that is deselected
            del self.consoleData[choice]
            for shipConsole in self.consoleData.keys():
                if shipConsole not in self.clientObj.myShip.consoles:
                    self.clientObj.myStatus = False
        else:
            #create a new copy of the dictionary to ensure it is unique for each client.
            newaddition = self.constructConsoleData(choice)
            self.consoleData.update({choice: newaddition})

    def setupSubConsoles(self):
        for key, value in self.consoleData.items():
            if value.get("mainConsoleState") == "on":
                self.subConsoles = value.get("subConsoles")

    def constructConsoleData(self, choice):
        #this ensures an copy of the consoleData is created to avoid conflicts with shared dictionaries.
        newConsoleData = {}
        newsubconsoles = {}
        consoleChoice = ConsoleDatabase.consoleData.get(choice)
        mainstate = consoleChoice.get("mainConsoleState")
        subconsoles = consoleChoice.get("subConsoles")
        for subconsole, data in subconsoles.items():
            newsubdata = {}
            state = data.get("subConsoleState")
            render = data.get("render")
            newsubdata.update({"subConsoleState": state})
            newsubdata.update({"render": render})
            newsubconsoles.update({subconsole: newsubdata.copy()})
        newConsoleData.update({"subConsoles": newsubconsoles.copy()})
        newConsoleData.update({"mainConsoleState": mainstate})
        return newConsoleData.copy()

    def resetConsoleData(self):
        self.consoleData.clear()
        sbs.send_client_widget_list(self.clientObj.clientID, "", "")
        if self.setNavpoint:
            self.setNavpoint = False

    def consoleTriggers(self, event):
        #these triggers are simply to change the console being displayed to the client.
        #consoleTriggers only runs whilst the game is running
        #console triggers are only triggered by the specific client
        if self.clientObj.myStatus:
            #when the client is active and in game, these change between the different main consoles.
            if event.sub_tag in self.consoleData.keys():
                for data in self.consoleData.values():
                    data.update({"mainConsoleState": "off"})
                data = self.consoleData.get(event.sub_tag)
                data.update({"mainConsoleState": "on"})
                self.subConsoles = data.get("subConsoles")
                sbs_tools.crender(self.clientObj, "")

        if event.sub_tag in self.subConsoles.keys():
            #this ensures the client can change between different sub-consoles.
            for subConsole in self.subConsoles.values():
                subConsole.update({"subConsoleState": "off"})
            subConsole = self.subConsoles.get(event.sub_tag)
            subConsole.update({"subConsoleState": "on"})
            sbs_tools.crender(self.clientObj, "")

        self.clientObj.EngineeringPresetTriggers(event)
        self.clientObj.LogisticsTriggers(event)
        self.clientObj.EngineeringPresetManagementTriggers(event)
        self.clientObj.ShuttleBayTriggers(event)
        self.clientObj.NavigationMenuTriggers(event)
        self.clientObj.CrewManagementTriggers(event)
        self.clientObj.AMCManagementTriggers(event)
        self.clientObj.SensorSuiteTriggers(event)
        self.clientObj.MagSystemsTriggers(event)

    def consoleRender(self):
        if self.clientObj.myStatus:
            # send the header displaying the available consoles
            self.consoleMainOptions()
            #send the footer displaying the available subconsoles
            self.consoleSubOptions()
        #render the selected subconsole on the screen
        self.consoleSubRender()

    def consoleMainOptions(self):
        #renders the buttons at the top showing all the available main consoles
        xpos = 20
        ypos = 0
        for console, data in self.consoleData.items():
            sbs.send_gui_checkbox(self.clientObj.clientID, "", console, f"text:{console};state:{data.get('mainConsoleState')}", xpos, ypos, xpos + 14, ypos + 3)
            xpos += 15

    def consoleSubOptions(self):
        #renders the buttons at the bottom of the currently selected main console
        xpos = 0.5
        ypos = 96
        for console, data in self.consoleData.items():
            if data.get("mainConsoleState") == "on":
                for subConsole, subData in data.get("subConsoles").items():
                    sbs.send_gui_checkbox(self.clientObj.clientID, "", subConsole, f"text:{subConsole};state:{subData.get('subConsoleState')}", xpos, ypos, xpos + 24, ypos + 4)
                    xpos += 25

    def consoleSubRender(self):
        #renders the sub-console selected
        for console, data in self.consoleData.items():
            if data.get("mainConsoleState") == "on":
                subConsoles = data.get("subConsoles")
                for subConsole, subData in subConsoles.items():
                    if subData.get("subConsoleState") == 'on':
                        subData.get("render")(self.clientObj)
