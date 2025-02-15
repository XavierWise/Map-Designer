import sbs, simulation

import sbs_tools
from Objects import SpaceObjects
from NPC_Ships import AI_Commanders
from Terrain import TerrainHandling
from Clients import ClientNEW


scriptrunning = False


def StartScript(sim):
    global scriptrunning, simul
    #this completes an initial set up of the script when it is first run
    if scriptrunning == False:
        scriptrunning = True
        sbs.suppress_client_connect_dialog(0)
        sbs.create_new_sim()
        sbs.resume_sim()
        simulation.simul = sim
        for client in sbs.get_client_ID_list():
            ClientNEW.setupClient(client)
        simulation.HandleSimulationStart()


def cosmos_event_handler(sim, event):
    #this only runs once, when the script is first started
    StartScript(sim)
    #print(event.tag)
    if "client_connect" == event.tag:
        clientID = event.client_id
        ClientNEW.setupClient(clientID)
    if "mission_tick" == event.tag:
        if simulation.simstatus:
            HandleSimulationTick(sim)
    else:
        #these will only execute when the simulation is not running

        simulation.Server.myMenu.menuTriggers(event)
        simulation.Server.clientMonitors(event)

        #these will only execute when the simulation is running
        if simulation.simstatus:

            if ClientNEW.activeClients.get(event.client_id):
                clientObj = ClientNEW.activeClients.get(event.client_id)
                clientObj.clientMonitors(event)
                clientObj.myShip.ObjectEventTriggers(event)
                clientObj.myConsoles.consoleTriggers(event)

            if SpaceObjects.activeStations.get(event.selected_id):
                stationObj = SpaceObjects.activeStations.get(event.selected_id)
                stationObj.ObjectEventTriggers(event)

            if SpaceObjects.activeNPCs.get(event.selected_id):
                npcObj = SpaceObjects.activeNPCs.get(event.selected_id)
                npcObj.ObjectEventTriggers(event)

            if SpaceObjects.activeShuttles.get(event.parent_id):
                shuttleObj = SpaceObjects.activeShuttles.get(event.parent_id)
                shuttleObj.ObjectEventTriggers(event)

            # Specific listener functions for each of the lists
            for station in SpaceObjects.activeStations.values():
                station.ObjectEventMonitors(event)

            for shuttle in SpaceObjects.availableShuttles.values():
                shuttle.ObjectEventMonitors(event)

            for GM in SpaceObjects.activeGameMasters.values():
                GM.ObjectEventMonitors(event)


StationDestroyedList = set()
NPCDestroyedList = set()
ObjectDestroyedList = set()


def HandleSimulationTick(sim):
    for CommanderID, Commander in AI_Commanders.commanders.items():
        Commander.AITickMonitors()
    if AI_Commanders.commanderkillList:
        for CommanderID in AI_Commanders.commanderkillList:
            AI_Commanders.commanders.pop(CommanderID)
        AI_Commanders.commanderkillList.clear()
    if AI_Commanders.commanderaddList:
        for CommanderObj in AI_Commanders.commanderaddList:
            AI_Commanders.commanders.update({id(CommanderObj): CommanderObj})
        AI_Commanders.commanderaddList.clear()

    for NPCID, NPCObj in SpaceObjects.activeNPCs.items():
        if sim.space_object_exists(NPCID):
            NPCObj.Damage.damagerepairroutine()
            NPCObj.ObjectTickMonitors()
        else:
            if not sbs.in_standby_list_id(NPCID):
                NPCDestroyedList.add(NPCObj)
    if NPCDestroyedList:
        for dead in NPCDestroyedList:
            del SpaceObjects.activeNPCs[dead.ObjectID]
            del(dead)
        NPCDestroyedList.clear()

    for minefield in TerrainHandling.minefields.values():
        minefield.trackArea()

    for shuttleObj in SpaceObjects.activeShuttles.values():
        shuttleObj.ObjectTickMonitors()

    for marker in SpaceObjects.activeGameMasters.values():
        marker.ObjectTickMonitors()

    for StationID, StationObj in SpaceObjects.activeStations.items():
        if sim.space_object_exists(StationID):
            StationObj.ObjectTickMonitors()
        else:
            StationDestroyedList.add(StationObj)
    if StationDestroyedList:
        for destroyed in StationDestroyedList:
            del SpaceObjects.activeStations[destroyed.ObjectID]
            del destroyed
        StationDestroyedList.clear()

    for jumppoint in SpaceObjects.activeJumpPoints.values():
        jumppoint.ObjectTickMonitors()

    for objectID, objectObj in SpaceObjects.activeObjects.items():
        if sim.space_object_exists(objectID):
            if objectObj.Timer < sbs.app_minutes():
                sbs.delete_object(objectID)
                ObjectDestroyedList.add(objectObj)
    if ObjectDestroyedList:
        for destroyed in ObjectDestroyedList:
            del SpaceObjects.activeObjects[destroyed.ObjectID]
            del destroyed
        ObjectDestroyedList.clear()
