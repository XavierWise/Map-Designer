import sbs_tools
import simulation, random, sbs, math, tsn_databases
from Objects import SpaceObjects, OtherObjects


class StationDamage:
    def __init__(self, ship, shipObj, shipdata):
        self.ship = ship
        self.shipObj = shipObj # the sbs ship object
        self.shipdata = shipdata
        self.destroyed = False

    def damagemonitor(self):
        if self.shipdata.get("deathTick", 0) > 0 and self.destroyed == False:
            self.shipdata.set("radar_color_override", "#A9A9A9", 0)
            self.debriscalculation()
            self.destroyed = True

    def debriscalculation(self):
        prob = random.randint(0, 100)
        if prob > 40:
            cargoHold = self.ship.Cargo.CargoHold
            randomamount = random.randint(0, min(len(cargoHold.keys()), 10))
            for x in range(randomamount):
                random.choice([self.spawncargo, self.spawndebris, self.spawndebris, self.spawndebris])()

    def spawncargo(self):
        scatterx = random.randint(-500, 500)
        scattery = random.randint(-500, 500)
        scatterz = random.randint(-500, 500)
        coordinate = (self.shipObj.pos.x + scatterx, self.shipObj.pos.y + scattery, self.shipObj.pos.z + scatterz)
        x = random.randint(0, min(len(self.ship.Cargo.CargoHold.keys()), 10))
        name = list(self.ship.Cargo.CargoHold.keys())[x]
        newObj = OtherObjects.CargoPod(position=coordinate, cargotype=name)
        newObj.SpawnObject(simulation.simul)
        for GM in SpaceObjects.activeGameMasters.values():
            newObj.ObjectData.set(GM.Object.side + "scan", "scandata", 0)
            index = GM.ObjectData.get("num_extra_scan_sources", 0)
            GM.ObjectData.set("extra_scan_source", newObj.ObjectID, index)
            index += 1
            GM.ObjectData.set("num_extra_scan_sources", index, 0)

    def spawndebris(self):
        scatterx = random.randint(-500, 500)
        scattery = random.randint(-500, 500)
        scatterz = random.randint(-500, 500)
        coordinate = (self.shipObj.pos.x + scatterx, self.shipObj.pos.y + scattery, self.shipObj.pos.z + scatterz)
        newObj = OtherObjects.Debris(position=coordinate)
        newObj.SpawnObject(simulation.simul)
        for GM in SpaceObjects.activeGameMasters.values():
            newObj.ObjectData.set(GM.Object.side + "scan", "scandata", 0)
            index = GM.ObjectData.get("num_extra_scan_sources", 0)
            GM.ObjectData.set("extra_scan_source", newObj.ObjectID, index)
            index += 1
            GM.ObjectData.set("num_extra_scan_sources", index, 0)
