import sbs, random, tsn_databases
from Objects import SpaceObjects, Shuttles, CrewData
from NPC_Stations import Station_Damage


def setupStation(name, data):
    hull = "starbase_civil"
    if data.get('hull') in tsn_databases.stationProperties.keys():
        hull = data.get('hull')
    if "USFP" in data.get("sides"):
        newStation = USFPStation(name, "behav_station", hull, "USFP", position=data.get("coordinate"), info=data)
    else:
        newStation = Station(name, "behav_station", hull, random.choice(data.get("sides")), position=data.get("coordinate"), info=data)
    return newStation


class Station(SpaceObjects.SpaceObject):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)
        if "info" in kwargs.keys():
            self.StationInfo = kwargs.get("info")
        self.initCargo = self.StationInfo.get("cargo")

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectData.set("name_tag", self.ObjectName, 0)
        self.stationsetup()
        SpaceObjects.activeStations.update({self.ObjectID: self})
        self.Shuttles = {}
        self.configureshuttles()
        self.CrewMembers = SpaceObjects.Crew(self)
        self.setupsystems()
        self.Damage = Station_Damage.StationDamage(self, self.Object, self.ObjectData)
        emissions = self.shipSystems.get("Emissions")
        emissions.EmissionCoeff = 10
        self.compileCargoHold()
        self.compileTeams()

    def compileCargoHold(self):
        cargo = self.StationInfo.get("cargo")
        for key, value in cargo.items():
            self.Cargo.addCargo(key, count=value)

    def compileTeams(self):
        teams = self.StationInfo.get("teams")
        if teams:
            self.CrewMembers.createteams({"Teams": teams}, location="Shuttle Bay")
        else:
            data = tsn_databases.stationProperties.get(self.ObjectHullClass)
            self.CrewMembers.createteams(data, location="Shuttle Bay")

    def stationsetup(self):
        self.facilitiessetup()
        self.dockingPorts = {}
        self.dockingsetup()

    def configureshuttles(self):
        data = tsn_databases.stationProperties.get(self.ObjectHullClass)
        shuttleData = data.get("Shuttles")
        for type, value in shuttleData.items():
            for x in range(value):
                shuttleclass = Shuttles.TSNShuttles.get(type)
                self.createshuttlecraft(shuttleclass, type)

    def createshuttlecraft(self, shuttleclass, type):
        #first create the shuttle
        NewCraft = Shuttles.Shuttle(None, "behav_playership", shuttleclass, self.ObjectSide, type=type, parentship=self)
        NewCraft.SpawnObject(self.sim)
        self.Shuttles.update({NewCraft.ObjectID: NewCraft})
        #now add the shuttle as a scan source to the player ships
        for ship in SpaceObjects.activeShips.values():
            index = ship.ObjectData.get("num_extra_scan_sources", 0) #issue here if the value is None
            if index == None:
                index = 0
            ship.ObjectData.set("extra_scan_source", NewCraft.ObjectID, index)
            index += 1
            ship.ObjectData.set("num_extra_scan_sources", index, 0)

    def dockingsetup(self):
        if "Docking" in self.facilities:
            if self.StationInfo.get("dockaccesscode") == "Random" or self.StationInfo.get("dockaccesscode") == None or self.StationInfo.get("dockaccesscode") == "":
                randomcode = random.randint(10000, 99999)
                self.ObjectData.set("dockaccess", str(randomcode), 0)
            else:
                self.ObjectData.set("dockaccess", self.StationInfo.get("dockaccesscode"), 0)
        else:
            self.ObjectData.set("dockaccess", "ACCESS UNAVAILABLE", 0)

    def facilitiessetup(self):
        self.facilities = self.StationInfo.get("facilities")
        for facility in self.facilities:
            self.ObjectData.set(facility, True, 0)

    def ObjectTickMonitors(self):
        super().ObjectTickMonitors()
        self.ProcessDockedShips(self.sim)
        self.Damage.damagemonitor()

    def ObjectEventTriggers(self, event):
        for system in self.shipSystems.values():
            system.SystemEventTriggers(event)

    def ProcessDockedShips(self, sim):
        for id in list(self.dockingPorts.keys()):
            dockedship = sim.get_space_object(id)
            dockedShipData = dockedship.data_set
            if self.ObjectData.get("Refuel", 0):
                # refuel
                fuel_value = dockedShipData.get("energy", 0)
                fuel_value += 20
                if fuel_value > 1000:
                    fuel_value = 1000
                dockedShipData.set("energy", fuel_value)

            if self.ObjectData.get("Repair", 0):
                shieldCoeff = dockedShipData.get("repair_rate_shields", 0)
                systemCoeff = dockedShipData.get("repair_rate_systems", 0)

                sCount = dockedShipData.get("shield_count", 0)
                for g in range(sCount - 1):
                    sVal = dockedShipData.get("shield_val", g)
                    sValMax = dockedShipData.get("shield_max_val", g)
                    changed = (sVal < sValMax)
                    sVal = max(0.0, min(sVal + shieldCoeff, sValMax))  # clamp the value
                    if changed:
                        dockedShipData.set("shield_val", sVal, g)

                # repair systems (more than normal)
                for g in range(sbs.SHPSYS.SHIELDS):
                    damage = dockedShipData.get("system_damage", g)
                    maxDamage = dockedShipData.get("system_max_damage", g)
                    changed = (damage > 0.0)
                    damage = max(0.0, min(damage - systemCoeff, maxDamage))  # clamp the value
                    if changed:
                        dockedShipData.set("system_damage", damage, g)

            if self.ObjectData.get("Crew", 0):
                shipObj = SpaceObjects.activeShips.get(id)
                curcrew = shipObj.CrewMembers.shipCrew
                for teamID, teamObj in curcrew.items():
                    teamdata = teamObj.teamdata
                    type = teamdata.get("Type")
                    teaminfo = CrewData.teams.get(type)
                    maxstrength = teaminfo.get("strength")
                    teamdata.update({"OK": maxstrength,
                                     "SeriousWound": 0,
                                     "Killed": 0,
                                     "LightWound": 0})


