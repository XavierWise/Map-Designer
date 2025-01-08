import sbs, random

from Objects import SpaceObjects


class JumpPoint(SpaceObjects.SpaceObject):
    def __init__(self, name, behav, hull, side, **kwargs):
        super().__init__(name, behav, hull, side, **kwargs)
        self.JumpPointInfo = {
            "type": "jump_point",
            "jumppointtype": "Linked",
            "destinations": {},
            "state": "Untethered",
            "drift": 0
        }
        if "info" in kwargs.keys():
            self.JumpPointInfo = kwargs.get("info")
        if self.JumpPointInfo.get("state") == "Tethered":
            self.ObjectHullClass = "generic-tetrahedron"

    def SpawnObject(self, sim, **kwargs):
        super().SpawnObject(sim, **kwargs)
        #spawn the object and gather the key data
        self.drift = int(self.JumpPointInfo.get("drift"))
        if self.JumpPointInfo.get("state") == "Untethered":
            self.ConfigureAsNode(sim)
        self.ObjectData.set("name_tag", self.ObjectName, 0)
        self.ObjectData.set("type", self.JumpPointInfo.get("jumppointtype"), 0) #Linked, Outbound, Inbound, Multi-Link
        self.Destinations = self.JumpPointInfo.get("destinations") #dictionary of gates and systems
        self.ObjectData.set("state", self.JumpPointInfo.get("state"), 0)
        self.jumpnodeData() #configure the scan data of the jump point
        SpaceObjects.activeJumpPoints.update({self.ObjectID: self})
        self.SystemStatus = "Offline"

    def ConfigureAsNode(self, sim):
        #gather key jump point data
        #update the position based on drift data
        self.position = (self.initpos[0] + random.randint(0 - self.drift, self.drift), self.initpos[1], self.initpos[2] + random.randint(0 - self.drift, self.drift))
        self.driftx = random.randint(5, 10)
        self.driftz = random.randint(5, 10)

    def jumpnodeData(self):
        #scan data for the jump node
        if self.JumpPointInfo.get("state") == "Tethered":
            self.ObjectData.set("access_key", "AK1", 0)

    def ObjectTickMonitors(self):
        if self.JumpPointInfo.get("state") == "Untethered":
            self.jumppointDrift(self.sim)

    def jumppointDrift(self, sim):
        updatex = 0
        updatez = 0
        #drift on the y coordinate
        if self.initpos[0] - self.drift < self.position[0] + self.driftx < self.initpos[0] + self.drift:
            updatex = self.position[0] + self.driftx
        elif self.position[0] + self.driftx > self.initpos[0] + self.drift:
            self.driftx = random.randint(-10, -5)
            updatex = self.position[0] + self.driftx
        elif self.position[0] + self.driftx < self.initpos[0] - self.drift:
            self.driftx = random.randint(5, 10)
            updatex = self.position[0] + self.driftx
        #drift on the z coordinate
        if self.initpos[2] - self.drift < self.position[2] + self.driftz < self.initpos[2] + self.drift:
            updatez = self.position[2] + self.driftz
        elif self.position[2] + self.driftz > self.initpos[2] + self.drift:
            self.driftz = random.randint(-10, -5)
            updatez = self.position[2] + self.driftz
        elif self.position[2] + self.driftz < self.initpos[2] - self.drift:
            self.driftz = random.randint(5, 10)
            updatez = self.position[2] + self.driftz
        self.position = (updatex, self.position[1], updatez)
        sim.reposition_space_object(self.Object, self.position[0], self.position[1], self.position[2])
