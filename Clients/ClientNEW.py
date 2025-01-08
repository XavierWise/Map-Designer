import sbs, simulation, sbs_tools

from Clients import ClientConsoles, ClientMenusNEW
from Objects import SpaceObjects
from Objects import GameMasterObject as GM
from NPC_Ships import AI_Commanders
from Terrain import TerrainHandling


activeClients = {}


def setupClient(client):
    # this sets up a brand new client when it first joins
    newclient = Client(client)
    activeClients.update({newclient.clientID: newclient})


class Server:
    def __init__(self, clientID):
        self.clientID = clientID
        self.myRole = "Server"
        self.serverModes = {
            "server-GM-mode": {"name": "GM Mode",
                               "state": "on"}
        }
        self.myMenu = ClientMenusNEW.MapDesignerMenu(self)
        sbs_tools.mrender(self, "")
        self.ListPosition = 0

    def clientMonitors(self, event):
        if "load-system" in event.sub_tag:
            simulation.HandleSimulationStart()
        if "save-system" in event.sub_tag:
            TerrainHandling.saveData(simulation.startSystem)


class Client:
    def __init__(self, clientID):
        self.clientID = clientID
        self.myStatus = False
        self.myConsoles = ClientConsoles.Consoles(self)
        self.myRole = "Map"
        self.myShip = GM.GMObject("GameMaster", "behav_playership", "invisible", "CiC")
        self.myShip.Officers = self
        controls = self.myConsoles.constructConsoleData("GM Controls")
        self.myConsoles.consoleData.update({"GM Controls": controls})
        self.ListPosition = 0
        self.SpawnNewGMObj()
        sbs_tools.crender(self, "")

    def clientMonitors(self, event):
        self.hotkeyTriggers(event)

    def assigntoShip(self, ObjectID):
        sbs.assign_client_to_ship(self.clientID, ObjectID)
        first = list(self.myConsoles.consoleData.keys())
        firstconsole = self.myConsoles.consoleData.get(first[0])
        firstconsole.update({"mainConsoleState": "on"})
        self.myConsoles.setupSubConsoles()
        sbs_tools.crender(self, "")

    def SpawnNewGMObj(self):
        self.myShip.SpawnObject(simulation.simul)  # spawn the new GM object in game
        self.myCommsSelection = self.myShip.ObjectID
        self.myShip.addscansources()
        sbs.assign_client_to_ship(self.clientID, self.myShip.ObjectID)
        first = list(self.myConsoles.consoleData.keys())
        firstconsole = self.myConsoles.consoleData.get(first[0])
        firstconsole.update({"mainConsoleState": "on"})
        self.myConsoles.setupSubConsoles()

    def hotkeyTriggers(self, event):
        if "GM-deleteObj" in event.sub_tag:
            menuSystems = self.myShip.shipSystems.get("Menus")
            selectionPanel = menuSystems.selectionPanel
            selectionPanel.paneldata.clear()
            moveSystems = self.myShip.shipSystems.get("Movement")
            moveSystems.selectedObj = -1

            target = self.myShip.ObjectData.get("science_target_UID", 0)
            sbs.delete_object(int(target))
            for GM, GMObj in SpaceObjects.activeGameMasters.items():
                GMObj.ObjectData.set("science_target_UID", -1, 0)

            # clear the data of the selection panel
            sbs_tools.crender(self, "")

        if "GM-deleteGrp" in event.sub_tag:
            menuSystems = self.myShip.shipSystems.get("Menus")
            selectionPanel = menuSystems.selectionPanel
            selectionPanel.paneldata.clear()
            moveSystems = self.myShip.shipSystems.get("Movement")
            moveSystems.selectedObj = -1

            target = self.myShip.ObjectData.get("science_target_UID", 0)

            if SpaceObjects.activeNPCs.get(int(target)):
                ship = SpaceObjects.activeNPCs.get(int(target))
                AICommanderID = ship.ObjectData.get("Fleet Commander", 0)
                AICommanderObj = AI_Commanders.commanders.get(AICommanderID)

                for Obj in AICommanderObj.FleetMembers.values():
                    sbs.delete_object(Obj.ObjectID)

                for GM, GMObj in SpaceObjects.activeGameMasters.items():
                    GMObj.ObjectData.set("science_target_UID", -1, 0)
            # clear the data of the selection panel
            sbs_tools.crender(self, "")

    def EngineeringPresetManagementTriggers(self, event):
        pass

    def EngineeringPresetTriggers(self, event):
        pass

    def ShuttleBayTriggers(self, event):
        pass

    def NavigationMenuTriggers(self, event):
        pass

    def CrewManagementTriggers(self, event):
        pass

    def AMCManagementTriggers(self, event):
        pass

    def LogisticsTriggers(self, event):
        pass

    def SensorSuiteTriggers(self, event):
        pass

    def MagSystemsTriggers(self, event):
        pass
