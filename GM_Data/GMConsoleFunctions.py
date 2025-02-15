import sbs, random, simulation, copy
from Objects import NPCShips, SpaceObjects, CrewData, Stations, OtherObjects, JumpPoints
from GM_Data import GMData
from NPC_Ships import AI_Commanders, fleetOrders
import sbs_tools, tsn_databases
from Clients import ClientNEW
from Clients import Console_GUI as GUI
from Terrain import TerrainHandling, TerrainTypes

#icon bar at the top, that can display different options for which panels to display
class IconBar:
    def __init__(self, clientObj):
        self.clientObj = clientObj
        self.icondatabase = {
            f"{id(self)}FleetSpawn": {"icon": 324,
                                      "name": "Fleet Spawn",
                                    "colour": "#02FA38",
                                    "type": GMPanelTypes.FleetSpawnPanel,
                                    "triggers": PanelTriggers.FleetSpawn},
            f"{id(self)}ShipSpawn": {"icon": 325,
                                    "name": "Ship Spawn",
                                     "colour": "#02FA38",
                                     "type": GMPanelTypes.ShipSpawnPanel,
                                     "triggers": PanelTriggers.ShipSpawn},
            f"{id(self)}StationSpawn": {"icon": 114,
                                    "name": "Station Spawn",
                                    "colour": "#02FA38",
                                    "type": GMPanelTypes.StationSpawnPanel,
                                    "triggers": PanelTriggers.StationSpawn},
            f"{id(self)}ObjSpawn": {"icon": 99,
                                    "name": "Object Spawn",
                                     "colour": "#02FA38",
                                     "type": GMPanelTypes.ObjectSpawnPanel,
                                     "triggers": PanelTriggers.ObjectSpawn},
            f"{id(self)}JumpSpawn": {"icon": 323,
                                        "name": "Jump Point Spawn",
                                        "colour": "#02FA38",
                                        "type": GMPanelTypes.JumpSpawnPanel,
                                        "triggers": PanelTriggers.JumpSpawn},
            f"{id(self)}TerSpawn": {"icon": 13,
                                    "name": "Terrain",
                                    "colour": "#02FA38",
                                    "type": GMPanelTypes.TerrainPanel,
                                    "triggers": PanelTriggers.Terrain},
            f"{id(self)}Settings": {"icon": 321,
                                    "name": "Settings",
                                    "colour": "#02FA38",
                                    "type": GMPanelTypes.SettingsPanel,
                                    "triggers": PanelTriggers.Settings}
        }
        self.iconbarControls = {
            "Expand": {"icon": 18,
                       "trigger": f"{id(self)}expand",
                       "colour": "white"},
            "Collapse": {"icon": 97,
                         "trigger": f"{id(self)}collapse",
                         "colour": "orange"}}
        self.pos = (2, 5)
        self.state = "expanded"
        self.width = 1

    def Triggers(self, event):
        if str(id(self)) in event.sub_tag:
            if event.sub_tag == f"{id(self)}expand":
                self.state = "expanded"
                sbs_tools.crender(self.clientObj, "")
            if event.sub_tag == f"{id(self)}collapse":
                self.state = "collapsed"
                sbs_tools.crender(self.clientObj, "")
            if event.sub_tag in self.icondatabase.keys():
                #set up a new menu to display in game
                data = self.icondatabase.get(event.sub_tag)
                paneltype = data.get("type")
                paneltriggers = data.get("triggers")
                panelname = data.get("name")
                self.addnewPanel(panelname, paneltype, paneltriggers)

    def displayBar(self):
        self.width = 1
        if self.state == "expanded":
            self.expandedBar()
            control = self.iconbarControls.get("Collapse")
        else:
            control = self.iconbarControls.get("Expand")
        sbs.send_gui_image(self.clientObj.clientID, "", "iconbar_background", "image: ../missions/TSN Cosmos/Images/Box-50; color: #4f4f4f", self.pos[0], self.pos[1], self.pos[0] + self.width + 1, self.pos[1] + 4)
        sbs.send_gui_rawiconbutton(self.clientObj.clientID, "", f"{control.get('trigger')}", f"icon_index: {control.get('icon')}; color: {control.get('colour')}", self.pos[0] + self.width, self.pos[1] + 1, self.pos[0] + self.width + 2, self.pos[1] + 3)

    def expandedBar(self):
        position = self.pos[0]
        for icon, data in self.icondatabase.items():
            sbs.send_gui_rawiconbutton(self.clientObj.clientID, "", f"{icon}", f"icon_index: {data.get('icon')}; color: {data.get('colour')}", position + self.width, self.pos[1], position + self.width + 4, self.pos[1] + 4)
            self.width += 4

    def addnewPanel(self, name, type, triggers):
        xpos = 1
        ypos = 10
        menus = self.clientObj.myShip.shipSystems.get("Menus")
        for panel in menus.panelDatabase[1:]:
            ypos += 43
        if ypos > 80:
            pass
        else:
            newPanel = FunctionsPanel(self.clientObj, name, (xpos, ypos), type, triggers)
            menus.panelDatabase.append(newPanel)
            sbs_tools.crender(self.clientObj, "")


#parent class of the functions and selection panels
class Panel:
    def __init__(self, clientObj):
        self.clientObj = clientObj
        self.panelControls = {
            "Expand": {"icon": 18,
                       "trigger": f"{id(self)}-expand",
                       "colour": "white"},
            "Collapse": {"icon": 97,
                         "trigger": f"{id(self)}-collapse",
                         "colour": "orange"}
        }
        self.page = 1
        self.paneldata = {}
        self.active = False

    def Triggers(self, event):
        # these triggers are for the individual console functions, as well as the triggers for the console type
        if self.active:
            if GMGlobalFunctions.GlobalTriggers(event, self.paneldata):
                sbs_tools.crender(self.clientObj, "")
        if str(id(self)) in event.sub_tag:
            if event.sub_tag == f"{id(self)}-expand": # expand the menu to view the options
                self.state = "expanded"
                self.switchActive()
                sbs_tools.crender(self.clientObj, "")
            if event.sub_tag == f"{id(self)}-collapse": # collapse the menu to side
                self.state = "collapsed"
                self.active = False # make this inactive when collapsed
                sbs_tools.crender(self.clientObj, "")
            if "pageTrigger" in event.sub_tag: # change the displayed page on the menu
                page = event.sub_tag.split("-")
                self.page = page[0]
                self.switchActive()
                sbs_tools.crender(self.clientObj, "")
            if "makeactive" in event.sub_tag:
                self.switchActive()
                sbs_tools.crender(self.clientObj, "")

    def switchActive(self):
        menus = self.clientObj.myShip.shipSystems.get("Menus")
        for panel in menus.panelDatabase:
            panel.active = False
        self.active = True # make this the active panel when it is expanded

    def displayPanel(self):
        pass


#code for displaying the basic panel on the left
class FunctionsPanel(Panel):
    def __init__(self, clientObj, name, position, paneltype, paneltriggers):
        super().__init__(clientObj)
        self.name = name
        self.pos = position
        self.paneltype = paneltype
        self.paneltriggers = paneltriggers
        self.state = "expanded"
        self.panelControls.update(
            {"Close": {"icon": 97,
                      "trigger": f"{id(self)}-close",
                      "colour": "red"}
             })
        self.configurePanelData()

    def configurePanelData(self):
        if self.name == "Fleet Spawn":
            self.paneldata = {
                "FactionList": list(GMData.factions.keys()),
                "RaceList": [],
                "FleetList": [],
                "Factions": [],
                "Races": [],
                "Fleets": [],
                "FactionListPos": 0,
                "RaceListPos": 0,
                "SpawnList": "",
                "SpawnListPos": 0
            }
        if self.name == "Ship Spawn":
            self.paneldata = {
                "FactionList": list(GMData.factions.keys()),
                "RaceList": [],
                "ShipList": [],
                "Factions": [],
                "Races": [],
                "Ships": [],
                "FactionListPos": 0,
                "RaceListPos": 0,
                "ShipSpawnList": "",
                "ShipSpawnListPos": 0
            }
        if self.name == "Settings":
            self.paneldata = {
                "PlayerBeams": 5,
                "NPCBeams": 5
            }
        if self.name == "Station Spawn":
            self.paneldata = {
                "FactionList": list(GMData.factions.keys()),
                "RaceList": [],
                "StationList": [],
                "Factions": [],
                "Races": [],
                "Stations": [],
                "FactionListPos": 0,
                "RaceListPos": 0,
                "SpawnList": "",
                "SpawnListPos": 0
            }
        if self.name == "Jump Point Spawn":
            self.paneldata = {
                "JumpPointSpawn": True,
                "Type": "Jump Point"
            }
        if self.name == "Object Spawn":
            self.paneldata = {
                "ScrollPos": 0
            }
        if self.name == "Terrain":
            self.paneldata = {
                "Terrain": True,
                "StartEndPoint": "",
                "scatter": 1000,
                "density": 1,
                "type": "asteroids",
                "composition": ["Ast. Std Rand"],
                "start": (0, 0, 0),
                "end": (0, 0, 0),
                "SNavID": -1,
                "ENavID": -1

            }

    def Triggers(self, event):
        # these triggers are for the individual console functions, as well as the triggers for the console type
        super().Triggers(event)
        if str(id(self)) in event.sub_tag:
            if self.paneltriggers(event, self.paneldata): # triggers linked to the console type being displayed
                self.switchActive()
                sbs_tools.crender(self.clientObj, "")
            if event.sub_tag == f"{id(self)}-close": # close the menu and delete it
                menus = self.clientObj.myShip.shipSystems.get("Menus")
                menus.panelDatabase.remove(self)
                self.active = False  # make this inactive as it is being deleted
                sbs_tools.crender(self.clientObj, "")
                del self
                for panel in menus.panelDatabase[1:]:
                    panel.updatePosition()

    def updatePosition(self):
        xpos = 1
        ypos = 10
        menus = self.clientObj.myShip.shipSystems.get("Menus")
        panelNumber = menus.panelDatabase.index(self)
        ypos += 43 * (panelNumber - 1)
        self.pos = (xpos, ypos)
        sbs_tools.crender(self.clientObj, "")

    def displayPanel(self):
        close = self.panelControls.get("Close")
        if self.state == "expanded":
            control = self.panelControls.get("Collapse")
            self.holoBox(self.pos[0], self.pos[1], 35, 40)
            sbs.send_gui_rawiconbutton(self.clientObj.clientID, "", f"{control.get('trigger')}", f"icon_index: {control.get('icon')}; color: {control.get('colour')}", self.pos[0] + 35, self.pos[1], self.pos[0] + 37, self.pos[1] + 2)
            sbs.send_gui_rawiconbutton(self.clientObj.clientID, "", f"{close.get('trigger')}", f"icon_index: {close.get('icon')}; color: {close.get('colour')}", self.pos[0] + 35, self.pos[1] + 2, self.pos[0] + 37, self.pos[1] + 4)
            self.paneltype(id(self), self.name, self.clientObj, self.pos, (35, 40), self.page, self.paneldata)
            if self.active:
                sbs.send_gui_clickregion(self.clientObj.clientID, "", f"{id(self)}-makeactive", f"color: green; background_color:#ffffff3d", self.pos[0], self.pos[1], self.pos[0] + 35, self.pos[1] + 2)
                sbs.send_gui_image(self.clientObj.clientID, "", f"{id(self)}-titlebackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: green", self.pos[0], self.pos[1], self.pos[0] + 35, self.pos[1] + 2)
            else:
                sbs.send_gui_clickregion(self.clientObj.clientID, "", f"{id(self)}-makeactive", f"color: gray; background_color:#ffffff3d", self.pos[0], self.pos[1], self.pos[0] + 35, self.pos[1] + 2)
                sbs.send_gui_image(self.clientObj.clientID, "", f"{id(self)}-titlebackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: white", self.pos[0], self.pos[1], self.pos[0] + 35, self.pos[1] + 2)
        else:
            control = self.panelControls.get("Expand")
            sbs.send_gui_rawiconbutton(self.clientObj.clientID, "", f"{control.get('trigger')}", f"icon_index: {control.get('icon')}; color: {control.get('colour')}", self.pos[0], self.pos[1], self.pos[0] + 2, self.pos[1] + 2)
            sbs.send_gui_rawiconbutton(self.clientObj.clientID, "", f"{close.get('trigger')}", f"icon_index: {close.get('icon')}; color: {close.get('colour')}", self.pos[0], self.pos[1] + 2, self.pos[0] + 2, self.pos[1] + 4)
            self.holoBox(self.pos[0], self.pos[1], 1, 40)

    def holoBox(self, posx, posy, w, h):
        sbs.send_gui_image(self.clientObj.clientID, "", f"{id(self)}-holomenu_background", "image: ../missions/TSN Cosmos/Images/Box-50; color: #4f4f4f; draw_layer: 100", posx, posy, posx + w, posy + h)


