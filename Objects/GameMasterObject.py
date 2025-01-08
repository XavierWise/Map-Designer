import sbs, sbs_tools

import Clients.ClientNEW
from Objects import SpaceObjects
from GM_Data import GMConsoleFunctions
from NPC_Ships import AI_Commanders
from Clients import Console_GUI


class GMObject(SpaceObjects.SimulationObject):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)
        self.consoles = ["GM Controls"]
        self.Officers = None

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.setupsystems()
        SpaceObjects.activeGameMasters.update({self.ObjectID: self})
        self.ObjectData.get("ship_base_scan_range", 0)
        self.ObjectData.set("ship_base_scan_range", 1000000, 0)
        self.ObjectData.get("ship_base_scan_range", 0)

    def addscansources(self):
        index = self.ObjectData.get("num_extra_scan_sources", 0)
        for station, value in SpaceObjects.activeStations.items():
            # currently this applies to all stations, no matter what side
            self.ObjectData.set("extra_scan_source", station, index)
            index += 1
        for shuttle, value in SpaceObjects.availableShuttles.items():
            # currently this applies to all shuttles, no matter what side
            self.ObjectData.set("extra_scan_source", shuttle, index)
            index += 1
        for ship, value in SpaceObjects.activeShips.items():
            self.ObjectData.set("extra_scan_source", ship, index)
            index += 1
        self.ObjectData.set("num_extra_scan_sources", index, 0)

    def setupsystems(self):
        self.shipSystems = {
            "Movement": MovementSystems(self),
            "Menus": Menus(self)
        }

    def ObjectEventTriggers(self, event):
        for system in self.shipSystems.values():
            system.SystemEventTriggers(event)

    def ObjectTickMonitors(self):
        for system in self.shipSystems.values():
            system.SystemTickMonitors()

    def ObjectEventMonitors(self, event):
        for system in self.shipSystems.values():
            system.SystemEventMonitors(event)

    def updateclientConsoles(self):
        sbs_tools.crender(self.Officers, "")


class ShipSystems:
    def __init__(self, shipObj):
        self.Ship = shipObj

    def SystemEventTriggers(self, event):
        pass

    def SystemTickMonitors(self):
        pass

    def SystemEventMonitors(self, event):
        pass


class MovementSystems(ShipSystems):
    def __init__(self, shipObj):
        super().__init__(shipObj)
        self.scrollSpeed = 100
        self.NavMenu = "--"
        self.Moveto = True
        self.selectedObj = -1

    def SystemEventTriggers(self, event):
        if event.tag == "select_space_object" and event.sub_tag == "GMControls" and event.value_tag == "science_2d_view" and event.selected_id != event.origin_id:
            if event.extra_extra_tag == "lmb":
                if event.selected_id > 0:
                    self.settarget(event.selected_id)
                else:
                    self.settarget(-1)
            if event.extra_extra_tag == "rmb":
                if self.selectedObj != -1 and self.Ship.sim.space_object_exists(self.selectedObj):
                    object = self.Ship.sim.get_space_object(self.selectedObj)
                    pos = event.source_point
                    self.Ship.sim.reposition_space_object(object, pos.x, pos.y, pos.z)
                    self.settarget(-1)
                else:
                    pos = event.source_point
                    self.Ship.sim.reposition_space_object(self.Ship.Object, pos.x, pos.y, pos.z)

    def settarget(self, selected_id):
        self.selectedObj = selected_id
        self.Ship.ObjectData.set("science_target_UID", selected_id, 0)

    def jumptoSpace(self, event):
        pos = event.source_point
        self.Ship.sim.reposition_space_object(self.Ship.Object, pos.x, pos.y, pos.z)


class Menus(ShipSystems):
    def __init__(self, shipObj):
        super().__init__(shipObj)
        self.selectionPanel = GMConsoleFunctions.SelectionPanel(self.Ship.Officers)
        self.panelDatabase = [self.selectionPanel]
        self.iconbar = GMConsoleFunctions.IconBar(self.Ship.Officers)
        self.autoDisableState = False

    def SystemEventTriggers(self, event):
        for panel in self.panelDatabase:
            panel.Triggers(event)
        self.iconbar.Triggers(event)
        if "auto-disable" in event.sub_tag:
            self.autoDisableState = not self.autoDisableState
            self.Ship.updateclientConsoles()

    def SystemEventMonitors(self, event):
        logisticsmonitors = ["-LogisticsCargo-", "-LogisticsPersonnel-", "-dockedToCargo-", "-dockedToPersonnel-"]
        for x in logisticsmonitors:
            if x in event.sub_tag:
                client = Clients.ClientNEW.activeClients.get(event.client_id)
                if hasattr(client, "myShip"):
                    if client.myShip:
                        if client.myShip.ObjectData.get("dock_base_id", 0) == self.selectionPanel.paneldata.get("ID") or client.myShip.ObjectID == self.selectionPanel.paneldata.get("ID"):
                            self.Ship.updateclientConsoles()
