import sbs, math

import tsn_databases
#each function below is the console - it includes layout data, widgets and buttons
import simulation
from GM_Data import GMConsoleData
from Objects import SpaceObjects
from Clients import Console_GUI as GUI


def destroyedConsole(clientObj):
    name = "ShipDestroyed"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    sbs.send_gui_text(clientObj.clientID, "", "destroyed", f"text: Emergency Systems Active", 35, 48, 75, 52)
    sbs.send_gui_button(clientObj.clientID, "", "eject", "text:Launch Life Pod", 40, 53, 60, 56)


def CommandNav(clientObj):
    name = "CommandNav"
    widgets = "science_2d_view"
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    sbs.send_gui_checkbox(clientObj.clientID, "", "command-navmarker", f"text: Nav Marker; font: gui-1; state:{clientObj.myConsoles.setNavpoint}", 0, 10, 15, 14)
    menu = "All^"
    for markerID, markerObj in clientObj.myConsoles.NavPoints.items():
        menu += f"{markerObj.text}^"
    sbs.send_gui_dropdown(clientObj.clientID, "", "nav-marker-menu", f"text: Delete Marker; font: gui-1; list: {menu}; font: gui-1", 0, 14, 15, 18)


def CommandMiss(clientObj):
    name = "CommandMiss"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    missionorders = clientObj.myShip.MissionData
    sbs.send_gui_text(clientObj.clientID, "", "mission-orders", f"text: {missionorders[0]}", 20, 20, 80, 90)
    sbs.send_gui_text(clientObj.clientID, "", "mission-primary", f"text: {missionorders[1]}", 20, 40, 80, 90)
    sbs.send_gui_text(clientObj.clientID, "", "mission-secondary", f"text: {missionorders[2]}", 20, 60, 80, 90)


def CommandData(clientObj):
    name = "CommandData"
    widgets = "ship_data^"
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])