#code for displaying the basic panel on the right
class SelectionPanel(Panel):
    def __init__(self, clientObj):
        super().__init__(clientObj)
        self.state = "collapsed"
        self.paneltype = GMPanelTypes.SelectionPanel
        self.paneltriggers = PanelTriggers.Selection

    def displayPanel(self):
        if self.state == "expanded":
            control = self.panelControls.get("Collapse")
            self.holoBox(100, 10, 25, 80)
            sbs.send_gui_rawiconbutton(self.clientObj.clientID, "", f"{control.get('trigger')}", f"icon_index: {control.get('icon')}; color: {control.get('colour')}", 73, 10, 75, 12)
            self.paneltype(id(self), self.clientObj, (75, 10), (25, 80), self.page, self.paneldata)
            if self.active:
                sbs.send_gui_clickregion(self.clientObj.clientID, "", f"{id(self)}-makeactive", f"color: green; background_color:#ffffff3d", 75, 10, 100, 14)
                sbs.send_gui_image(self.clientObj.clientID, "", f"{id(self)}-titlebackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: green", 75, 10, 100, 14)
            else:
                sbs.send_gui_clickregion(self.clientObj.clientID, "", f"{id(self)}-makeactive", f"color: gray; background_color:#ffffff3d", 75, 10, 100, 14)
                sbs.send_gui_image(self.clientObj.clientID, "", f"{id(self)}-titlebackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: white", 75, 10, 100, 14)
        else:
            control = self.panelControls.get("Expand")
            sbs.send_gui_rawiconbutton(self.clientObj.clientID, "", f"{control.get('trigger')}", f"icon_index: {control.get('icon')}; color: {control.get('colour')}", 96, 10, 99, 12)
            self.holoBox(100, 10, 1, 80)

    def Triggers(self, event):
        # these triggers are for the individual console functions, as well as the triggers for the console type
        super().Triggers(event)
        if str(id(self)) in event.sub_tag:
            if self.paneltriggers(event, self.paneldata):  # triggers linked to the console type being displayed
                self.switchActive()
                sbs_tools.crender(self.clientObj, "")

        if event.tag == "select_space_object" and event.sub_tag == "GMControls" and event.value_tag == "science_2d_view" and event.selected_id != 0 and event.extra_extra_tag == "lmb":
            # if a valid object is selected, immediately expand this panel to show the information on it
            self.state = "expanded"
            if self.paneldata.get("AIDefendAdd"):
                allActive = SpaceObjects.activeShips | SpaceObjects.activeStations | SpaceObjects.activeNPCs | SpaceObjects.activeShuttles
                defenseObj = allActive.get(event.selected_id)
                commander = self.paneldata.get("Commander")
                params = commander.Orders.get("Parameters")
                params.update({"SpecialData": [int(event.selected_id), defenseObj, 3000]})
                params.update({"Locations": []})
                self.clientObj.myShip.ObjectData.set("science_target_UID", self.paneldata.get("ID"), 0)
                self.paneldata.update({"AIDefendAdd": False})
                sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            elif self.paneldata.get("AILocsAdd"):
                allActive = SpaceObjects.activeShips | SpaceObjects.activeStations | SpaceObjects.activeNPCs | SpaceObjects.activeShuttles
                locObj = allActive.get(event.selected_id)
                if locObj:
                    commander = self.paneldata.get("Commander")
                    params = commander.Orders.get("Parameters")
                    locsList = params.get("Locations")
                    locsList.append(locObj.ObjectName)
                    PanelTriggers.updateVisibleLocs(self.paneldata, event)
                self.clientObj.myShip.ObjectData.set("science_target_UID", self.paneldata.get("ID"), 0)
                sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            elif self.paneldata.get("ID"):
                if event.selected_id != self.paneldata.get("ID"):
                    navpointList = self.paneldata.get("AILocsNavPoints")
                    if navpointList:
                        for navpointID in navpointList:
                            simulation.simul.delete_navpoint_by_id(navpointID)
                    self.paneldata = self.buildData(event.selected_id)
            else:
                self.paneldata = self.buildData(event.selected_id)
            self.switchActive()
            sbs_tools.crender(self.clientObj, "")
        elif event.value_tag == "science_2d_view" and self.paneldata and not self.paneldata.get("AILocsAdd"):
            self.state = ""
            navpointList = self.paneldata.get("AILocsNavPoints")
            if navpointList:
                for navpointID in navpointList:
                    simulation.simul.delete_navpoint_by_id(navpointID)
            self.paneldata.clear()
            sbs_tools.crender(self.clientObj, "")

    def holoBox(self, posx, posy, w, h):
        sbs.send_gui_image(self.clientObj.clientID, "", f"{id(self)}-holomenu_background", "image: ../missions/TSN Cosmos/Images/Box-50; color: #4f4f4f; draw_layer: 100", posx - w, posy, posx, posy + h)

    def buildData(self, selectedID):
        #decide what kind of space object this is
        #data = {"PanelAI": self.newAI}
        data = {}
        if selectedID in SpaceObjects.activeShips.keys():
            Object = SpaceObjects.activeShips.get(selectedID)
            data.update({"ID": Object.ObjectID})
            data.update({"Type": "Player Ship"})
            data.update({"Object Data":
                             {"Name": Object.ObjectName,
                              "Side": Object.Object.side,
                              "Hull": Object.ObjectHullClass}})
            data.update({"CargoPos": 0,
                         "PersonnelPos": 0,
                         "playerCarPos": 0,
                         "playerperPos": 0})
            return data
        elif selectedID in SpaceObjects.activeNPCs.keys():
            Object = SpaceObjects.activeNPCs.get(selectedID)
            data.update({"ID": Object.ObjectID})
            data.update({"Type": "NPC Ship",
                         "Rename": "",
                         })
            data.update({"Object Data":
                             {"Name": Object.ObjectName,
                              "Side": Object.Object.side,
                              "Hull": Object.ObjectHullClass,
                              }
                         })
            AICommanderID = Object.ObjectData.get("Fleet Commander", 0)
            AICommanderObj = AI_Commanders.commanders.get(AICommanderID)
            data.update({"AITaskPos": 0,
                         "AISidePos": 0,
                         "AISupportPos": 0,
                         "AITagsPos": 0,
                         "AILocsPos": 0,
                         "AILocsAdd": False,
                         "AILocsShow": False,
                         "AILocsNavPoints": [],
                         "AIDefendAdd": False,
                         "Commander": AICommanderObj})

            return data
        elif selectedID in SpaceObjects.activeStations.keys():
            Object = SpaceObjects.activeStations.get(selectedID)
            data.update({"ID": Object.ObjectID})
            data.update({"Type": "NPC Station",
                         "Rename": "",
                         })
            data.update({"Object Data":
                             {"Name": Object.ObjectName,
                              "Side": Object.Object.side,
                              "Hull": Object.ObjectHullClass,
                              "Cargo": Object.Cargo,
                              "Crew": Object.CrewMembers
                              }
                         })
            data.update({"CargoPos": 0,
                         "PersonnelPos": 0,
                         "playerCarPos": 0,
                         "playerperPos": 0})
            return data
        elif selectedID in SpaceObjects.activeShuttles.keys():
            Object = SpaceObjects.activeShuttles.get(selectedID)
            data.update({"ID": Object.ObjectID})
            data.update({"Type": "Player Shuttle"})
            data.update({"Object Data":
                             {"Name": Object.ObjectName,
                              "Side": Object.Object.side,
                              "Hull": Object.ObjectHullClass}})
            return data
        elif selectedID in SpaceObjects.activeJumpPoints.keys():
            Object = SpaceObjects.activeJumpPoints.get(selectedID)
            data.update({"ID": Object.ObjectID,
                         "Type": "Jump Point",
                         "Rename": ""})
            data.update({"Object Data":
                             {"Name": Object.ObjectName,
                              "Destinations": Object.Destinations,
                              "Drift": Object.drift,
                              "State": Object.ObjectData.get("state", 0),
                              "Type": Object.ObjectData.get("jumppointtype", 0),
                              }
                         })
            return data
        elif selectedID in TerrainHandling.asteroidIDs + TerrainHandling.nebulaIDs:
            Object = simulation.simul.get_space_object(selectedID)
            ObjData = Object.data_set
            FieldID = ObjData.get("FieldID", 0)
            FieldData = {}
            print(Object.tick_type)
            if Object.tick_type == "behav_asteroid":
                FieldData = TerrainHandling.asteroidfields.get(FieldID)
            elif Object.tick_type == "behav_nebula":
                FieldData = TerrainHandling.nebulafields.get(FieldID)
            print(FieldData)
            data.update({"Type": "Terrain",
                         "FieldID": FieldID,
                         "FieldData": FieldData,
                         "ObjID": selectedID,
                         "ObjData": ObjData})
            return data
        else:
            self.state = "collapsed"
            self.active = False
            return {}


