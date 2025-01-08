import random, tsn_databases, sbs_tools, sbs
import Names.Names
import simulation
from Objects import CrewData
from Names import Names
from Communications import NPC_faces

availableShuttles = {}
activeShips = {}

activeShuttles = {}
activeGameMasters = {}

activeStations = {}
activeJumpPoints = {}
activeObjects = {}
activeNPCs = {} #ID, Object of NPCs


def setupOrdnance():
    for key, value in tsn_databases.ordnanceDatabase.items():
        sbs.set_shared_string(key,
                              f"gui_text:{key};"
                              f"speed:{value.get('speed')};"
                              f"lifetime:{value.get('lifetime')};"
                              f"flare_color:{value.get('flare_color')};"
                              f"trail_color:{value.get('trail_color')};"
                              f"warhead:{value.get('warhead')[0]};"
                              f"blast_radius:{value.get('warhead')[1]};"
                              f"damage:{value.get('damage')};"
                              f"explosion_size:{value.get('explosion_size')};"
                              f"explosion_color:{value.get('explosion_color')};"
                              f"behavior:{value.get('behavior')};"
                              f"energy_conversion_value:{value.get('energy_conversion_value')}")


setupOrdnance()


class SimulationObject:
    def __init__(self, name, behav, hull, side, **kwargs):
        self.ObjectName = name
        self.ObjectBehaviour = behav
        self.ObjectHullClass = hull
        self.ObjectSide = side
        self.ObjectState = "Readying"
        self.initpos = (0, 0, 0)
        if "position" in kwargs.keys():
            self.initpos = kwargs.get("position")

    def SpawnObject(self, sim, **kwargs):
        self.sim = sim
        self.ObjectID = sim.create_space_object(self.ObjectBehaviour, self.ObjectHullClass, 0xfff0)
        self.Object = sim.get_space_object(self.ObjectID)
        self.ObjectData = self.Object.data_set
        self.Object.side = self.ObjectSide
        sim.reposition_space_object(self.Object, self.initpos[0], self.initpos[1], self.initpos[2])
        self.ObjectState = "Active"

    def ObjectEventTriggers(self, event):
        pass

    def ObjectTickMonitors(self):
        pass

    def ObjectEventMonitors(self, event):
        pass


class SpaceObject(SimulationObject):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)
        self.initCargo = list(tsn_databases.masterDatabase.keys()) #used only once to compile the cargo hold
        self.Officers = set()
        self.setupAllies()

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectTags = self.gathertags() #returns a list of tags from the tsn_databases, ShipProperties database
        self.Cargo = CargoHold(self)
        self.CrewMembers = Crew(self)

    def gathertags(self):
        data = tsn_databases.allProperties.get(self.ObjectHullClass)
        if data:
            return data.get("tags")
        else:
            return []

    def setupAllies(self):
        self.Faction = None
        for key, value in tsn_databases.factions.items():
            if self.ObjectSide in value:
                self.Faction = key
                break

    def updateclientConsoles(self):
        for client in self.Officers:
            if not client.myStatus:
                sbs_tools.mrender(client, "")
            else:
                sbs_tools.crender(client, "")

    def updateclientGUIElement(self, GUITag):
        for client in self.Officers:
            if not client.myStatus:
                sbs_tools.mrender(client, GUITag)
            else:
                sbs_tools.crender(client, GUITag)

    def setupsystems(self):
        self.shipSystems = {
            "Emissions": EmissionsSystems(self),
            "ShuttleBay": ShuttleBaySystems(self),
            "Communications": CommsSystems(self)
        }

    def ObjectEventMonitors(self, event):
        for system in self.shipSystems.values():
            system.SystemEventMonitors(event)

    def ObjectTickMonitors(self):
        for system in self.shipSystems.values():
            system.SystemTickMonitors()


class CargoHold:
    def __init__(self, SpaceObject):
        self.SpaceObject = SpaceObject
        self.CargoHold = {}
        #self.compileCargoHold(self.SpaceObject.initCargo)

    def compileCargoHold(self, cargoList):
        for cargotype in cargoList:
            count = random.randint(1, 10)
            self.addCargo(cargotype)
            cargodata = self.CargoHold.get(cargotype)
            cargodata.update({'count': count})

    def addCargo(self, cargotype, **kwargs):
        data = tsn_databases.masterDatabase.get(cargotype)
        cargodata = data.copy()
        if "count" in kwargs:
            count = kwargs.get("count")
        else:
            count = 1
        cargodata.update({'count': count})
        self.CargoHold.update({cargotype: cargodata})