def StandardHelm(clientObj):
    name = "Helm_main"
    widgets = "2dview^3dview^helm_movement^throttle^request_dock^ship_data^main_screen_control^text_waterfall"
    layoutdata = {"ship_data": [70, 0, 100, 40, 70, 0, 100, 40],
                  "helm_movement": [7, 66, 25, 94, 7, 66, 25, 94],
                  "throttle": [0, 66, 7, 94, 0, 66, 7, 94],
                  "request_dock": [0, 54, 17, 59, 0, 54, 17, 59],
                  "2dview": [0, 3, 100, 96, 0, 0, 100, 100],
                  "main_screen_control": [0, 29, 18, 54, 0, 29, 18, 54],
                  "3dview": [0, 5, 24, 29, 0, 5, 24, 29],
                  "text_waterfall": [70, 86, 100, 96, 70, 86, 100, 96]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    engineeringsystems = clientObj.myShip.shipSystems.get("Engineering")
    if engineeringsystems.FCS:
        sbs.send_gui_text(clientObj.clientID, "", "FCSStateIndicator", f"text:FCS = {engineeringsystems.FCSState}", 70, 40, 100, 80)
    jumpsystems = clientObj.myShip.shipSystems.get("JumpSystems")
    if jumpsystems.JumpNode:
        sbs.send_gui_button(clientObj.clientID, "", "active-node", "text:Activate Jump", 0, 59, 17, 64)


def PilotHelm(clientObj):
    name = "Pilot_Helm_main"
    widgets = "3dview^2dview^helm_movement^throttle^main_screen_control^request_dock^ship_data^text_waterfall"
    layoutdata = {"ship_data": [70, 0, 100, 40, 70, 0, 100, 40],
                  "helm_movement": [7, 66, 25, 94, 7, 66, 25, 94],
                  "throttle": [0, 66, 7, 94, 0, 66, 7, 94],
                  "2dview": [0, 5, 24, 29, 0, 5, 24, 29],
                  "main_screen_control": [0, 29, 18, 54, 0, 29, 18, 54],
                  "3dview": [0, 3, 100, 96, 0, 0, 100, 96],
                  "request_dock": [0, 54, 17, 59, 0, 54, 17, 59],
                  "text_waterfall": [70, 86, 100, 96, 70, 86, 100, 96]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.clientID}-Pilot2DBack", "image: ../missions/TSN Cosmos/Images/Box-10; color: white; draw_layer: 901", 0, 5, 24, 29)
    jumpsystems = clientObj.myShip.shipSystems.get("JumpSystems")
    if jumpsystems.JumpNode:
        sbs.send_gui_button(clientObj.clientID, "", "active-node", "text:Activate Jump", 0, 59, 17, 64)


def JumpControl(clientObj):
    name = "Jump_Controls_Helm_main"
    widgets = "^text_waterfall"
    layoutdata = {"text_waterfall": [70, 40, 100, 50, 70, 40, 100, 50]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    jumpsystems = clientObj.myShip.shipSystems.get("JumpSystems")
    jumpsystems.InterfaceProgress.send_gui_progressbar(clientObj.clientID, "", f"{clientObj.clientID}-Interface-Progress", (71, 55))

    if jumpsystems.JumpNode:
        destinations = jumpsystems.JumpNode.Destinations
        sbs.send_gui_button(clientObj.clientID, "", "active-node", "text:Activate Jump", 0, 59, 17, 64)
        sbs.send_gui_button(clientObj.clientID, "", "jump-node-disconnect", "text:Disconnect", 0, 65, 17, 70)
        xpos = 20
        ypos = 10
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-Destination", xpos, ypos, 28, 22, scrollbar=True, currentPos=clientObj.DestinationPos, maxLength=len(list(destinations.keys())) - 3, background=True, text="Destinations")
        for s in range(clientObj.ScanTypePos, min(len(list(destinations.keys())), clientObj.DestinationPos + 4)):
            destination = list(destinations.keys())[s]
            if jumpsystems.SelectedDestination == destination:
                colour = "#006600"
            else:
                colour = "#ff3300"
            GUI.ToggleButton(clientObj.clientID, "", f"{clientObj.clientID}-{destination}-DestinationSelect", xpos + 1, ypos + 1, 18, 3, text=destination, togglecolour=colour)
            ypos += 3.1
    else:
        sbs.send_gui_button(clientObj.clientID, "", "jump-node-interface", "text:Node Interface", 0, 59, 17, 64)


def StandardEngineering(clientObj):
    name = "StandardEngineering_main"
    widgets = "ship_internal_view^eng_heat_controls^eng_power_controls^ship_data"
    layoutdata = {"ship_data": [70, 0, 100, 40, 70, 0, 100, 40],
                  "eng_heat_controls": [10, 65, 60, 96, 10, 65, 60, 96],
                  "eng_power_controls": [0, 20, 70, 65, 0, 20, 70, 65],
                  "ship_internal_view": [70, 40, 100, 95, 70, 40, 100, 95]
                  }

    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])

    Engineering = clientObj.myShip.shipSystems.get("Engineering")
    Emissions = clientObj.myShip.shipSystems.get("Emissions")
    GUI.holotextDisplay(clientObj.clientID, "", "HullIntegrity", 1, 6, 29, 5, text=f"Hull Integrity: {Engineering.HullIntegrity}%", justify="center", colour="#999966")
    GUI.holotextDisplay(clientObj.clientID, "", "EmissionsLevelDisplay", 1, 12, 29, 5, text=f"E-Level: {round(Emissions.EmissionLevel, 2)}", colour="#999966")
    posx = 41
    posy = 6.5
    presetList = list(clientObj.myEngineeringPresets.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-Preset", 41, 5, 28, 13, text="Config Menu", font="smallest", currentPos=clientObj.PresetPosition, maxLength=len(presetList), background=True, scrollbar=True, colour="#2d3a3d")
    for x in range(clientObj.PresetPosition, min(len(presetList), clientObj.PresetPosition + 4)):
        presetdata = presetList[x]
        name = presetdata[0]
        data = presetdata[1]
        if clientObj.PresetSelected == name:
            colour = "#006600"
        else:
            colour = "#ff3300"
        if data.get("display"):
            GUI.ToggleButton(clientObj.clientID, "", f"Presetclick-{name}", posx + 1, posy, 25, 2.5, text=name, togglecolour=colour, font="smallest")
            posy += 3.1
    for key, data in clientObj.myEngineeringPresets.items():
        if data.get("hotkey") != "Unassigned" and data.get("hotkey"):
            sbs.send_gui_clickregion(clientObj.clientID, "", f"Presetclick-{data.get('hotkey')}", "", 100, 100, 101, 101)
            sbs.send_gui_hotkey(clientObj.clientID, "CSTMPRESET", f"Presetclick-{data.get('hotkey')}", data.get("hotkey"), f"Custom engineering preset hotkey")


def StandardEngineeringControls(clientObj):
    name = "StandardEngineeringControls_main"
    widgets = "ship_internal_view^ship_data^grid_object_list"
    layoutdata = {"ship_data": [72, 0, 100, 40, 72, 0, 100, 40],
                  "grid_object_list": [72, 40, 100, 89, 72, 40, 100, 89],
                  "ship_internal_view": [29, 6, 72, 94, 29, 6, 72, 94],
                  "grid_control": [0, 6, 29, 50, 0, 6, 29, 50]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    sbs.send_gui_image(clientObj.clientID, "", "interal_view_background", "image: ../missions/TSN Cosmos/Images/Box-50; color: white; draw_layer: 901", 29, 6, 72, 94)

    Engineering = clientObj.myShip.shipSystems.get("Engineering")
    GUI.holotextDisplay(clientObj.clientID, "", "HullIntegrity", 1, 10, 25, 5, text=f"Hull Integrity: {Engineering.HullIntegrity}%", justify="center", colour="#999966")
    shipCrew = clientObj.myShip.CrewMembers
    if shipCrew.selectedActive in shipCrew.activeCrew.keys():
        team = shipCrew.activeCrew.get(shipCrew.selectedActive)
        teamdata = team.teamdata
        datadisplay = ""
        datadisplay += f"-Team Leader-^ {teamdata.get('Name')}^^"
        datadisplay += f"-Health Status-^  OK: {teamdata.get('OK')}^  Lightly Wounded: {teamdata.get('LightWound')}^  Seriously Wounded: {teamdata.get('SeriousWound')}^  Killed: {teamdata.get('Killed')}"
        GUI.menuBackground(clientObj.clientID, "", "GridInfo", 1, 20, 25, 30, text=f"---Data---^^{datadisplay}", colour="#006600")

        GUI.menuBackground(clientObj.clientID, "", "TeamOrders", 1, 65, 25, 30, text="Orders")
        orderlist = teamdata.get("orders")
        ypos = 66
        for order in orderlist:
            colour = "orange"
            if teamdata.get("currentOrder") == order:
                colour = "green"
            GUI.ToggleButton(clientObj.clientID, "", order, 2, ypos, 23, 3, text=order, togglecolour=colour)
            ypos += 3.2
    else:
        ypos = 21
        for system in clientObj.myShip.Internals.shipSystems.keys():

            systemdisplay = ""
            damagedisplay = "^"
            systemdisplay += f"{system}^"
            data = Player_Ships.PlayerShipData.GridConfig.get(clientObj.myShip.ObjectHullClass)
            systeminfo = data.get(system)
            for key, value in systeminfo.items():
                damageType = value.get("damage")
                damageValue = clientObj.myShip.ObjectData.get(damageType, 0)
                systemdisplay += f"- {key}^"
                damagedisplay += f"{int(damageValue * 100)}%^"
            height = GUI.holotextBox(clientObj.clientID, "", "SystemInfo", 2, ypos, 20, text=systemdisplay)
            GUI.holotextBox(clientObj.clientID, "", "SystemDamage", 16, ypos, 20, text=damagedisplay)
            ypos += height + 2

        GUI.menuBackground(clientObj.clientID, "", "GridInfo", 1, 20, 25, 60, text=f"---Data---^", colour="#006600")

    if clientObj.myShip.ObjectData.get("jumpengine", 0) == "Charging":
        colour = "orange"
    elif clientObj.myShip.ObjectData.get("jumpengine", 0) == "Ready":
        colour = "green"
    else:
        colour = "gray"
    #sbs.send_gui_button(clientObj.clientID, "", "jump_engine_toggle", f"text: Jump Engine; color: {colour}", 72, 89, 100, 94)


def OperationsEngineering(clientObj):
    name = "OperationsEngineering_main"
    widgets = "ship_internal_view^eng_heat_controls^eng_power_controls^ship_data^grid_object_list^grid_control"
    layoutdata = {"ship_data": [70, 0, 100, 40, 70, 0, 100, 40],
                  "eng_heat_controls": [37, 58, 77, 79, 37, 58, 77, 79],
                  "eng_power_controls": [19, 79, 100, 96, 19, 79, 100, 96],
                  "ship_internal_view": [2, 5, 37, 77, 2, 5, 37, 77],
                  "grid_object_list": [37, 6, 70, 46, 37, 6, 70, 46],
                  "grid_control": [0, 40, 100, 94, 0, 40, 100, 94]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])


def EngerineeringSystemManagement(clientObj):
    name = "EngineeringSystemManagement_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    Engineering = clientObj.myShip.shipSystems.get("Engineering")
    shipAuxSystems = Engineering.AuxSystems
    xpos = 50
    ypos = 10
    for AuxSystem, AuxData in shipAuxSystems.items():
        if ypos > 80:
            xpos += 30
            ypos = 10
        state = False
        colour1 = "gray"
        colour2 = "gray"
        if AuxData.get("state") == "online":
            state = True
            colour1 = "green"
            colour2 = "gray"
        elif AuxData.get("state") == "offline":
            state = False
            colour1 = "red"
            colour2 = "green"
        elif AuxData.get("state") == "detached":
            state = False
            colour1 = "gray"
            colour2 = "red"
        sbs.send_gui_checkbox(clientObj.clientID, "", f"SystemControl-{AuxSystem}", f"text: {AuxSystem}; state:{state}; color:{colour1}", xpos, ypos, xpos + 25, ypos + 4)
        sbs.send_gui_rawiconbutton(clientObj.clientID, "", f"DetachControl-{AuxSystem}", f"icon_index: {AuxData.get('icon')}; color: {colour2}", xpos + 25, ypos, xpos + 29, ypos + 4)
        ypos += 5
    engineeringpresets(clientObj)


def engineeringpresets(clientObj):
    #preset menu shown on System Management panel
    posx = 2
    posy = 11
    presetList = list(clientObj.myEngineeringPresets.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-Preset", 2, 10, 30, 38, text="Power Config", colour="#999966", currentPos=clientObj.PresetPosition, maxLength=len(presetList), background=True, scrollbar=True)
    for x in range(clientObj.PresetPosition, min(len(presetList), clientObj.PresetPosition + 7)):
        presetdata = presetList[x]
        name = presetdata[0]
        data = presetdata[1]
        if name == "position":
            pass
        else:
            if isinstance(data.get("hotkey"), str):
                hotkey = f"{data.get('hotkey')}"
            else:
                hotkey = "UNASSIGNED"
            if clientObj.EditPresetSelected == name:
                colour = "#006600"
            else:
                colour = "#ff3300"
            GUI.TabletButton(clientObj.clientID, "", f"{clientObj.clientID}-PresetManclick-{name}", posx + 2, posy, 24, 5, text=name, subtext=hotkey, buttoncolour=colour)
            if data.get("display"):
                menuDisplay = "white"
            else:
                menuDisplay = "gray"
            sbs.send_gui_rawiconbutton(clientObj.clientID, "", f"{clientObj.clientID}-PresetManmenuDisplay-{name}", f"icon_index: 31; color: {menuDisplay}", posx + 25, posy, posx + 29, posy + 4)
            sbs.send_gui_rawiconbutton(clientObj.clientID, "", f"{clientObj.clientID}-PresetManDelete-{name}", f"icon_index: 97; color: red", posx, posy, posx + 2, posy + 2)
            posy += 5.2

    if clientObj.EditPresetSelected:
        presetdata = clientObj.myEngineeringPresets.get(clientObj.EditPresetSelected)
        xpos = 1
        sbs.send_gui_typein(clientObj.clientID, "", f"{clientObj.clientID}-PresetManRename", f"text:{clientObj.PresetText}; font: gui-1", xpos, 55, xpos + 20, 58)
        sbs.send_gui_button(clientObj.clientID, "", f"{clientObj.clientID}-PresetUpdate", "text: Update; font: smallest", xpos + 25, 55, xpos + 30, 58)
        # power setting sliders
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-Preset", xpos, 62, 55, 33, text="Power", colour="white")
        for key, value in presetdata.items():
            if isinstance(key, int):
                name = tsn_databases.EngineeringPowerSliderDatabase.get(key)
                sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-PresetManTitle-{key}", f"text:{name}; font: smallest; justify: center", xpos, 62, xpos + 6, 68)
                sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-PresetManValue-{key}", f"text: {int(presetdata.get(key)[0] * 100)}%; font: smallest; justify: center", xpos, 65, xpos + 6, 68)
                sbs.send_gui_slider(clientObj.clientID, "", f"{clientObj.clientID}-PresetManSlider-{key}", presetdata.get(key)[0] * 100, f"high: 300; low: 0", xpos + 2, 68, xpos + 4, 90)
                sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-PresetManRSTText-{key}", f"text:Reset; color: white; font: smallest; justify:center", xpos, 90, xpos + 6, 94)
                sbs.send_gui_clickregion(clientObj.clientID, "", f"{clientObj.clientID}-PresetManSliderRST-{key}", f"text:Reset; color: orange; font: smallest", xpos, 90, xpos + 6, 94)
                xpos += 7
        # coolant sliders
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-Coolant", xpos-1, 62, 28, 33, text="Coolant", colour="#29f500")
        for key, value in presetdata.items():
            if isinstance(key, int) and key < 4:
                name = tsn_databases.EngineeringCoolantDatabase.get(key)
                sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-PresetCManTitle-{key}", f"text:{name}; font: smallest; justify: center", xpos, 62, xpos + 6, 68)
                sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-PresetCManValue-{key}", f"text: {int(presetdata.get(key)[1])}; font: smallest; justify: center", xpos, 65, xpos + 6, 68)
                sbs.send_gui_slider(clientObj.clientID, "", f"{clientObj.clientID}-PresetCManSlider-{key}", presetdata.get(key)[1], "high: 8; low: 0", xpos + 2, 68, xpos + 4, 90)
                sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-PresetManCRSTText-{key}", f"text:Reset; color: white; font: smallest; justify:center", xpos, 90, xpos + 6, 94)
                sbs.send_gui_clickregion(clientObj.clientID, "", f"{clientObj.clientID}-PresetCManSliderRST-{key}", f"text:Reset; color: orange; font: smallest", xpos, 90, xpos + 6, 94)
                xpos += 7

        #showing the hotkey menu
        posy = 63
        hotkeyList = tsn_databases.hotkeys
        maxvalue = min(clientObj.hotListPos + 10, len(hotkeyList))
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-Hotkeys", xpos, 62, 15, 33, text="HotKey", colour="blue", currentPos=clientObj.hotListPos, maxLength=len(hotkeyList), background=True, scrollbar=True)
        for x in range(clientObj.hotListPos, maxvalue):
            hotkeyname = list(hotkeyList)[x]

            assignedkey = presetdata.get("hotkey")
            if assignedkey == hotkeyname:
                colour = "#006600"
            else:
                colour = "#ff3300"

            GUI.ToggleButton(clientObj.clientID, "", f"{clientObj.clientID}-Hotkeysetting-{hotkeyname}", xpos + 1, posy, 13, 3, text=hotkeyname, font="smallest", togglecolour=colour)
            posy += 3
    else:
        sbs.send_gui_typein(clientObj.clientID, "", f"{clientObj.clientID}-PresetManRename", f"text:{clientObj.PresetText}; font: gui-1", 1, 55, 41, 58)
        sbs.send_gui_button(clientObj.clientID, "", f"{clientObj.clientID}-PresetCreate", "text: Create; font: smallest", 46, 55, 56, 58)


def StandardWeapons(clientObj):
    name = "StandardWeapons_main"
    widgets = "weapon_2d_view^weapon_control^ship_data^shield_control^weap_beam_freq"
    layoutdata = {"ship_data": [70, 0, 100, 40, 70, 0, 100, 40],
                  "weapon_2d_view": [3, 5, 74, 85, 3, 5, 74, 85],
                  "shield_control": [76, 40, 100, 45, 76, 40, 100, 45],
                  "weapon_control": [0, 82, 37, 95, 0, 82, 37, 95],
                  "weap_torp_conversion": [76, 47, 100, 51, 76, 47, 100, 51],
                  "weap_beam_freq": [76, 45, 100, 50, 76, 45, 100, 50]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    shipdata = clientObj.myShip.ObjectData
    systems = clientObj.myShip.shipSystems.get("Weapons")
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    sbs.send_gui_checkbox(clientObj.clientID, "", "weapons-auto-manual", f"text: Auto/Manual; font: smallest; state:{systems.WeaponManAuto}", 76, 51, 100, 53)
    if systems.WeaponManAuto:
        sbs.send_gui_text(clientObj.clientID, "", "config", f"text: Configuration", 76, 54, 100, 90)
    else:
        sbs.send_gui_text(clientObj.clientID, "", "label-fire-rate", f"text: Fire Rate {shipdata.get('beamRate', 0)}%; font: smallest", 76, 54, 100, 90)
        sbs.send_gui_slider(clientObj.clientID, "", "beam-fire-rate", shipdata.get("beamRate", 0), "low:10 ; high: 300; color:#0D4D00",  76, 56, 100, 59)

        sbs.send_gui_text(clientObj.clientID, "", "label-aperture", f"text: Aperture {shipdata.get('beamAperture', 0)}%; font: smallest", 76, 60, 100, 90)
        sbs.send_gui_slider(clientObj.clientID, "", "beam-aperture", shipdata.get("beamAperture", 0), "low:10 ; high: 300; color:#0D4D00", 76, 62, 100, 65)

        sbs.send_gui_text(clientObj.clientID, "", "label-targeting", f"text: Target Priority; font: smallest", 76, 68, 100, 90)

        targets = shipdata.get("targetPoints", 0)
        sbs.send_gui_dropdown(clientObj.clientID, "", "targeting-focus", f"text:{shipdata.get('targetSubSystem', 0)}; list:{targets}; font:gui-1", 76, 70, 100, 73)


def StandardWeaponsControls(clientObj):
    name = "StandardWeaponsControls_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    systems = clientObj.myShip.shipSystems.get("Weapons")
    sbs.send_gui_text(clientObj.clientID, "", "weap-controlstxt", "text: Targeting Controls; font:gui-1", 10, 8, 30, 12)
    sbs.send_gui_image(clientObj.clientID, "", f"weap-controlbackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: #999966", 9, 11, 36, 23)
    sbs.send_gui_checkbox(clientObj.clientID, "", "weapons_safe", f"text:Safety;state:{systems.WeaponSafe}; font: gui-1", 10, 12, 35, 16)
    sbs.send_gui_checkbox(clientObj.clientID, "", "weapons_auto", f"text:Auto-Targeting;state:{systems.WeaponAuto}; font: gui-1", 10, 18, 35, 22)

    sbs.send_gui_text(clientObj.clientID, "", "weap-ordmantxt", "text: Ordnance Management; font:gui-1", 10, 50, 90, 70)
    sbs.send_gui_image(clientObj.clientID, "", f"weap-ordmanbackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: #5c5c3d", 8, 54, 77, 82)
    WeaponsCargo(clientObj)
    WeaponsMagazine(clientObj)


def WeaponsMagazine(clientObj):
    shipObj = clientObj.myShip
    availbleOrdList = shipObj.ObjectData.get("torpedo_types_available", 0)
    torp_types = [x.strip() for x in availbleOrdList.split(',')]
    torp_types = torp_types[:-1]
    posx = 10
    posy = 60

    GUI.menuBackground(clientObj.clientID, "", f"{shipObj.ObjectID}-WeapMag", posx, posy, 31, 22, scrollbar=True, currentPos=clientObj.MagPos, maxLength=len(torp_types) - 3, background=True, text="Magazine")
    for n in range(clientObj.MagPos, min(len(torp_types), clientObj.MagPos + 4)):
        torp = torp_types[n]
        magCount = shipObj.ObjectData.get(f"{torp}_NUM", 0)
        for x in range(shipObj.ObjectData.get("torpedo_tube_count", 0)):
            tubeCurType = shipObj.ObjectData.get("torpedoTubeCurrentType", x)
            if torp == tubeCurType:
                magCount -= 1
        count = f"{magCount}/{shipObj.ObjectData.get(f'{torp}_MAX', 0)}"
        data = tsn_databases.ordnanceDatabase.get(torp)
        GUI.IconTabletButton(clientObj.clientID, "", f"{shipObj.ObjectID}-WeapMagTrans-{torp}", posx + 1, posy + 1, 29, 5, text=f"{torp} - {count}", icon=data.get('icon'), iconcolour=data.get('colour'))
        posy += 5.1


def WeaponsCargo(clientObj):
    shipObj = clientObj.myShip

    posx = 45
    posy = 60
    availbleOrdList = shipObj.ObjectData.get("torpedo_types_available", 0)
    torp_types = [x.strip() for x in availbleOrdList.split(',')]
    torp_types = torp_types[:-1]
    storedTorps = []
    for torp in torp_types:
        if torp in shipObj.Cargo.CargoHold.keys():
            storedTorps.append(torp)

    GUI.menuBackground(clientObj.clientID, "", f"{shipObj.ObjectID}-WeapCargoBay", posx, posy, 31, 22, scrollbar=True, currentPos=clientObj.OrdCarPos, maxLength=len(storedTorps) - 3, background=True, text="Cargo Bay")
    for n in range(clientObj.OrdCarPos, min(len(storedTorps), clientObj.OrdCarPos + 4)):
        torp = storedTorps[n]
        torpData = shipObj.Cargo.CargoHold.get(torp)
        count = f"{torpData.get('count')}"
        GUI.IconTabletButton(clientObj.clientID, "", f"{shipObj.ObjectID}-WeapCargoTrans-{torp}", posx + 1, posy + 1, 29, 5, text=f"{torp} - {count}", icon=torpData.get('icon'), iconcolour=torpData.get('colour'))
        posy += 5.1


def TurretBeams(clientObj):
    name = "WeaponsTurretBeams_main"
    widgets = "weapon_2d_view^ship_data^shield_control^weap_beam_freq"
    layoutdata = {"ship_data": [70, 0, 100, 40, 70, 0, 100, 40],
                  "weapon_2d_view": [3, 5, 74, 85, 3, 5, 74, 85],
                  "shield_control": [76, 40, 100, 45, 76, 40, 100, 45],
                  "weap_beam_freq": [76, 45, 100, 50, 76, 45, 100, 50]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    shipdata = clientObj.myShip.ObjectData
    systems = clientObj.myShip.shipSystems.get("Weapons")
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    sbs.send_gui_text(clientObj.clientID, "", "label-turret-control", f"text: Turret Angle {int(shipdata.get('beamBarrelAngle', 0))}; justify:center; font: smallest", 3, 83, 74, 87)
    sbs.send_gui_slider(clientObj.clientID, "", "turret-direction-control", shipdata.get("beamBarrelAngle", 0), f"low:-180; high: 180;", 3, 87, 74, 90)
    sbs.send_gui_checkbox(clientObj.clientID, "", "weapons-auto-manual", f"text: Auto/Manual; font: smallest; state:{systems.WeaponManAuto}", 76, 51, 100, 53)
    if systems.WeaponManAuto:
        sbs.send_gui_text(clientObj.clientID, "", "config", f"text: Configuration", 76, 54, 100, 90)
    else:
        sbs.send_gui_text(clientObj.clientID, "", "label-fire-rate", f"text: Fire Rate {shipdata.get('beamRate', 0)}%; font: smallest", 76, 54, 100, 90)
        sbs.send_gui_slider(clientObj.clientID, "", "beam-fire-rate", shipdata.get("beamRate", 0), "low:10 ; high: 300; color:#0D4D00",  76, 56, 100, 59)

        sbs.send_gui_text(clientObj.clientID, "", "label-aperture", f"text: Aperture {shipdata.get('beamAperture', 0)}%; font: smallest", 76, 60, 100, 90)
        sbs.send_gui_slider(clientObj.clientID, "", "beam-aperture", shipdata.get("beamAperture", 0), "low:10 ; high: 300; color:#0D4D00", 76, 62, 100, 65)

        sbs.send_gui_text(clientObj.clientID, "", "label-targeting", f"text: Target Priority; font: smallest", 76, 68, 100, 90)

        targets = shipdata.get("targetPoints", 0)
        sbs.send_gui_dropdown(clientObj.clientID, "", "targeting-focus", f"text:{shipdata.get('targetSubSystem', 0)}; list:{targets}; font:gui-1", 76, 70, 100, 73)


def StandardScience(clientObj):
    name = "StandardScience_main"
    widgets = "science_2d_view^"
    layoutdata = {"science_2d_view": [1, 6, 69, 94, 1, 6, 69, 94],
                  "science_data": [69, 75, 100, 94, 69, 75, 100, 94],
                  "science_sorted_list": [69, 14, 100, 50, 69, 14, 100, 50],
                  "text_waterfall": [69, 14, 100, 50, 69, 14, 100, 50]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    sbs.send_gui_hotkey(clientObj.clientID, "TSNSCI", f"SCI-scanObj", "KEY_RETURN", f"Science key to initiate active scan of an object")
    sbs.send_gui_clickregion(clientObj.clientID, "", f"SCI-scanObj", "", 100, 100, 101, 101)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])

    scienceSystems = clientObj.myShip.shipSystems.get("Science")
    if clientObj.myShip.ObjectData.get("science_target_UID", 0) in scienceSystems.ScanData.keys() and simulation.simul.space_object_exists(clientObj.myShip.ObjectData.get("science_target_UID", 0)):
        scannedData = scienceSystems.ScanData.get(clientObj.myShip.ObjectData.get("science_target_UID", 0))
        scanTargetData = scannedData.get("objDataSet")
        xpos = 70
        ypos = 8
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-scan-data", xpos, ypos, 30, 85, text="Scan Data", colour="#4f4f4f")
        ScannedBaseDisp(clientObj, scannedData, 71, 8)
        match scannedData.get("objBehav"):
            case "behav_station":
                maxShieldsList = [scanTargetData.get("shield_max_val", x) for x in range(scanTargetData.get("shield_count", 0))]
                curShieldsList = [scanTargetData.get("shield_val", x) for x in range(scanTargetData.get("shield_count", 0))]
                ScannedShieldLevelsDisp(clientObj, maxShieldsList, curShieldsList, 71, 20, 16)
            case "behav_npcship":
                maxShieldsList = [scanTargetData.get("shield_max_val", x) for x in range(scanTargetData.get("shield_count", 0))]
                curShieldsList = [scanTargetData.get("shield_val", x) for x in range(scanTargetData.get("shield_count", 0))]
                ScannedShieldLevelsDisp(clientObj, maxShieldsList, curShieldsList, 71, 20, 16)
                shieldfreq = [scanTargetData.get("shield_freq_strength", x) for x in range(5)]
                ScannedShieldFrequenciesDisp(clientObj, shieldfreq, 88, 20, 10)
                ScannedShipDataDisp(clientObj, scanTargetData, 71, 40, 29, 50)
            case _:
                pass
    else:
        sbs.send_gui_button(clientObj.clientID, "", "ping", "text:Scan", 85, 3, 100, 7)

    #sbs.send_gui_button(clientObj.clientID, "", "jpscan", "text:JP Scan", 85, 7, 100, 11)


def ScannedBaseDisp(clientObj, scannedData, xpos, ypos):
    hulltype = scannedData.get("objHull")
    properties = tsn_databases.allProperties.get(hulltype)
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipDes", f"text:{scannedData.get('Name')}; font:gui-3", xpos, ypos, xpos + 30, ypos + 4)
    range = round(sbs.distance(clientObj.myShip.Object, scannedData.get('obj')))
    unit = ""
    if range > 5000:
        range = round(range/1000)
        unit = "k"
    bearing = round(getheadingtoTarget(clientObj.myShip.Object, scannedData.get('obj')))
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipRan", f"text:Range - {range}{unit}; font:gui-1", xpos + 15, ypos + 4, xpos + 30, ypos + 6)
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipBear", f"text:Bearing - {bearing}; font:gui-1", xpos + 15, ypos + 7, xpos + 30, ypos + 9)

    match scannedData.get("objBehav"):
        case "behav_station":
            sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipClass", f"text:{properties.get('type')} Station; font:gui-1", xpos, ypos + 4, xpos + 30, ypos + 6)
            sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipRace", f"text: Origin - {properties.get('race')}; font:gui-1", xpos, ypos + 7, xpos + 30, ypos + 9)
        case "behav_npcship":
            sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipClass", f"text:{properties.get('type')} Class; font:gui-1", xpos, ypos + 4, xpos + 30, ypos + 6)
            sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipRace", f"text: Origin - {properties.get('race')}; font:gui-1", xpos, ypos + 7, xpos + 30, ypos + 9)
        case _:
            if properties:
                sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipClass", f"text:{properties.get('type')}; font:gui-1", xpos, ypos + 4, xpos + 30, ypos + 6)
            else:
                objData = scannedData.get("objDataSet")
                sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-display-shipClass", f"text:{objData.get('hull_name', 0)}; font:gui-1", xpos, ypos + 4, xpos + 30, ypos + 6)
    # sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.clientID}-displayed-shieldFreq", f"image: ../missions/TSN Cosmos/Images/Factions/{properties.get('race')}Symbol; color: gray", xpos, ypos, xpos + 28, ypos + 90)


def getheadingtoTarget(SpaceObj, target):
    # return the heading in degrees between the ship and a target space object
    ang = math.atan2(target.pos.x - SpaceObj.pos.x, target.pos.z - SpaceObj.pos.z)
    if ang < 0:
        ang = ang + (2 * math.pi)
    return math.degrees(ang)

def ScannedShieldFrequenciesDisp(clientObj, shieldFreqList, xpos, ypos, w):
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-displayed-shieldFreqTitle", f"text:Frequencies; font:gui-1", xpos, ypos, xpos + w, ypos + 5)
    ypos += 10
    letters = ["A", "B", "C", "D", "E"]
    no = 0
    for freq in shieldFreqList:
        if freq: #only display if there is a value to display
            h = freq / 10
            sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.clientID}-displayed-shieldFreq", f"image: ../missions/TSN Cosmos/Images/box-70; color: yellow", xpos, ypos, xpos + (w/5), ypos - h)
            sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-displayed-shieldFreqLetter{letters[no]}", f"text:{letters[no]}; font:gui-1; justify: center", xpos, ypos, xpos + (w/5), ypos + 3)
            xpos += (w/5) + 0.3
            no += 1


def ScannedShieldLevelsDisp(clientObj, maxLevels, curLevels, xpos, ypos, w):
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-displayed-shieldLevelTitle", f"text:Shields; font:gui-1", xpos, ypos, xpos + 26, ypos + 3)
    ypos += 3
    position = ["Front", "Rear"]
    if len(maxLevels) == 1:
        position = ["Strength"]
    no = 0
    for mlevel in maxLevels:
        percent = (curLevels[no] / mlevel) * w
        colour = "green"
        if round(mlevel/4) > round(curLevels[no]):
            colour = "red"
        elif round(mlevel/2) > round(curLevels[no]) >= round(mlevel/4):
            colour = "yellow"
        sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.clientID}-displayed-shieldback{position[no]}-", f"image: ../missions/TSN Cosmos/Images/box-20; color: white", xpos, ypos, xpos + w, ypos + 3)
        sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.clientID}-displayed-shieldbar{position[no]}-", f"image: ../missions/TSN Cosmos/Images/box-70; color: {colour}", xpos, ypos, xpos + percent, ypos + 3)
        sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-displayed-shieldLevel{position[no]}", f"text:{position[no]} - {round(curLevels[no])}/{round(mlevel)}; font:gui-1; justify: center", xpos, ypos, xpos + w, ypos + 3)
        ypos += 4
        no += 1