#panels displayed on the left when an icon is clicked to open the panel
class GMPanelTypes:
    # these are specifically the designed consoles for each console type. These will display when selected

    @staticmethod
    def pageSelection(clientID, trigger, pages, position):
        xpos = position[0]
        ypos = position[1]
        w = 2
        h = 2
        pNum = 0
        for page in range(pages):
            pNum += 1
            sbs.send_gui_text(clientID, "", f"{pNum}{trigger}-text", f"color: white; font: gui-1; text:{pNum}; justify: center", xpos, ypos, xpos + w, ypos + h)
            sbs.send_gui_clickregion(clientID, "", f"{pNum}-{trigger}", f"background_color: green; color: gray; text:{pNum}", xpos, ypos, xpos + w, ypos + h)
            xpos += w
        sbs.send_gui_image(clientID, "", f"{trigger}-background", "image: ../missions/TSN Cosmos/Images/Box-50; color: #636363", position[0], ypos, xpos + w, ypos + h)

    @staticmethod
    def SelectionPanel(panelID, clientObj, position, wh, pageNo, data): # panel displayed when an object is selected - displayed on the right.
        xpos = position[0]
        ypos = position[1]
        w = wh[0]
        h = wh[1]
        selectedData = data.get("Object Data")
        panelname = "Select an Object"
        if selectedData:
            panelname = selectedData.get('Name')
        sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-title", f"color: white; font: gui-2; text:{panelname}", xpos, ypos, xpos + w, ypos + 5)
        sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-pageNo", f"color: white; font: gui-1; text:p. {pageNo}; justify: right", xpos, ypos, xpos + w, ypos + 2)
        GMPanelTypes.pageSelection(clientObj.clientID, f"{panelID}-pageTrigger", 5, (xpos, ypos + h - 2))
        if data.get("Type") == "Player Ship":
            GMSelectionPanels.PlayerSelection(panelID, clientObj, position, wh, pageNo, data)
        elif data.get("Type") == "NPC Station":
            GMSelectionPanels.StationSelection(panelID, clientObj, position, wh, pageNo, data)
        elif data.get("Type") == "NPC Ship":
            GMSelectionPanels.NPCSelection(panelID, clientObj, position, wh, pageNo, data)
        elif data.get("Type") == "Player Shuttle":
            GMSelectionPanels.ShuttleSelection(panelID, clientObj, position, wh, pageNo, data)
        elif data.get("Type") == "Jump Point":
            GMSelectionPanels.JumpNodeSelection(panelID, clientObj, position, wh, pageNo, data)
        elif data.get("Type") == "Terrain":
            GMSelectionPanels.TerrainSelection(panelID, clientObj, position, wh, pageNo, data)

    @staticmethod
    def MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data): # main panel functions
        xpos = position[0]
        ypos = position[1]
        w = wh[0]
        h = wh[1]
        sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-title", f"color: white; font: gui-1; text:{panelName}", xpos, ypos, xpos + w, ypos + 2)
        sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-pageNo", f"color: white; font: gui-1; text:Page: {pageNo}; justify: right", xpos, ypos, xpos + w, ypos + 2)
        #sbs.send_gui_image(clientObj.clientID, "", f"{panelID}-titlebackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: white", xpos, ypos, xpos + w, ypos + 2)
        GMPanelTypes.pageSelection(clientObj.clientID, f"{panelID}-pageTrigger", 5, (xpos, ypos + h - 2))

    @staticmethod
    def ObjectSpawnPanel(panelID, panelName, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1]
        ypos += 3
        GMPanelTypes.MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data)
        match int(pageNo):
            case 1:  # do this on page 1 of this console
                xpos += 1.5
                ypos += 2
                objectsList = list(GMData.otherObjectsDatabase.items())
                listPosition = data.get("ScrollPos")
                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-SelectObj", xpos, ypos, 23, 26, scrollbar=True, text="Object", currentPos=listPosition, maxLength=len(objectsList) - 4, colour="#ffffff3d")
                for x in range(listPosition, min(len(objectsList), listPosition + 8)):
                    objdata = objectsList[x]
                    name = objdata[0]
                    if data.get("SelectedObj") == name:
                        colour = "#006600"
                    else:
                        colour = "orange"
                    GUI.TabletButton(clientObj.clientID, "", f"{panelID}-SelectObjclick-{name}", xpos + 0.5, ypos, 22, 3, text=name, buttoncolour=colour)
                    ypos += 3.1

    @staticmethod
    def FleetSpawnPanel(panelID, panelName, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1]
        GMPanelTypes.MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data)
        match int(pageNo):
            case 1:
                factionlist = data.get("FactionList")
                factions = data.get("Factions")
                racelist = data.get("RaceList")
                races = data.get("Races")
                fleetlist = data.get("FleetList")
                fleets = data.get("Fleets")
                ypos += 5

                starty = ypos
                xpos += 1
                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-faction", xpos, ypos, 10.5, 17, scrollbar=True, text="Faction", currentPos=data.get("FactionListPos"),maxLength=len(factionlist)-1, colour="#ffffff3d")
                for x in range(data.get("FactionListPos"), min(len(factionlist), data.get("FactionListPos") + 5)):
                    faction = factionlist[x]
                    if faction in factions:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{faction}-factionList", xpos + 0.5, ypos, 9.5, 3, text=faction, togglecolour=colour, font="smallest")
                    ypos += 3.1

                ypos = starty
                xpos += 11.5
                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-race", xpos, ypos, 10.5, 17, scrollbar=True, currentPos=data.get("RaceListPos"), maxLength=len(racelist)-1, text="Race", colour="#ffffff3d")
                for x in range(data.get("RaceListPos"), min(len(racelist), data.get("RaceListPos") + 5)):
                    race = racelist[x]
                    if race in races:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{race}-raceList", xpos + 0.5, ypos, 9.5, 3, text=race, togglecolour=colour, font="smallest")
                    ypos += 3.1

                ypos = starty
                xpos += 11.5
                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-fleet", xpos, ypos, 10.5, 17, scrollbar=True, text="Fleet", currentPos=data.get("SpawnListPos"), maxLength=len(fleetlist)-1, colour="#ffffff3d")
                for x in range(data.get("SpawnListPos"), min(len(fleetlist), data.get("SpawnListPos") + 5)):
                    fleet = fleetlist[x]
                    if fleet in fleets:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{fleet}-fleetList", xpos + 0.5, ypos, 9.5, 3, text=fleet, togglecolour=colour, font="smallest")
                    ypos += 3.1
            case _:
                pass

    @staticmethod
    def ShipSpawnPanel(panelID, panelName, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1]
        GMPanelTypes.MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data)
        match int(pageNo):
            case 1:
                factionlist = data.get("FactionList")
                factions = data.get("Factions")
                racelist = data.get("RaceList")
                races = data.get("Races")
                shiplist = data.get("ShipList")
                ships = data.get("Ships")
                ypos += 5

                starty = ypos
                xpos += 1
                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-faction", xpos, ypos, 10.5, 17, scrollbar=True, text="Faction", currentPos=data.get("FactionListPos"),  maxLength=len(factionlist) - 1, colour="#ffffff3d")
                for x in range(data.get("FactionListPos"), min(len(factionlist), data.get("FactionListPos") + 5)):
                    faction = factionlist[x]
                    if faction in factions:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{faction}-factionList", xpos + 0.5, ypos, 9.5, 3, text=faction, togglecolour=colour, font="smallest")
                    ypos += 3.1

                ypos = starty
                xpos += 11.5
                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-race", xpos, ypos, 10.5, 17, scrollbar=True, currentPos=data.get("RaceListPos"), maxLength=len(racelist) - 1, text="Race", colour="#ffffff3d")
                for x in range(data.get("RaceListPos"), min(len(racelist), data.get("RaceListPos") + 5)):
                    race = racelist[x]
                    if race in races:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{race}-raceList", xpos + 0.5, ypos, 9.5, 3, text=race, togglecolour=colour, font="smallest")
                    ypos += 3.1

                ypos = starty
                xpos += 11.5
                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-ship", xpos, ypos, 10.5, 17, scrollbar=True, text="Ship", currentPos=data.get("ShipSpawnListPos"), maxLength=len(shiplist) - 1, colour="#ffffff3d")
                for x in range(data.get("ShipSpawnListPos"), min(len(shiplist), data.get("ShipSpawnListPos") + 5)):
                    ship = shiplist[x]
                    if ship in ships:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    shipData = tsn_databases.shipProperties.get(ship)
                    name = shipData.get("type")
                    #ship.split("_")[1]
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{ship}-shipList", xpos + 0.5, ypos, 9.5, 3, text=name.capitalize(), togglecolour=colour, font="smallest")
                    ypos += 3.1
            case _:
                pass

    @staticmethod
    def SchedulePanel(panelID, panelName, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1]
        w = wh[0]
        h = wh[1]
        GMPanelTypes.MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data)
        match pageNo:
            case _:
                pass

    @staticmethod
    def TerrainPanel(panelID, panelName, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1]
        w = wh[0]
        h = wh[1]
        GMPanelTypes.MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data)
        match pageNo:
            #terrain type
            #terrain sub-type
            #single or field
            #density of field
            case _:
                startendpoint = data.get("StartEndPoint")
                xpos += 1
                ypos += 5
                colour1 = "#ff3300"
                colour2 = "#ff3300"
                if startendpoint == "StartPoint":
                    colour1 = "#006600"
                elif startendpoint == "EndPoint":
                    colour2 = "#006600"
                GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-StartPoint", xpos + 0.5, ypos, 9.5, 3, text="Start", togglecolour=colour1, font="smallest")
                xpos += 10
                GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-EndPoint", xpos + 0.5, ypos, 9.5, 3, text="End", togglecolour=colour2, font="smallest")
                xpos += 11
                terrainList = "nebula^asteroids"
                selectedTerrain = data.get("type")
                sbs.send_gui_dropdown(clientObj.clientID, "", f"{panelID}-TerrainType", f"text: Terrain Type; font: gui-1; list:{terrainList}", xpos, ypos, xpos + 10, ypos + 3)

                xpos = position[0] + 1
                ypos += 5
                sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-terrainTitle", f"text:Selected Terrain - {selectedTerrain}; font: gui-1", xpos, ypos, xpos + 30, ypos + 3)
                scatter = data.get("scatter")
                ypos += 5
                sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-scatterTitle", f"text:Scatter {scatter}; font: gui-1", xpos, ypos, xpos + 30, ypos + 3)
                ypos += 3
                sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-scatter", scatter, "low:1000; high: 10000", xpos, ypos, xpos + 30, ypos + 3)
                density = data.get("density")
                ypos += 5
                sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-densityTitle", f"text:Density {density}; font: gui-1", xpos, ypos, xpos + 30, ypos + 3)
                ypos += 3
                sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-density", density, "low:1; high: 1000", xpos, ypos, xpos + 30, ypos + 3)
                xpos += 20
                ypos += 5
                GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-CreateTerrain", xpos + 0.5, ypos, 9.5, 3, text="Generate", togglecolour="green", font="smallest")

    @staticmethod
    def StationSpawnPanel(panelID, panelName, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1]
        w = wh[0]
        h = wh[1]
        GMPanelTypes.MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data)
        match pageNo:
            case 1:
                factionlist = data.get("FactionList")
                factions = data.get("Factions")
                racelist = data.get("RaceList")
                races = data.get("Races")
                stationlist = data.get("StationList")
                stations = data.get("Stations")
                ypos += 5

                starty = ypos
                xpos += 1
                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-faction", xpos, ypos, 10.5, 17, scrollbar=True, text="Faction", currentPos=data.get("FactionListPos"), maxLength=len(factionlist) - 1, colour="#ffffff3d")
                for x in range(data.get("FactionListPos"), min(len(factionlist), data.get("FactionListPos") + 5)):
                    faction = factionlist[x]
                    if faction in factions:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{faction}-factionList", xpos + 0.5, ypos, 9.5, 3, text=faction, togglecolour=colour, font="smallest")
                    ypos += 3.1

                ypos = starty
                xpos += 11.5

                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-race", xpos, ypos, 10.5, 17, scrollbar=True, currentPos=data.get("RaceListPos"), maxLength=len(racelist) - 1, text="Race", colour="#ffffff3d")
                for x in range(data.get("RaceListPos"), min(len(racelist), data.get("RaceListPos") + 5)):
                    race = racelist[x]
                    if race in races:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{race}-raceList", xpos + 0.5, ypos, 9.5, 3, text=race, togglecolour=colour, font="smallest")
                    ypos += 3.1

                ypos = starty
                xpos += 11.5

                GUI.menuBackground(clientObj.clientID, "", f"{panelID}-station", xpos, ypos, 10.5, 17, scrollbar=True, text="Station", currentPos=data.get("SpawnListPos"), maxLength=len(stationlist) - 1, colour="#ffffff3d")
                for x in range(data.get("SpawnListPos"), min(len(stationlist), data.get("SpawnListPos") + 5)):
                    station = stationlist[x]
                    if station in stations:
                        colour = "#006600"
                    else:
                        colour = "#ff3300"
                    stationData = tsn_databases.stationProperties.get(station)
                    name = stationData.get("type")
                    GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-{station}-stationList", xpos + 0.5, ypos, 9.5, 3, text=name.capitalize(), togglecolour=colour, font="smallest")
                    ypos += 3.1
            case _:
                pass

    @staticmethod
    def JumpSpawnPanel(panelID, panelName, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1]
        w = wh[0]
        h = wh[1]
        GMPanelTypes.MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data)
        ypos += 5
        xpos += 1
        match pageNo:
            case 1:
                GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-jump-node", xpos + 0.5, ypos, 9.5, 3, text=data.get("Type"), togglecolour="#006600", font="smallest")

    @staticmethod
    def SettingsPanel(panelID, panelName, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1]
        w = wh[0]
        h = wh[1]
        GMPanelTypes.MainPanel(panelID, panelName, clientObj, position, wh, pageNo, data)
        match int(pageNo):
            case 1:
                xpos += 20
                ypos += 10
                GUI.IncDecDisplay(clientObj.clientID, "", f"{panelID}-playerbeams", xpos + 0.5, ypos, 3, 3, name="Player Beams", value=data.get("PlayerBeams"))
                ypos += 5
                GUI.IncDecDisplay(clientObj.clientID, "", f"{panelID}-NPCbeams", xpos + 0.5, ypos, 3, 3, name= "NPC Beams", value=data.get("NPCBeams"))
                ypos += 10
                GUI.TabletButton(clientObj.clientID, "", f"{panelID}-update-beam-setting", xpos + 0.5, ypos, 10, 5, text="Update")
            case _:
                pass