class USFPStation(Station):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)

    def stationsetup(self):
        super().stationsetup()
        self.manufacturingsetup()
        self.facilitiessetup()

    def manufacturingsetup(self):
        self.allStock = {}
        self.buildStatus = "building"
        self.AMC = tsn_databases.tier1AMC
        self.build = random.choice(list(self.AMC.keys()))
        self.ObjectData.set("build_ready_time", sbs.app_seconds() + 60, 0)

    def ObjectTickMonitors(self):
        super().ObjectTickMonitors()
        self.ProcessAutoBuild(self.sim)

    def ProcessManufacturing(self, buildCargo):
        #only manufacture more if the station has facilities to restock
        if "Restock" in self.facilities:
            self.ObjectData.set("build_type", buildCargo, 0)
            if self.ObjectData.get("build_ready_time", 0) < sbs.app_seconds():
                cargotype = self.ObjectData.get("build_type", 0)
                if cargotype in self.Cargo.CargoHold.keys():
                    cargodata = self.Cargo.CargoHold.get(cargotype)
                    count = cargodata.get("count")
                    cargodata.update({"count": count + 1})
                else:
                    self.Cargo.addCargo(cargotype)
                self.ObjectData.set("build_ready_time", sbs.app_seconds() + 60)
                for shipID, ship in self.dockingPorts.items():
                    if shipID in SpaceObjects.activeShips.keys():
                        ship.updateclientConsoles()
                self.buildStatus = "complete"

    def ProcessAutoBuild(self, sim):
        self.ProcessManufacturing(self.build)
        if self.buildStatus == "complete":
            self.build = random.choice(list(self.AMC.keys()))
            self.buildStatus = "building"