class Crew:
    def __init__(self, spaceObj):
        self.Ship = spaceObj
        self.shipCrew = {}
        self.activeCrew = {}

    def createteams(self, data, **kwargs):
        if "location" in kwargs:
            location = kwargs.get("location")
        else:
            location = "Crew Quarters"
        teamsdata = data.get("Teams")
        for key, value in teamsdata.items():
            for n in range(value):
                newteam = Team(key, location)
                self.shipCrew.update({id(newteam): newteam})


class Team:
    def __init__(self, teamtype, location):
        temp = CrewData.teams.get(teamtype)
        self.teamdata = temp.copy()
        orders = self.teamdata.get("orders")
        completeOrders = ["Report to Medical Bay",
                          "Report to Shuttle Bay",
                          "Report to Crew Quarters",
                          "Report to Guest Quarters",
                          "Report to Brig"]
        self.teamdata.update({"orders": completeOrders + orders})
        self.teamdata.update({"ID": id(self),
                         "Name": Names.teamleaderDatabase.pop(),
                         "Type": teamtype,
                         "OK": temp.get("strength"),
                         "LightWound": 0,
                         "SeriousWound": 0,
                         "Killed": 0,
                         "healing": False,
                         "working": [False, 0],
                         "gridObj": None,
                         "report": ["None", 0],
                         "location": location,
                         "currentOrder": ""})
        self.configureTeam()

    def configureTeam(self):
        if self.teamdata.get("Type") == "Evacuees":
            strength = random.randint(1, 8)
            self.teamdata.update({"strength": strength})
            lwound = random.randint(1, strength)
            swound = random.randint(0, strength - lwound)
            ok = strength - swound - lwound
            self.teamdata.update({
                "OK": ok,
                "LightWound": lwound,
                "SeriousWound": swound,
                "Killed": 0,
            })


class ShipSystems:

    def __init__(self, shipObj):
        self.Ship = shipObj

    def SystemEventTriggers(self, event):
        pass

    def SystemTickMonitors(self):
        pass

    def SystemEventMonitors(self, event):
        pass


class ShuttleBaySystems(ShipSystems):
    def __init__(self, shipObj):
        super().__init__(shipObj)
        self.BayStatus = False


class EmissionsSystems(ShipSystems):
    def __init__(self, shipObj):
        super().__init__(shipObj)
        self.EmissionLevel = 0
        self.EmissionCoeff = 1

    def SystemTickMonitors(self):
        self.calculateEmissionLvl()

    def calculateEmissionLvl(self):
        general = self.GeneralEmissions()
        targeting = self.TargetingMonitor()
        shields = self.ShieldMonitor()
        sensors = self.ScanMonitor()
        engines = self.EngineMonitor()
        total = general + targeting + shields + sensors + engines
        self.EmissionLevel = total * self.EmissionCoeff

    def GeneralEmissions(self):
        Emission = 1
        return Emission

    def TargetingMonitor(self):
        targeting = self.Ship.ObjectData.get("weapon_target_UID", 0)
        if not targeting:
            targeting = self.Ship.ObjectData.get("target_id", 0)
        Emission = 0
        if targeting:
            if targeting > 0:
                Emission = 1
        return Emission

    def ShieldMonitor(self):
        shieldState = self.Ship.ObjectData.get("shields_raised_flag", 0)
        Emission = 0
        if shieldState:
            Emission = 1
        return Emission

    def ScanMonitor(self):
        Emission = 1
        return Emission

    def EngineMonitor(self):
        Emission = 1
        return Emission


class NPCEmissionsSystem(EmissionsSystems):
    def __init__(self, shipObj):
        super().__init__(shipObj)

    def SystemTickMonitors(self):
        super().SystemTickMonitors()
        self.setVisDistance()

    def setVisDistance(self):
        pass
        """distance = self.EmissionLevel * 2500
        print(f"{self.Ship.ObjectName} vis distance = {distance}")
        self.Ship.ObjectData.set("elite_low_vis", 1, 0)
        self.Ship.ObjectData.set("elite_low_vis_distance", distance, 0)"""


