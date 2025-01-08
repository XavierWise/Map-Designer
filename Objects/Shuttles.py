import sbs, sbs_tools, simulation
from Objects import SpaceObjects, OtherObjects
from Names import Names

TSNShuttles = {
    "Fighter": "tsn_fighter",
    "Cargo Shuttle": "tsn_shuttle",
    "Transport Shuttle": "tsn_shuttle",
    "Ranger": "tsn_fighter",
    "LR Shuttle": "tsn_shuttle",
}

#specific data for different shuttle types available for players to control
shuttleData = {
    "Fighter": {
        "icon": 140,
        "colour": "red",
        "tag": ["fighter", "combat", "usfp"],
        "personnelCap": 1,
        "cargoCap": 1
    },
    "LR Shuttle": {
        "icon": 140,
        "colour": "red",
        "tags": ["shuttle", "noncombat", "usfp"],
        "personnelCap": 5,
        "cargoCap": 5
    },
    "Ranger": {
        "icon": 140,
        "colour": "red",
        "tags": ["fighter", "combat", "usfp"],
        "personnelCap": 1,
        "cargoCap": 2
    },
    "Cargo Shuttle": {
        "icon": 140,
        "colour": "red",
        "tags": ["shuttle", "noncombat", "usfp"],
        "personnelCap": 2,
        "cargoCap": 12
    },
    "Transport Shuttle": {
        "icon": 140,
        "colour": "red",
        "tags": ["shuttle", "noncombat", "usfp"],
        "personnelCap": 4,
        "cargoCap": 5
    }
}


class SoloCraft(SpaceObjects.SpaceObject):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side)
        self.ShuttlePilot = None
        self.ShuttleCallSign = ""
        self.ShuttleType = "Shuttle"
        if "type" in kwargs.keys():
            self.ShuttleType = kwargs.get("type")
        if "parentship" in kwargs.keys():
            self.ParentShip = kwargs.get("parentship")
        self.state = "Docked"

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectData.set("name_tag", self.ShuttleCallSign, 0)
        self.ObjectName = self.ShuttleCallSign
        self.ObjectData.set("call_sign", self.ShuttleCallSign, 0)
        self.ObjectData.set("hull_side", "TSN", 0)
        self.ObjectData.set("hull_name", f"{self.ShuttleType}", 0)

    def updatepilotConsoles(self):
        sbs_tools.crender(self.ShuttlePilot, "")

    # these are now in game functions
    def ObjectEventTriggers(self, event):
        super().ObjectEventTriggers(event)

    def ObjectEventMonitors(self, event):
        super().ObjectEventMonitors(event)

    def ObjectTickMonitors(self):
        super().ObjectTickMonitors()


