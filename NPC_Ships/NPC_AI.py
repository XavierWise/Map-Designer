import sbs, random, math, simulation
import tsn_databases, copy, sbs_tools
from Objects import SpaceObjects
from NPC_Ships import AI_Commanders, fleetOrders

#elite_low_vis (set in ObjectData: 1 ON, 0 OFF)
#elite_low_vis_distance (set in ObjectData: distance that ship can be seen up to - anything beyond and it is invisible on 2D radar


class GeneralComputations:

    @staticmethod
    def getpointfromheading(distance, heading):
        # using a distance and degrees, find a specific coordinate
        opplength = math.sin(math.radians(heading)) * distance
        adjlength = math.cos(math.radians(heading)) * distance
        return (int(opplength), 0, int(adjlength))

    @staticmethod
    def calculatecoordinate(SpaceObj, distance, heading):
        # get a coordinate from the ship to a position in space at a specific distance and heading
        relativecoordinate = GeneralComputations.getpointfromheading(distance, heading)
        mycoordinate = (SpaceObj.Object.pos.x, SpaceObj.Object.pos.y, SpaceObj.Object.pos.z)
        actualcoordinate = (int(mycoordinate[0]) + int(relativecoordinate[0]), 0, int(mycoordinate[2]) + int(relativecoordinate[2]))
        return actualcoordinate

    @staticmethod
    def getrelativecoord(SpaceObj, distance, heading):
        # get a coordinate position based off a distance and direction from a specified object
        relativecoordinate = GeneralComputations.getpointfromheading(distance, heading)
        objcoordinate = (SpaceObj.Object.pos.x, SpaceObj.Object.pos.y, SpaceObj.Object.pos.z)
        actualcoordinate = (int(objcoordinate[0] + relativecoordinate[0]), 0, int(objcoordinate[2] + relativecoordinate[2]))
        return actualcoordinate

    @staticmethod
    def getrelativevectorcoord(SpaceObj, distance, heading, height):
        # get a coordinate position based off a distance and direction from a specified object
        relativecoordinate = GeneralComputations.getpointfromheading(distance, heading)
        vector = SpaceObj.Object.forward_vector()
        objcoordinate = (SpaceObj.Object.pos.x + vector.x, SpaceObj.Object.pos.y + vector.y, SpaceObj.Object.pos.z + vector.z)
        actualcoordinate = (int(objcoordinate[0] + relativecoordinate[0]), int(objcoordinate[1] + relativecoordinate[1] + height), int(objcoordinate[2] + relativecoordinate[2]))
        return actualcoordinate

    @staticmethod
    def getrelativepoint(distance, heading, coord):
        # get a coordinate position based off a distance and direction from a specified coordinate
        relativecoordinate = GeneralComputations.getpointfromheading(distance, heading)
        actualcoordinate = (int(coord[0] + relativecoordinate[0]), 0, int(coord[2] + relativecoordinate[2]))
        return actualcoordinate

    @staticmethod
    def setmovetopoint(SpaceObj, coord):
        # set a coordinate to move to
        SpaceObj.ObjectData.set("target_pos_x", coord[0], 0)
        SpaceObj.ObjectData.set("target_pos_y", coord[1], 0)
        SpaceObj.ObjectData.set("target_pos_z", coord[2], 0)

    @staticmethod
    def setmovetoobject(SpaceObj, target):
        # set a coordinate to target to
        coord = (target.pos.x, target.pos.y, target.pos.z)
        SpaceObj.ObjectData.set("target_pos_x", coord[0], 0)
        SpaceObj.ObjectData.set("target_pos_y", coord[1], 0)
        SpaceObj.ObjectData.set("target_pos_z", coord[2], 0)


    @staticmethod
    def getheadingtoTarget(SpaceObj, target):
        # return the heading in degrees between the ship and a target space object
        ang = math.atan2(target.Object.pos.x - SpaceObj.Object.pos.x, target.Object.pos.z - SpaceObj.Object.pos.z)
        if ang < 0:
            ang = ang + (2 * math.pi)
        return ang

    @staticmethod
    def getheadingtoCoordinate(SpaceObj, coord):
        # return the heading in degrees between the ship and a target space object
        ang = math.atan2(coord[0] - SpaceObj.Object.pos.x, coord[2] - SpaceObj.Object.pos.z)
        if ang < 0:
            ang = ang + (2 * math.pi)
        return ang

    @staticmethod
    def getshipHeading(SpaceObj):
        # return the heading of space object in radians
        ang = math.atan2(SpaceObj.Object.forward_vector().x, SpaceObj.Object.forward_vector().z)
        if ang < 0:
            ang = ang + (2 * math.pi)
        return ang

    @staticmethod
    def getdistancebetweencoords(pointA, pointB):
        # get the distance between two coordinate points
        d = math.sqrt(pow(pointA[0] - pointB[0], 2) + pow(pointA[2] - pointB[2], 2))
        return d

    @staticmethod
    def getdistancetocoord(SpaceObj, coord):
        # get the distance between two coordinate points
        d = math.sqrt(pow(coord[0] - SpaceObj.Object.pos.x, 2) + pow(coord[2] - SpaceObj.Object.pos.z, 2))
        return d

    @staticmethod
    def heading(coord):
        # calculates the heading of a ship
        ang = math.atan2(coord[0], coord[1])
        if ang < 0:
            ang = ang + (2 * math.pi)
        return ang

    @staticmethod
    def checkonpoint(SpaceObj, targetcoord):
        # checks to see if an object is within 200 of a specified coordinate
        distance = GeneralComputations.getdistancetocoord(SpaceObj, targetcoord)
        if distance < 200:
            return True
        else:
            return False

    @staticmethod
    def calculateshields(SpaceObj):
        # returns a list of shield percentage values
        shieldcount = SpaceObj.ObjectData.get("shield_count", 0)
        shieldpercentages = []
        for shield in range(shieldcount):
            maxshields = SpaceObj.ObjectData.get("shield_max_val", shield)
            curshields = SpaceObj.ObjectData.get("shield_val", shield)
            shieldpercent = (curshields/maxshields) * 100
            shieldpercentages.append(shieldpercent)
        return shieldpercentages

    @staticmethod
    def compareHeadings(Heading1, Heading2):
        pass

    @staticmethod
    def checkdestroyed(unique_ID):
        # check to see if a player ship is destroyed or not
        if unique_ID in SpaceObjects.activeShips.keys():
            ship = SpaceObjects.activeShips.get(unique_ID)
            if ship.ObjectState == "Damaged":
                return False
            else:
                return True

    @staticmethod
    def checkclosestCoord(SpaceObj, coordList):
        # checks a set of objects to determine which is the closest
        distance = []
        for coord in coordList:
            if type(coord) == str:
                if GeneralComputations.findObjectbyName(coord):
                    coord = GeneralComputations.findObjectbyName(coord)  # get the coordinate
            distance.append(GeneralComputations.getdistancetocoord(SpaceObj, coord))
        if len(distance) > 0:
            index = distance.index(min(distance))
            return coordList[index]
        else:
            return coordList[0]

    @staticmethod
    def findObject(unique_id):
        allActive = SpaceObjects.activeShips | SpaceObjects.activeStations | SpaceObjects.activeNPCs | SpaceObjects.activeShuttles
        if allActive.get(unique_id):
            return allActive.get(unique_id)

    @staticmethod
    def findObjectbyName(name):
        allActive = SpaceObjects.activeShips | SpaceObjects.activeStations | SpaceObjects.activeNPCs | SpaceObjects.activeShuttles
        for value in allActive.values():
            if value.ObjectData.get("name_tag", 0).lower() == name.lower():
                coord = (value.Object.pos.x, value.Object.pos.y, value.Object.pos.z)
                return coord