def ScannedShipDataDisp(clientObj, shipDataSet, xpos, ypos, w, h):
    text = ""
    if shipDataSet.get("beamCount", 0) > 0:
        text += f"{shipDataSet.get('beamCount', 0)} Beam Arrays^"
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-displayed-data", f"text:{text}; font:gui-1", xpos, ypos, xpos + w, ypos + h)


def StandardNavigation(clientObj):
    name = "StandardNavigation_main"
    widgets = "science_2d_view"
    layoutdata = {"science_2d_view": [10, 10, 90, 90, 10, 10, 90, 90],
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    systems = clientObj.myShip.shipSystems.get("NavSystems")

    posx = 1
    posy = 5
    sbs.send_gui_checkbox(clientObj.clientID, "", "command-navmarker", f"text: Marker; font: gui-1; state:{clientObj.myConsoles.setNavpoint}", posx, posy, posx + 9, posy + 4)
    posy += 5
    posy += 1
    navpoints = systems.NavPoints.items()
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-navpoint", posx, posy, 10, 55, scrollbar=True, currentPos=clientObj.NavPointPos, maxLength=len(list(navpoints))-9, background=True)
    for n in range(clientObj.NavPointPos, min(len(list(navpoints)), clientObj.NavPointPos + 10)):
        navpoint = list(navpoints)[n]
        navpointID = navpoint[0]
        navpointObj = navpoint[1]
        GUI.TabletButton(clientObj.clientID, "", f"{clientObj.clientID}-{navpointID}-NavpointSelect", posx + 1, posy, 8, 5, text=navpointObj.text)
        posy += 5.1

    if systems.NavMenu != "--":
        xpos1 = 80
        ypos1 = 60
        waypoints = tsn_databases.waypointDatabase.get(systems.NavMenu)
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-waypoint", xpos1, ypos1, 20, 29, scrollbar=True, currentPos=clientObj.WaypointPos, maxLength=len(list(waypoints))-3, background=True, text="Waypoints")
        for n in range(clientObj.WaypointPos, min(len(list(waypoints.items())), clientObj.WaypointPos + 4)):
            waypoint = list(waypoints.items())[n]
            if waypoint[0] in systems.Waypoints.keys():
                colour = "#006600"
            else:
                colour = "#ff3300"
            GUI.ToggleButton(clientObj.clientID, "", f"{clientObj.clientID}-{waypoint[0]}-{systems.NavMenu}-WaypointSelect", xpos1, ypos1 + 4, 20, 5, text=waypoint[0], togglecolour=colour)
            ypos1 += 5.1


def StandardScienceVis(clientObj):
    name = "StandardScienceVis_main"
    widgets = "3dview^science_2d_view^science_data^science_sorted_list"
    layoutdata = {"3dview": [24, 37, 100, 96, 24, 37, 100, 96],
                  "science_2d_view": [37, 4, 82, 37, 37, 4, 82, 37],
                  "science_data": [0, 57, 24, 96, 0, 57, 24, 96],
                  "science_sorted_list": [0, 5, 24, 57, 0, 5, 24, 57]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])