class Shuttle(SoloCraft):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)
        self.ShuttleCallSign = Names.shuttleDatabase.pop()
        self.PersonnelGo = False
        self.configureshuttle()
        self.JettisonTube = {}
        self.gonogoTimer = 0
        self.CargoPos = 0
        self.PersonnelPos = 0

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        sbs.push_to_standby_list(self.Object)
        SpaceObjects.availableShuttles.update({self.ObjectID: self})
        self.setupsystems()
        #configure the emissions to be much smaller
        emissions = self.shipSystems.get("Emissions")
        emissions.EmissionCoeff = 0.25

    def setupsystems(self):
        self.shipSystems = {
            "Emissions": SpaceObjects.EmissionsSystems(self)
        }

    def configureshuttle(self):
        data = shuttleData.get(self.ShuttleType)
        self.cargoCapacity = data.get("cargoCap")
        self.personnelCapacity = data.get("personnelCap")
        self.CargoHold = {}
        self.Personnel = {}

    #these are now in game functions
    def ObjectEventTriggers(self, event):
        if event.tag == "fighter_requests_dock":
            self.dockShuttle()
        super().ObjectEventTriggers(event)

    def ObjectEventMonitors(self, event):
        if str(self.ObjectID) in event.sub_tag:
            if self.state == "Docked":
                self.loadShuttle(event)
                self.unloadShuttle(event)
            if self.state == "Flight":
                self.Jettison(event)
                self.PrepPersonnelDrop(event)
                self.Capture(event)
        super().ObjectEventMonitors(event)

    def ObjectTickMonitors(self):
        if self.PersonnelGo:
            self.PersonnelDrop()
        super().ObjectTickMonitors()

    def deployShuttle(self, position, clientObj):
        sbs.retrieve_from_standby_list(self.Object)
        self.sim.reposition_space_object(self.Object, position[0], position[1], position[2])
        # pop out of ship list
        self.ParentShip.Shuttles.pop(self.ObjectID)
        self.ShuttlePilot = clientObj
        SpaceObjects.activeShuttles.update({self.ObjectID: self})
        self.state = "Flight"

    def dockShuttle(self):
        #error here - docks all shuttles in range??
        for ping in sbs.broad_test(-500 + self.Object.pos.x, -500 + self.Object.pos.z, 500 + self.Object.pos.x, 500 + self.Object.pos.z, 0xfff0):
            # add in a filter to dock at the nearest
            if ping.unique_ID in SpaceObjects.activeShips.keys():
                spaceObj = SpaceObjects.activeShips.get(ping.unique_ID)
                shuttleBay = spaceObj.shipSystems.get("ShuttleBay")
                if shuttleBay.BayStatus and spaceObj.ObjectState == "Active":
                    if sbs.distance_id(self.ObjectID, ping.unique_ID) < 500:
                        sbs.push_to_standby_list(self.Object)
                        #update the Shuttle list on the ship I have docked with
                        ship = SpaceObjects.activeShips.get(ping.unique_ID)
                        ship.Shuttles.update({self.ObjectID: self})
                        #now update my parent ship
                        self.ParentShip = ship

                        if self.ShuttlePilot:
                            #now configure the shuttle pilot correctly
                            self.ShuttlePilot.myConsoles.resetConsoleData()
                            if self.ParentShip == self.ShuttlePilot.myShip:
                                # if you are docking back at your own ship
                                for console in self.ShuttlePilot.myConsoles.storedConsoleData:
                                    newaddition = self.ShuttlePilot.myConsoles.constructConsoleData(console)
                                    self.ShuttlePilot.myConsoles.consoleData.update({console: newaddition})
                                self.ShuttlePilot.myConsoles.storedConsoleData.clear()
                                self.ShuttlePilot.myShip.Officers.add(self.ShuttlePilot)

                                # set the selected console to Shuttle Bay

                            else:
                                # if you are docking at a different player ship
                                self.ShuttlePilot.mytempDock = self.ParentShip
                                self.ShuttlePilot.mytempDock.Officers.add(self.ShuttlePilot)
                                self.ShuttlePilot.myConsoles.resetConsoleData()
                                newaddition = self.ShuttlePilot.myConsoles.constructConsoleData("Docking Bay")
                                self.ShuttlePilot.myConsoles.consoleData.update({"Docking Bay": newaddition})

                            sbs.assign_client_to_ship(self.ShuttlePilot.clientID, self.ParentShip.ObjectID)
                            for data in self.ShuttlePilot.myConsoles.consoleData.values():
                                data.update({"mainConsoleState": "off"})
                            data = {}
                            if "Shuttle Bay" in self.ShuttlePilot.myConsoles.consoleData.keys():
                                data = self.ShuttlePilot.myConsoles.consoleData.get("Shuttle Bay")
                            elif "Docking Bay" in self.ShuttlePilot.myConsoles.consoleData.keys():
                                data = self.ShuttlePilot.myConsoles.consoleData.get("Docking Bay")
                            data.update({"mainConsoleState": "on"})
                            self.ShuttlePilot.myConsoles.setupSubConsoles()
                            #self.ShuttlePilot.myShuttle = None
                            sbs_tools.crender(self.ShuttlePilot, "")
                        # remove the client from the shuttle
                        self.ShuttlePilot = None
                        SpaceObjects.activeShuttles.pop(self.ObjectID)
                        self.state = "Docked"
                        break

            if ping.unique_ID in SpaceObjects.activeStations.keys():
                spaceObj = SpaceObjects.activeStations.get(ping.unique_ID)
                shuttleBay = spaceObj.shipSystems.get("ShuttleBay")
                if shuttleBay.BayStatus:
                    if sbs.distance_id(self.ObjectID, ping.unique_ID) < 500:
                        sbs.push_to_standby_list(self.Object)
                        # update the Shuttle list on the spaceobject I have docked with
                        station = SpaceObjects.activeStations.get(ping.unique_ID)
                        station.Shuttles.update({self.ObjectID: self})
                        # now update my parent spaceobject
                        self.ParentShip = station

                        if self.ShuttlePilot:
                            # now configure the shuttle pilot correctly
                            self.ShuttlePilot.myConsoles.resetConsoleData()
                            self.ShuttlePilot.mytempDock = self.ParentShip
                            self.ShuttlePilot.mytempDock.Officers.add(self.ShuttlePilot)
                            self.ShuttlePilot.myConsoles.resetConsoleData()
                            newaddition = self.ShuttlePilot.myConsoles.constructConsoleData("Docking Bay")
                            self.ShuttlePilot.myConsoles.consoleData.update({"Docking Bay": newaddition})
                            self.ShuttlePilot.assigntoShip(self.ParentShip.ObjectID)
                            #self.ShuttlePilot.myShuttle = None
                            sbs_tools.crender(self.ShuttlePilot, "")
                        # remove the client from the shuttle
                        self.ShuttlePilot = None
                        SpaceObjects.activeShuttles.pop(self.ObjectID)
                        self.state = "Docked"
                        break

    def loadShuttle(self, event):
        if "-BayPersonnel" in event.sub_tag:
            teamid = event.sub_tag.split("-")[2]
            if self.ParentShip.CrewMembers.shipCrew.get(int(teamid)):
                loadingteam = self.ParentShip.CrewMembers.shipCrew.get(int(teamid))
                loadingteamdata = loadingteam.teamdata
                if loadingteamdata.get("working")[0] == False:
                    for key in range(self.personnelCapacity):
                        if key not in self.Personnel.keys():
                            self.ParentShip.CrewMembers.shipCrew.pop(int(teamid))
                            self.Personnel.update({key: [int(teamid), loadingteam]})
                            self.ParentShip.updateclientConsoles()
                            break

        if "-BayCargo" in event.sub_tag:
            #need to add in a stop if the cargo quantity is 0
            cargoname = event.sub_tag.split("-")[2]
            if self.ParentShip.Cargo.CargoHold.get(cargoname):
                cargo = self.ParentShip.Cargo.CargoHold.get(cargoname)
                cargocount = cargo.get("count")
                if cargocount > 0:
                    for key in range(self.cargoCapacity):
                        if key not in self.CargoHold.keys():
                            loadingcargo = cargo.copy()
                            loadingcargo.update({"count": 1})
                            self.CargoHold.update({key: [cargoname, loadingcargo]})
                            cargo.update({"count": cargocount - 1})
                            if cargo.get("count") == 0:
                                self.ParentShip.Cargo.CargoHold.pop(cargoname)
                            self.ParentShip.updateclientConsoles()
                            break

    def unloadShuttle(self, event):
        if "-ShutPerson" in event.sub_tag:
            key = event.sub_tag.split("-")[2]
            if self.Personnel.get(int(key)):
                unloadteam = self.Personnel.pop(int(key))
                teamdata = unloadteam[1].teamdata
                teamdata.update({"location": "Shuttle Bay"})
                self.ParentShip.CrewMembers.shipCrew.update({unloadteam[0]: unloadteam[1]})
                self.ParentShip.updateclientConsoles()

        if "-ShutCargo" in event.sub_tag:
            key = event.sub_tag.split("-")[2]
            if self.CargoHold.get(int(key)):
                unloadcargo = self.CargoHold.pop(int(key))
                if unloadcargo[0] in self.ParentShip.Cargo.CargoHold.keys():
                    data = self.ParentShip.Cargo.CargoHold.get(unloadcargo[0])
                    shipcount = data.get("count")
                    data.update({"count": shipcount + 1})
                else:
                    self.ParentShip.Cargo.CargoHold.update({unloadcargo[0]: unloadcargo[1]})
                self.ParentShip.updateclientConsoles()

    def Capture(self, event):
        if "shuttle-capture" in event.sub_tag:
            print("capture activated")
            for ping in sbs.broad_test(-200 + self.Object.pos.x, -200 + self.Object.pos.z, 200 + self.Object.pos.x, 200 + self.Object.pos.z, 0xfff0):
                if ping.unique_ID in SpaceObjects.activeObjects.keys():
                    object = SpaceObjects.activeObjects.pop(ping.unique_ID)
                    object.retrieval(self)

    def Jettison(self, event):
        if "ShuttleCar-scroll" in event.sub_tag:
            self.CargoPos = abs(int(event.sub_float))
            self.updatepilotConsoles()

        if "ShuttlePerson-scroll" in event.sub_tag:
            self.PersonnelPos = abs(int(event.sub_float))
            self.updatepilotConsoles()

        if "ShuttleCargo" in event.sub_tag:
            #setting up cargo to be jettisoned
            key = int(event.sub_tag.split("-")[2])
            if len(self.JettisonTube.keys()) < 1:
                if key in self.CargoHold.keys():
                    data = self.CargoHold.get(key) #gather the data about the item
                    self.JettisonTube.update({data[0]: data[1]}) #update the data in the jettison tube
                    self.CargoHold.pop(key) #remove the item from the hold
                    self.updatepilotConsoles()
        if "shuttle-jettisontube-" in event.sub_tag:
            # move the from the tube to the shuttle hold
            item = self.JettisonTube.popitem()
            if isinstance(item[1], SpaceObjects.Team):
                for key in range(self.personnelCapacity):
                    if key not in self.Personnel.keys():
                        self.Personnel.update({key: list(item)})
                        self.JettisonTube.clear()
                        self.updatepilotConsoles()
                        break
            else:
                for key in range(self.cargoCapacity):
                    if key not in self.CargoHold.keys():
                        self.CargoHold.update({key: list(item)})
                        self.JettisonTube.clear()
                        self.updatepilotConsoles()
                        break

        if "shuttle-jettisoncargo" in event.sub_tag:
            newObj = self.JettisonTube.popitem()
            position = (self.Object.pos.x, self.Object.pos.y - 100, self.Object.pos.z)
            if newObj[0] == "Sensor Buoy":
                object = OtherObjects.SensorBuoy(position=position)
                object.SpawnObject(simulation.simul)
            elif newObj[0] == "Comms Relay":
                object = OtherObjects.CommsRelay(position=position)
                object.SpawnObject(simulation.simul)
            else:
                object = OtherObjects.CargoPod(position=position, cargotype=newObj[0])
                object.SpawnObject(simulation.simul)
            self.updatepilotConsoles()

    def PrepPersonnelDrop(self, event):
        #setting up personnel to jump
        if "ShuttlePersonnel" in event.sub_tag:
            key = int(event.sub_tag.split("-")[2])
            if len(self.JettisonTube.keys()) < 1:
                if key in self.Personnel.keys():
                    data = self.Personnel.get(key)
                    self.JettisonTube.update({data[0]: data[1]}) #data 0 is team ID, data1 is team object
                    self.Personnel.pop(key)
                    self.updatepilotConsoles()
        if "shuttle-jumpgreenlight" in event.sub_tag:
            self.PersonnelGo = not self.PersonnelGo
            self.gonogoTimer = sbs.app_seconds() + 30
            self.updatepilotConsoles()

    def PersonnelDrop(self):
        # direct drop onto a base
        if self.gonogoTimer > sbs.app_seconds():
            for ping in sbs.broad_test(-1000 + self.Object.pos.x, -1000 + self.Object.pos.z, 1000 + self.Object.pos.x, 1000 + self.Object.pos.z, 0xfff0):
                if sbs.distance(ping, self.Object) < 200:
                    allObjects = SpaceObjects.activeNPCs | SpaceObjects.activeStations | SpaceObjects.activeShips
                    if allObjects.get(ping.unique_ID):
                        target = allObjects.get(ping.unique_ID)
                        team = list(self.JettisonTube.popitem())
                        target.CrewMembers.shipCrew.update({team[0]: team[1]})
                        data = team[1].teamdata

                        target.updateclientConsoles()
                        self.PersonnelGo = False
                        sbs.send_message_to_player_ship(self.ObjectID, "white", f"{data.get('Name')}: Team Deployed")
                        self.updatepilotConsoles()
        else:
            self.PersonnelGo = False
            self.updatepilotConsoles()


