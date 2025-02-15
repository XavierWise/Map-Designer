import random, hjson, os, sbs
import sbs_tools as tools
import simulation
import tsn_databases, Objects
from Terrain import TerrainTypes
from Objects import SpaceObjects, JumpPoints, Stations


blackholeIDs = []
asteroidIDs = []
nebulaIDs = []
asteroidfields = {}
nebulafields = {}
minefields = {}
sensorMarkers = []


def systemlist():
    path = os.getcwd() + "\data\missions\Map Designer\Terrain\\"
    systems = set()
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".json"): #changed from .dat
                save_name = os.path.splitext(file)[0]
                systems.add(save_name)
    return systems


def compileSystemInformation():
    allsystems = {}
    for systemname in systemlist():
        print(systemname)
        with open(tools.find(f"{systemname}.json", os.getcwd()), "r") as systemdatafile:
            systemdata = hjson.load(systemdatafile)
            alignment = systemdata.get("systemalignment")
            mapCoord = systemdata.get("systemMapCoord")
        allsystems.update({systemname: [mapCoord, alignment]})
    return allsystems


allsystems = compileSystemInformation()


def generateLineCoords(seed, start, end, density, scatter, height):
    random.seed(seed)
    coordList = []
    if start[0] == end[0]:
        coordList.append((start[0], start[1], start[2]))
    else:
        gradient = (end[2] - start[2]) / (end[0] - start[0])
        constant = start[2] - (gradient * start[0])
        for d in range(density):
            try:
                xcoord = random.randint(int(start[0]), int(end[0]))
            except:
                xcoord = random.randint(int(end[0]), int(start[0]))
            zcoord = (gradient * xcoord) + constant
            changex = random.choice([random.randint(0, int(scatter)), 0 - (random.randint(0, int(scatter)))])
            changez = random.choice([random.randint(0, int(scatter)), 0 - (random.randint(0, int(scatter)))])
            ycoord = random.uniform(-600, 600)
            finalcoordinate = (int(xcoord + changex), ycoord, int(zcoord + changez))
            coordList.append(finalcoordinate)
    return coordList


#checked and improved code
def loaddata(systemname):
    with open(tools.find(f"{systemname}.json", os.getcwd()), "r") as systemdatafile:
        systemdata = hjson.load(systemdatafile)
        simulation.systemMapCoord = systemdata.get("systemMapCoord")
        simulation.systemAlignment = systemdata.get("systemalignment")
        terrainlist = systemdata.get("terrain")
        objectlist = systemdata.get("objects")
    return terrainlist, objectlist


def spawnTerrain(sim, system):
    # create all the terrain
    terrain, objects = loaddata(system)
    generateTerrain(sim, terrain)
    systemObjectList = setupObjects(system, objects)
    for object in systemObjectList:
        object.SpawnObject(sim)
    for marker, GMobject in SpaceObjects.activeGameMasters.items():
        GMobject.ObjectData.set("num_extra_scan_sources", 0, 0)
        GMobject.addscansources()


def generateTerrain(sim, terrainlist):
    #create the asteroids, nebula, minefields and blackholes in the system
    for id, data in terrainlist.items():
        if data.get("type") == "blackhole":
            newBlackhole = TerrainTypes.AddBlackHole(sim, data.get("name"), data.get("coordinate"))
            blackholeIDs.append(newBlackhole)
        elif data.get("type") == "hidden_minefield":
            minefield = TerrainTypes.HiddenMinefield(sim, data.get("coordinate"), data.get("height"), data.get("width"), data.get("density"))
            minefields.update({minefield.ID: minefield})
        else:
            coordinates = generateLineCoords(data.get("seed"), data.get("start"), data.get("end"), int(data.get("density")), int(data.get("scatter")), 0)
            fieldIDList = []
            if data.get("type") == "asteroids":
                choiceList = []
                for coordinate in coordinates:
                    asteroidTypeList = data.get("composition")
                    for asteroidType in asteroidTypeList:
                        choiceList += tsn_databases.terrainDatabase.get(asteroidType)
                    ast = random.choice(choiceList)
                    newAsteroid = TerrainTypes.AddAsteroid(sim, ast, coordinate)
                    asteroidIDs.append(newAsteroid)
                    fieldIDList.append(newAsteroid)
                    AsteroidObj = simulation.simul.get_space_object(newAsteroid)
                    AsteroidData = AsteroidObj.data_set
                    AsteroidData.set("FieldID", id, 0)
                data.update({"fieldIDList": fieldIDList})
                asteroidfields.update({id: data})
            elif data.get("type") == "nebulas":
                for coordinate in coordinates:
                    newNebula = TerrainTypes.AddNebula(sim, "nebula", coordinate)
                    nebulaIDs.append(newNebula)
                    fieldIDList.append(newNebula)
                    NebulaObj = simulation.simul.get_space_object(newNebula)
                    NebulaData = NebulaObj.data_set
                    NebulaData.set("FieldID", id, 0)
                data.update({"fieldIDList": fieldIDList})
                nebulafields.update({id: data})
            createSensorMarker(id, data.get("start"))
            createSensorMarker(id, data.get("end"))