class Sensors:

    @staticmethod
    def filterbyEmissions(SpaceObj, scanList):
        filteredObjs = []
        for object in scanList:
            distanceCoeff = 1000/sbs.distance(SpaceObj.Object, object.Object)
            emissions = object.shipSystems.get("Emissions")
            detectionLevel = emissions.EmissionLevel * distanceCoeff
            if detectionLevel >= 0.1:
                filteredObjs.append(object)
        return filteredObjs

    @staticmethod
    def scanforalliedships(SpaceObj, scandistance):
        #returns a list of script NPC ship Objects
        allies = set()
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            if ping.unique_ID in SpaceObjects.activeNPCs.keys() and ping.unique_ID != SpaceObj.ObjectID and ping.side == SpaceObj.Object.side:
                value = SpaceObjects.activeNPCs.get(ping.unique_ID)
                if value:
                    if value.ObjectState in ["Damaged", "Surrendered"]:
                        pass
                    else:
                        allies.add(value)
        return allies

    @staticmethod
    def scanfornamed(SpaceObj, targetNames, scandistance):
        targetList = set()
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            allObjects = SpaceObjects.activeShips | SpaceObjects.activeNPCs | SpaceObjects.activeStations
            if ping.unique_ID in allObjects.keys():
                value = allObjects.get(ping.unique_ID)
                if value.ObjectState in ["Damaged", "Surrendered"]:
                    pass
                else:
                    for type in targetNames:
                        if type == value.ObjectData.get("name_tag", 0):
                            targetList.add(value.Object)
        return targetList

    @staticmethod
    def scanfornamedObjects(SpaceObj, targetNames, scandistance):
        # returns a list of script Objects, based on specific names
        targetList = set()
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            targetObj = GeneralComputations.findObject(ping.unique_ID)
            if targetObj:
                if targetObj.ObjectData.get("name_tag", 0) in targetNames:
                    targetList.add(targetObj)
        return targetList

    @staticmethod
    def scanfortargetObjects(SpaceObj, targetTypes, scandistance):
        # creates a list of script ship objects within a set distance
        targetList = set()
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            targetObj = GeneralComputations.findObject(ping.unique_ID)
            if targetObj:
                for type in targetTypes:
                    if type in targetObj.ObjectTags:
                        posstarget = targetObj
                        if posstarget.Faction == SpaceObj.Faction:
                            pass
                        elif posstarget.ObjectState in ["Damaged", "Surrendered"]:
                            pass
                        else:
                            targetList.add(targetObj)
        return targetList

    @staticmethod
    def scanforallyObjects(SpaceObj, targetTypes, scandistance):
        # creates a list of ships within a set distance
        targetList = set()
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            targetObj = GeneralComputations.findObject(ping.unique_ID)
            if targetObj:
                for type in targetTypes:
                    if type in targetObj.ObjectTags:
                        posstarget = targetObj
                        if posstarget.Object.side == SpaceObj.Object.side:
                            targetList.add(targetObj)
        return targetList

    @staticmethod
    def scanforhostileObjects(SpaceObj, scandistance):
        # creates a list of ships within a set distance
        targetList = set()
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            targetObj = GeneralComputations.findObject(ping.unique_ID)
            if targetObj:
                if targetObj.Object.side != SpaceObj.Object.side and targetObj.Faction != SpaceObj.Faction:
                    targetList.add(targetObj)
        return targetList


    @staticmethod
    def scanfortargets(SpaceObj, targetTypes, scandistance):
        # creates a list of ships within a set distance
        targetList = set()
        for type in targetTypes:
            #check the custom ship properties first
            for key, value in tsn_databases.allProperties.items():
                if "tags" in value.keys():
                    if type in value.get("tags"):
                        targetList.add(key)
        targets = set()
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            if ping.data_tag in targetList:
                if ping.unique_ID == SpaceObj.ObjectID:
                    pass
                if ping.tick_type in ["behav_npcship", "behav_station"]:
                    if ping.side != SpaceObj.Object.side:
                        targets.add(ping)
                elif ping.tick_type == "behav_playership":
                    if ping.data_tag == "tsn_life_pod":
                        #ignore lifepods
                        pass
                    else:
                        if GeneralComputations.checkdestroyed(ping.unique_ID):
                            if ping.side != SpaceObj.Object.side:
                                targets.add(ping)
        return targets

    @staticmethod
    def scanforactiveobjects(SpaceObj, scandistance):
        objects = []
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            if ping.unique_ID != SpaceObj.ObjectID:
                if ping.tick_type in ["behav_npcship", "behav_playership", "behav_station"]:
                    if ping.side == "CiC":
                        pass
                    elif ping.side != SpaceObj.Object.side:
                        # check if the object is on your side
                        if ping.data_tag == "tsn_life_pod":
                            # ignore lifepods
                            pass
                        elif ping.tick_type == "behav_playership":
                            # do an extra check on player ships
                            if GeneralComputations.checkdestroyed(ping.unique_ID):
                                # check if the object is still alive
                                objects.append(ping)
                        else:
                            objects.append(ping)
        return objects

    @staticmethod
    def scanforterrain(SpaceObj, scandistance):
        terrain = []
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            if ping.unique_ID != SpaceObj.ObjectID:
                if ping.tick_type in ["behav_asteroid", "behav_nebula"]:
                    terrain.append(ping)
        return terrain

    @staticmethod
    def scanforbehavtype(SpaceObj, scandistance, behavList):
        objects = []
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            if ping.unique_ID != SpaceObj.ObjectID:
                if ping.tick_type in behavList:
                    objects.append(ping)
        return objects


    @staticmethod
    def checkclosest(SpaceObj, set):
        # checks a set of script objects to determine which is the closest
        objectlist = list(set)
        distance = []
        for object in objectlist:
            if simulation.simul.space_object_exists(object.ObjectID):
                distance.append(sbs.distance(SpaceObj.Object, object.Object))
        if len(distance) > 0:
            index = distance.index(min(distance))
            return objectlist[index]
        else:
            return None

    @staticmethod
    def checkclosestEnemy(SpaceObj, set):
        # checks a set of objects to determine which is the closest
        objectlist = list(set)
        distance = []
        for object in objectlist:
            if object.ObjectSide != SpaceObj.ObjectSide:
                distance.append(sbs.distance(SpaceObj.Object, object.Object))
        if len(distance) > 0:
            index = distance.index(min(distance))
            return objectlist[index]
        else:
            return None

    @staticmethod
    def checkaggressors(SpaceObj, targetList):
        objectlist = list(targetList)
        aggressorlist = set()
        for object in objectlist:
            if SpaceObj.ObjectData.get("target_id", 0) == SpaceObj.ObjectID or SpaceObj.ObjectData.get("weapon_target_UID", 0) == SpaceObj.ObjectID:
                aggressorlist.add(object)
        return aggressorlist

    @staticmethod
    def checkunshielded(targetList):
        objectlist = list(targetList)
        unshieldedlist = set()
        for object in objectlist:
            objectdata = object.data_set
            if objectdata.get("shield_raised_flag", 0) == 0:
                unshieldedlist.add(object)
            for shieldNo in objectdata.get("shield_count", 0):
                if objectdata.get("shield_val", shieldNo) == 0:
                    unshieldedlist.add(object)
        return unshieldedlist

    @staticmethod
    def checkshielded(targetList):
        objectlist = list(targetList)
        shieldedlist = set()
        for object in objectlist:
            objectdata = object.data_set
            if objectdata.get("shield_raised_flag", 0) != 0:
                shieldedlist.add(object)
            for shieldNo in objectdata.get("shield_count", 0):
                if objectdata.get("shield_val", shieldNo) != 0:
                    shieldedlist.add(object)
        return shieldedlist

    @staticmethod
    def checkarmed(targetList):
        objectlist = list(targetList)
        armedlist = set()
        for object in objectlist:
            objectdata = object.data_set
            if objectdata.get("torpedo_tube_count", 0) > 0 or objectdata.get("beamCount", 0) > 0:
                armedlist.add(object)
        return armedlist

    @staticmethod
    def checkunarmed(targetList):
        objectlist = list(targetList)
        unarmedlist = set()
        for object in objectlist:
            objectdata = object.data_set
            if objectdata.get("torpedo_tube_count", 0) == 0 or objectdata.get("beamCount", 0) == 0:
                unarmedlist.add(object)
        return unarmedlist

    """@staticmethod
    def checklarger(SpaceObj, targetList):
        objectlist = list(targetList)
        largerlist = set()
        for object in objectlist:
            objectdata = object.data_set
            shieldstrength = 0
            for x in range(objectdata.get("shield_count", 0)):
                shieldstrength += objectdata.get("shield_max_val", x)
            if shieldstrength > SpaceObj.AI.durability:
                largerlist.add(object)
        return largerlist"""

    """@staticmethod
    def checksmaller(SpaceObj, targetList):
        objectlist = list(targetList)
        smallerlist = set()
        for object in objectlist:
            objectdata = object.data_set
            shieldstrength = 0
            for x in range(objectdata.get("shield_count", 0)):
                shieldstrength += objectdata.get("shield_max_val", x)
            if shieldstrength < SpaceObj.AI.durability:
                smallerlist.add(object)
        return smallerlist"""

    """@staticmethod
    def checkfirepower(SpaceObj, targetList):
        objectlist = list(targetList)
        firepowerlist = set()
        for object in objectlist:
            objectdata = object.data_set
            power = 0
            for x in range(objectdata.get("beamCount", 0)):
                power += objectdata.get("beamDamage", x) / objectdata.get("beamCycleTime", 0)
            if power < SpaceObj.AI.durability:
                firepowerlist.add(object)
        return firepowerlist"""