#panels displayed on the right, when an object is selected by the GM
class GMSelectionPanels: #the panels displayed when a GM selects an object

    @staticmethod
    def PlayerSelection(panelID, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1] + 1
        w = wh[0]
        h = wh[1]
        # change the position of the page number so it doesn't overlap
        match int(pageNo):
            case 1:
                output = ""
                height = 6
                height += 4
                factions = GMData.factions.keys()
                menuitems = ""
                for faction in list(factions):
                    menuitems += f"{faction}^"
                sbs.send_gui_dropdown(clientObj.clientID, "", f"{panelID}-reassignSide-{data.get('ID')}", f"text: Select Side; font: gui-1; list:{menuitems}", xpos + 1, ypos + height, xpos + 20, ypos + height + 4)

            case 2:
                xpos += 1.5
                ypos += 8
                GMSelectionPanels.CargoManagementControls(panelID, clientObj, xpos, ypos, data)
            case 3:
                xpos += 1.5
                ypos += 8
                GMSelectionPanels.PersonnelManagementControls(panelID, clientObj, xpos, ypos, data)

    @staticmethod
    def StationSelection(panelID, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1] + 1
        w = wh[0]
        h = wh[1]
        sbs.send_gui_hotkey(clientObj.clientID, "TSNGM", f"GM-deleteObj", "KEY_DELETE", f"GM key to delete a single selected ship")
        sbs.send_gui_clickregion(clientObj.clientID, "", f"GM-deleteObj", "", 100, 100, 101, 101)
        StationID = data.get("ID")
        StationObj = SpaceObjects.activeStations.get(int(StationID))
        NPCRename = data.get("Rename")
        if StationObj:
            match int(pageNo):
                case 1:
                    shuttleBay = StationObj.shipSystems.get("ShuttleBay")
                    height = 6
                    #hull = GMData.stationsByHull.get(StationObj.ObjectHullClass)
                    stationdata = tsn_databases.stationProperties.get(StationObj.ObjectHullClass)
                    hull = stationdata.get("type")
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-StationHull", f"color: white; font: gui-1; text:{hull}; justify: left", xpos + 1, ypos + 3, xpos + w - 1, ypos + height)
                    height += 4
                    if shuttleBay.BayStatus:
                        colour = "green"
                    else:
                        colour = "red"
                    sbs.send_gui_button(clientObj.clientID, "", f"{panelID}-allowShuttleDock-{data.get('ID')}", f"text: Shuttle Dock; font: gui-1; color:{colour}", xpos + 1, ypos + height, xpos + 20, ypos + height + 4)
                    height += 4
                    factions = GMData.factions.keys()
                    menuitems = ""
                    for faction in list(factions):
                        menuitems += f"{faction}^"
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-renameHeader", f"color: white; font: gui-1; text:Rename Ship; justify: left", xpos + 1, ypos + 37, xpos + w - 1, ypos + 40)
                    sbs.send_gui_typein(clientObj.clientID, "", f"{panelID}-renameText", f"text: {NPCRename}", xpos + 1, ypos + 40, xpos + w - 1, ypos + 43)
                    sbs.send_gui_button(clientObj.clientID, "", f"{panelID}-renameSet", f"text: Set; font: gui-1", xpos + w - 5, ypos + 43, xpos + w - 1, ypos + 46)

                    sbs.send_gui_dropdown(clientObj.clientID, "", f"{panelID}-reassignSide-{data.get('ID')}", f"text: Select Side; font: gui-1; list:{menuitems}", xpos + 1, ypos + height, xpos + 20, ypos + height + 4)
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-hintsText", "text: Hotkeys^----------^DEL - Delete selected object^RMB - Move to point^; font: gui-1", xpos + 1, ypos + h - 20, 99, ypos + h - 5)
                case 2:
                    xpos += 1.5
                    ypos += 8
                    GMSelectionPanels.CargoManagementControls(panelID, clientObj, xpos, ypos, data)
                case 3:
                    xpos += 1.5
                    ypos += 8
                    GMSelectionPanels.PersonnelManagementControls(panelID, clientObj, xpos, ypos, data)

    @staticmethod
    def NPCSelection(panelID, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1] + 1
        w = wh[0]
        h = wh[1]
        NPCID = data.get("ID")
        NPCObj = SpaceObjects.activeNPCs.get(int(NPCID))
        NPCRename = data.get("Rename")
        # hot keys
        sbs.send_gui_hotkey(clientObj.clientID, "TSNGM", f"GM-deleteObj", "KEY_DELETE", f"GM key to delete a single selected ship")
        sbs.send_gui_hotkey(clientObj.clientID, "TSNGM", f"GM-deleteGrp", "KEY_END", f"GM key to delete a selected fleet of ships")
        sbs.send_gui_clickregion(clientObj.clientID, "", f"GM-deleteObj", "", 100, 100, 101, 101)
        sbs.send_gui_clickregion(clientObj.clientID, "", f"GM-deleteGrp", "", 100, 100, 101, 101)
        if NPCObj:
            AICommanderID = NPCObj.ObjectData.get("Fleet Commander", 0)
            AICommanderObj = AI_Commanders.commanders.get(AICommanderID)
            match int(pageNo):
                case 1: # basic functions related to NPC selection
                    currentOrders = AICommanderObj.Orders
                    parameters = currentOrders.get("Parameters")
                    fleetList = f"Side - {NPCObj.ObjectSide}^" \
                                f"----------^" \
                                f"Fleet Members^" \
                                f"----------^"
                    for obj in AICommanderObj.FleetMembers.values():
                        type = obj.ObjectHullClass.split("_")
                        fleetList += f"{obj.ObjectData.get('name_tag', 0)} - {type[1].capitalize()}^"
                    fleetList += f"----------^"\
                                 f"AI^" \
                                 f"----------^"\
                                 f"Orders - {currentOrders.get('Fleet Task')}^" \
                                 f"Sensor Range - {parameters.get('Sensor Range')}"
                    height = 5

                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-fleetlist", f"color: white; font: gui-1; text:{fleetList}; justify: left", xpos + 1, ypos + height, xpos + w - 1, ypos + height + 30)
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-renameHeader", f"color: white; font: gui-1; text:Rename Ship; justify: left", xpos + 1, ypos + 37, xpos + w - 1, ypos + 40)
                    sbs.send_gui_typein(clientObj.clientID, "", f"{panelID}-renameText", f"text: {NPCRename}", xpos + 1, ypos + 40, xpos + w - 1, ypos + 43)
                    sbs.send_gui_button(clientObj.clientID, "", f"{panelID}-renameSet", f"text: Set; font: gui-1", xpos + w - 5, ypos + 43, xpos + w - 1, ypos + 46)
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-hintsText", "text: Hotkeys^----------^DEL - Delete selected object^END - Delete selected fleet^RMB - Move to point^; font: gui-1", xpos + 1, ypos + h - 20, 99, ypos + h - 5)
                case 2: #AI controls for the NPC ship and fleet
                    ypos += 6
                    xpos += 1
                    currentOrders = AICommanderObj.Orders
                    fleetTask = currentOrders.get("Fleet Task")
                    taskList = list(NPCShips.AI_Commanders.tasksDatabase.items())
                    taskListPos = data.get("AITaskPos")
                    GUI.menuBackground(clientObj.clientID, "", f"{panelID}-AITaskSelect", xpos, ypos, 23, 16, colour="#ffffff3d", scrollbar=True, text="AI Task", currentPos=taskListPos, maxLength=len(taskList) - 4)
                    for x in range(taskListPos, min(len(taskList), taskListPos + 5)):
                        task = taskList[x]
                        name = task[0]
                        colour = "#ffffff3d"
                        if name == fleetTask:
                            colour = "green"
                        GUI.TabletButton(clientObj.clientID, "", f"{panelID}-AITaskSelection-{name}", xpos + 0.5, ypos, 22, 3, text=f"{name}", buttoncolour=colour)
                        ypos += 3.1

                    ypos = 39
                    params = currentOrders.get("Parameters")
                    if fleetTask == "Defend":
                        specialData = params.get("SpecialData")
                        defenseObjID = specialData[0]
                        defenseObj = specialData[1]
                        defenseDist = specialData[2]
                        name = "No designated target"
                        if defenseObj:
                            name = f"Defend {defenseObj.ObjectName}"
                        if not defenseDist:
                            defenseDist = 1000

                        sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-AIDefenseTargetTitle", f"text:{name}; font: gui-1", xpos, ypos, xpos + 22, ypos + 6)
                        colour = "#ffffff3d"
                        if data.get("AIDefendAdd"):
                            colour = "green"
                        ypos = 42
                        GUI.TabletButton(clientObj.clientID, "", f"{panelID}_AIDefendAdd", xpos, ypos, 10, 6, text="Designate Target", buttoncolour=colour)
                        ypos = 53
                        sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-AIDefenseDistTitle", f"text:Defense Zone = {round(defenseDist, -3)}k; font: gui-1", xpos, ypos, xpos + 22, ypos + 6)
                        sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-AIDefenseDist", round(defenseDist, -3), "low:1000 ; high: 100000; color:#0D4D00", xpos, ypos + 3, xpos + 22, ypos + 5)
                    else:
                        supportList = list(NPCShips.AI_Commanders.SupportElementDatabase.items())
                        supportListPos = data.get("AISupportPos")
                        GUI.menuBackground(clientObj.clientID, "", f"{panelID}-AISupportSelect", xpos, ypos, 23, 16, colour="#ffffff3d", scrollbar=True, text="Support Task", currentPos=supportListPos, maxLength=len(supportList) - 4)
                        for x in range(supportListPos, min(len(supportList), supportListPos + 5)):
                            supporttask = supportList[x]
                            name = supporttask[0]
                            colour = "#ffffff3d"
                            if name == params.get("Support Elements"):
                                colour = "green"
                            GUI.TabletButton(clientObj.clientID, "", f"{panelID}-AISupportSelection-{name}", xpos + 0.5, ypos, 22, 3, text=f"{name}", buttoncolour=colour)
                            ypos += 3.1

                    ypos = 60
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-AISensorRangeTitle", f"text:Sensor Range = {round(params.get('Sensor Range'), -3)}k; font: gui-1", xpos, ypos, xpos + 22, ypos + 6)
                    sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-AISensorRange", round(params.get('Sensor Range'), -3), "low:1000 ; high: 100000; color:#0D4D00", xpos, ypos + 3, xpos + 22, ypos + 5)

                    ypos = 67
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-AISeparationTitle", f"text:Fleet Separation = {round(params.get('Fleet Separation'))}; font: gui-1", xpos, ypos, xpos + 22, ypos + 6)
                    sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-AISeparation", round(params.get('Fleet Separation')), "low:100 ; high: 1000; color:#0D4D00", xpos, ypos + 3, xpos + 22, ypos + 5)

                    ypos = 74
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-AIMDistanceTitle", f"text:Max Separation = {round(params.get('Max Distance'))}; font: gui-1",  xpos, ypos, xpos + 22, ypos + 6)
                    sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-AIMDistance", round(params.get('Max Distance')), "low:100 ; high: 2000; color:#0D4D00", xpos, ypos + 3, xpos + 22, ypos + 5)

                    ypos = 81
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-AISpeedTitle", f"text:Speed = x{params.get('Fleet Speed')}; font: gui-1", xpos, ypos, xpos + 22, ypos + 6)
                    sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-AISpeed", params.get('Fleet Speed'), "low:0.1 ; high: 5; color:#0D4D00", xpos, ypos + 3, xpos + 22, ypos + 5)

                case 3:
                    ypos += 6
                    xpos += 1
                    tagsList = list(tsn_databases.TagsDatabase)
                    tagsListPos = data.get("AITagsPos")
                    currentOrders = AICommanderObj.Orders
                    targetTags = currentOrders.get("Targets")
                    GUI.menuBackground(clientObj.clientID, "", f"{panelID}-AITagsSelect", xpos, ypos, 23, 16, colour="#ffffff3d", scrollbar=True, text="Targets", currentPos=tagsListPos, maxLength=len(tagsList) - 4)
                    for x in range(tagsListPos, min(len(tagsList), tagsListPos + 5)):
                        tag = tagsList[x]
                        colour = "#ffffff3d"
                        if tag in targetTags:
                            colour = "green"
                        GUI.TabletButton(clientObj.clientID, "", f"{panelID}-AITagSelection-{tag}", xpos + 0.5, ypos, 22, 3, text=f"{tag}", buttoncolour=colour)
                        ypos += 3.1

                    ypos = 39
                    params = currentOrders.get("Parameters")
                    locsList = params.get("Locations")
                    locsListPos = data.get("AILocsPos")
                    GUI.menuBackground(clientObj.clientID, "", f"{panelID}-AILocsSelect", xpos, ypos, 23, 16, colour="#ffffff3d", scrollbar=True, text="Locations", currentPos=locsListPos, maxLength=len(locsList) - 4)
                    for x in range(locsListPos, min(len(locsList), locsListPos + 5)):
                        location = locsList[x]
                        if x == params.get("Patrol Point"):
                            colour = "green"
                        else:
                            colour = "#ffffff3d"
                        GUI.holotextDisplay(clientObj.clientID, "", f"{panelID}-AILocsSelection-{location}", xpos + 0.5, ypos, 22, 3, text=f"{x}. {location}", colour=colour)
                        GUI.IconButton(clientObj.clientID, "", f"{panelID}_AILocsDelete_{location}", xpos + 20, ypos + 0.5, iconcolour="red", icon=97, iconsize=2)
                        if x != 0 and len(locsList) > 1:
                            GUI.IconButton(clientObj.clientID, "", f"{panelID}_AILocsUp_{location}", xpos + 0.5, ypos + 0.5, iconcolour="white", icon=148, iconsize=2)
                        if x != len(locsList) - 1:
                            GUI.IconButton(clientObj.clientID, "", f"{panelID}_AILocsDown_{location}", xpos + 2, ypos + 0.5, iconcolour="white", icon=150, iconsize=2)
                        ypos += 3.1
                    ypos = 60
                    colour = "#ffffff3d"
                    if data.get("AILocsAdd"):
                        colour = "green"
                    colour1 = "#ffffff3d"
                    if data.get("AILocsShow"):
                        colour1 = "green"
                    GUI.TabletButton(clientObj.clientID, "", f"{panelID}_AILocsAdd", xpos, ypos, 10, 5, text="Add Location", buttoncolour=colour)
                    GUI.TabletButton(clientObj.clientID, "", f"{panelID}_AILocsShow", xpos, ypos + 7, 10, 5, text="Show Route", buttoncolour=colour1)
                case _:
                    currentOrders = AICommanderObj.Orders
                    task = currentOrders.get("Fleet Task")
                    targets = currentOrders.get("Targets")
                    parameterData = currentOrders.get("Parameters")
                    fleetData = f"Task - {task}^"
                    fleetData += f"Targets - "
                    for item in targets:
                        fleetData += f"{item}"
                    fleetData += "^"
                    for key, value in parameterData.items():
                        if key == "Locations":
                            fleetData += f"{key} - "
                            for item in value:
                                fleetData += f"{item}"
                            fleetData += "^"
                        else:
                            fleetData += f"{key} - {value}^"
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-fleetdata", f"text:{fleetData}; font:gui-1",
                                      xpos + (w / 2), ypos + 3, xpos + w, ypos + h)
        else:
            GUI.textBox(clientObj.clientID, "", f"{panelID}-NoData", xpos, ypos + 3, w / 2, 10, text="No Data", header="Selection", headingfont="gui-1", font="smallest")

    @staticmethod
    def JumpNodeSelection(panelID, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1] + 1
        w = wh[0]
        h = wh[1]
        sbs.send_gui_hotkey(clientObj.clientID, "TSNGM", f"GM-deleteObj", "KEY_DELETE", f"GM key to delete a single selected ship")
        sbs.send_gui_clickregion(clientObj.clientID, "", f"GM-deleteObj", "", 100, 100, 101, 101)
        PointID = data.get("ID")
        PointObj = SpaceObjects.activeJumpPoints.get(int(PointID))
        PointRename = data.get("Rename")
        if PointObj:
            match int(pageNo):
                case 1:
                    output = ""
                    coreData = data.get("Object Data")
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-JumpDriftHeader", f"text: Drift Distance = {coreData.get('Drift')}; font: gui-1", xpos + 1, ypos + 8, xpos + w - 1, ypos + 10)
                    sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-JumpDrift", int(coreData.get('Drift')), "low: 0; high: 40000", xpos + 1, ypos + 10, xpos + w - 1, ypos + 13)
                    sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-renameHeader", f"color: white; font: gui-1; text:Rename Gate; justify: left", xpos + 1, ypos + 37, xpos + w - 1, ypos + 40)
                    sbs.send_gui_typein(clientObj.clientID, "", f"{panelID}-renameText", f"text: {PointRename}", xpos + 1, ypos + 40, xpos + w - 1, ypos + 43)
                    sbs.send_gui_button(clientObj.clientID, "", f"{panelID}-renameSet", f"text: Set; font: gui-1", xpos + w - 5, ypos + 43, xpos + w - 1, ypos + 46)
                    sbs.send_gui_dropdown(clientObj.clientID, "", f"{panelID}-JumpState", f"text: {coreData.get('State')}; font: gui-1; list:Tethered, Untethered", xpos + 1, ypos + 15, xpos + w - 1, ypos + 18)

                case _:
                        pass

    @staticmethod
    def ShuttleSelection(panelID, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1] + 1
        w = wh[0]
        h = wh[1]
        match int(pageNo):
            case 1:
                output = ""
                height = 6
            case 2:  # add in code to delete station
                pass

    @staticmethod
    def CargoManagementControls(panelID, clientObj, xpos, ypos, data):
        cargoList = list(tsn_databases.masterDatabase.items())
        cargoListPos = data.get("CargoPos")
        GUI.menuBackground(clientObj.clientID, "", f"{panelID}-CargoSelect", xpos, ypos, 23, 26, colour="#ffffff3d", scrollbar=True, text="Cargo Options", currentPos=cargoListPos, maxLength=len(cargoList) - 4)
        for x in range(cargoListPos, min(len(cargoList), cargoListPos + 5)):
            cargo = cargoList[x]
            name = cargo[0]
            cargodata = cargo[1]
            GUI.IconToggleButton(clientObj.clientID, "", f"{panelID}-cargoSelection-add-{data.get('ID')}-{name}", xpos + 0.5, ypos, 22, 5, text=f"{name}", icon=cargodata.get('icon'), iconcolour=cargodata.get('colour'))
            ypos += 5.1

        ypos = 50

        objDatabase = SpaceObjects.activeShips | SpaceObjects.activeStations
        playership = objDatabase.get(data.get("ID"))
        playercarList = list(playership.Cargo.CargoHold.items())
        playercarPos = data.get("playerCarPos")
        GUI.menuBackground(clientObj.clientID, "", f"{panelID}-PlayerCarSelect", xpos, ypos, 23, 26, colour="#ffffff3d", scrollbar=True, text="Cargo Onboard", currentPos=playercarPos, maxLength=len(playercarList) - 4)
        for c in range(playercarPos, min(len(playercarList), playercarPos + 5)):
            cargo = playercarList[c]
            name = cargo[0]
            cargodata = cargo[1]
            GUI.IconToggleButton(clientObj.clientID, "", f"{panelID}-cargoSelection-remove-{data.get('ID')}-{name}", xpos + 0.5, ypos, 21, 5, text=f"{name} {cargodata.get('count')}", icon=cargodata.get('icon'), iconcolour=cargodata.get('colour'))
            GUI.IconButton(clientObj.clientID, "", f"{panelID}-cargoSelection-allremove-{data.get('ID')}-{name}", xpos + 21, ypos, iconsize=2, icon=97, iconcolour="red")
            ypos += 5.1

    @staticmethod
    def PersonnelManagementControls(panelID, clientObj, xpos, ypos, data):
        personnelList = list(CrewData.teams.items())
        personnelListPos = data.get("PersonnelPos")
        GUI.menuBackground(clientObj.clientID, "", f"{panelID}-PersonnelSelect", xpos, ypos, 23, 26, colour="#ffffff3d", scrollbar=True, text="Personnel Options", currentPos=personnelListPos, maxLength=len(personnelList) - 4)
        for x in range(personnelListPos, min(len(personnelList), personnelListPos + 5)):
            personnel = personnelList[x]
            name = personnel[0]
            personneldata = personnel[1]
            GUI.IconToggleButton(clientObj.clientID, "", f"{panelID}-personnelSelection-add-{data.get('ID')}-{name}",  xpos + 0.5, ypos, 22, 5, text=f"{name}", icon=personneldata.get('icon'), iconcolour=personneldata.get('colour'))
            ypos += 5.1

        ypos = 50

        objDatabase = SpaceObjects.activeShips | SpaceObjects.activeStations
        playership = objDatabase.get(data.get("ID"))
        playerperList = list(playership.CrewMembers.shipCrew.items())
        playerperPos = data.get("playerperPos")
        GUI.menuBackground(clientObj.clientID, "", f"{panelID}-PlayerPerSelect", xpos, ypos, 23, 26, colour="#ffffff3d", scrollbar=True, text="Personnel Onboard", currentPos=playerperPos, maxLength=len(playerperList) - 4)
        for x in range(playerperPos, min(len(playerperList), playerperPos + 5)):
            personnel = playerperList[x]
            teamID = personnel[0]
            teamObj = personnel[1]
            teamdata = teamObj.teamdata
            GUI.IconTabletButton(clientObj.clientID, "", f"{panelID}-personnelSelection-remove-{data.get('ID')}-{teamID}", xpos + 0.5, ypos, 19, 5, text=teamdata.get("Name"), subtext=f"{teamdata.get('Type')}", icon=teamdata.get('icon'), iconcolour=teamdata.get('colour'))
            GUI.IconButton(clientObj.clientID, "", f"{panelID}-personnelSelection-deploy-{data.get('ID')}-{teamID}", xpos + 19, ypos, iconsize=4, icon=93, iconcolour="orange")
            ypos += 5.1

    @staticmethod
    def TerrainSelection(panelID, clientObj, position, wh, pageNo, data):
        xpos = position[0]
        ypos = position[1] + 1
        w = wh[0]
        h = wh[1]
        match int(pageNo):
            case 1:
                output = ""
                height = 6
                sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-fieldID", f"text: Field ID - {data.get('FieldID')}; font: gui-1", xpos + 5, ypos + 5, xpos + w, ypos + 10)
                startendpoint = data.get("StartEndPoint")
                """xpos += 1
                ypos += 5
                if startendpoint == "StartPoint":
                    colour1 = "#006600"
                    colour2 = "#ff3300"
                else:
                    colour1 = "#ff3300"
                    colour2 = "#006600"
                GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-StartPoint", xpos + 0.5, ypos, 9.5, 3,
                                 text="Start", togglecolour=colour1, font="smallest")
                xpos += 10
                GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-EndPoint", xpos + 0.5, ypos, 9.5, 3, text="End",
                                 togglecolour=colour2, font="smallest")
                xpos += 11
                terrainList = "Nebulae^Asteroids"
                selectedTerrain = data.get("TerrainType")
                sbs.send_gui_dropdown(clientObj.clientID, "", f"{panelID}-TerrainType",
                                      f"text: Terrain Type; font: gui-1; list:{terrainList}", xpos, ypos, xpos + 10,
                                      ypos + 3)

                xpos = position[0] + 1
                ypos += 5
                sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-terrainTitle",
                                  f"text:Selected Terrain - {selectedTerrain}; font: gui-1", xpos, ypos, xpos + 30,
                                  ypos + 3)
                scatter = data.get("Scatter")
                ypos += 5
                sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-scatterTitle",
                                  f"text:Scatter {scatter}; font: gui-1", xpos, ypos, xpos + 30, ypos + 3)
                ypos += 3
                sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-scatter", scatter, "low:1000; high: 10000",
                                    xpos, ypos, xpos + 30, ypos + 3)
                density = data.get("Density")
                ypos += 5
                sbs.send_gui_text(clientObj.clientID, "", f"{panelID}-densityTitle",
                                  f"text:Density {density}; font: gui-1", xpos, ypos, xpos + 30, ypos + 3)
                ypos += 3
                sbs.send_gui_slider(clientObj.clientID, "", f"{panelID}-density", density, "low:1; high: 1000", xpos,
                                    ypos, xpos + 30, ypos + 3)
                xpos += 20
                ypos += 5
                GUI.ToggleButton(clientObj.clientID, "", f"{panelID}-CreateTerrain", xpos + 0.5, ypos, 9.5, 3,
                                 text="Generate", togglecolour="green", font="smallest")"""

                sbs.send_gui_button(clientObj.clientID, "", f"{panelID}-rebuildField", f"text: Rebuild; font: gui-1", xpos + w - 15, ypos + 43, xpos + w - 1, ypos + 46)
                sbs.send_gui_button(clientObj.clientID, "", f"{panelID}-deleteField", f"text: Delete Field; font: gui-1", xpos + w - 15, ypos + 48, xpos + w - 1, ypos + 51)
            case 2:
                pass