def createSensorMarker(fieldID, coord):
    marker = simulation.simul.create_space_object("behav_sensormarker", "generic-cylinder", 0xfff0)
    markerObj = simulation.simul.get_space_object(marker)
    markerData = markerObj.data_set
    markerData.set("local_scale_coeff", 0.1, 0)
    markerData.set("fieldID", fieldID, 0)
    simulation.simul.reposition_space_object(markerObj, coord[0], coord[1], coord[2])
    sensorMarkers.append(markerObj)
    for GMID, GMObj in SpaceObjects.activeGameMasters.items():
        index = GMObj.ObjectData.get("num_extra_scan_sources", 0)
        GMObj.ObjectData.set("extra_scan_source", marker, index)


def setupObjects(system, objects):
    #create the stations and jump points in the system
    objectList = []
    waypoints = {}
    for name, data in objects.items():
        if data.get("type") == "station":
            newObject = Stations.setupStation(name, data)
        elif data.get("type") == "jump_point":
            newObject = JumpPoints.JumpPoint(name, "behav_jumpnode", "invisible", "Jump Point", position=data.get("coordinate"), info=data)
        else:
            newObject = None
        if newObject:
            objectList.append(newObject)
            coord = data.get("coordinate")
            actCoord = coord[0], coord[1], coord[2]
            waypoints.update({name: actCoord})
    tsn_databases.waypointDatabase.update({system: waypoints})
    return objectList


def clearTerrain():
    # SpaceObjects.activeStations key/value dictionary of stations: ID, Object
    # SpaceObjects.activeJumpPoints key/value dictionary of jump points: ID, Object
    # SpaceObjects.activeObjects (eg. Lifepods, Marine pods, cargo pods etc) key/value dictionary of Objects: ID, Object
    # SpaceObjects.activeNPCs key/value dictionary of NPCs: ID, Object
    # asteroidIDs
    # nebulaIDs
    # minefields - key/value dictionary of minefields: ID, Object
    global asteroidIDs, nebulaIDs, blackholeIDs, minefields, asteroidfields, nebulafields
    for asteroid in asteroidIDs:
        sbs.delete_object(asteroid)
    for nebula in nebulaIDs:
        sbs.delete_object(nebula)
    for blackhole in blackholeIDs:
        sbs.delete_object(blackhole)
    asteroidIDs = []
    blackholeIDs = []
    nebulaIDs = []
    asteroidfields = {}
    nebulafields = {}

    deleteList = []
    for activeObjID in SpaceObjects.activeStations.keys() | SpaceObjects.activeObjects.keys() | SpaceObjects.activeJumpPoints.keys():
        deleteList.append(activeObjID)
    for object in deleteList:
        sbs.delete_object(object)

    SpaceObjects.activeStations = {}
    SpaceObjects.activeObjects = {}

    deleteList = []
    for minefieldID in minefields.keys():
        deleteList.append(minefields.get(minefieldID))
    for minefield in deleteList:
        del minefield
    for markerObj in sensorMarkers:
        sbs.delete_object(markerObj.unique_ID)
    minefields = {}


