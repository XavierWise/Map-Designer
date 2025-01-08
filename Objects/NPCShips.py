import simulation
import tsn_databases, sbs, random
from Objects import SpaceObjects
from NPC_Ships import NPC_Damage, AI_Commanders
import inspect


def SpawnShip(sim, race, hull_type, position, **kwargs):
    ship = NPCShip(race, "behav_npcship", hull_type, race, position=position)
    ship.SpawnObject(sim)
    return ship


class NPCShip(SpaceObjects.SpaceObject):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectName = self.ObjectData.get("name_tag", 0)
        self.ObjectData.set("throttle", 1, 0)
        self.ObjectData.set("evasion", False, 0) # set up the initial data for evasive actions
        self.ObjectData.set("target_id", -1, 0)
        self.ObjectData.set("PatrolPoint", 0, 0) # set up the initial data for patrol points
        normalspeed = self.ObjectData.get("speed_coeff", 0)
        self.ObjectData.set("standard_speed", normalspeed, 0)

        if not self.ObjectData.get("torpedo_tube_count", 0):
            self.ObjectData.set("torpedo_tube_count", 0, 0)
        if not self.ObjectData.get("beamCount", 0):
            self.ObjectData.set("beamCount", 0, 0)
        self.spawnposition = (self.Object.pos.x, self.Object.pos.y, self.Object.pos.z)
        self.Damage = NPC_Damage.NPCDamage(self, self.Object, self.ObjectData)
        self.setupScanSources()
        self.setupsystems()
        self.setupSpecials()

        SpaceObjects.activeNPCs.update({self.ObjectID: self})

    def ObjectEventTriggers(self, event):
        for system in self.shipSystems.values():
            system.SystemEventTriggers(event)

    def ObjectTickMonitors(self):
        for system in self.shipSystems.values():
            system.SystemTickMonitors()
        self.Damage.damagemonitor()

    def setupsystems(self):
        self.shipSystems = {
            "Emissions": SpaceObjects.NPCEmissionsSystem(self),
            "ShuttleBay": SpaceObjects.ShuttleBaySystems(self),
            "Communications": SpaceObjects.CommsSystems(self)
        }

    def setupScanSources(self):
        if self.Object.side == "TSN":
            for player, ship in SpaceObjects.activeShips.items():
                index = ship.ObjectData.get("num_extra_scan_sources", 0) + 1
                ship.ObjectData.set("extra_scan_source", self.ObjectID, index)
                ship.ObjectData.set("num_extra_scan_sources", index, 0)
        if "civilian" in self.ObjectTags:
            self.ObjectData.set("radar_color_override", "#fffc4f", 0)

    def setupScanData(self):
        self.ObjectData.set("scan_type_list", "scan", 0)

    def setupSpecials(self):
        """self.ObjectData.set("elite_low_vis", 1, 0)
        self.ObjectData.set("elite_low_vis_distance", 5000, 0)"""
        if "elite" in self.ObjectTags:
            ability = random.choice(tsn_databases.eliteabilities)
            self.ObjectData.set(ability, 1, 0)


class NPCCarrier(NPCShip):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)
        self.ObjectHanger = {}
        self.WingCommanders = {}

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.WingSize = 5
        self.HangerSize = 1
        for h in range(self.HangerSize):
            self.setupFighterWing()

    def setupFighterWing(self):
        fighterList = {}
        hull_type = self.fighterType()
        race = self.ObjectSide
        for slot in range(self.WingSize):
            newFighter = NPCFighter(race, "behav_npcship", hull_type, race, parentship=self, type=hull_type)
            newFighter.SpawnObject(simulation.simul)
            fighterList.update({newFighter.ObjectID: newFighter})
        fleetCommander = list(fighterList.values())[0]
        NewFleetCommander = AI_Commanders.AIFighterCommander(fleetCommander, fighterList, self.WingSize)
        AI_Commanders.commanders.update({id(NewFleetCommander): NewFleetCommander})
        self.WingCommanders.update({id(NewFleetCommander): NewFleetCommander})

    def fighterType(self):
        if "pirate" in self.ObjectTags:
            return "pirate_fighter"
        elif "hegemony" in self.ObjectTags:
            return "arvonian_fighter"
        elif "usfp" in self.ObjectTags:
            return "tsn_fighter"
        else:
            return "tsn_fighter"


class NPCFighter(NPCShip):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)
        if "type" in kwargs.keys():
            self.ShuttleType = kwargs.get("type")
        if "parentship" in kwargs.keys():
            self.ParentShip = kwargs.get("parentship")

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectData.set("name_tag", str(self.ObjectID)[-5:], 0)
        self.ObjectData.set("speed_coeff", 1, 0)
        self.dockFighter()

    def deployFighter(self):
        sbs.retrieve_from_standby_list(self.Object)
        position = self.ParentShip.Object.pos
        vector = self.ParentShip.Object.forward_vector()
        self.sim.reposition_space_object(self.Object, position.x + vector.x, position.y + vector.y, position.z + vector.z)
        self.Object.rot_quat = self.ParentShip.Object.rot_quat

    def dockFighter(self):
        sbs.push_to_standby_list(self.Object)
        self.ObjectData.set("evasion", False, 0)

        for shield in range(self.ObjectData.get("shield_count", 0)):
            maxVal = self.ObjectData.get("shield_max_val", shield)
            self.ObjectData.set("shield_val", maxVal, shield)