def ScienceSensorSuite(clientObj):
    name = "ScienceSensorSuite_main"
    widgets = "science_2d_view^text_waterfall"
    layoutdata = {"science_2d_view": [0, 4, 50, 54, 0, 4, 50, 54],
                  "text_waterfall": [71, 46, 99, 55, 71, 46, 99, 55]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    scienceSystems = clientObj.myShip.shipSystems.get("Science")

    #display the different scan types available for selection
    xpos = 70
    ypos = 8
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-scan-types", xpos, ypos, 28, 15, scrollbar=True, currentPos=clientObj.ScanTypePos, maxLength=len(list(scienceSystems.LRSScanTypes.keys())) - 3, background=True, text="Available Scans")
    for s in range(clientObj.ScanTypePos, min(len(list(scienceSystems.LRSScanTypes.keys())), clientObj.ScanTypePos + 4)):
        scantype = list(scienceSystems.LRSScanTypes.keys())[s]
        if scienceSystems.LRSScanSelected == scantype:
            colour = "#006600"
        else:
            colour = "#ff3300"
        GUI.ToggleButton(clientObj.clientID, "", f"{clientObj.clientID}-{scantype}-ScanSelect", xpos+1, ypos+1, 26, 3, text=scantype, togglecolour=colour)
        ypos += 3.4

    # display the configuration for the scan type selected
    if scienceSystems.LRSScanSelected:
        scanconfig = scienceSystems.LRSScanTypes.get(scienceSystems.LRSScanSelected)
        xpos1 = 70
        ypos1 = 27
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-scan-configuration", xpos1, ypos1, 28, 22, background=True, text="Scan Configuration")
        sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-scan-range-text", f"text:Range: {round(scanconfig.get('range'), -3)/1000}k; font: gui-1;", xpos1+1, ypos1+2, xpos1 + 18, ypos1+4)
        sbs.send_gui_slider(clientObj.clientID, "", f"{clientObj.clientID}-scan-range-{scienceSystems.LRSScanSelected}", round(scanconfig.get('range'),-3), "low:50000 ; high: 200000; color:#0D4D00",  xpos1+1, ypos1+4, xpos1 + 26, ypos1+6)
        sbs.send_gui_button(clientObj.clientID, "", f"{clientObj.clientID}-activateScan-{scienceSystems.LRSScanSelected}", f"text:Activate Scan; font: gui-1;", xpos1+1, ypos1+8, xpos1 + 16, ypos1+12)
        scienceSystems.LRSScanningProgress.send_gui_progressbar(clientObj.clientID, "", f"{clientObj.clientID}-LRSScan-Progress", (71, 55))

    # display a list of data entries created from the scan
    xpos2 = 2
    ypos2 = 60
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-LRSscan-data", xpos2, ypos2, 20, 32, scrollbar=True, currentPos=clientObj.ScanDataPos, maxLength=len(list(scienceSystems.LRSScanData.keys())) - 5, background=True, text="LRS Scan Data")
    for s in range(clientObj.ScanDataPos, min(len(list(scienceSystems.LRSScanData.keys())), clientObj.ScanDataPos + 6)):
        scandata = list(scienceSystems.LRSScanData.keys())[s]
        if scienceSystems.LRSScanDataDisplay == scandata:
            colour = "#006600"
        else:
            colour = "#ff3300"
        GUI.ToggleButton(clientObj.clientID, "", f"{clientObj.clientID}-{scandata}-ScanDataSelect", xpos2 + 1, ypos2 + 1, 15, 3, text=scandata, togglecolour=colour)
        navdata = scienceSystems.LRSScanData.get(scandata)
        if navdata:
            if navdata.get("NavPoint")[0]:
                colour = "#44ED01"
            else:
                colour = "#CECECE"
        GUI.IconButton(clientObj.clientID, "", f"{clientObj.clientID}-{scandata}-ScanNavSelect", xpos2 + 15, ypos2 + 1, icon=9, iconcolour=colour, iconsize=3)
        GUI.IconButton(clientObj.clientID, "", f"{clientObj.clientID}-Scan-DeleteEntry-{scandata}", xpos2 + 17.5, ypos2 + 1, icon=97, iconcolour="red", iconsize=2)

        ypos2 += 3.1
    # display the stored data related to the selected navpoint reference
    xpos3 = 25
    ypos3 = 60
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-LRSscan-data", xpos3, ypos3, 60, 32, background=True, text="Data")
    scanheading = ""
    scantext = ""
    if scienceSystems.LRSScanDataDisplay in scienceSystems.LRSScanData.keys():
        data = scienceSystems.LRSScanData.get(scienceSystems.LRSScanDataDisplay)
        for key, value in data.items():
            if key == "NavPoint":
                pass
            else:
                scanheading += f"{key}:^^"
                scantext += f"{value}^^"
        sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-LRSScan-textheading", f"text:{scanheading}; font: gui-1", xpos3 + 3, ypos3 + 2, xpos3 + 20, ypos3 + 30)
        sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-LRSScan-text", f"text:{scantext}; font: gui-1", xpos3 + 20, ypos3 + 2, xpos3 + 60, ypos3 + 30)
        sbs.send_gui_button(clientObj.clientID, "", f"{clientObj.clientID}-LRSScan-DeleteEntry-{scienceSystems.LRSScanDataDisplay}", "text: Delete; font: gui-1", xpos3 + 50, ypos3 + 2, xpos3 + 59, ypos3 + 6)


def StandardComms(clientObj):
    name = "StandardComms_main"
    widgets = "comms_waterfall^comms_control^comms_face^comms_sorted_list"
    layoutdata = {"comms_waterfall": [53, 9, 100, 69, 53, 9, 100, 69],
                  "comms_control": [29, 6, 53, 69, 29, 6, 53, 69],
                  "comms_face": [3, 69, 24, 96, 3, 69, 24, 96],
                  "comms_sorted_list": [0, 6, 29, 69, 0, 6, 29, 69]
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    commssystems = clientObj.myShip.shipSystems.get("Communications")
    sbs.send_gui_text(clientObj.clientID, "", "dockaccess", f'text:Dock Access Code: {clientObj.myShip.ObjectData.get("dockaccess", 0)}; font:gui-1', 73, 85, 99, 88)
    sbs.send_gui_typein(clientObj.clientID, "", "dock-access-code-update", f"text:{commssystems.docktext}; desc:Update Code; font:gui-1; password:off", 73, 88, 99, 92)
    sbs.send_gui_button(clientObj.clientID, "", "submit-dock-code-update", "text:Confirm; font:smallest", 92, 92, 99, 95)
    sbs.send_gui_image(clientObj.clientID, "", "jumpdock-background", "image: ../missions/TSN Cosmos/Images/Box-50; color: #5c5c3d", 72.5, 73, 99.5, 95)


def StandardCommsInterface(clientObj):
    name = "StandardCommsInt_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])


def StandardCommsFleet(clientObj):
    name = "StandardCommsFleet_main"
    widgets = "2dview^comms_control^comms_waterfall^comms_sorted_list"
    layoutdata = {"comms_control": [0, 6, 21, 92, 0, 6, 21, 92],
                  "2dview": [21, 6, 78, 92, 21, 6, 78, 92],
                  "comms_waterfall": [78, 6, 100, 92, 78, 6, 100, 92],
                  }
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])