class CommsSystems(ShipSystems):
    def __init__(self, shipObj):
        super().__init__(shipObj)
        self.setface()
        self.commsDirectory = {} # who I am connected to
        self.commsAnalysis = {} # who I am analysing
        self.commsConnections = {} # who is connected to me
        self.securityLevel = 3
        self.commsEncryption = {
            "Quantum Key": random.randint(1001, 9999),
            "Hyperwave Frequency": random.randint(101, 999),
            "Oscillation": random.randint(10001, 99999)
        }
        self.commsSystemHack = [0,""]

    def SystemTickMonitors(self):
        killlist = []
        for key, listdata in self.commsAnalysis.items():
            time = listdata[1]
            if time < sbs.app_seconds() and simulation.simul.space_object_exists(key):
                ship = listdata[0]
                shipComms = ship.shipSystems.get("Communications")
                if listdata[2]:
                    message = "Analysis Complete^^Encryption data...^"
                    for type, code in shipComms.commsEncryption.items():
                        message += f" - {type}: {code}^"
                    self.commsDirectory.update({key: listdata[0]})
                    if self.Ship.ObjectData.get("comms_target_UID", 0) == key:
                        shipComms.connectMenu(self.Ship.ObjectID) # prompt the target ship to resend its menu
                else:
                    message = "Analysis Failed^"
                message += "^"
                sbs.send_comms_message_to_player_ship(self.Ship.ObjectID, key, "gen #fff 0 0", ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                killlist.append(key)
            elif not simulation.simul.space_object_exists(key):
                killlist.append(key)

        for key in killlist:
            self.commsAnalysis.pop(key)

    def SystemEventTriggers(self, event):
        if "comms_sorted_list" in event.value_tag and self.Ship.ObjectID == event.selected_id:
            # this happens when the ship is selected on the comms list
            if event.selected_id != event.origin_id:
                playerShip = activeShips.get(event.origin_id)
                playerCommsSystems = playerShip.shipSystems.get("Communications")
                if self.Ship.ObjectID in playerCommsSystems.commsDirectory.keys():
                    # if a connection has already been established, then show who this is
                    self.connectMenu(event.origin_id)
                else:
                    self.initialCommsConnection(event.origin_id)
            elif event.selected_id == event.origin_id:
                sbs.send_comms_selection_info(event.origin_id, "", "", "")

        if "press_comms_button" in event.tag and self.Ship.ObjectID == event.selected_id:
            playerShip = activeShips.get(event.origin_id)
            playerCommsSystems = playerShip.shipSystems.get("Communications")
            match event.sub_tag:
                case "Hail":
                    playerCommsSystems.commsDirectory.update({self.Ship.ObjectID: self.Ship}) # add to the hailing ship's directory
                    sbs.send_comms_selection_info(event.origin_id, self.Ship.ObjectData.get("faceDesc", 0), "White", self.Ship.ObjectData.get("name_tag", 0))
                    message = "Channel Open"
                    sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, self.Ship.ObjectData.get("faceDesc", 0), self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                    self.connectMenu(event.origin_id)
                case "Analyse":
                    success = False
                    if random.randint(0, 10) > self.securityLevel:
                        success = True
                    playerCommsSystems.commsAnalysis.update({self.Ship.ObjectID: [self.Ship, sbs.app_seconds() + 10, success]})
                    message = "Operation Initiated^...Accessing database^...Analysing signal^...Gathering Additional data"
                    sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, "gen #fff 0 0", self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                case _:
                    pass
            if "station" in self.Ship.ObjectTags:
                self.stationTriggers(event)
            elif playerCommsSystems.Faction == self.Faction:
                pass
            else:
                self.hackingTriggers(event)

    def SystemEventMonitors(self, event):
        pass

    def setface(self):
        match self.Ship.ObjectSide:
            case "Kralien":
                self.Faction = "Hegemony"
                face = NPC_faces.random_kralien()
            case "USFP":
                self.Faction = "USFP"
                face = NPC_faces.random_terran(civilian=True)
            case "TSN":
                self.Faction = "USFP"
                face = NPC_faces.random_terran()
            case "Torgoth":
                self.Faction = "Hegemony"
                face = NPC_faces.random_torgoth()
            case "Arvonian":
                self.Faction = "Hegemony"
                face = NPC_faces.random_arvonian()
            case "Skaraan":
                self.Faction = "Hegemony"
                face = NPC_faces.random_skaraan()
            case "Ximni":
                self.Faction = "Ximni"
                face = NPC_faces.random_zimni()
            case _:
                face = NPC_faces.random_terran()
        self.Ship.ObjectData.set("faceDesc", face, 0)

    def initialCommsConnection(self, origin_id):
        sbs.send_comms_selection_info(origin_id, "gen #fff 0 0", "White", self.Ship.ObjectData.get("name_tag", 0))
        playerShip = activeShips.get(origin_id)
        playerCommsSystems = playerShip.shipSystems.get("Communications")
        if playerCommsSystems.Faction == self.Faction:
            sbs.send_comms_button_info(origin_id, "#00FFFF", "Hail", "Hail")
        else:
            sbs.send_comms_button_info(origin_id, "#C72100", "Analyse", "Analyse")

    def connectMenu(self, origin_id):
        playerShip = activeShips.get(origin_id)
        playerCommsSystems = playerShip.shipSystems.get("Communications")
        if playerCommsSystems.Faction == self.Faction:
            sbs.send_comms_selection_info(origin_id, self.Ship.ObjectData.get("faceDesc", 0), "White", self.Ship.ObjectData.get("name_tag", 0))
            if "station" in self.Ship.ObjectTags:
                self.stationMenu(origin_id)
            else:
                sbs.send_comms_button_info(origin_id, "#00FFFF", "Send Hello", "Hello")
        else:
            # this is shown when comms have been analysed
            sbs.send_comms_selection_info(origin_id, "gen #fff 0 0", "White", self.Ship.ObjectData.get("name_tag", 0))
            if self.Ship.ObjectID == playerCommsSystems.commsSystemHack[0]:
                if playerCommsSystems.commsSystemHack[1] == "quantumcypher":
                    sbs.send_comms_button_info(origin_id, "#00FFFF", "Transmit engine virus", "engvirushack")
                    sbs.send_comms_button_info(origin_id, "#00FFFF", "Transmit weapons virus", "weapvirushack")
                    sbs.send_comms_button_info(origin_id, "#00FFFF", "Transmit shield virus", "shivirushack")
                elif playerCommsSystems.commsSystemHack[1] == "hypermatrix":
                    sbs.send_comms_button_info(origin_id, "#00FFFF", "Access network", "networkhack")
                elif playerCommsSystems.commsSystemHack[1] == "starengine":
                    sbs.send_comms_button_info(origin_id, "#00FFFF", "Capture data", "datahack")
                sbs.send_comms_button_info(origin_id, "#00FFFF", "Drop connection", "droplink")
            else:
                sbs.send_comms_button_info(origin_id, "#00FFFF", "Quantum Key Cipher", "quantumcypher")
                sbs.send_comms_button_info(origin_id, "#00FFFF", "StarCypher Engine", "starengine")
                sbs.send_comms_button_info(origin_id, "#00FFFF", "Hyperwave Matrix", "hypermatrix")

    def stationMenu(self, origin_id):
        sbs.send_comms_button_info(origin_id, "yellow", "Query Request", "Station-Request-Details")
        sbs.send_comms_button_info(origin_id, "yellow", "Sign Off", "Station-Sign-Off")

    def stationTriggers(self, event):
        match event.sub_tag:
            case "Station-Request-Details":
                message = f"Query Request   ^Dock Access Code: {self.Ship.ObjectData.get('dockaccess', 0)}^"
                message += "^Available Facilities:^"
                for facility in self.Ship.facilities:
                    message += f" - {facility}^"
                if "Restock" in self.Ship.facilities:
                    message += "^We can replenish our supplies at your request"
                message += "^Supplies^"
                cargo = self.Ship.Cargo.CargoHold
                for name, data in cargo.items():
                    message += f" - {name}: {data.get('count')}^"
                sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, self.Ship.ObjectData.get("faceDesc", 0), self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")

            case "Station-Sign-Off":
                playerShip = activeShips.get(event.origin_id)
                playerCommsSystems = playerShip.shipSystems.get("Communications")
                playerCommsSystems.commsDirectory.pop(self.Ship.ObjectID)
                message = "Sign Off   ^Until next time!"
                sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, self.Ship.ObjectData.get("faceDesc", 0), self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                self.initialCommsConnection(event.origin_id)

    def hackingTriggers(self, event):
        probability = random.randint(0, 100)
        match event.sub_tag:
            case "quantumcypher":
                if probability > 50 and self.commsEncryption.get("Quantum Key") < 8000:
                    #access to enable distribution of viruses
                    playerShip = activeShips.get(event.origin_id)
                    playerCommsSystems = playerShip.shipSystems.get("Communications")
                    playerCommsSystems.commsSystemHack = [self.Ship.ObjectID, "quantumcypher"]
                    message = "System accessed"
                    sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, "gen #fff 0 0", self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                    self.connectMenu(event.origin_id)
            case "starengine":
                if probability > 50 and self.commsEncryption.get("Hyperwave Frequency") > 200:
                    # access to enable capture of data
                    playerShip = activeShips.get(event.origin_id)
                    playerCommsSystems = playerShip.shipSystems.get("Communications")
                    playerCommsSystems.commsSystemHack = [self.Ship.ObjectID, "starengine"]
                    message = "System accessed"
                    sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, "gen #fff 0 0", self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                    self.connectMenu(event.origin_id)
            case "hypermatrix":
                if probability > 50 and 70000 > self.commsEncryption.get("Oscillation") > 30000:
                    # access to enable access to sensor data
                    playerShip = activeShips.get(event.origin_id)
                    playerCommsSystems = playerShip.shipSystems.get("Communications")
                    playerCommsSystems.commsSystemHack = [self.Ship.ObjectID, "hypermatrix"]
                    message = "System accessed"
                    sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, "gen #fff 0 0", self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                    self.connectMenu(event.origin_id)
            case "networkhack":
                message = f"Network accessed^Gathering sensor data^"
                sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, "gen #fff 0 0", self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                for player, ship in activeShips.items():
                    index = ship.ObjectData.get("num_extra_scan_sources", 0) + 1
                    ship.ObjectData.set("extra_scan_source", self.Ship.ObjectID, index)
                    ship.ObjectData.set("num_extra_scan_sources", index, 0)
                self.resetHackingMenu(event)
            case "datahack":
                message = f"Downloading internal manifests^"
                sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, "gen #fff 0 0", self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
                self.resetHackingMenu(event)
            case "droplink":
                self.resetHackingMenu(event)
        if event.sub_tag in ["engvirushack", "weapvirushack", "shivirushack"]:
            systems = {}
            if event.sub_tag == "engvirushack":
                systems.update({"Manoeuvre": "turnRate"})
                systems.update({"Impulse": "throttle"})
            elif event.sub_tag == "weapvirushack":
                systems.update({"Torpedoes": "drone_launch_timer"})
                systems.update({"Beams": "beamCycleTime"})
            elif event.sub_tag == "shivirushack":
                systems.update({"Shields": "shield_max_val"})
            hackedSystem = random.choice(list(systems.keys()))
            cycles = 1
            if systems.get(hackedSystem) == "beamCycleTime":
                cycles = self.Ship.ObjectData.get("beamCount", 0)
            elif systems.get(hackedSystem) == "shield_max_val":
                cycles = self.Ship.ObjectData.get("shield_count", 0)
            for cycle in range(cycles):
                self.Ship.ObjectData.set(systems.get(hackedSystem), 0, cycle)
            self.Ship.Damage.damagedsystems.add(hackedSystem)
            message = f"Virus transmitted.... ^Target {hackedSystem} disrupted"
            sbs.send_comms_message_to_player_ship(event.origin_id, self.Ship.ObjectID, "gen #fff 0 0", self.Ship.ObjectData.get("name_tag", 0), "#00FFFF", message, "White")
            self.resetHackingMenu(event)

    def resetHackingMenu(self, event):
        playerShip = activeShips.get(event.origin_id)
        playerCommsSystems = playerShip.shipSystems.get("Communications")
        playerCommsSystems.commsSystemHack = [0, ""]
        playerCommsSystems.commsDirectory.pop(self.Ship.ObjectID)
        self.initialCommsConnection(event.origin_id)

    def shipTriggers(self, event):
        match event.sub_tag:
            case _:
                pass