class Targeting(GeneralComputations):
    # this is all basic targeting and scanning data functions

    @staticmethod
    def setweaponstarget(SpaceObj, target):
        # sets the target to fire at
        if target.ObjectID == SpaceObj.ObjectData.get("target_id", 0):
            pass
        else:
            message = f"Targeting a new ship"

        SpaceObj.ObjectData.set("target_id", target.ObjectID, 0)

    @staticmethod
    def clearweaponstarget(SpaceObj):
        SpaceObj.ObjectData.set("target_id", -1, 0)

    """@staticmethod
    def smarttarget(SpaceObj, sensorRange, **kwargs):
        if kwargs.get("targets"):
            targetList = kwargs.get("targets")
        else:
            # smart target list - choosing a target that makes sense
            targetList = Sensors.scanfortargets(SpaceObj, SpaceObj.AI.myOrders.get("Targets"), sensorRange)
        if len(targetList) < 1:
            target = None
            Targeting.clearweaponstarget(SpaceObj)
        else:
            target = Sensors.checkclosest(SpaceObj, targetList)
            Targeting.setweaponstarget(SpaceObj, target)
        return target"""

    @staticmethod
    def TargetClosest(SpaceObj, myOrders, sensorRange):
        # this is a submethod of the attack and is set up to allow ships to target enemies nearby, but not move to them
        targets1 = Sensors.scanfortargetObjects(SpaceObj, myOrders.get("Targets"), sensorRange)
        targets2 = Sensors.scanfornamedObjects(SpaceObj, myOrders.get("Targets"), sensorRange)
        alltargets = Sensors.filterbyEmissions(SpaceObj, targets1 | targets2)
        selectedTarget = Sensors.checkclosest(SpaceObj, alltargets)
        if selectedTarget and sbs.distance(SpaceObj.Object, selectedTarget.Object) < 5000:
            Targeting.setweaponstarget(SpaceObj, selectedTarget)
            return selectedTarget
        else:
            Targeting.clearweaponstarget(SpaceObj)
            return selectedTarget

    @staticmethod
    def DesignatedTarget(SpaceObj, target):
        if target and sbs.distance(SpaceObj.Object, target.Object) < 5000:
            Targeting.setweaponstarget(SpaceObj, target)
            return target
        else:
            Targeting.clearweaponstarget(SpaceObj)
            return target