def StandardCrewManagement(clientObj):
    name = "StandardCrewManagement_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)

    ShipLocation(clientObj, "Crew Quarters", (2, 10))
    ShipLocation(clientObj, "Medical Bay", (2, 37))
    ShipLocation(clientObj, "Shuttle Bay", (2, 64))
    ShipLocation(clientObj, "Guest Quarters", (35, 64))
    ShipLocation(clientObj, "Brig", (68, 64))

    if clientObj.myShip.CrewMembers.selectedTeam != "":
        SelectedTeam(clientObj)


def ShipLocation(clientObj, locname, pos):
    teams = clientObj.myShip.CrewMembers.shipCrew
    presentteams = {}
    for teamid, team in teams.items():
        teamdata = team.teamdata
        teamloc = teamdata.get("location")
        if teamloc == locname:
            presentteams.update({teamid: teamdata})
    teamList = list(presentteams.items())
    posx = pos[0]
    posy = pos[1]

    locationposition = clientObj.LocPositions.get(locname)
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-{locname}-{len(teamList)}-Crew", posx, posy, 30, 22, background=True, scrollbar=True, text=locname, colour="#2d3a3d", currentPos=locationposition, maxLength=len(teamList)-3)

    for t in range(locationposition, min(len(list(presentteams.items())), locationposition + 4)):
        teamdata = teamList[t]
        data = teamdata[1]
        if data.get("working")[0] == "relocating":
            colour = "gray"
        else:
            colour = data.get('colour')
        GUI.IconTabletButton(clientObj.clientID, "", f"{clientObj.clientID}-{locname}SelectTeam-{teamdata[0]}", posx+1, posy + 1, 28, 5, text=data.get('Type'), subtext=data.get('Name'), icon=data.get('icon'), iconcolour=colour)
        posy += 5.1


def SelectedTeam(clientObj):
    system = clientObj.myShip.CrewMembers
    teams = system.shipCrew
    team = teams.get(int(system.selectedTeam))
    teamdata = team.teamdata
    posx = 50
    posy = 10
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-TeamData-name", f"text:{teamdata.get('Name')}", posx, posy, posx + 30, posy + 5)

    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-TeamData-type", f"text: {teamdata.get('Type')}; font: gui-1", posx, posy + 3, posx + 30, posy + 7)
    health = f"OK: {teamdata.get('OK')}^"
    health += f"Lightly Wounded: {teamdata.get('LightWound')}^"
    health += f"Seriously Wounded: {teamdata.get('SeriousWound')}^"
    health += f"Killed: {teamdata.get('Killed')}"
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-TeamData-health", f"text: {health}; font: gui-1", posx, posy + 9, posx + 30, posy + 25)

    teamid = system.selectedTeam
    sbs.send_gui_button(clientObj.clientID, "", f"{teamid}-move-Medical Bay", "text: Move to Med Bay; font: gui-1", posx, posy + 20, posx + 22, posy + 24)
    sbs.send_gui_button(clientObj.clientID, "", f"{teamid}-move-Shuttle Bay", "text: Move to Shuttle; font: gui-1", posx, posy + 25, posx + 22, posy + 29)
    sbs.send_gui_button(clientObj.clientID, "", f"{teamid}-move-Crew Quarters", "text: Return to Quarters; font: gui-1", posx, posy + 30, posx + 22, posy + 34)
    sbs.send_gui_button(clientObj.clientID, "", f"{teamid}-move-Guest Quarters", "text: Move to Guest Quarters; font: gui-1", posx + 23, posy + 20, posx + 45, posy + 24)
    sbs.send_gui_button(clientObj.clientID, "", f"{teamid}-move-Brig", "text: Move to Brig; font: gui-1", posx + 23, posy + 25, posx + 45, posy + 29)
    if teamdata.get('tag') == "DamCon":
        sbs.send_gui_button(clientObj.clientID, "", f"{teamid}-activateTeam", "text: Activate Team; font: gui-1", posx, posy + 35, posx + 22, posy + 39)


def AMCConsole(clientObj):
    name = "AMC Console_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    AMCCargoDisplay(clientObj)
    AMCInternalDisplay(clientObj)
    AMCOutputDisplay(clientObj)
    AMCLibraryDisplay(clientObj)
    AMCProcessingList(clientObj)