def compileObjectList():
    # compiling all the data ready to save
    objectList = {}
    for SimObj in SpaceObjects.activeObjects.values(): #stored dictionary of script ID an script Object
        pass
    for SimObj in SpaceObjects.activeStations.values():  # stored dictionary of script ID an script Object
        name = SimObj.ObjectName
        coordinate = [SimObj.Object.pos.x, SimObj.Object.pos.y, SimObj.Object.pos.z]
        sides = [SimObj.Object.side]
        hull = SimObj.ObjectHullClass
        type = "station"
        facilities = SimObj.facilities
        cargo = {}
        for cargotype, cargodata in SimObj.Cargo.CargoHold.items():
            cargo.update({cargotype: cargodata.get("count")})
        teams = {}
        for team in SimObj.CrewMembers.shipCrew.values():

            if team.teamdata.get("Type") in teams.keys():
                count = teams.get(team.teamdata.get("Type")) + 1
                teams.update({team.teamdata.get("Type"): count})
            else:
                teams.update({team.teamdata.get("Type"): 1})
        objectList.update({
            name: {
                "coordinate": coordinate,
                "sides": sides,
                "hull": hull,
                "type": type,
                "facilities": facilities,
                "cargo": cargo,
                "teams": teams
            }
        })
    for SimObj in SpaceObjects.activeJumpPoints.values():  # stored dictionary of script ID an script Object
        name = SimObj.ObjectName
        coordinate = [SimObj.Object.pos.x, SimObj.Object.pos.y, SimObj.Object.pos.z]
        type = "jump_point"
        jumppointtype = SimObj.ObjectData.get("type", 0)
        state = SimObj.ObjectData.get("state", 0)
        drift = SimObj.JumpPointInfo.get("drift")
        destinations = SimObj.Destinations.copy()
        objectList.update({
            name: {
                "coordinate": coordinate,
                "type": type,
                "jumppointtype": jumppointtype,
                "destinations": destinations,
                "state": state,
                "drift": drift
            }
        })
    return objectList


def compileTerrainList():
    # compiling all the data ready to save
    terrainList = {}
    for AsteroidID, asteroidData in asteroidfields.items(): #stored dictionary of script ID an script Object
        asteroidFieldData = {
            "type": "asteroids",
            "seed": 2010,
            "start": asteroidData.get("start"),
            "end": asteroidData.get("end"),
            "density": asteroidData.get("density"),
            "scatter": asteroidData.get("scatter"),
            "composition": asteroidData.get("composition")}
        terrainList.update({AsteroidID: asteroidFieldData})

    for NebulaID, NebulaData in nebulafields.items():  # stored dictionary of script ID an script Object
        nebulaFieldData = {
            "type": "nebulas",
            "seed": 2010,
            "start": NebulaData.get("start"),
            "end": NebulaData.get("end"),
            "density": NebulaData.get("density"),
            "scatter": NebulaData.get("scatter"),
            "composition": NebulaData.get("composition")}
        terrainList.update({NebulaID: nebulaFieldData})
    return terrainList


def saveData(systemName):
    objectlist = compileObjectList()
    terrainlist = compileTerrainList()
    #terrainlist - parameters for spawning terrain locations
    #objectlist - individual objects and all attached data
    with open(tools.find(f"{systemName}.json", os.getcwd()), "w") as file:
        file.write(hjson.dumpsJSON({"systemMapCoord": simulation.systemMapCoord, "systemalignment": simulation.systemAlignment, "objects": objectlist, "terrain": terrainlist}, separators=(",", ":"), indent=5))


def createSystem(systemName):
    clearTerrain()
    objectlist = compileObjectList()
    terrainlist = compileTerrainList()
    path = os.getcwd() + f"\data\missions\Map Designer\Terrain\\{systemName}.json"
    with open(path, "w") as file:
        file.write(hjson.dumpsJSON(
            {"systemMapCoord": simulation.systemMapCoord, "systemalignment": simulation.systemAlignment, "objects": objectlist, "terrain": terrainlist}, separators=(",", ":"), indent=5))