class Maneouvring:
    # this is all the basic movement orders that can be given

    @staticmethod
    def gettargetheading(targetObj):
        # calculate the heading that the targeted object is currently moving on
        return GeneralComputations.heading((targetObj.Object.forward_vector().x, targetObj.Object.forward_vector().z))

    @staticmethod
    def closeontarget(SpaceObj, targetObj, rapidmove, tacticalmove):
        # takes the targeted object, calculates the coordinate and then sets the move to point
        coord = (targetObj.Object.pos.x, targetObj.Object.pos.y, targetObj.Object.pos.z)
        Maneouvring.acceleratetotarget(SpaceObj, targetObj, rapidmove, tacticalmove)
        GeneralComputations.setmovetopoint(SpaceObj, coord)

    @staticmethod
    def movetorelativeposition(SpaceObj, targetObj, distance, rapidmove, tacticalmove, **kwargs):
        # takes a targeted object and calculates a coordinate at a bearing and distance relative to its heading then sets as a move to point
        if 'bearing' in kwargs.keys():
            bearing = kwargs.get('bearing')
        else:
            bearing = 180
        if 'height' in kwargs.keys():
            height = kwargs.get('height')
        else:
            height = 0
        targetheading = Maneouvring.gettargetheading(targetObj)
        coord = GeneralComputations.getrelativevectorcoord(targetObj, distance, math.degrees(targetheading) - bearing, height)
        Maneouvring.acceleratetocoord(SpaceObj, coord, rapidmove, tacticalmove)
        GeneralComputations.setmovetopoint(SpaceObj, coord)

    @staticmethod
    def movetorelativepoint(SpaceObj, coord, distance, rapidmove, tacticalmove, **kwargs):
        # takes a coordinate and then calculates a move to point based on a range and bearing to the coordinate
        if 'bearing' in kwargs.keys():
            bearing = kwargs.get('bearing')
        else:
            bearing = 180
        coord = GeneralComputations.getrelativepoint(distance, bearing, coord)
        Maneouvring.acceleratetocoord(SpaceObj, coord, rapidmove, tacticalmove)
        GeneralComputations.setmovetopoint(SpaceObj, coord)

    @staticmethod
    def acceleratetocoord(SpaceObj, coord, rapidmove, tacticalmove):
        standard = SpaceObj.ObjectData.get("standard_speed", 0)
        # changes the speed that ship should moves at depending on the distance from the coordinate
        distance = GeneralComputations.getdistancetocoord(SpaceObj, coord)
        Maneouvring.alterSpeed(SpaceObj, standard, tacticalmove, rapidmove, distance)

        #this increases the turn rate so the ship moves on to course more quickly
        direction = math.degrees(GeneralComputations.getheadingtoCoordinate(SpaceObj, coord))
        Maneouvring.alterTurn(SpaceObj, direction)

    @staticmethod
    def acceleratetotarget(SpaceObj, targetObj, rapidmove, tacticalmove):
        standard = SpaceObj.ObjectData.get("standard_speed", 0)
        # changes the speed that ship should moves at depending on the distance from the target
        distance = sbs.distance(SpaceObj.Object, targetObj.Object)
        Maneouvring.alterSpeed(SpaceObj, standard, tacticalmove, rapidmove, distance)

        # this increases the turn rate so the ship moves on to course more quickly
        direction = math.degrees(GeneralComputations.getheadingtoTarget(SpaceObj, targetObj))
        Maneouvring.alterTurn(SpaceObj, direction)

    @staticmethod
    def alterSpeed(Obj, standardSpeed, tacSpeed, rapSpeed, dist):
        if 3000 < dist:
            Obj.ObjectData.set("speed_coeff", standardSpeed * rapSpeed * 2, 0)
        elif 1000 < dist <= 3000:
            Obj.ObjectData.set("speed_coeff", standardSpeed * rapSpeed, 0)
        elif 500 < dist <= 1000:
            Obj.ObjectData.set("speed_coeff", standardSpeed * tacSpeed * 1.5, 0)
        elif 80 < dist <= 500:
            Obj.ObjectData.set("speed_coeff", standardSpeed * (tacSpeed + (tacSpeed / 2)), 0)
        elif 40 < dist <= 80:
            Obj.ObjectData.set("speed_coeff", standardSpeed * tacSpeed, 0)
        elif dist <= 40:
            Obj.ObjectData.set("speed_coeff", standardSpeed * (tacSpeed / 2), 0)

    @staticmethod
    def alterTurn(Obj, direction):
        if direction > 90:
            Obj.ObjectData.set("turn_upgrade_coeff", 2, 0)
        elif 45 < direction < 90:
            Obj.ObjectData.set("turn_upgrade_coeff", 1.5, 0)
        elif 15 < direction < 45:
            Obj.ObjectData.set("turn_upgrade_coeff", 1.2, 0)
        else:
            Obj.ObjectData.set("turn_upgrade_coeff", 1, 0)

    @staticmethod
    def moveonheading(SpaceObj, heading):
        coord = GeneralComputations.getrelativecoord(SpaceObj, 10000, heading)
        GeneralComputations.setmovetopoint(SpaceObj, coord)