#triggers linked to the displayed panels
class PanelTriggers:

    @staticmethod
    def Terrain(event, data):
        if "StartPoint" in event.sub_tag:
            data.update({"StartEndPoint": "StartPoint"})
            #sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "EndPoint" in event.sub_tag:
            data.update({"StartEndPoint": "EndPoint"})
            #sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-scatter" in event.sub_tag:
            data.update({"scatter": round(event.sub_float)})
            #sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-density" in event.sub_tag:
            data.update({"density": round(event.sub_float)})
            #sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-TerrainType" in event.sub_tag:
            data.update({"type": event.value_tag})
            if event.value_tag == "asteroids":
                data.update({"composition": ["Ast. Std Rand"]})
            if event.value_tag == "nebula":
                data.update({"composition": []})
            #sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-CreateTerrain" in event.sub_tag:
            start = data.get("start")
            end = data.get("end")
            density = data.get("density")
            scatter = data.get("scatter")
            simulation.simul.delete_navpoint_by_id(data.get("SNavID"))
            simulation.simul.delete_navpoint_by_id(data.get("ENavID"))
            coordList = TerrainHandling.generateLineCoords(2010, start, end, density, scatter, 0)
            fieldIDList = []
            if data.get("type") == "asteroids":
                choiceList = []
                for coordinate in coordList:
                    asteroidTypeList = data.get("composition")
                    for asteroidType in asteroidTypeList:
                        choiceList += tsn_databases.terrainDatabase.get(asteroidType)
                    ast = random.choice(choiceList)
                    newAsteroid = TerrainTypes.AddAsteroid(simulation.simul, ast, coordinate)
                    TerrainHandling.asteroidIDs.append(newAsteroid)
                    AsteroidObj = simulation.simul.get_space_object(newAsteroid)
                    AsteroidData = AsteroidObj.data_set
                    AsteroidData.set("FieldID", id(coordList), 0)
                    fieldIDList.append(newAsteroid)
                data.update({"fieldIDList": fieldIDList})
                TerrainHandling.asteroidfields.update({id(coordList): data})
            elif data.get("type") == "nebula":
                for coordinate in coordList:
                    newNebula = TerrainTypes.AddNebula(simulation.simul, "nebula", coordinate)
                    TerrainHandling.nebulaIDs.append(newNebula)
                    NebulaObj = simulation.simul.get_space_object(newNebula)
                    NebulaData = NebulaObj.data_set
                    fieldIDList.append(newNebula)
                    NebulaData.set("FieldID", id(coordList), 0)
                data.update({"fieldIDList": fieldIDList})
                TerrainHandling.nebulafields.update({id(coordList): data})
            TerrainHandling.createSensorMarker(id, data.get("start"))
            TerrainHandling.createSensorMarker(id, data.get("end"))
            return True


    @staticmethod
    def TerrainConfig(event, data):
        if "-deleteField" in event.sub_tag:
            fieldData = data.get("FieldData")
            fieldIDList = fieldData.get("fieldIDList")
            fieldType = fieldData.get("type")
            if fieldType == "asteroids":
                for objID in fieldIDList:
                    TerrainHandling.asteroidIDs.remove(objID)
                    sbs.delete_object(objID)
                TerrainHandling.asteroidfields.pop(data.get("FieldID"))
            elif fieldType == "nebula":
                for objID in fieldIDList:
                    TerrainHandling.nebulaIDs.remove(objID)
                    sbs.delete_object(objID)
                TerrainHandling.nebulafields.pop(data.get("FieldID"))
            for markerObj in TerrainHandling.sensorMarkers:
                markerData = markerObj.data_set
                if markerData.get("fieldID", 0) == data.get("FieldID"):
                    sbs.delete_object(markerObj.unique_ID)

            return True

    @staticmethod
    def Settings(event, data):
        subtagdata = event.sub_tag.split("-")
        if "playerbeams-increase" in event.sub_tag:
            state = data.get("PlayerBeams")
            data.update({"PlayerBeams": state + 1})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
        if "playerbeams-decrease" in event.sub_tag:
            state = data.get("PlayerBeams")
            if state > 0:
                data.update({"PlayerBeams": state - 1})
                sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
        if "NPCbeams-increase" in event.sub_tag:
            state = data.get("NPCBeams")
            data.update({"NPCBeams": state + 1})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
        if "NPCbeams-decrease" in event.sub_tag:
            state = data.get("NPCBeams")
            if state > 0:
                data.update({"NPCBeams": state - 1})
                sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
        if "update-beam-setting" in event.sub_tag:
            npc = data.get("NPCBeams")
            player = data.get("PlayerBeams")
            sbs.set_beam_damages(0, player, npc)

    @staticmethod
    def Selection(event, data):
        subtagdata = event.sub_tag.split("-")
        if "reassignSide" in event.sub_tag:
            newside = event.value_tag
            if SpaceObjects.activeNPCs.get(int(subtagdata[2])):
                ship = SpaceObjects.activeNPCs.get(int(subtagdata[2]))
                AICommanderID = ship.ObjectData.get("Fleet Commander", 0)
                AICommanderObj = AI_Commanders.commanders.get(AICommanderID)
                for Obj in AICommanderObj.FleetMembers.values():
                    Obj.Object.side = newside
                    Obj.ObjectSide = newside
            else:
                singleActive = SpaceObjects.activeShips | SpaceObjects.activeStations | SpaceObjects.activeShuttles
                if singleActive.get(int(subtagdata[2])):
                    object = singleActive.get(int(subtagdata[2]))
                    object.Object.side = newside
                    object.ObjectSide = newside
            return True
        if "-allowShuttleDock-" in event.sub_tag:
            if SpaceObjects.activeStations.get(int(subtagdata[2])):
                station = SpaceObjects.activeStations.get(int(subtagdata[2]))
                shuttleBay = station.shipSystems.get("ShuttleBay")
                shuttleBay.BayStatus = not shuttleBay.BayStatus
                sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
        PanelTriggers.CargoManagement(event, data)
        PanelTriggers.PersonnelManagement(event, data)
        PanelTriggers.AIConfig(event, data)
        PanelTriggers.JumpGateConfig(event, data)
        PanelTriggers.TerrainConfig(event, data)

    @staticmethod
    def AIConfig(event, data):
        if "-AITaskSelect-scroll" in event.sub_tag:
            data.update({"AITaskPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "AITaskSelection-" in event.sub_tag:
            buttonData = event.sub_tag.split("-")
            newTask = buttonData[2]
            commander = data.get("Commander")
            commander.Orders.update({"Fleet Task": newTask})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-AISupportSelect-scroll" in event.sub_tag:
            data.update({"AISupportPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "AISupportSelection-" in event.sub_tag:
            buttonData = event.sub_tag.split("-")
            newTask = buttonData[2]
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            params.update({"Support Elements": newTask})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-AISensorRange" in event.sub_tag:
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            newRange = abs(int(event.sub_float))
            params.update({"Sensor Range": newRange})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-AISeparation" in event.sub_tag:
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            newRange = abs(int(event.sub_float))
            params.update({"Fleet Separation": newRange})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-AIMDistance" in event.sub_tag:
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            newRange = abs(int(event.sub_float))
            params.update({"Max Distance": newRange})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-AISpeed" in event.sub_tag:
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            newRange = abs(round(event.sub_float, 1))
            params.update({"Fleet Speed": newRange})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-AITagsSelect-scroll" in event.sub_tag:
            data.update({"AITagsPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-AITagSelection" in event.sub_tag:
            tagData = event.sub_tag.split("-")
            tag = tagData[2]
            commander = data.get("Commander")
            currTags = commander.Orders.get("Targets")
            if tag in currTags:
                currTags.remove(tag)
            else:
                currTags.append(tag)
            commander.Orders.update({"Targets": currTags})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-AILocsSelect-scroll" in event.sub_tag:
            data.update({"AILocsPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True

        if "-renameText" in event.sub_tag:
            data.update({"Rename": event.value_tag})
            return True

        if "renameSet" in event.sub_tag:
            newname = data.get("Rename")
            shipID = data.get("ID")
            panelname = data.get("Object Data")
            panelname.update({'Name': newname})
            objectDatabase = SpaceObjects.activeStations | SpaceObjects.activeJumpPoints | SpaceObjects.activeObjects | SpaceObjects.activeNPCs
            ship = objectDatabase.get(shipID)
            ship.ObjectName = newname
            ship.ObjectData.set("name_tag", newname, 0)
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True

        if "AILocsUp" in event.sub_tag:
            location = event.sub_tag.split("_")[2]
            if "(" in location:
                location = location.replace("(", "")
                location = location.replace(")", "")
                location = location.replace(" ", "")
                location = location.split(",")
                location = tuple(int(x) for x in location)
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            locsList = params.get("Locations")
            index = locsList.index(location)
            locsList.remove(location)
            locsList.insert(index - 1, location)
            params.update({"Locations": locsList})
            PanelTriggers.updateVisibleLocs(data, event)
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "AILocsDown" in event.sub_tag:
            location = event.sub_tag.split("_")[2]
            if "(" in location:
                location = location.replace("(", "")
                location = location.replace(")", "")
                location = location.replace(" ", "")
                location = location.split(",")
                location = tuple(int(x) for x in location)
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            locsList = params.get("Locations")
            index = locsList.index(location)
            locsList.remove(location)
            locsList.insert(index + 1, location)
            params.update({"Locations": locsList})
            PanelTriggers.updateVisibleLocs(data, event)
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "AILocsDelete" in event.sub_tag:
            location = event.sub_tag.split("_")[2]
            if "(" in location:
                location = location.replace("(", "")
                location = location.replace(")", "")
                location = location.replace(" ", "")
                location = location.split(",")
                location = tuple(int(x) for x in location)
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            locsList = params.get("Locations")
            locsList.remove(location)
            params.update({"Locations": locsList})

            PanelTriggers.updateVisibleLocs(data, event)

            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "AILocsAdd" in event.sub_tag:
            state = data.get("AILocsAdd")
            data.update({"AILocsAdd": not state})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "AILocsShow" in event.sub_tag:
            GMClient = ClientNEW.activeClients.get(event.client_id)
            GMObjID = GMClient.myShip.ObjectID
            state = data.get("AILocsShow")
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            locsList = params.get("Locations")
            data.update({"AILocsShow": not state})
            if data.get("AILocsShow"):
                point = 0
                navpointList = []
                for location in locsList:
                    if type(location) == str:
                        location = PanelTriggers.findObjectbyName(location)
                    newpoint = sbs_tools.AddNavPoint(simulation.simul, f"{point}", location, objectID=GMObjID)
                    navpointList.append(newpoint)
                    point += 1
                data.update({"AILocsNavPoints": navpointList})
            else:
                navpointList = data.get("AILocsNavPoints")
                for navpointID in navpointList:
                    simulation.simul.delete_navpoint_by_id(navpointID)
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "AIDefendAdd" in event.sub_tag:
            state = data.get("AIDefendAdd")
            data.update({"AIDefendAdd": not state})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

    @staticmethod
    def updateVisibleLocs(data, event):
        if data.get("AILocsShow"):
            commander = data.get("Commander")
            params = commander.Orders.get("Parameters")
            locsList = params.get("Locations")
            navpointList = data.get("AILocsNavPoints")
            for navpointID in navpointList:
                simulation.simul.delete_navpoint_by_id(navpointID)
            point = 0
            GMClient = ClientNEW.activeClients.get(event.client_id)
            GMObjID = GMClient.myShip.ObjectID
            for location in locsList:
                if type(location) == str:
                    location = PanelTriggers.findObjectbyName(location)
                newpoint = sbs_tools.AddNavPoint(simulation.simul, f"{point}", location, objectID=GMObjID)
                navpointList.append(newpoint)
                point += 1
            data.update({"AILocsNavPoints": navpointList})

    @staticmethod
    def findObjectbyName(name):
        allActive = SpaceObjects.activeShips | SpaceObjects.activeStations | SpaceObjects.activeNPCs | SpaceObjects.activeShuttles
        for value in allActive.values():
            if value.ObjectData.get("name_tag", 0).lower() == name.lower():
                coord = (value.Object.pos.x, value.Object.pos.y, value.Object.pos.z)
                return coord

    @staticmethod
    def CargoManagement(event, data):
        subtagdata = event.sub_tag.split("-")
        if "-CargoSelect-scroll" in event.sub_tag:
            data.update({"CargoPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "-PlayerCarSelect-scroll" in event.sub_tag:
            data.update({"playerCarPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "-cargoSelection" in event.sub_tag:
            objDatabase = SpaceObjects.activeShips | SpaceObjects.activeStations
            selectedship = objDatabase.get(int(subtagdata[3]))
            cargoname = subtagdata[4]
            if "add" in event.sub_tag:
                if cargoname in selectedship.Cargo.CargoHold.keys():
                    cargodata = selectedship.Cargo.CargoHold.get(cargoname)
                    count = cargodata.get("count")
                    cargodata.update({"count": count + 1})
                else:
                    selectedship.Cargo.addCargo(cargoname)
                selectedship.updateclientConsoles()
            if "-remove" in event.sub_tag:
                try:
                    cargodata = selectedship.Cargo.CargoHold.get(cargoname)
                    count = cargodata.get("count")
                    if count - 1 <= 0:
                        selectedship.Cargo.CargoHold.pop(cargoname)
                    else:
                        cargodata.update({"count": count - 1})
                except:
                    print("Clicked too fast")
                selectedship.updateclientConsoles()
            if "-allremove" in event.sub_tag:
                try:
                    selectedship.Cargo.CargoHold.pop(cargoname)
                except:
                    print("Clicked too fast")
                selectedship.updateclientConsoles()
            if isinstance(selectedship, Stations.Station) or isinstance(selectedship, Stations.USFPStation):
                for shipID, ship in selectedship.dockingPorts.items():
                    if shipID in SpaceObjects.activeShips.keys():
                        ship.updateclientConsoles()
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

    @staticmethod
    def PersonnelManagement(event, data):
        subtagdata = event.sub_tag.split("-")
        if "-PersonnelSelect-scroll" in event.sub_tag:
            data.update({"PersonnelPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "-PlayerPerSelect-scroll" in event.sub_tag:
            data.update({"playerperPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

        if "-personnelSelection" in event.sub_tag:
            objDatabase = SpaceObjects.activeShips | SpaceObjects.activeStations
            selectedship = objDatabase.get(int(subtagdata[3]))
            if "add" in event.sub_tag:
                teamtype = subtagdata[4]
                newteam = SpaceObjects.Team(teamtype, "Shuttle Bay")
                selectedship.CrewMembers.shipCrew.update({id(newteam): newteam})
                selectedship.updateclientConsoles()
            if "remove" in event.sub_tag:
                teamtype = int(subtagdata[4])
                try:
                    selectedship.CrewMembers.shipCrew.pop(teamtype)
                except:
                    print("Clicked too fast")
                selectedship.updateclientConsoles()

            if "deploy" in event.sub_tag:
                objDatabase = SpaceObjects.activeShips | SpaceObjects.activeStations
                selectedship = objDatabase.get(int(subtagdata[3]))
                teamID = int(subtagdata[4])
                teamObj = selectedship.CrewMembers.shipCrew.pop(teamID)
                teamData = teamObj.teamdata

                position = selectedship.Object.pos
                coordinate = (position.x, position.y - 20, position.z)
                ObjRef = GMData.otherObjectsDatabase.get(teamData.get("Type"))
                newObj = ObjRef(teamObj, position=coordinate)
                newObj.SpawnObject(simulation.simul)
                newObj.Object.cur_speed = 0.5
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
                selectedship.updateclientConsoles()

            if isinstance(selectedship, Stations.Station) or isinstance(selectedship, Stations.USFPStation):
                for shipID, ship in selectedship.dockingPorts.items():
                    if shipID in SpaceObjects.activeShips.keys():
                        ship.updateclientConsoles()
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

    @staticmethod
    def JumpGateConfig(event, data):
        subtagdata = event.sub_tag.split("-")
        if "-JumpDrift" in event.sub_tag:
            shipID = data.get("ID")
            ship = SpaceObjects.activeJumpPoints.get(shipID)
            ship.drift = int(event.sub_float)
            panelname = data.get("Object Data")
            panelname.update({'Drift': ship.drift})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-JumpState" in event.sub_tag:
            shipID = data.get("ID")
            ship = SpaceObjects.activeJumpPoints.get(shipID)
            ship.ObjectData.set('state', event.value_tag, 0)
            panelname = data.get("Object Data")
            panelname.update({'State': event.value_tag})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True

    @staticmethod
    def FleetSpawn(event, data):
        subtagdata = event.sub_tag.split("-")
        if "factionList" in event.sub_tag:
            currList = data.get("Factions")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
                raceList = data.get("Races")
                for race in GMData.factions.get(subtagdata[1]):
                    if race in raceList:
                        raceList.remove(race)
                        fleetList = data.get("FleetList")
                        for fleet in GMData.masterFleetTypes.get(race):
                            if fleet in fleetList:
                                fleetList.remove(fleet)
            else:
                currList.append(subtagdata[1])
            data.update({"Factions": currList})

            racelist = []
            for faction in currList:
                racelist += GMData.factions.get(faction)
            data.update({"RaceList": racelist})
            return True # this will trigger the GUI to update
        if "raceList" in event.sub_tag:
            currList = data.get("Races")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
                fleetList = data.get("Fleets")
                for fleet in GMData.masterFleetTypes.get(subtagdata[1]):
                    if fleet in fleetList:
                        fleetList.remove(fleet)
            else:
                currList.append(subtagdata[1])
            data.update({"Races": currList})

            fleetlist = []
            for race in currList:
                fleetlist += GMData.masterFleetTypes.get(race)
            data.update({"FleetList": fleetlist})
            return True # this will trigger the GUI to update

        if "fleetList" in event.sub_tag:
            currList = data.get("Fleets")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
            else:
                currList.append(subtagdata[1])
            data.update({"Fleets": currList})
            return True

        if "scroll" in event.sub_tag:
            if "faction" in event.sub_tag:
                data.update({"FactionListPos": abs(int(event.sub_float))})
            if "race" in event.sub_tag:
                data.update({"RaceListPos": abs(int(event.sub_float))})
            if "fleet" in event.sub_tag:
                data.update({"SpawnListPos": abs(int(event.sub_float))})
            return True

    @staticmethod
    def ShipSpawn(event, data):
        subtagdata = event.sub_tag.split("-")
        if "factionList" in event.sub_tag:
            currList = data.get("Factions")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
                raceList = data.get("Races")
                for race in GMData.factions.get(subtagdata[1]):
                    if race in raceList:
                        raceList.remove(race)
                        shipList = data.get("ShipList")
                        for ship in GMData.masterShipTypes.get(race):
                            if ship in shipList:
                                shipList.remove(ship)
            else:
                currList.append(subtagdata[1])
            data.update({"Factions": currList})

            racelist = []
            for faction in currList:
                racelist += GMData.factions.get(faction)
            data.update({"RaceList": racelist})
            return True  # this will trigger the GUI to update

        if "raceList" in event.sub_tag:
            currList = data.get("Races")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
                shipList = data.get("Ships")
                for ship in GMData.masterShipTypes.get(subtagdata[1]):
                    if ship in shipList:
                        shipList.remove(ship)
            else:
                currList.append(subtagdata[1])
            data.update({"Races": currList})
            shiplist = []
            for race in currList:
                shiplist += GMData.masterShipTypes.get(race)
            data.update({"ShipList": shiplist})
            return True  # this will trigger the GUI to update

        if "shipList" in event.sub_tag:
            currList = data.get("Ships")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
            else:
                currList.append(subtagdata[1])
            data.update({"Ships": currList})
            return True

        if "scroll" in event.sub_tag:
            if "faction" in event.sub_tag:
                data.update({"FactionListPos": abs(int(event.sub_float))})
            if "race" in event.sub_tag:
                data.update({"RaceListPos": abs(int(event.sub_float))})
            if "ship" in event.sub_tag:
                data.update({"ShipSpawnListPos": abs(int(event.sub_float))})
            return True

    @staticmethod
    def StationSpawn(event, data):
        subtagdata = event.sub_tag.split("-")
        if "factionList" in event.sub_tag:
            currList = data.get("Factions")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
                raceList = data.get("Races")
                for race in GMData.factions.get(subtagdata[1]):
                    if race in raceList:
                        raceList.remove(race)
                        stationList = data.get("Stations")
                        for station in GMData.masterStationTypes.get(race):
                            if station in stationList:
                                stationList.remove(station)
            else:
                currList.append(subtagdata[1])
            data.update({"Factions": currList})

            racelist = []
            for faction in currList:
                racelist += GMData.factions.get(faction)
            data.update({"RaceList": racelist})
            return True  # this will trigger the GUI to update

        if "raceList" in event.sub_tag:
            currList = data.get("Races")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
                stationList = data.get("Stations")
                for station in GMData.masterStationTypes.get(subtagdata[1]):
                    if station in stationList:
                        stationList.remove(station)
            else:
                currList.append(subtagdata[1])
            data.update({"Races": currList})

            stationlist = []
            for race in currList:
                stationlist += GMData.masterStationTypes.get(race)
            data.update({"StationList": stationlist})
            return True  # this will trigger the GUI to update

        if "stationList" in event.sub_tag:
            currList = data.get("Stations")
            if subtagdata[1] in currList:
                currList.remove(subtagdata[1])
            else:
                currList.append(subtagdata[1])
            data.update({"Stations": currList})
            return True

        if "scroll" in event.sub_tag:
            if "faction" in event.sub_tag:
                data.update({"FactionListPos": abs(int(event.sub_float))})
            if "race" in event.sub_tag:
                data.update({"RaceListPos": abs(int(event.sub_float))})
            if "station" in event.sub_tag:
                data.update({"SpawnListPos": abs(int(event.sub_float))})
            return True

    @staticmethod
    def Schedule(event, data):
        print("Triggered Schedule")

    @staticmethod
    def ObjectSpawn(event, data):
        subtagdata = event.sub_tag.split("-")
        if "-SelectObjclick" in event.sub_tag:
            data.update({"SelectedObj": subtagdata[2]})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True
        if "-SelectObj-scroll" in event.sub_tag:
            data.update({"ScrollPos": abs(int(event.sub_float))})
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")
            return True

    @staticmethod
    def JumpSpawn(event, data):
        pass


class GMGlobalFunctions:
    # static methods that carry out the functions linked to the console triggers

    @staticmethod
    def GlobalTriggers(event, data):
        if event.tag == "select_space_object" and event.sub_tag == "GMControls" and event.value_tag == "science_2d_view" and event.selected_id == 0 and event.extra_extra_tag == "lmb":
            if data.get("Fleets"):
                data.update({"SpawnCoordinate": (event.source_point.x, event.source_point.y, event.source_point.z)})
                GMGlobalFunctions.SpawnFleets(data)
            elif data.get("Ships"):
                data.update({"SpawnCoordinate": (event.source_point.x, event.source_point.y, event.source_point.z)})
                GMGlobalFunctions.SpawnShips(data)
            elif data.get("Stations"):
                data.update({"SpawnCoordinate": (event.source_point.x, event.source_point.y, event.source_point.z)})
                GMGlobalFunctions.SpawnStations(data)
            elif data.get("SelectedObj"):
                data.update({"SpawnCoordinate": (event.source_point.x, event.source_point.y, event.source_point.z)})
                GMGlobalFunctions.SpawnObject(data)
            elif data.get("AILocsAdd"):
                data.update({"Location": (round(event.source_point.x), round(event.source_point.y), round(event.source_point.z))})
                GMGlobalFunctions.AddLocation(data, event=event)
            elif data.get("JumpPointSpawn"):
                data.update({"SpawnCoordinate": (round(event.source_point.x), round(event.source_point.y), round(event.source_point.z))})
                GMGlobalFunctions.SpawnJumpPoint(data, event=event)
            elif data.get("Terrain"):
                coord = (round(event.source_point.x), round(event.source_point.y), round(event.source_point.z))
                GMGlobalFunctions.TerrainPoint(data, coord=coord)
                print(coord)
            else:
                #data.clear()
                return True

    @staticmethod
    def AddLocation(data, **kwargs):
        event = kwargs.get("event")
        data.get("Location")
        commander = data.get("Commander")
        params = commander.Orders.get("Parameters")
        locsList = params.get("Locations")
        locsList.append(data.get("Location"))
        PanelTriggers.updateVisibleLocs(data, event)
        if event:
            sbs_tools.crenderID(event.client_id, ClientNEW.activeClients, "")

    @staticmethod
    def SpawnFleets(data, **kwargs):
        if "coord" in kwargs:
            coordinate = kwargs.get("coord")
        else:
            coordinate = data.get("SpawnCoordinate")
        for fleet in data.get("Fleets"):
            race = fleet.split(" ")[0]
            racedatabase = GMData.masterFleetTypes.get(race)
            fleetdatabase = racedatabase.get(fleet)
            GMGlobalFunctions.SpawnFleet(coordinate, race, fleetdatabase)

    @staticmethod
    def SpawnFleet(coordinate, race, fleetdatabase, **kwargs):
        fleetSize = fleetdatabase.get("fleetsize")
        fleetMembers = {}
        #create a basic set of fleet orders
        Orders = copy.deepcopy(fleetOrders.standardOrders)
        for x in range(fleetSize):
            key = random.choice(fleetdatabase.get("ships"))
            shipData = tsn_databases.shipProperties.get(key)
            tags = shipData.get("tags")
            newcoord = [coordinate[0] + random.randint(-500, 500), coordinate[1], coordinate[2] + random.randint(-500, 500)]
            if "carrier" in tags:
                newship = NPCShips.NPCCarrier(race, "behav_npcship", key, race, position=newcoord)
                Orders = copy.deepcopy(fleetOrders.carrierOrders)
            else:
                newship = NPCShips.NPCShip(race, "behav_npcship", key, race, position=newcoord)
            newship.SpawnObject(simulation.simul)
            fleetMembers.update({newship.ObjectID: newship})
            for GM in SpaceObjects.activeGameMasters.values():
                index = GM.ObjectData.get("num_extra_scan_sources", 0)
                index += 1
                GM.ObjectData.set("extra_scan_source", newship.ObjectID, index)
                GM.ObjectData.set("num_extra_scan_sources", index, 0)
        fleetCommander = list(fleetMembers.values())[0]
        NewFleetCommander = AI_Commanders.AIGroupCommander(fleetCommander, fleetMembers, fleetSize, Orders=Orders)
        AI_Commanders.commanders.update({id(NewFleetCommander): NewFleetCommander})

    @staticmethod
    def SpawnShips(data, **kwargs):
        if "coord" in kwargs:
            coordinate = kwargs.get("coord")
        else:
            coordinate = data.get("SpawnCoordinate")
        for ship in data.get("Ships"):
            shipData = tsn_databases.shipProperties.get(ship)
            tags = shipData.get("tags")
            race = shipData.get("race")
            GMGlobalFunctions.SpawnShip(coordinate, race, ship, tags)

    @staticmethod
    def SpawnShip(coordinate, race, shipHull, tags, **kwargs):
        fleetMembers = {}
        # create a basic set of fleet orders
        Orders = copy.deepcopy(fleetOrders.standardOrders)

        newcoord = [coordinate[0] + random.randint(-500, 500), coordinate[1],
                    coordinate[2] + random.randint(-500, 500)]
        if "carrier" in tags:
            newship = NPCShips.NPCCarrier(race, "behav_npcship", shipHull, race, position=newcoord)
            Orders = copy.deepcopy(fleetOrders.carrierOrders)
        else:
            newship = NPCShips.NPCShip(race, "behav_npcship", shipHull, race, position=newcoord)
        newship.SpawnObject(simulation.simul)
        fleetMembers.update({newship.ObjectID: newship})
        for GM in SpaceObjects.activeGameMasters.values():
            index = GM.ObjectData.get("num_extra_scan_sources", 0)
            index += 1
            GM.ObjectData.set("extra_scan_source", newship.ObjectID, index)
            GM.ObjectData.set("num_extra_scan_sources", index, 0)

        fleetCommander = list(fleetMembers.values())[0]
        NewFleetCommander = AI_Commanders.AIGroupCommander(fleetCommander, fleetMembers, 1, Orders=Orders)
        AI_Commanders.commanders.update({id(NewFleetCommander): NewFleetCommander})


    @staticmethod
    def SpawnObject(data, **kwargs):
        if "coord" in kwargs:
            coordinate = kwargs.get("coord")
        else:
            coordinate = data.get("SpawnCoordinate")
        name = data.get("SelectedObj")
        ObjRef = GMData.otherObjectsDatabase.get(name) #this grabs the class reference from the GM Data database
        if name in CrewData.teams.keys():
            newTeam = SpaceObjects.Team(name, "Space")
            newObj = ObjRef(newTeam, position=coordinate)
        elif name in ["Comms Relay", "Sensor Buoy"]:
            newObj = ObjRef(position=coordinate)
        else:
            newObj = ObjRef(position=coordinate, cargotype=name)
        newObj.SpawnObject(simulation.simul)
        for GM in SpaceObjects.activeGameMasters.values():
            newObj.ObjectData.set(GM.Object.side + "scan", "scandata", 0)
            index = GM.ObjectData.get("num_extra_scan_sources", 0)
            GM.ObjectData.set("extra_scan_source", newObj.ObjectID, index)
            index += 1
            GM.ObjectData.set("num_extra_scan_sources", index, 0)

    @staticmethod
    def SpawnStations(data, **kwargs):
        if "coord" in kwargs:
            coordinate = kwargs.get("coord")
        else:
            coordinate = data.get("SpawnCoordinate")
        for station in data.get("Stations"):
            stationdata = tsn_databases.stationProperties.get(station)
            data = {
                "coordinate": coordinate,
                "sides": [stationdata.get('race')],
                "type": "station",
                "hull": station,
                "facilities": [],
                "ordnance": {},
                "cargo": [],
            }
            station = Stations.setupStation("Station", data)
            station.SpawnObject(simulation.simul)

    @staticmethod
    def SpawnJumpPoint(data, **kwargs):
        if "coord" in kwargs:
            coordinate = kwargs.get("coord")
        else:
            coordinate = data.get("SpawnCoordinate")
        hull = "generic-tetrahedron"
        data = {
            "coordinate": coordinate,
            "jumppointtype": "Node", #Linked, Outbound, Inbound, Multi-Link
            "state": "Tethered", #Tethered or Untethered
            "drift": 0,
            "destinations": {} # Gate Name, System
        }
        # hull = "jump_node"
        newjumppoint = JumpPoints.JumpPoint("Gate", "behav_jumpnode", hull, "Jump Point", position=data.get("coordinate"), info=data)
        newjumppoint.SpawnObject(simulation.simul)

    @staticmethod
    def TerrainPoint(data, **kwargs):
        coord = (0, 0, 0)
        if "coord" in kwargs:
            coord = kwargs.get("coord")

        if data.get("StartEndPoint") == "StartPoint":
            data.update({"start": coord})
            if simulation.simul.navpoint_exists(data.get("SNavID")):
                navObj = simulation.simul.get_navpoint_by_id(data.get("SNavID"))
                navObj.pos.x = coord[0]
                navObj.pos.z = coord[2]
                navObj.has_changed_flag = 1
            else:
                newNav = simulation.simul.add_navpoint(coord[0], coord[1], coord[2], "Start", "white")
                data.update({"SNavID": newNav})
        else:
            data.update({"end": coord})
            if simulation.simul.navpoint_exists(data.get("ENavID")):
                navObj = simulation.simul.get_navpoint_by_id(data.get("ENavID"))
                navObj.pos.x = coord[0]
                navObj.pos.z = coord[2]
                navObj.has_changed_flag = 1
            else:
                newNav = simulation.simul.add_navpoint(coord[0], coord[1], coord[2], "End", "white")
                data.update({"ENavID": newNav})