def AMCProcessingList(clientObj):
    shipObj = clientObj.myShip
    AMCsystems = shipObj.shipSystems.get("AMC")
    posx = 45
    posy = 75
    sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCProcessingtitle", f"text: Currently Processing; font: gui-1", 45, 73, 76, 95)
    if len(AMCsystems.AMCProcessing) > 0:
        for item in AMCsystems.AMCProcessing:
            name = item[0]
            type = item[1]
            progbar = item[3]
            sbs.send_gui_text(clientObj.clientID, "", f"{id(item)}-AMCProcessingtxt-{name}", f"text:{name}; color: #ccffff; font: gui-1; justify: center", posx + 1, posy + 1, posx + 30, posy + 5)
            if type == "deconstruct":
                colour = "red"
            else:
                colour = "#006600"
            sbs.send_gui_image(clientObj.clientID, "", f"{id(item)}-AMCProcessingbackground-{name}", f"image: ../missions/TSN Cosmos/Images/Box-50; color: {colour}", posx + 1, posy + 1, posx + 30, posy + 5)
            progbar[1].send_gui_progressbar(clientObj.clientID, "", f"{clientObj.clientID}-{progbar[0]}", (posx + 2, posy + 4.5))
            posy += 5.1
    sbs.send_gui_image(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCProcessing-wholebackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: #999966", 45, 75, 76, 95)


def AMCOutputDisplay(clientObj):
    shipObj = clientObj.myShip
    AMCsystems = shipObj.shipSystems.get("AMC")
    sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCOutput-title", f"text: Output; font: gui-1", 45, 48, 76, 50)
    key_with_value = [key for key, value in AMCsystems.AMCSystem.items() if set(value) == set(AMCsystems.AMC.keys())]
    database = tsn_databases.masterDatabase
    if key_with_value:
        # display the output of a single item to create
        data = database.get(key_with_value[0])
        sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCOutput-name-{key_with_value[0]}", f"text: {key_with_value[0]}; font: gui-1; justify: center", 45, 63, 76, 67)
        sbs.send_gui_icon(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCOutput-{key_with_value[0]}", f"icon_index: {data.get('icon')}; color: {data.get('colour')}", 54.5, 51, 66.5, 63)
        sbs.send_gui_button(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCCreate-{key_with_value[0]}", f"text: Create; font: gui-1; justify: center", 60, 68, 77, 72)
    elif len(AMCsystems.AMC.keys()) == 1:
        # display the output of items which will be obtained on deconstruction
        key = list(AMCsystems.AMC.keys())[0]
        if key in AMCsystems.AMCSystem.keys():
            output = AMCsystems.AMCSystem.get(key)
            width = 2.55 * len(output)
            posx = 60.5 - width
            posy = 55
            for item in output:
                data = database.get(item)
                sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCOutput-name-{item}", f"text: {item}; font: smallest; justify: center", posx, posy - 3, posx + 5, posy)
                sbs.send_gui_icon(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCOutput-{item}", f"icon_index: {data.get('icon')}; color: {data.get('colour')}", posx, posy, posx + 5, posy + 5)
                posx += 5.1
                if posx > 70:
                    posy += 12
                    posx = 45
            sbs.send_gui_button(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCDeconstruct-{key}", f"text: Deconstruct; font: gui-1", 60, 68, 77, 72)
    sbs.send_gui_image(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCOutput-background", "image: ../missions/TSN Cosmos/Images/Box-50; color: #999966", 45, 50, 76, 70)


def AMCCargoDisplay(clientObj):
    shipObj = clientObj.myShip
    allcargo = shipObj.Cargo.CargoHold
    cargoList = list(allcargo.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-Cargo", 4, 12, 32, 56, currentPos=clientObj.AMCCargoPos, maxLength=len(cargoList)-9, background=True, scrollbar=True, text="Cargo Bay", colour="#2d3a3d")
    posx = 5
    posy = 14
    for x in range(clientObj.AMCCargoPos, min(len(cargoList), clientObj.AMCCargoPos + 10)):
        cargodata = cargoList[x]
        name = cargodata[0]
        data = cargodata[1]
        GUI.IconTabletButton(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCCargoTrans-{name}", posx, posy, 30, 5, text=f"{name} - {data.get('count')}", icon=f"{data.get('icon')}", iconcolour=f"{data.get('colour')}", colour="#006600")
        posy += 5.1


def AMCInternalDisplay(clientObj):
    shipObj = clientObj.myShip
    AMCsystems = shipObj.shipSystems.get("AMC")
    AMCList = list(AMCsystems.AMC.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-AMCInt", 44, 12, 32, 31, currentPos=clientObj.AMCIntPos, maxLength=len(AMCList)-5, background=True, scrollbar=True, text="AMC", colour="#2d3a3d")
    posx = 45
    posy = 14
    for x in range(clientObj.AMCIntPos, min(len(list(AMCsystems.AMC.items())), clientObj.AMCIntPos + 5)):
        AMCIntData = AMCList[x]
        name = AMCIntData[0]
        data = AMCIntData[1]
        GUI.IconTabletButton(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCIntTrans-{name}", posx, posy, 30, 5, text=f"{name} - {data.get('count')}", icon=f"{data.get('icon')}", iconcolour=f"{data.get('colour')}", colour="#006600")
        posy += 5.1


def AMCLibraryDisplay(clientObj):
    shipObj = clientObj.myShip
    AMCsystems = shipObj.shipSystems.get("AMC")
    requirements = ""
    linked = ""
    menuitems = ""
    AMCLibSelected = clientObj.myConsoles.AMCLibrarySel
    sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCLibrarytxt", f"text: Library; font: gui-1", 80, 10, 98, 14)
    sbs.send_gui_image(clientObj.clientID, "", f"AMCLibrarybackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: #5c5c3d", 79, 19, 99, 60)
    for item in AMCsystems.AMCSystem.keys():
        menuitems += f"{item}^"
    sbs.send_gui_dropdown(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCLibrMenu", f"text:{AMCLibSelected}; list:{menuitems}; font:gui-1", 80, 14, 98, 17)
    if AMCLibSelected in AMCsystems.AMCSystem.keys():
        for item in AMCsystems.AMCSystem.get(AMCLibSelected):
            requirements += f" * {item}^"
        sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCLibraryReqT", f"text: Components; font: gui-1", 80, 20, 98, 50)
        sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCLibraryReq", f"text: ^{requirements}; font: smallest", 81, 22, 98, 39)
        sbs.send_gui_image(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCLibraryReqbackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: #006600", 80, 22, 98, 39)
    for output, components in AMCsystems.AMCSystem.items():
        if AMCLibSelected in components:
            linked += f" * {output}^"
    if linked != "":
        sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCLibraryLinkT", f"text: Used for; font: gui-1", 80, 40, 98, 70)
        sbs.send_gui_text(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCLibraryLink", f"text: ^{linked}; font: smallest", 81, 42, 98, 70)
        sbs.send_gui_image(clientObj.clientID, "", f"{shipObj.ObjectID}-AMCLibraryLinkbackground", "image: ../missions/TSN Cosmos/Images/Box-50; color: #006600", 80, 42, 98, 59)


def Logistics(clientObj):
    name = "Logistics_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    # this is a readout of what is on the spaceobject
    shipObj = clientObj.myShip
    allcargo = shipObj.Cargo.CargoHold
    cargoList = list(allcargo.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-BayCargo", 10, 15, 30, 22, currentPos=clientObj.BayCargoPos, maxLength=len(cargoList) -3, background=True, scrollbar=True, text="Ship Cargo Bay", colour="#2d3a3d")
    posx = 10
    posy = 15
    for x in range(clientObj.BayCargoPos, min(len(cargoList), clientObj.BayCargoPos + 4)):
        cargodata = cargoList[x]
        name = cargodata[0]
        data = cargodata[1]
        GUI.IconTabletButton(clientObj.clientID, "", f"{clientObj.myShip.ObjectID}-LogisticsCargo-{name}", posx + 1, posy + 1, 28, 5, text=f"{name} - {data.get('count')}", icon=f"{data.get('icon')}", iconcolour=f"{data.get('colour')}")
        posy += 5.1

    # show the teams that are available to load
    teams = clientObj.myShip.CrewMembers.shipCrew
    availableteams = {}
    for teamid, team in teams.items():
        teamdata = team.teamdata
        location = teamdata.get("location")
        if location == "Shuttle Bay":
            availableteams.update({teamid: teamdata})
    personnelList = list(availableteams.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-BayPerson", 10, 55, 30, 22, currentPos=clientObj.BayPersonPos, maxLength=len(personnelList)-3, background=True, scrollbar=True, text="Ship Personnel", colour="#2d3a3d")
    posx = 10
    posy = 55
    for x in range(clientObj.BayPersonPos, min(len(personnelList), clientObj.BayPersonPos + 4)):
        personnelData = personnelList[x]
        teamid = personnelData[0]
        data = personnelData[1]
        if data.get("working")[0] == "relocating":
            colour = "gray"
        else:
            colour = data.get('colour')
        GUI.IconTabletButton(clientObj.clientID, "", f"{clientObj.clientID}-LogisticsPersonnel-{teamid}", posx + 1, posy + 1, 28, 5, text=data.get('Type'), subtext=data.get('Name'), icon=data.get('icon'), iconcolour=colour)
        posy += 5.1

    #checking if the ship is docked
    dockingState = shipObj.ObjectData.get("dock_state", 0)
    dockPortState = shipObj.sim.space_object_exists(shipObj.ObjectData.get("dock_base_id", 0))
    allActiveDocks = SpaceObjects.activeShips | SpaceObjects.activeStations | SpaceObjects.activeObjects
    if dockingState == "docked" and dockPortState:
        dockedToID = shipObj.ObjectData.get("dock_base_id", 0)
        dockedToObj = allActiveDocks.get(dockedToID)

        dockedToCargo = dockedToObj.Cargo.CargoHold
        dockedToCargoList = list(dockedToCargo.items())
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-dockedToCargoMenu", 50, 15, 30, 22, currentPos=clientObj.dockedToCargoPos, maxLength=len(dockedToCargoList)-3, background=True, scrollbar=True, text=f"{dockedToObj.ObjectName} Cargo Bay", colour="#2d3a3d")
        posx = 50
        posy = 15
        for x in range(clientObj.dockedToCargoPos, min(len(dockedToCargoList), clientObj.dockedToCargoPos + 4)):
            dockedTocargodata = dockedToCargoList[x]
            name = dockedTocargodata[0]
            data = dockedTocargodata[1]
            GUI.IconTabletButton(clientObj.clientID, "", f"{clientObj.clientID}-dockedToCargo-{name}", posx + 1, posy + 1, 28, 5, text=f"{name} - {data.get('count')}", icon=f"{data.get('icon')}", iconcolour=f"{data.get('colour')}")
            posy += 5.1

        # show the teams that are available to load
        teams = dockedToObj.CrewMembers.shipCrew
        availableteams = {}
        for teamid, team in teams.items():
            teamdata = team.teamdata
            location = teamdata.get("location")
            if location == "Shuttle Bay":
                availableteams.update({teamid: teamdata})
        personnelList = list(availableteams.items())
        GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-dockedToPersonnelMenu", 50, 55, 30, 22, currentPos=clientObj.dockedToPersonPos, maxLength=len(personnelList)-3, background=True, scrollbar=True, text=f"{dockedToObj.ObjectName} Personnel", colour="#2d3a3d")
        posx = 50
        posy = 55
        for x in range(clientObj.dockedToPersonPos, min(len(personnelList), clientObj.dockedToPersonPos + 4)):
            personnelData = personnelList[x]
            teamid = personnelData[0]
            data = personnelData[1]
            if data.get("working")[0] == "relocating":
                colour = "gray"
            else:
                colour = data.get('colour')
            GUI.IconTabletButton(clientObj.clientID, "", f"{clientObj.clientID}-dockedToPersonnel-{teamid}", posx + 1, posy + 1, 28, 5, text=data.get('Type'), subtext=data.get('Name'), icon=data.get('icon'), iconcolour=colour)
            posy += 5.1


# shuttle bay consoles
def ShuttleBay(clientObj):
    # this is the console onboard the player's own ship
    name = "ShuttleBay_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    if clientObj.mytempDock:
        shipObj = clientObj.mytempDock
    else:
        shipObj = clientObj.myShip
    locationName = shipObj.ObjectName
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.clientID}-BayLocTitle", f"text:{locationName} Shuttle Bay; justify: center", 0, 3, 100, 10)
    posx = 3
    posy = 15
    ShuttleList = list(shipObj.Shuttles.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-BayShuttle", 3, 15, 27, 23, text="Available Shuttles", currentPos=clientObj.BayShuttlePos, maxLength=len(ShuttleList)-4, background=True, scrollbar=True, colour="#2d3a3d")
    for s in range(clientObj.BayShuttlePos, min(len(list(shipObj.Shuttles.keys())), clientObj.BayShuttlePos + 5)):
        ShuttleData = ShuttleList[s]
        shuttleID = ShuttleData[0]
        data = ShuttleData[1]
        GUI.TabletButton(clientObj.clientID, "", f"{clientObj.clientID}-ShuttleSel-{shuttleID}", posx + 1, posy + 1, 25, 4, text=f"{data.ObjectData.get('name_tag', 0)}", subtext=f"Class: {data.ShuttleType}")
        posy += 4.1
    vposx = 5
    vposy = 44
    if clientObj.myShuttle:
        shuttlename = clientObj.myShuttle.ObjectData.get("call_sign", 0)
        sbs.send_gui_image(clientObj.clientID, "", "shuttle-image-background","image: ../missions/TSN Cosmos/Images/Box-50; color: #2d3a3d", vposx - 2, vposy - 4, vposx + 27, vposy + 25)
        sbs.send_gui_text(clientObj.clientID, "", "shuttle-name", f"text: Designation: {shuttlename}; font: gui-1", vposx, vposy - 1, vposx + 27, vposy + 16)
        sbs.send_gui_text(clientObj.clientID, "", "shuttle-type", f"text: Class: {clientObj.myShuttle.ShuttleType}; font: smallest", vposx, vposy + 1, vposx + 27, vposy + 9)
        sbs.send_gui_button(clientObj.clientID, "", "deploy-shuttle", "text: Deploy; font: gui-1", vposx + 17, vposy + 20, vposx + 25.5, vposy + 23)
        sbs.send_gui_button(clientObj.clientID, "", "unassign-shuttle", "text: Unassign; font: gui-1", vposx, vposy + 20, vposx + 8.5, vposy + 23)
        sbs.send_gui_3dship(clientObj.clientID, "", f"shuttle-image", f"hull_tag: {clientObj.myShuttle.ObjectHullClass}", vposx - 2, vposy - 5, vposx + 27, vposy + 25)
        shuttleCargoHandling(clientObj, shipObj)
        shuttlePersonnelHandling(clientObj, shipObj)


def shuttleCargoHandling(clientObj, ship):
    # show the cargo bay
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-ShutCargo", 69, 15, 23, 22, background=True, text="Cargo Hold", colour="#2d3a3d")
    x = 70
    y = 16
    for space in range(clientObj.myShuttle.cargoCapacity):
        sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-ShutCargo-background-{space}", "image: ../missions/TSN Cosmos/Images/Box-50; color: #006600", x, y, x + 5, y + 5)
        x += 5.1
        if x > 90:
            y += 5.1
            x = 70
    x = 70
    y = 16
    for key, value in clientObj.myShuttle.CargoHold.items():
        cargoData = value[1]
        icon = cargoData.get("icon")
        colour = cargoData.get("colour")
        sbs.send_gui_rawiconbutton(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-ShutCargo-{key}", f"icon_index: {icon}; color: {colour}", x, y, x + 5, y + 5)
        x += 5.1
        if x > 90:
            y += 5.1
            x = 70

    # this is a readout of what is on the spaceobject
    allcargo = ship.Cargo.CargoHold
    cargoList = list(allcargo.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-BayCargo", 37, 15, 30, 22, currentPos=clientObj.BayCargoPos, maxLength=len(cargoList)-3, background=True, scrollbar=True, text="Ship Cargo Bay", colour="#2d3a3d")
    posx = 37
    posy = 15
    for x in range(clientObj.BayCargoPos, min(len(cargoList), clientObj.BayCargoPos + 3)):
        cargodata = cargoList[x]
        name = cargodata[0]
        data = cargodata[1]
        GUI.IconTabletButton(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-BayCargo-{name}", posx + 1, posy + 1, 28, 5, text=f"{name} - {data.get('count')}", icon=f"{data.get('icon')}", iconcolour=f"{data.get('colour')}")
        posy += 5.1


def shuttlePersonnelHandling(clientObj, ship):
    x = 70
    y = 46
    # create rings to represent each space that is available on the shuttle
    for space in range(clientObj.myShuttle.personnelCapacity):
        sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-ShutPerson-background-{space}", "image: ../missions/TSN Cosmos/Images/Box-50; color: #006600", x, y, x + 5, y + 5)
        x += 5.1
        if x > 90:
            y += 5.1
            x = 70
    x = 70
    y = 46
    # create an icon to represent each loaded team on the shuttle
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-BayPerson", 69, 45, 23, 22, background=True, text="Personnel", colour="#2d3a3d")
    for key, value in clientObj.myShuttle.Personnel.items():
        personnelObj = value[1]
        personnelData = personnelObj.teamdata
        icon = personnelData.get("icon")
        colour = personnelData.get('colour')
        sbs.send_gui_rawiconbutton(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-ShutPerson-{key}", f"icon_index: {icon}; color: {colour}", x, y, x + 5, y + 5)
        x += 5.1
        if x > 90:
            y += 5.1
            x = 70

    # show the teams that are available to load
    teams = ship.CrewMembers.shipCrew
    availableteams = {}
    for teamid, team in teams.items():
        teamdata = team.teamdata
        location = teamdata.get("location")
        if location == "Shuttle Bay":
            availableteams.update({teamid: teamdata})
    personnelList = list(availableteams.items())
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-BayPerson", 37, 45, 30, 22, currentPos=clientObj.BayPersonPos, maxLength=len(personnelList)-3, background=True, scrollbar=True, text="Ship Available Personnel", colour="#2d3a3d")
    posx = 37
    posy = 45
    for x in range(clientObj.BayPersonPos, min(len(personnelList), clientObj.BayPersonPos + 4)):
        personnelData = personnelList[x]
        teamid = personnelData[0]
        data = personnelData[1]
        if data.get("working")[0] == "relocating":
            colour = "gray"
        else:
            colour = data.get('colour')
        GUI.IconTabletButton(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-BayPersonnel-{teamid}", posx + 1, posy + 1, 28, 5, text=data.get('Type'), subtext=data.get('Name'), icon=data.get('icon'), iconcolour=colour)
        posy += 5.1


def ShuttleBayControls(clientObj):
    name = "ShuttleBayControls_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    sbs.send_gui_button(clientObj.clientID, "", "recover-shuttle", "text: Recover Shuttle", 15, 10, 40, 14)


# shuttle consoles
def ShuttleMain(clientObj):
    name = "ShuttleMain_main"
    widgets = "3dview^fighter_control^helm_free_3d^2dview^text_waterfall"
    layoutdata = {"3dview": [0, 0, 100, 100, 0, 0, 100, 100],
                  "fighter_control": [1, 68, 20, 95, 1, 60, 20, 90],
                  "helm_free_3d": [80, 65, 100, 92, 80, 55, 100, 92],
                  "2dview": [25, 70, 75, 91, 25, 60, 75, 91],
                  "text_waterfall": [0, 20, 30, 25, 45, 0, 55, 20]}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    sbs.send_gui_image(clientObj.clientID, "", "shuttle-movement-frame", "image: ../missions/TSN Cosmos/Images/R; color: #FFBF00", -30, 0, 130, 100)
    sbs.send_gui_image(clientObj.clientID, "", "shuttle-movement-background", "image: ../missions/TSN Cosmos/Images/Box-20; color: #FFBF00", 20, 65, 80, 96)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])
    sbs.send_gui_button(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}shuttle-capture", "text: Capture Object", 80, 92, 100, 96)
    sbs.send_gui_hotkey(clientObj.clientID, "TSNSHUT", f"SHUT-shuttle-capture", "KEY_RETURN", f"Capture Hotkey for shuttles")
    sbs.send_gui_clickregion(clientObj.clientID, "", f"SHUT-shuttle-capture", "", 100, 100, 101, 101)
    if clientObj.myShuttle.JettisonTube:
        data = list(clientObj.myShuttle.JettisonTube.values())
        if isinstance(data[0], SpaceObjects.Team):
            if clientObj.myShuttle.PersonnelGo:
                colour = "Green"
            else:
                colour = "Red"
            sbs.send_gui_checkbox(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}shuttle-jumpgreenlight", f"text: Go-NoGo; state: {clientObj.myShuttle.PersonnelGo}; color: {colour}", 80, 4, 100, 8)
        else:
            sbs.send_gui_button(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}shuttle-jettisoncargo", "text: Jettison Cargo", 80, 4, 100, 8)
    if clientObj.myShuttle.PersonnelGo:
        pass


def ShuttleCargoJettison(clientObj):
    # cargo screen on the shuttle
    name = "ShuttleCargo_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)

    ShuttleCargoDeploy(clientObj)
    ShuttlePersonnelDeploy(clientObj)

    posx = 42
    posy = 70
    for item, data in clientObj.myShuttle.JettisonTube.items():
        if isinstance(data, SpaceObjects.Team):
            data = data.teamdata
            name = data.get('Name')
        else:
            name = item
        sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-JettisonTube-name-{item}", f"text: {name}; font: smallest; justify: center", posx, posy - 3, posx + 5, posy)
        sbs.send_gui_rawiconbutton(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}shuttle-jettisontube-{item}", f"icon_index: {data.get('icon')}; color: {data.get('colour')}", posx, posy, posx + 5, posy + 5)
    sbs.send_gui_text(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-JettisionTube-Title", f"text: Staging Area", posx, posy - 10, posx + 30, posy)
    sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-JettisonTube-background", "image: ../missions/TSN Cosmos/Images/Box-50; color: #ff9900", 35, 56, 60, posy + 7)

    sbs.send_gui_button(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}shuttle-capture", "text: Capture Object", 80, 4, 100, 8)


def ShuttlePersonnelDeploy(clientObj):
    # Personnel on the shuttle, that can be moved to the staging area
    Shuttle = clientObj.myShuttle
    personnelList = list(clientObj.myShuttle.Personnel.items())


    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-ShuttlePerson", 2, 13, 30, 34, text="Personnel", scrollbar=True, background=True, maxLength=len(personnelList) -3, currentPos=Shuttle.PersonnelPos, colour="#2d3a3d")
    posx = 2
    posy = 15
    for x in range(Shuttle.PersonnelPos, min(len(personnelList), Shuttle.PersonnelPos + 4)):
        slot = personnelList[x]
        personneldata = slot[1]
        name = personneldata[0]
        object = personneldata[1]
        data = object.teamdata
        GUI.IconTabletButton(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-ShuttlePersonnel-{slot[0]}", posx, posy, 30, 5, iconcolour=data.get("colour"), icon=data.get("icon"), text=data.get('Name'))
        posy += 5.1


def ShuttleCargoDeploy(clientObj):
    # Cargo on the shuttle, that can be moved to the staging area
    GUI.menuBackground(clientObj.clientID, "", f"{clientObj.clientID}-ShutCargo", 69, 15, 23, 22, background=True, text="Cargo Hold", colour="#2d3a3d")
    x = 70
    y = 16
    for space in range(clientObj.myShuttle.cargoCapacity):
        sbs.send_gui_image(clientObj.clientID, "", f"{clientObj.myShuttle.ObjectID}-ShuttleCar-background-{space}", "image: ../missions/TSN Cosmos/Images/Box-50; color: #006600", x, y, x + 5, y + 5)
        x += 5.1
        if x > 90:
            y += 5.1
            x = 70
    x = 70
    y = 16
    for key, value in clientObj.myShuttle.CargoHold.items():
        cargoData = value[1]
        icon = cargoData.get("icon")
        colour = cargoData.get("colour")
        sbs.send_gui_rawiconbutton(clientObj.clientID, "", f"icon{clientObj.myShuttle.ObjectID}-ShuttleCargo-{key}", f"icon_index: {icon}; color: {colour}", x, y, x + 5, y + 5)
        x += 5.1
        if x > 90:
            y += 5.1
            x = 70


def LifePodHelm(clientObj):
    name = "LifePodHelm_main"
    widgets = "3dview^fighter_control^helm_free_3d^2dview"
    layoutdata = {"3dview": [0, 0, 100, 100, 0, 0, 100, 100],
                  "fighter_control": [1, 68, 20, 95, 1, 60, 20, 90],
                  "helm_free_3d": [80, 65, 100, 92, 80, 55, 100, 92],
                  "2dview": [25, 70, 75, 91, 25, 60, 75, 91],
                  "text_waterfall": [45, 0, 55, 20, 45, 0, 55, 20]}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    sbs.send_gui_image(clientObj.clientID, "", "shuttle-movement-frame",
                       "image: ../missions/TSN Cosmos/Images/R; color: #FFBF00", -30, 0, 130, 100)
    sbs.send_gui_image(clientObj.clientID, "", "shuttle-movement-background",
                       "image: ../missions/TSN Cosmos/Images/Box-50; color: #FFBF00", 20, 65, 80, 96)
    if clientObj.myLayout:
        for widget in widgets.split("^"):
            if layoutdata.get(widget):
                pos = layoutdata.get(widget)
                sbs.send_client_widget_rects(clientObj.clientID, widget, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7])


def LifePodComms(clientObj):
    name = "LifePodComms_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)


def LifePodBay(clientObj):
    name = "LifePodBay_main"
    widgets = ""
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)
    sbs.send_gui_image(clientObj.clientID, "", f"lifpodBay", "image: ../missions/TSN Cosmos/Images/LifePodBay; color: white", 0, 0, 100, 100)


def MainScreen(clientObj):
    name = "MainScreen_main"
    widgets = "3dview"
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, widgets)


def DefaultStreamer(clientObj):
    name = "Default_main"
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, clientObj.widgets)
    if clientObj.displayname:
        sbs.send_gui_text(clientObj.clientID, "", "ship name", f"text: {clientObj.myShip.ObjectName}; color: white", 10, 6, 100, 100)


def StreamerControls(clientObj):
    name = "StreamerControls_main"
    layoutdata = {}
    sbs.send_client_widget_list(clientObj.clientID, name, clientObj.widgets)
    if clientObj.displayname:
        sbs.send_gui_text(clientObj.clientID, "", "ship name", f"text: {clientObj.myShip.ObjectName}; color: white", 10,
                          6, 100, 100)


shipConsoles = {

    "ShipDestroyed": {
        "subConsoles": {
            "Emergency Systems": {"subConsoleState": "on",
                                  "render": destroyedConsole}
            },
        "mainConsoleState": "on"
    },

    "Helm": {
        "subConsoles": {
            "Manoeuvre": {"subConsoleState": "on",
                          "render": StandardHelm},
            "Pilot": {"subConsoleState": "off",
                      "render": PilotHelm},
            "Jump Control": {'subConsoleState': "off",
                             "render": JumpControl}
            },
        "mainConsoleState": "off"
        },

    "Tactical": {
        "subConsoles": {
            "Weapons": {"subConsoleState": "on",
                          "render": StandardWeapons},
            "Weapon Systems": {"subConsoleState": "off",
                         "render": StandardWeaponsControls},
            "Navigation": {"subConsoleState": "off",
                           "render": StandardNavigation},

            },
        "mainConsoleState": "off"
        },

    "Engineering": {
        "subConsoles": {
            "Ship Systems": {"subConsoleState": "on",
                             "render": StandardEngineeringControls},
            "Main Engineering": {"subConsoleState": "off",
                                 "render": StandardEngineering},
            "Sys. Management": {"subConsoleState": "off",
                                 "render": EngerineeringSystemManagement},
            },
        "mainConsoleState": "off"
        },

    "Science": {
        "subConsoles": {
            "Active Sensors": {"subConsoleState": "on",
                               "render": StandardScience},
            "LRS Sensors": {"subConsoleState": "off",
                            "render": ScienceSensorSuite}
            },
        "mainConsoleState": "off"
        },

    "Operations": {
        "subConsoles": {
            "Comms": {"subConsoleState": "on",
                      "render": StandardComms},
            "Crew": {"subConsoleState": "off",
                     "render": StandardCrewManagement},
            "AMC": {"subConsoleState": "off",
                         "render": AMCConsole}
            },
        "mainConsoleState": "off"
        },

    "Shuttle Bay": {
        "subConsoles": {
            "Shuttle": {"subConsoleState": "on",
                        "render": ShuttleBay},
            "Controls": {"subConsoleState": "off",
                         "render": ShuttleBayControls},
            "Logistics": {"subConsoleState": "off",
                          "render": Logistics}
            },
        "mainConsoleState": "off"
        },

    "Docking Bay": {
        "subConsoles": {
            "Shuttle": {"subConsoleState": "on",
                        "render": ShuttleBay}
            },
        "mainConsoleState": "off"
        },

    "Pilot": {
        "subConsoles": {
            "Manoeuvre": {"subConsoleState": "on",
                              "render": StandardHelm},
            "Navigation": {"subConsoleState": "off",
                               "render": StandardNavigation},
            },
        "mainConsoleState": "off"
        },

    "Co-Pilot": {
        "subConsoles": {
            "Main Engineering": {"subConsoleState": "on",
                                     "render": StandardEngineering},
            },
        "mainConsoleState": "off"
        },

    "Cargo Ops": {
        "subConsoles": {
            "Comms": {"subConsoleState": "on",
                          "render": StandardComms},
            "Interface": {"subConsoleState": "off",
                              "render": StandardCommsInterface},
                },
        "mainConsoleState": "off"
        },

    "Int. Ops": {
        "subConsoles": {
            "Engineering": {"subConsoleState": "on",
                                 "render": OperationsEngineering},
            "Sensors": {"subConsoleState": "off",
                                 "render": StandardScience},
            "Targeting": {"subConsoleState": "off",
                                 "render": StandardWeapons},
            },
        "mainConsoleState": "off"
        },

    "Seat A": {
        "subConsoles": {
            "Helm": {"subConsoleState": "on",
                         "render": PilotHelm},
            "Sensors": {"subConsoleState": "off",
                            "render": StandardScience},
            "Navigation": {"subConsoleState": "off",
                            "render": StandardNavigation},
            "Interface": {"subConsoleState": "off",
                              "render": StandardCommsInterface}
            },
        "mainConsoleState": "off"
        },

    "Seat B": {
        "subConsoles": {
            "Engineering": {"subConsoleState": "on",
                            "render": OperationsEngineering},
            "Crew": {"subConsoleState": "off",
                     "render": StandardCrewManagement},
            "Comms": {"subConsoleState": "off",
                      "render": StandardCommsFleet},
            "Weapons": {"subConsoleState": "off",
                        "render": StandardWeapons},
            },
        "mainConsoleState": "off"
        },
    "Fire Control": {
        "subConsoles": {
            "Beam Control": {"subConsoleState": "on",
                          "render": TurretBeams},
            },
        "mainConsoleState": "off"
        },
}

otherConsoles = {
    "Server": {
        "subConsoles": {
            "Main": {"subConsoleState": "on",
                     "render": MainScreen}
        },
        "mainConsoleState": "on"
    },

    "GM Controls": {
        "subConsoles": {
            "Controls": {"subConsoleState": "on",
                         "render": GMConsoleData.GMControls},
            },
        "mainConsoleState": "on"
        },

    "Streamer": {
        "subConsoles": {
            "Default": {"subConsoleState": "on",
                         "render": DefaultStreamer},
            },
        "mainConsoleState": "on"
        },
}

commandConsoles = {
    "Flt Cpt": {
        "subConsoles": {
            "Command": {"subConsoleState": "on",
                         "render": CommandNav},
            "Mission": {"subConsoleState": "off",
                        "render": CommandMiss},
            "Ship Data": {"subConsoleState": "off",
                          "render": CommandData}
            },
        "mainConsoleState": "on"
        },

    "Captain": {
        "subConsoles": {
            "Command": {"subConsoleState": "on",
                         "render": CommandNav},
            },
        "mainConsoleState": "on"
        }
}

smallCraft = {
    "Shuttle": {
        "subConsoles": {
            "Main": {"subConsoleState": "on",
                     "render": ShuttleMain},
            "Cargo Hold": {"subConsoleState": "off",
                           "render": ShuttleCargoJettison}
        },
        "mainConsoleState": "on"
    },

    "Lifepod": {
        "subConsoles": {
            "Main": {"subConsoleState": "on",
                     "render": LifePodHelm},
            "Comms": {"subConsoleState": "off",
                      "render": LifePodComms}
        },
        "mainConsoleState": "on"
    },

    "Lifepod Bay": {
        "subConsoles": {
            "Bay": {"subConsoleState": "on",
                     "render": LifePodBay},
        },
        "mainConsoleState": "on"
    },
}

#the consoleData is a dictionary of all the main consoles and the related subconsoles
consoleData = smallCraft | commandConsoles | otherConsoles | shipConsoles