class EvasiveBehaviours:

    @staticmethod
    def CheckEvasion(SpaceObj):
        #replace
        tolerance = 30 #percentage value of any shield
        evasionState = SpaceObj.ObjectData.get("evasion", 0)
        if not all(x > tolerance for x in GeneralComputations.calculateshields(SpaceObj)) and evasionState == False:
            SpaceObj.ObjectData.set("evasion", True, 0)
            evasionOrders = copy.deepcopy(fleetOrders.evasiveOrders)
            waypoint = GeneralComputations.getrelativecoord(SpaceObj, 200, 180)
            EvasiveBehaviours.EvasiveWaypointUpdate(SpaceObj, waypoint)
            newCommander = AI_Commanders.AISoloCommander(SpaceObj, {}, 1, Orders=evasionOrders)
            AI_Commanders.commanderaddList.append(newCommander)
        if evasionState and all(x > tolerance for x in GeneralComputations.calculateshields(SpaceObj)):
            SpaceObj.ObjectData.set("evasion", False, 0)
            commanderID = SpaceObj.ObjectData.get("Fleet Commander", 0)
            commanderObj = AI_Commanders.commanders.get(commanderID)
            if SpaceObj.ObjectData.get("exitpoint", 0) == "Exiting":
                newOrders = copy.deepcopy(fleetOrders.fallbackOrders)
            else:
                newOrders = copy.deepcopy(fleetOrders.reformOrders)
            commanderObj.Orders = newOrders

    @staticmethod
    def Evade(SpaceObj, myOrders, **kwargs):
        # first, scan for the threats (ships targeting the NPC) and find the closest
        # because I am evading, I cannot command other ships
        armed = Sensors.scanforhostileObjects(SpaceObj, 8000)
        waypoint = (SpaceObj.ObjectData.get("evasion", 1), SpaceObj.ObjectData.get("evasion", 2), SpaceObj.ObjectData.get("evasion", 3))
        Targeting.TargetClosest(SpaceObj, myOrders, 5000)
        if "carrier" in SpaceObj.ObjectTags:
            if len(armed) > 0:
                # if I am a carrier, authorise fighter launch!
                CarrierBehaviours.AuthoriseFighterLaunch(SpaceObj)
        if GeneralComputations.checkonpoint(SpaceObj, waypoint):
            if len(armed) > 0:
                closestthreat = Sensors.checkclosest(SpaceObj, armed)
                # now, pick a random direction to move away from that threat
                heading = math.degrees(GeneralComputations.getheadingtoTarget(SpaceObj, closestthreat))
                direction = heading - 180
                if direction > 360:
                    direction -= 360
                elif direction < 0:
                    direction += 360
                # finally, determine a waypoint to move towards
                waypoint = GeneralComputations.getrelativecoord(SpaceObj, 1000, direction)
                """for GM in SpaceObjects.activeGameMasters.keys():
                    sbs_tools.AddNavPoint(simulation.simul, f"Evade Point", waypoint, objectID=GM)"""
                Maneouvring.acceleratetocoord(SpaceObj, waypoint, 2, 2)
                GeneralComputations.setmovetopoint(SpaceObj, waypoint)
                EvasiveBehaviours.EvasiveWaypointUpdate(SpaceObj, waypoint)
            else:
                myHeading = GeneralComputations.getshipHeading(SpaceObj)
                direction = math.degrees(myHeading) + random.randint(-30, 30)
                if direction > 360:
                    direction -= 360
                elif direction < 0:
                    direction += 360
                waypoint = GeneralComputations.getrelativecoord(SpaceObj, 3000, direction)
                Maneouvring.acceleratetocoord(SpaceObj, waypoint, 2, 2)
                GeneralComputations.setmovetopoint(SpaceObj, waypoint)
                EvasiveBehaviours.EvasiveWaypointUpdate(SpaceObj, waypoint)

    @staticmethod
    def EvasiveWaypointUpdate(SpaceObj, waypoint):
        SpaceObj.ObjectData.set("evasion", waypoint[0], 1)
        SpaceObj.ObjectData.set("evasion", waypoint[1], 2)
        SpaceObj.ObjectData.set("evasion", waypoint[2], 3)

    @staticmethod
    def CheckFallback(SpaceObj, myOrders, **kwargs):
        pass

    @staticmethod
    def FallBack(SpaceObj, myOrders, **kwargs):
        EvasiveBehaviours.ExitWaypointUpdate(SpaceObj)
        exitpoint = (SpaceObj.ObjectData.get("exitpoint", 1), SpaceObj.ObjectData.get("exitpoint", 2), SpaceObj.ObjectData.get("exitpoint", 3))
        EvasiveBehaviours.ExitCleanUp(SpaceObj)
        if GeneralComputations.checkonpoint(SpaceObj, exitpoint):
            GeneralBehaviours.RemoveFleet(SpaceObj)
        else:
            EvasiveBehaviours.ExitWaypointUpdate(SpaceObj)
            Maneouvring.acceleratetocoord(SpaceObj, exitpoint, 2, 2)
            GeneralComputations.setmovetopoint(SpaceObj, exitpoint)

    @staticmethod
    def ExitWaypointUpdate(SpaceObj):
        if SpaceObj.ObjectData.get("exitpoint", 0) != "Exiting":
            if SpaceObj.Object.pos.x > 0:
                x = SpaceObj.Object.pos.x + 1000000
            else:
                x = SpaceObj.Object.pos.x -1000000
            if SpaceObj.Object.pos.z > 0:
                z = SpaceObj.Object.pos.z + 1000000
            else:
                z = SpaceObj.Object.pos.z - 1000000
            waypoint = (x, 0, z)
            SpaceObj.ObjectData.set("exitpoint", "Exiting", 0)
            SpaceObj.ObjectData.set("exitpoint", waypoint[0], 1)
            SpaceObj.ObjectData.set("exitpoint", waypoint[1], 2)
            SpaceObj.ObjectData.set("exitpoint", waypoint[2], 3)

    @staticmethod
    def Surrender(SpaceObj, myOrders, **kwargs):
        EvasiveBehaviours.ExitCleanUp(SpaceObj)
        if SpaceObj.ObjectState != "Surrendered":
            SpaceObj.ObjectData.set("speed_coeff", 0, 0)
            SpaceObj.ObjectState = "Surrendered"
            SpaceObj.ObjectData.set("radar_color_override", "yellow", 0)
            simulation.simul.force_update_to_clients(SpaceObj.ObjectID, 0)
            commanderID = SpaceObj.ObjectData.get("Fleet Commander", 0)
            commanderObj = AI_Commanders.commanders.get(commanderID)
            commanderObj.Orders = copy.deepcopy(fleetOrders.surrenderOrders)

    @staticmethod
    def ExitCleanUp(SpaceObj):
        scandistance = 50000
        objects = []
        for ping in sbs.broad_test(-scandistance + SpaceObj.Object.pos.x, -scandistance + SpaceObj.Object.pos.z, scandistance + SpaceObj.Object.pos.x, scandistance + SpaceObj.Object.pos.z, 0xfff0):
            if ping.unique_ID != SpaceObj.ObjectID:
                if ping.tick_type in ["behav_npcship", "behav_playership", "behav_station"]:
                    if ping.side == "CiC" or ping.side == SpaceObj.Object.side or ping.data_tag == "tsn_life_pod":
                        pass
                    elif ping.tick_type == "behav_playership":
                        # do an extra check on player ships
                        if GeneralComputations.checkdestroyed(ping.unique_ID):
                            # check if the object is still alive
                            objects.append(ping)
                    else:
                        objects.append(ping)
        if len(objects) == 0:
            GeneralBehaviours.RemoveFleet(SpaceObj)