class LifePod(SoloCraft):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        if "client" in kwargs:
            clientObj = kwargs.get("client")
            self.initpos = [clientObj.myShip.Object.pos.x, clientObj.myShip.Object.pos.y, clientObj.myShip.Object.pos.z]
            self.ShuttleCallSign = clientObj.myCallsign
            self.ObjectData.set("name_tag", self.ShuttleCallSign, 0)
            self.ObjectData.set("call_sign", self.ShuttleCallSign, 0)
            self.ShuttlePilot = clientObj
        sim.reposition_space_object(self.Object, self.initpos[0], self.initpos[1], self.initpos[2])
        SpaceObjects.activeShuttles.update({self.ObjectID: self})
        self.setupsystems()
        self.state = "Emergency"

    def setupsystems(self):
        self.shipSystems = {}

    def ObjectEventTriggers(self, event):
        if event.tag == "fighter_requests_dock":
            self.dockPod()
        super().ObjectEventTriggers(event)

    def dockPod(self):
        for ping in sbs.broad_test(-500 + self.Object.pos.x, -500 + self.Object.pos.z, 500 + self.Object.pos.x, 500 + self.Object.pos.z, 0xfff0):
            # add in a filter to dock at the nearest
            if ping.unique_ID in SpaceObjects.activeShips.keys():
                spaceObj = SpaceObjects.activeShips.get(ping.unique_ID)
                shuttleBay = spaceObj.shipSystems.get("ShuttleBay")
                if shuttleBay.BayStatus and spaceObj.ObjectState == "Active":
                    if sbs.distance_id(self.ObjectID, ping.unique_ID) < 500:
                        sbs.push_to_standby_list(self.Object)
                        # update the Shuttle list on the ship I have docked with
                        ship = SpaceObjects.activeShips.get(ping.unique_ID)
                        ship.Shuttles.update({self.ObjectID: self})
                        # now update my parent ship
                        self.ParentShip = ship

                        if self.ShuttlePilot:
                            # now configure the shuttle pilot correctly
                            self.ShuttlePilot.myConsoles.resetConsoleData()
                            if self.ParentShip == self.ShuttlePilot.myShip:
                                # if you are docking back at your own ship
                                for console in self.ShuttlePilot.myConsoles.storedConsoleData:
                                    newaddition = self.ShuttlePilot.myConsoles.constructConsoleData(console)
                                    self.ShuttlePilot.myConsoles.consoleData.update({console: newaddition})
                                self.ShuttlePilot.myConsoles.storedConsoleData.clear()
                                self.ShuttlePilot.myShip.Officers.add(self.ShuttlePilot)

                                # set the selected console to Shuttle Bay

                            else:
                                # if you are docking at a different player ship
                                self.ShuttlePilot.mytempDock = self.ParentShip
                                self.ShuttlePilot.mytempDock.Officers.add(self.ShuttlePilot)
                                self.ShuttlePilot.myConsoles.resetConsoleData()
                                newaddition = self.ShuttlePilot.myConsoles.constructConsoleData("Lifepod Bay")
                                self.ShuttlePilot.myConsoles.consoleData.update({"Lifepod Bay": newaddition})

                            sbs.assign_client_to_ship(self.ShuttlePilot.clientID, self.ParentShip.ObjectID)
                            for data in self.ShuttlePilot.myConsoles.consoleData.values():
                                data.update({"mainConsoleState": "off"})
                            data = self.ShuttlePilot.myConsoles.consoleData.get("Lifepod Bay")
                            data.update({"mainConsoleState": "on"})
                            self.subConsoles = data.get("subConsoles")

                            # self.ShuttlePilot.myShuttle = None
                            sbs_tools.crender(self.ShuttlePilot, "")
                        # remove the client from the shuttle
                        self.ShuttlePilot = None
                        SpaceObjects.activeShuttles.pop(self.ObjectID)
                        self.state = "Docked"
                        break

            if ping.unique_ID in SpaceObjects.activeStations.keys():
                spaceObj = SpaceObjects.activeStations.get(ping.unique_ID)
                shuttleBay = spaceObj.shipSystems.get("ShuttleBay")
                if shuttleBay.BayStatus:
                    if sbs.distance_id(self.ObjectID, ping.unique_ID) < 500:
                        sbs.push_to_standby_list(self.Object)
                        # update the Shuttle list on the spaceobject I have docked with
                        station = SpaceObjects.activeStations.get(ping.unique_ID)
                        station.Shuttles.update({self.ObjectID: self})
                        # now update my parent spaceobject
                        self.ParentShip = station

                        if self.ShuttlePilot:
                            # now configure the shuttle pilot correctly
                            self.ShuttlePilot.myConsoles.resetConsoleData()
                            self.ShuttlePilot.mytempDock = self.ParentShip
                            self.ShuttlePilot.mytempDock.Officers.add(self.ShuttlePilot)
                            self.ShuttlePilot.myConsoles.resetConsoleData()
                            newaddition = self.ShuttlePilot.myConsoles.constructConsoleData("Lifepod Bay")
                            self.ShuttlePilot.myConsoles.consoleData.update({"Lifepod Bay": newaddition})
                            self.ShuttlePilot.assigntoShip(self.ParentShip.ObjectID)
                            # self.ShuttlePilot.myShuttle = None
                            sbs_tools.crender(self.ShuttlePilot, "")
                        # remove the client from the shuttle
                        self.ShuttlePilot = None
                        SpaceObjects.activeShuttles.pop(self.ObjectID)
                        self.state = "Docked"
                        break
