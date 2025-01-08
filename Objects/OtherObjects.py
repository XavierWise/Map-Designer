import sbs, math, random
import tsn_databases
from Objects import SpaceObjects


def random_quaternion():
    u1 = random.random()
    u2 = random.random()
    u3 = random.random()

    w = math.sqrt(1 - u1) * math.sin(2 * math.pi * u2)
    x = math.sqrt(1 - u1) * math.cos(2 * math.pi * u2)
    y = math.sqrt(u1) * math.sin(2 * math.pi * u3)
    z = math.sqrt(u1) * math.cos(2 * math.pi * u3)

    return (w, x, y, z)


class OtherObject(SpaceObjects.SimulationObject):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        #add the data related to the cargo/team type
        #if it is a new spawn (from a GM), add brand new data, unless configured
        #if it is an existing item, copy the data
        self.addtoScanSources()
        SpaceObjects.activeObjects.update({self.ObjectID: self})
        self.ObjectData.set("hull_side", "", 0)
        self.ObjectData.set("local_scale_coeff", 0.2, 0)
        #self.Timer = sbs.app_minutes() + random.randint(5, 25)
        self.Timer = sbs.app_minutes() + 2

    def addtoScanSources(self):
        for ship, shipObj in SpaceObjects.activeShips.items():
            index = shipObj.ObjectData.get("num_extra_scan_sources", 0)
            shipObj.ObjectData.set("extra_scan_source", self.ObjectID, index)

    def retrieval(self, ShuttleObj):
        item = tsn_databases.masterDatabase.get(self.ObjectName)
        for key in range(ShuttleObj.cargoCapacity):
            if key not in ShuttleObj.CargoHold.keys():
                ShuttleObj.CargoHold.update({key: [self.ObjectName, item]})
                ShuttleObj.updatepilotConsoles()
                sbs.delete_object(self.ObjectID)
                break

    def getpointfromheading(self, distance, heading):
        # using a distance and degrees, find a specific coordinate
        opplength = math.sin(math.radians(heading)) * distance
        adjlength = math.cos(math.radians(heading)) * distance
        return (int(opplength), 0, int(adjlength))

    def calculatecoordinate(self, distance, heading):
        # get a coordinate from the ship to a position in space at a specific distance and heading
        relativecoordinate = self.getpointfromheading(distance, heading)
        mycoordinate = (self.Object.pos.x, self.Object.pos.y, self.Object.pos.z)
        actualcoordinate = (int(mycoordinate[0]) + int(relativecoordinate[0]), 0, int(mycoordinate[2]) + int(relativecoordinate[2]))
        return actualcoordinate

    def getrelativecoord(self, distance, heading):
        # get a coordinate position based off a distance and direction from a specified object
        relativecoordinate = self.getpointfromheading(distance, heading)
        objcoordinate = (self.Object.pos.x, self.Object.pos.y, self.Object.pos.z)
        actualcoordinate = (int(objcoordinate[0] + relativecoordinate[0]), 0, int(objcoordinate[2] + relativecoordinate[2]))
        return actualcoordinate


class SensorBuoy(OtherObject):
    def __init__(self, **kwargs):
        super().__init__("Sensor Buoy", "behav_buoy", "danger_4a", "USFP", **kwargs)

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectData.set("radar_color_override", "#FF5E00", 0)
        self.ObjectData.set("hull_name", "Sensor Buoy", 0)


class CommsRelay(OtherObject):
    def __init__(self, **kwargs):
        super().__init__("Comms Relay", "behav_buoy", "danger_5a", "USFP", **kwargs)

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectData.set("hull_name", "Comms Relay", 0)
        self.ObjectData.set("radar_color_override", "#6FFF00", 0)


class CargoPod(OtherObject):
    def __init__(self, **kwargs):
        super().__init__("Cargo Pod", "behav_cargo", "container_1a", "USFP", **kwargs)
        if "cargotype" in kwargs:
            self.cargotype = kwargs.get("cargotype")
        else:
            self.cargotype = "Container"

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectData.set("hull_name", "Cargo Pod", 0)
        self.ObjectData.set("radar_color_override", "#FFC300", 0)
        self.ObjectTags = ["cargo"]

    def retrieval(self, ShuttleObj):
        item = tsn_databases.masterDatabase.get(self.cargotype)
        for key in range(ShuttleObj.cargoCapacity):
            if key not in ShuttleObj.CargoHold.keys():
                loadingcargo = item.copy()
                loadingcargo.update({"count": 1})
                ShuttleObj.CargoHold.update({key: [self.cargotype, loadingcargo]})
                ShuttleObj.updatepilotConsoles()
                sbs.delete_object(self.ObjectID)
                break


class Debris(OtherObject):
    def __init__(self, **kwargs):
        type = random.choice([1, 2, 3, 4, 6])
        super().__init__("Debris", "behav_debris", f"container_small_{type}c", "", **kwargs)

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectData.set("hull_name", "Debris", 0)
        self.ObjectData.set("radar_color_override", "#a6a6a6", 0)

    def retrieval(self, ShuttleObj):
        pass


class CrewTeam(OtherObject):
    def __init__(self, teamObj, **kwargs):
        self.teamID = id(teamObj)
        self.teamObj = teamObj
        team = self.teamObj.teamdata.get("Type")
        super().__init__(team, "behav_team", "container_1a", "USFP", **kwargs)

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        self.ObjectData.set("hull_name", "Crew Pod", 0)
        self.ObjectData.set("radar_color_override", "#00FF1A", 0)

    def retrieval(self, ShuttleObj):
        for key in range(ShuttleObj.personnelCapacity):
            if key not in ShuttleObj.Personnel.keys():
                ShuttleObj.Personnel.update({key: [self.teamID, self.teamObj]})
                ShuttleObj.updatepilotConsoles()
                sbs.delete_object(self.ObjectID)
                break


class MarineTeam(CrewTeam):
    def __init__(self, teamObj, **kwargs):
        super().__init__(teamObj, **kwargs)


class CombatEngTeam(CrewTeam):
    def __init__(self, teamObj, **kwargs):
        super().__init__(teamObj, **kwargs)


class MedicTeam(CrewTeam):
    def __init__(self, teamObj, **kwargs):
        super().__init__(teamObj, **kwargs)


class DamConTeam(CrewTeam):
    def __init__(self, teamObj, **kwargs):
        super().__init__(teamObj, **kwargs)

class EvacueeTeam(CrewTeam):
    def __init__(self, teamObj, **kwargs):
        super().__init__(teamObj, **kwargs)
