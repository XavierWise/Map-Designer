import sbs, hjson, os, sbs_tools, tsn_databases
from Terrain import TerrainHandling
from Clients import ClientNEW
from Objects import SpaceObjects

#simul is the simulation object
simul = None

#simstatus is used to track whether the simulation is running
simstatus = False
simwarpmode = False
startSystem = "Corus2"
systemMapCoord = [0, 0, 0]
systemAlignment = ""

Server = ClientNEW.Server(0)



def HandleSimulationStart():
    global simstatus, simul, playerships
    TerrainHandling.clearTerrain()
    TerrainHandling.spawnTerrain(simul, startSystem)
    simstatus = True
    for client in ClientNEW.activeClients.values():
        sbs_tools.crender(client, "")

