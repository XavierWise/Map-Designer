import simulation, random, sbs, math, tsn_databases
from Objects import SpaceObjects, OtherObjects


class NPCDamage: #only used on NPC ships
    def __init__(self, ship, shipObj, shipdata):
        self.ship = ship
        self.shipObj = shipObj # the sbs ship object
        self.shipdata = shipdata
        self.systemsetup()
        self.shield = []
        for shield in range(self.shipdata.get("shield_count", 0)):
            self.shield.append(self.shipdata.get("shield_max_val", shield))
        self.systems.update({"Shields": self.shield})
        self.repairing = False
        self.damagedsystems = set()
        self.destroyed = False

    def systemsetup(self):
        self.systems = {}
        if tsn_databases.shipProperties.get(self.shipObj.data_tag):
            self.systemdata()

    def systemdata(self):
        properties = tsn_databases.shipProperties.get(self.shipObj.data_tag)
        if properties.get("systems"):
            for system in properties.get("systems"):
                match system:
                    case "Manoeuvre":
                        self.systems.update({system: self.shipdata.get("turnRate", 0)})
                    case "Impulse":
                        self.systems.update({system: self.shipdata.get("throttle", 0)})
                    case "Torpedoes":
                        self.systems.update({system: self.shipdata.get("drone_launch_timer", 0)})
                    case "Beams":
                        beams = []
                        for beam in range(self.shipdata.get("beamCount", 0)):
                            beams.append(self.shipdata.get("beamCycleTime", beam))
                        self.systems.update({system: beams})

    def damagecalculations(self, damage_event):
        #calculates whether damage will go through the shields to damage a ship's subsystem
        if damage_event.sub_tag == "beam":
            if damage_event.origin_id in SpaceObjects.activeShips.keys():
                shieldpercentage = self.determineShieldhit(damage_event.origin_id)
                #currently just an arbritary value of 50%.
                if shieldpercentage < 50:
                    firer = SpaceObjects.activeShips.get(damage_event.origin_id)
                    firerdata = firer.ObjectData
                    aperture = firerdata.get("beamAperture", 0)
                    subsystem = firerdata.get("targetSubSystem", 0)
                    probability = random.randrange(1, 100)
                    """if subsystem == "Hull":
                        subsystem = random.choice(list(self.systems.keys()))"""
                    if aperture < 30:
                        if probability < 50:
                            self.systemDamage(subsystem)
                    elif 30 < aperture < 70:
                        if probability < 10:
                            self.systemDamage(subsystem)

    def damagemonitor(self):
        if self.shipdata.get("deathTick", 0) > 0 and self.destroyed == False:
            print("destroyed")
            self.debriscalculation()
            self.destroyed = True

    def systemDamage(self, system):
        if system == "Hull":
            system = random.choice(list(self.systems.keys()))
        #damages a selected system
        self.damagedsystems.add(system)
        self.updateScanData()
        match system:
            case "Manoeuvre":
                self.changesystem(system, "turnRate")
            case "Impulse":
                self.changesystem(system, "throttle")
            case "Shields":
                for shield in range(self.shipdata.get("shield_count", 0)):
                    self.changesystem(system, "shield_max_val", number=shield)
                    if self.shipdata.get("shield_val", shield) > self.shipdata.get("shield_max_val", shield):
                        #check to make sure the current shield value is not above the new max value
                        lower = self.shipdata.get("shield_max_val", shield)
                        self.shipdata.set("shield_val", lower, shield)
            case "Torpedoes":
                self.changesystem(system, "drone_launch_timer", alter="increase")
            case "Beams":
                for beam in range(self.shipdata.get("beamCount", 0)):
                    self.changesystem(system, "beamCycleTime", number=beam, alter="increase")
            case _:
                pass

    def updateScanData(self):
        systemdata = ""
        for system in self.systems.keys():
            if system in self.damagedsystems:
                status = "Damaged"
            else:
                status = "Active"
            systemdata += f"{system}: {status}^"
        self.shipdata.set("systems_data", systemdata, 0)

    def changesystem(self, system, damage, **kwargs):
        #alters the value of a particular system based on repairs/damage
        maxvals = self.systems.get(system)
        if "number" in kwargs:
            x = kwargs.get("number")
        else:
            x = 0
        curval = self.shipdata.get(damage, x)
        if isinstance(maxvals, list):
            maxval = maxvals[x]
        else:
            maxval = maxvals
        newvalue = curval
        if kwargs.get("alter"):
            if "increase" in kwargs.get("alter"):
                if curval < maxval * 100:
                    newvalue = curval + (maxval/random.randint(5, 10))

            elif "repairup" in kwargs.get("alter"):
                if curval < maxval:
                    newvalue = curval + (maxval / random.randint(5, 10))
                    if newvalue > maxval:
                        newvalue = maxval
            elif "repairdown" in kwargs.get("alter"):
                if curval > maxval:
                    newvalue = curval - (maxval / random.randint(5, 10))
                    if newvalue < maxval:
                        newvalue = maxval
            else:
                if curval > maxval / 100:
                    newvalue = curval - (maxval/random.randint(5, 10))
                    if newvalue < 0:
                        newvalue = 0
        else:
            if curval > maxval / 100:
                newvalue = curval - (maxval / random.randint(5, 10))
                if newvalue < 0:
                    newvalue = 0

        self.shipdata.set(damage, newvalue, x)

    def systemRepair(self, system):
        #repairs a selected system
        maxval = self.systems.get(system)
        self.repairing = False
        match system:
            case "Manoeuvre":
                curval = self.shipdata.get("turnRate", 0)
                if curval < maxval:
                    self.changesystem(system, "turnRate", alter="repairup")
                elif curval >= maxval:
                    self.shipdata.set("turnRate", maxval, 0)
                    self.damagedsystems.discard(system)

            case "Impulse":
                curval = self.shipdata.get("throttle", 0)
                if curval < maxval:
                    self.changesystem(system, "throttle", alter="repairup")
                elif curval >= maxval:
                    self.shipdata.set("throttle", maxval, 0)
                    self.damagedsystems.discard(system)

            case "Shields":
                repairedshields = 0
                for shield in range(self.shipdata.get("shield_count", 0)):
                    maxshield = maxval[shield]
                    curval = self.shipdata.get("shield_max_val", 0)
                    if curval < maxshield:
                        self.changesystem(system, "shield_max_val", number=shield, alter="repairup")
                    elif curval >= maxshield:
                        self.shipdata.set("shield_max_val", maxshield, 0)
                        repairedshields += 1
                if repairedshields >= self.shipdata.get("shield_count", 0):
                    self.damagedsystems.discard(system)

            case "Torpedoes":
                curval = self.shipdata.get("drone_launch_timer", 0)
                if curval > maxval:
                    self.changesystem(system, "drone_launch_timer", alter="repairdown")
                elif curval <= maxval:
                    self.shipdata.set("drone_launch_timer", maxval, 0)
                    self.damagedsystems.discard(system)

            case "Beams":
                repairedbeams = 0
                for beam in range(self.shipdata.get("beamCount", 0)):
                    maxbeam = maxval[beam]
                    curval = self.shipdata.get("beamCycleTime", beam)
                    if curval > maxbeam:
                        self.changesystem(system, "beamCycleTime", number=beam, alter="repairdown")
                    elif curval <= maxbeam:
                        self.shipdata.set("beamCycleTime", maxbeam, 0)
                        repairedbeams += 1
                if repairedbeams >= self.shipdata.get("beamCount", 0):
                    self.damagedsystems.discard(system)

            case _:
                pass

    def myHeading(self):
        #returns a heading (in radians) that the ship is currently travelling on
        vector = self.shipObj.forward_vector()
        heading = (math.atan2(vector.x, vector.z))
        if heading < 0:
            heading = heading + (2 * math.pi)
        return heading

    def getdamagedir(self, firerID):
        #calculates the direction from which a hit is received from a firing ship
        firer = simulation.simul.get_space_object(firerID)
        if firer:
            ang = math.atan2(firer.pos.x - self.shipObj.pos.x, firer.pos.z - self.shipObj.pos.z)
            if ang < 0:
                ang = 2 * math.pi + ang
        else:
            ang = 0
        return ang

    def calculatehitarc(self, firerID):
        #returns the direction of the hit, relative to the forward heading of the ship
        direction = self.getdamagedir(firerID) - self.myHeading()
        if direction < 0:
            direction = 2 * math.pi + direction
        return direction

    def determineShieldhit(self, firerID):
        #returns the percentage value of the shield that has been hit
        attack_ang = math.degrees(self.calculatehitarc(firerID))
        shields = self.shipShields()
        forwardshield = list(shields.keys())[0]
        if attack_ang > forwardshield[0] or attack_ang < forwardshield[1]:
            return shields.get(forwardshield)
        else:
            for arc, percent in shields.items():
                if arc[0] < attack_ang < arc[1]:
                    return percent

    def shipShields(self):
        #calculates the percentage value of each shield arc
        shieldcount = self.shipdata.get("shield_count", 0)
        shieldpercentages = {}
        arcwidth = 360 / shieldcount

        #set up the forward arc first
        maxshields = self.shield[0]
        curshields = self.shipdata.get("shield_val", 0)
        shieldpercent = (curshields / maxshields) * 100
        shieldpercentages.update({(360 - (arcwidth/2), arcwidth/2): shieldpercent})

        start = arcwidth / 2
        end = start + arcwidth
        #now calculate the other arcs
        for shield in range(shieldcount - 1):
            maxshields = self.shield[shield + 1]
            curshields = self.shipdata.get("shield_val", shield + 1)
            shieldpercent = (curshields / maxshields) * 100
            shieldpercentages.update({(start, end): shieldpercent})
            start = end
            end = start + arcwidth
        return shieldpercentages

    def damagerepairroutine(self):
        #tracks a list of damaged systems and then selects one to repair
        if len(self.damagedsystems) > 0:
            currenttick = sbs.app_seconds()
            if not self.repairing:
                self.repairing = [random.choice(tuple(self.damagedsystems)), currenttick + 20]
            if currenttick >= self.repairing[1]:
                self.systemRepair(self.repairing[0])
                self.repairing = False

    def debriscalculation(self):
        prob = random.randint(0, 100)
        if prob > 60:
            cargoHold = self.ship.Cargo.CargoHold
            randomamount = random.randint(1, min(len(cargoHold.keys()), 10))
            for x in range(randomamount):
                random.choice([self.spawncargo, self.spawndebris, self.spawndebris, self.spawndebris])()
        else:
            for x in range(2, 4):
                self.spawndebris()

    def spawncargo(self):
        scatterx = random.randint(-10, 10)
        scattery = random.randint(-10, 10)
        scatterz = random.randint(-10, 10)
        coordinate = (self.shipObj.pos.x + scatterx, self.shipObj.pos.y + scattery, self.shipObj.pos.z + scatterz)
        x = random.randint(0, min(len(self.ship.Cargo.CargoHold.keys()), 10))
        name = list(self.ship.Cargo.CargoHold.keys())[x]
        newObj = OtherObjects.CargoPod(position=coordinate, cargotype=name)
        newObj.SpawnObject(simulation.simul)
        newObj.Object.cur_speed = 0.1
        quaternion = OtherObjects.random_quaternion()
        newObj.Object.rot_quat.w = quaternion[0]
        newObj.Object.rot_quat.x = quaternion[1]
        newObj.Object.rot_quat.y = quaternion[2]
        newObj.Object.rot_quat.z = quaternion[3]
        for GM in SpaceObjects.activeGameMasters.values():
            newObj.ObjectData.set(GM.Object.side + "scan", "scandata", 0)
            index = GM.ObjectData.get("num_extra_scan_sources", 0)
            GM.ObjectData.set("extra_scan_source", newObj.ObjectID, index)
            index += 1
            GM.ObjectData.set("num_extra_scan_sources", index, 0)

    def spawndebris(self):
        scatterx = random.randint(-10, 10)
        scattery = random.randint(-10, 10)
        scatterz = random.randint(-10, 10)
        coordinate = (self.shipObj.pos.x + scatterx, self.shipObj.pos.y + scattery, self.shipObj.pos.z + scatterz)
        newObj = OtherObjects.Debris(position=coordinate)
        newObj.SpawnObject(simulation.simul)
        newObj.Object.cur_speed = 0.1
        quaternion = OtherObjects.random_quaternion()
        newObj.Object.rot_quat.w = quaternion[0]
        newObj.Object.rot_quat.x = quaternion[1]
        newObj.Object.rot_quat.y = quaternion[2]
        newObj.Object.rot_quat.z = quaternion[3]
        for GM in SpaceObjects.activeGameMasters.values():
            newObj.ObjectData.set(GM.Object.side + "scan", "scandata", 0)
            index = GM.ObjectData.get("num_extra_scan_sources", 0)
            GM.ObjectData.set("extra_scan_source", newObj.ObjectID, index)
            index += 1
            GM.ObjectData.set("num_extra_scan_sources", index, 0)