class GeneralBehaviours:
    #space object, order reference, kwargs

    @staticmethod
    def RemoveFleet(SpaceObj, **kwargs):
        myCommander = SpaceObj.ObjectData.get("Fleet Commander", 0)
        myCommanderObj = AI_Commanders.commanders.get(myCommander)
        for Obj in myCommanderObj.FleetMembers.values():
            sbs.delete_object(Obj.ObjectID)
        for GM, GMObj in SpaceObjects.activeGameMasters.items():
            if GMObj.ObjectData.get("science_target_UID", 0) == SpaceObj.ObjectID:
                menuSystems = GMObj.shipSystems.get("Menus")
                selectionPanel = menuSystems.selectionPanel
                selectionPanel.paneldata.clear()
                moveSystems = GMObj.shipSystems.get("Movement")
                moveSystems.selectedObj = -1
                GMObj.ObjectData.set("science_target_UID", -1, 0)


    @staticmethod
    def AllStop(SpaceObj, myOrders, **kwargs):
        params = myOrders.get("Parameters")
        sensorRange = params.get("Sensor Range")
        Targeting.TargetClosest(SpaceObj, myOrders, sensorRange)
        SpaceObj.ObjectData.set("speed_coeff", 0, 0)

    @staticmethod
    def StandOff(SpaceObj, myOrders, **kwargs):
        params = myOrders.get("Parameters")
        sensorRange = params.get("Sensor Range")
        selectedTarget = Targeting.TargetClosest(SpaceObj, myOrders, sensorRange)
        if selectedTarget:
            bearing = GeneralComputations.getheadingtoTarget(selectedTarget, SpaceObj)
            Maneouvring.movetorelativeposition(SpaceObj, selectedTarget, 4000, 2, 1, bearing=bearing)

    @staticmethod
    def Move(SpaceObj, myOrders, **kwargs):
        params = myOrders.get("Parameters")
        locations = params.get("Locations")
        sensorRange = params.get("Sensor Range")
        Targeting.TargetClosest(SpaceObj, myOrders, sensorRange)
        if len(locations) == 0:
            heading = random.randint(0, 359)
            coord = GeneralComputations.getrelativecoord(SpaceObj, sensorRange, heading)
            locations.append(coord)
        else:
            coordinate = locations[0]
            if type(locations[0]) == str:
                if GeneralComputations.findObjectbyName(locations[0]):
                    coordinate = GeneralComputations.findObjectbyName(locations[0])  # get the coordinate
            if GeneralComputations.checkonpoint(SpaceObj, coordinate):  # returns true if within 500 of coordinate
                locations.clear()
                heading = random.randint(0, 359)
                coord = GeneralComputations.getrelativecoord(SpaceObj, sensorRange, heading)
                locations.append(coord)
                coordinate = locations[0]
            if coordinate:
                GeneralComputations.setmovetopoint(SpaceObj, coordinate)


class LeaderBehaviours:

    @staticmethod
    def Reform(SpaceObj, myOrders, **kwargs):
        params = myOrders.get("Parameters")
        sensorRange = params.get("Sensor Range")
        nearbyAllies = Sensors.scanforalliedships(SpaceObj, sensorRange * 2)
        if len(nearbyAllies) > 0:
            for ally in nearbyAllies:
                ship = SpaceObjects.activeNPCs.get(ally.ObjectID)
                fleetCommandID = ship.ObjectData.get("Fleet Commander", 0)
                fleetCommandObj = AI_Commanders.commanders.get(fleetCommandID)
                myCommander = SpaceObj.ObjectData.get("Fleet Commander", 0)
                if isinstance(fleetCommandObj, AI_Commanders.AISoloCommander) and fleetCommandObj.Orders.get("Fleet Task") != "Evade" and fleetCommandObj.FleetCommanderID != myCommander:
                    #if this is also a solo commander, we need to make a fleet
                    fleetmembers = {SpaceObj.ObjectID: SpaceObj,
                                    ship.ObjectID: ship}
                    AI_Commanders.commanderkillList.append(fleetCommandID)
                    newCommander = AI_Commanders.AIGroupCommander(SpaceObj, fleetmembers, 2)
                    AI_Commanders.commanderaddList.append(newCommander)
                    AI_Commanders.commanderkillList.append(myCommander)
                    break
                elif isinstance(fleetCommandObj, AI_Commanders.AIGroupCommander) and fleetCommandObj.FleetCommanderID != myCommander:
                    #if this is already a group commander, I will join them
                    fleetCommandObj.FleetMembers.update({SpaceObj.ObjectID: SpaceObj})
                    SpaceObj.ObjectData.set("Fleet Commander", id(fleetCommandObj), 0)
                    #now I am no longer a solo ship, I will remove my commander
                    AI_Commanders.commanderkillList.append(myCommander)
                    break
            LeaderBehaviours.Attack(SpaceObj, myOrders)
        else:
            LeaderBehaviours.Attack(SpaceObj, myOrders)


    @staticmethod
    def Patrol(SpaceObj, myOrders, **kwargs):
        # patrol to specified points in the location list

        params = myOrders.get("Parameters")
        locations = params.get("Locations")
        sensorRange = params.get("Sensor Range")
        patrolPoint = params.get("Patrol Point")
        if "Sensors" in kwargs.keys():
            sensorRange = kwargs.get("Sensors")
        Targeting.TargetClosest(SpaceObj, myOrders, sensorRange)
        hostiles = Sensors.scanforhostileObjects(SpaceObj, sensorRange)

        if len(hostiles) > 0:
            if not params.get("PatrolLoc"):
                coord = (SpaceObj.Object.pos.x, SpaceObj.Object.pos.y, SpaceObj.Object.pos.z)
                params.update({"PatrolLoc": coord})  # store the current location
            elif GeneralComputations.getdistancetocoord(SpaceObj, params.get("PatrolLoc")) > 8000:
                GeneralComputations.setmovetopoint(SpaceObj, params.get("PatrolLoc"))  # set a max range to move away from the current location
            else:
                LeaderBehaviours.Attack(SpaceObj, myOrders)

        elif len(locations) > 0 and len(hostiles) == 0:
            nextpoint = locations[patrolPoint]
            if params.get("PatrolLoc"):
                Maneouvring.acceleratetocoord(SpaceObj, nextpoint, 1.8, 1)
                GeneralComputations.setmovetopoint(SpaceObj, nextpoint)
                nextpoint = GeneralComputations.checkclosestCoord(SpaceObj, locations) #check which is the closest patrol point to return to
                curPoint = locations.index(nextpoint)
                params.pop("PatrolLoc")
                params.update({"Patrol Point": curPoint})

            if type(nextpoint) == str:
                if GeneralComputations.findObjectbyName(nextpoint):
                    coordinate = GeneralComputations.findObjectbyName(nextpoint)  # get the coordinate
                    nextpoint = coordinate  # now reset the next point to a coord
                else:
                    if patrolPoint + 1 == len(locations):
                        params.update({"Patrol Point": 0})
                    else:
                        params.update({"Patrol Point": patrolPoint + 1})
            if GeneralComputations.checkonpoint(SpaceObj, nextpoint):  # returns true if within 500 of coordinate
                if patrolPoint + 1 == len(locations):
                    params.update({"Patrol Point": 0})  # reset the index back to 0 to begin the patrol route again
                else:
                    params.update({"Patrol Point": patrolPoint + 1})
            GeneralComputations.setmovetopoint(SpaceObj, nextpoint)

        else:
            LeaderBehaviours.Attack(SpaceObj, myOrders)

    @staticmethod
    def Attack(SpaceObj, myOrders, **kwargs):
        # scan for a target based on my order, then move towards them and attack
        # this is set up specifically for a commander of a fleet
        params = myOrders.get("Parameters")
        sensorRange = params.get("Sensor Range")
        selectedTarget = Targeting.TargetClosest(SpaceObj, myOrders, sensorRange)
        if selectedTarget:
            Maneouvring.closeontarget(SpaceObj, selectedTarget, 1.8, 1)
        else:
            GeneralBehaviours.Move(SpaceObj, myOrders)

    @staticmethod
    def Support(SpaceObj, myOrders, **kwargs):
        pass
        """# scan the area for other allies that are not in my fleet
        # check if they are currently engaging a target or not
        # move in to attack their target too
        friendlies = [SpaceObj.Object.side.lower()]
        allies = Sensors.scanforallyObjects(SpaceObj, friendlies, 5000)
        # target any enemies that come close to me
        Targeting.TargetClosest(SpaceObj, myOrders, 5000)
        # override here if an ally is being targeted nearby
        FleetMembers = SpaceObj.AI.FleetMembers
        for allyObj in allies:
            if allyObj in FleetMembers:
                # ignore the target if it is already in my fleet
                pass
            if allyObj.ObjectData.get("target_id", 0) > 0:
                allyTarget = GeneralComputations.findObject(allyObj.ObjectData.get("target_id", 0))
                Maneouvring.closeontarget(SpaceObj, allyTarget, 1.9, 1)
                Targeting.TargetClosest(SpaceObj, myOrders, 5000)
                break
            else:
                leader = allyObj.AI.FleetCommander
                #move to a relative position to the leader of the fleet
                Maneouvring.movetorelativeposition(SpaceObj, leader, 3000, 1.9, 1, bearing=90)
                Targeting.TargetClosest(SpaceObj, myOrders, 5000)"""

    @staticmethod
    def HoldPosition(SpaceObj, myOrders, **kwargs):
        GeneralBehaviours.AllStop(SpaceObj, myOrders)

    @staticmethod
    def Defend(SpaceObj, myOrders):
        params = myOrders.get("Parameters")
        locations = params.get("Locations")
        sensorRange = params.get("Sensor Range")
        specialData = params.get("SpecialData")
        allActive = SpaceObjects.activeShips | SpaceObjects.activeStations | SpaceObjects.activeNPCs | SpaceObjects.activeShuttles
        if len(locations) > 1:
            locations.clear() #clear out the locations list
        if specialData[0] in allActive.keys():
            defenseObjID = specialData[0]
            defenseObj = specialData[1]
            defenseDist = specialData[2]
            hostiles = Sensors.scanforhostileObjects(defenseObj, defenseDist)
            if len(hostiles) > 0:
                aggressors = Sensors.checkaggressors(defenseObj, hostiles)
                if len(aggressors) > 0:
                    nearesttarget = Sensors.checkclosest(defenseObj, aggressors)
                else:
                    nearesttarget = Sensors.checkclosest(defenseObj, hostiles)
                selectedTarget = Targeting.DesignatedTarget(SpaceObj, nearesttarget)
                if selectedTarget:
                    Maneouvring.closeontarget(SpaceObj, selectedTarget, 1.8, 1)
            else:
                Targeting.TargetClosest(SpaceObj, myOrders, sensorRange)
                if len(locations) == 0:
                    heading = random.randint(0, 359)
                    coord = GeneralComputations.getrelativecoord(defenseObj, defenseDist/2, heading)
                    locations.append(coord)
                else:
                    if GeneralComputations.checkonpoint(SpaceObj, locations[0]):  # returns true if within 500 of coordinate
                        locations.clear()
                    LeaderBehaviours.Patrol(SpaceObj, myOrders, Sensors=defenseDist)
        else:
            LeaderBehaviours.Attack(SpaceObj, myOrders)


class NonCombatBehaviours:

    @staticmethod
    def Transport(SpaceObj, myOrders, **kwargs):
        params = myOrders.get("Parameters")
        locations = params.get("Locations")
        sensorRange = params.get("Sensor Range")
        patrolPoint = params.get("Patrol Point")
        Targeting.TargetClosest(SpaceObj, myOrders, sensorRange)
        if len(locations) > 0:
            nextpoint = locations[patrolPoint]
            if type(nextpoint) == str:
                if GeneralComputations.findObjectbyName(nextpoint):
                    coordinate = GeneralComputations.findObjectbyName(nextpoint)  # get the coordinate
                    nextpoint = coordinate  # now reset the next point to a coord
                else:
                    if patrolPoint + 1 == len(locations):
                        params.update({"Patrol Point": 0})
                    else:
                        params.update({"Patrol Point": patrolPoint + 1})
            if GeneralComputations.checkonpoint(SpaceObj, nextpoint):  # returns true if within 500 of coordinate
                if patrolPoint + 1 == len(locations):
                    params.update({"Patrol Point": 0})  # reset the index back to 0 to begin the patrol route again
                else:
                    params.update({"Patrol Point": patrolPoint + 1})
            GeneralComputations.setmovetopoint(SpaceObj, nextpoint)


class FollowerBehaviours:

    @staticmethod
    def Follow(SpaceObj, myOrders, **kwargs):
        pass
        """FollowerBehaviours.assumeFormation(SpaceObj, [], {})
        Targeting.TargetClosest(SpaceObj, myOrders, 5000)"""

    @staticmethod
    def assumeFormation(SpaceObj, fleetCommander, position, formation, myOrders):
        params = myOrders.get("Parameters")
        separation = params.get("Fleet Separation")
        match formation:
            case "v": # delta formation
                if position % 2 == 0:
                    bearing = 120
                else:
                    bearing = -120
            case "RightE": # echelon
                bearing = -120
            case "LeftE": # echelon
                bearing = 120
            case _:
                bearing = 180
        speed = fleetCommander.ObjectData.get("speed_coeff", 0)
        Maneouvring.movetorelativeposition(SpaceObj, fleetCommander, separation * position, speed * 2, speed, bearing=bearing)
        position += 1

    @staticmethod
    def SupportLeader(SpaceObj, myOrders, **kwargs):
        fleetCommander = SpaceObj
        position = 0
        formation = "astern"
        if "commander" in kwargs:
            fleetCommander = kwargs.get("commander")
        if "position" in kwargs:
            position = kwargs.get("position")
        if "formation" in kwargs:
            formation = kwargs.get('formation')
        # scan the area for other allies that are not in my fleet
        # check if they are currently engaging a target or not
        # move in to attack their target too
        # target any enemies that come close to me
        params = myOrders.get("Parameters")
        selectedTarget = Targeting.TargetClosest(SpaceObj, myOrders, 1000)
        if selectedTarget:
            if sbs.distance(SpaceObj.Object, fleetCommander.Object) < params.get("Max Distance") * 2:
                Maneouvring.closeontarget(SpaceObj, selectedTarget, 1.8, 1)
            else:
                FollowerBehaviours.assumeFormation(SpaceObj, fleetCommander, position, formation, myOrders)
        else:
            FollowerBehaviours.assumeFormation(SpaceObj, fleetCommander, position, formation, myOrders)


class CarrierBehaviours:

    @staticmethod
    def CarrierOperations(SpaceObj, myOrders, **kwargs):
        # scan for a target based on my order, then move towards them and attack
        # this is set up specifically for a commander of a fleet
        params = myOrders.get("Parameters")
        sensorRange = params.get("Sensor Range")
        threats = Sensors.scanforhostileObjects(SpaceObj, min(sensorRange/2, 5000))
        if len(threats) > 0:
            # if there are threats, authorise fighter launch!
            CarrierBehaviours.AuthoriseFighterLaunch(SpaceObj)
            GeneralBehaviours.StandOff(SpaceObj, myOrders)
        else:
            LeaderBehaviours.Attack(SpaceObj, myOrders)

    @staticmethod
    def CarrierSupport(SpaceObj, myOrders, **kwargs):
        if "commander" in kwargs:
            fleetCommander = kwargs.get("commander")
        else:
            fleetCommander = SpaceObj
        if "position" in kwargs:
            position = kwargs.get("position")
        else:
            position = 0
        if "formation" in kwargs:
            formation = kwargs.get('formation')
        else:
            formation = "astern"
        # scan the area for other allies that are not in my fleet
        # check if they are currently engaging a target or not
        # move in to attack their target too
        # target any enemies that come close to me
        params = myOrders.get("Parameters")
        sensorRange = params.get("Sensor Range")
        threats = Sensors.scanforhostileObjects(SpaceObj, min(sensorRange/2, 5000))
        if len(threats) > 0:
            CarrierBehaviours.AuthoriseFighterLaunch(SpaceObj)
        FollowerBehaviours.assumeFormation(SpaceObj, fleetCommander, position, formation, myOrders)

    @staticmethod
    def AuthoriseFighterLaunch(SpaceObj):
        commanderkilledList = []
        for commanderID, commanderObj in SpaceObj.WingCommanders.items():
            print(AI_Commanders.commanders.get(commanderID))
            if commanderID in AI_Commanders.commanders.keys(): #check it is still an active commander
                print(commanderObj.FighterState)
                print(commanderObj.RefitTimer)
                print(sbs.app_minutes())
                if commanderObj.FighterState == "Docked" and 0 < commanderObj.RefitTimer < sbs.app_minutes():
                    for fighterObj in commanderObj.FleetMembers.values():
                        fighterObj.deployFighter()

                    commanderObj.FighterState = "Deployed"
                    commanderObj.Orders.update({"Fleet Task": "Strike"})
                    params = commanderObj.Orders.get("Parameters")
                    params.update({"Support Elements": "Support Leader"})
                    commanderObj.RTBTimer = sbs.app_minutes() + 1
                    commanderObj.RefitTimer = 0
            else:
                commanderkilledList.append(commanderID)
        for commanderID in commanderkilledList:
            SpaceObj.WingCommanders.pop(commanderID) #if it isn't an active commander, remove it

    @staticmethod
    def RTB(FighterObj, myOrders, **kwargs):
        if simulation.simul.space_object_exists(FighterObj.ParentShip.ObjectID):
            Maneouvring.closeontarget(FighterObj, FighterObj.ParentShip, 2, 1.8)
            Targeting.TargetClosest(FighterObj, myOrders, 1000)
            distance = sbs.distance(FighterObj.Object, FighterObj.ParentShip.Object)
            if distance < 200:
                FighterObj.dockFighter()
        else:
            EvasiveBehaviours.FallBack(FighterObj, myOrders)

    @staticmethod
    def Strike(FighterObj, myOrders, **kwargs):
        LeaderBehaviours.Attack(FighterObj, myOrders)

    @staticmethod
    def CheckFighterEvasion(SpaceObj):
        # replace
        tolerance = 30  # percentage value of any shield
        evasionState = SpaceObj.ObjectData.get("evasion", 0)
        if not all(x > tolerance for x in GeneralComputations.calculateshields(SpaceObj)) and evasionState == False:
            SpaceObj.ObjectData.set("evasion", True, 0)

    @staticmethod
    def DefendMother():
        pass

    @staticmethod
    def DefendFleet():
        pass

    @staticmethod
    def DefendTarget():
        pass
