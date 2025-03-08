import random
import os, sbs
from NPC_Ships import NPC_ScanData

#Script object - created by the python script, using the classes (e.g. SpaceObject)
#Sim Object - created by the Cosmos game engine.

versionNo = "1a"

CommandCodes = {
    "Fleet Commander": ["Xav24", "FLT"],
    "CiC": ["GM"],
    "Captain": ["Cap1", "Cap2", "Cap3"],
    "Streamer": ["STM"]
}

waypointDatabase = {}

terrainDatabase = {
    "Ast1. Blue": ["asteroid_crystal_blue"],
    "Ast2. Red": ["asteroid_crystal_red"],
    "Ast3. Gold": ["asteroid_crystal_yellow"],
    "Ast4. Silver": ["asteroid_crystal_silver"],
    "Ast5. Green": ["asteroid_crystal_green"],
    "Ast. Colour Rand": ["asteroid_crystal_blue", "asteroid_crystal_red", "asteroid_crystal_yellow", "asteroid_crystal_silver", "asteroid_crystal_green"],
    "Ast6. Std": ["plain_asteroid_6"],
    "Ast7. Std": ["plain_asteroid_7"],
    "Ast8. Std": ["plain_asteroid_8"],
    "Ast9. Std": ["plain_asteroid_9"],
    "Ast10 Std": ["plain_asteroid_10"],
    "Ast11 Std": ["plain_asteroid_11"],
    "Ast. Std Rand": ["plain_asteroid_6", "plain_asteroid_7", "plain_asteroid_8", "plain_asteroid_9", "plain_asteroid_10", "plain_asteroid_11"],
    "Nebula": "Nebula",
    "Mine": "Mine"
}

asteroidDatabase = {
    "Ast1. Blue": {"Type": "Denebite", "Crystal Density": random.randint(50, 100)},
    "Ast2. Red": {"Type": "Volitile", "Crystal Density": random.randint(50, 100)},
    "Ast3. Gold": {"Type": "Gold", "Crystal Density": random.randint(50, 100)},
    "Ast4. Silver": {"Type": "Silver", "Crystal Density": random.randint(50, 100)},
    "Ast5. Green": {"Type": "Green", "Crystal Density": random.randint(50, 100)}
}

# AMC = Advanced Manufacturing Complex
tier1AMC = {
    "Homing": ["Warhead", "Torpedo Casing", "Guidance System"],
    "Mine": ["Casing", "High Yield Warhead", "Sensor Suite"],
    "Nuke": ["High Yield Warhead", "Torpedo Casing", "Guidance System"],
    "Sensor Buoy": ["Sensor Suite", "Casing", "Transmitter"],
    "Comms Relay": ["Transmitter", "Casing", "Receiver", "Analysis Suite"],
    "Aid Package": ["Medical Supplies", "Power Relay", "Repair Materials"]
}

tier2AMC = {
    "Power Relay": ["Denebite Crystals", "Micro Controller", "Container"],
    "Repair Materials": ["Tharium Plating", "Iso B Circuit"],
    "Casing": ["Tharium", "Alerite"],
    "Torpedo Casing": ["Casing", "Micro Controller", "Tharium"],
    "High Yield Warhead": ["Gredian", "Reisium", "Denebite"],
    "Warhead": ["Gredian", "Reisium"],
    "Guidance System": ["Micro Controller", "Iso B Circuit", "Tharium"]
}

tier2AMC.update(tier1AMC)

tier3AMC = {
    "Denebite Crystals": ["Denebite", "Aegirine"],
    "Tharium Plating": ["Tharium", "Iron", "Alerite"],
    "Iso B Circuit": ["Tharium", "Nuidinium"],
    "Micro Controller": ["Ashfilum", "Nuidinium", "Tharium"],
}

tier3AMC.update(tier2AMC)

rawMaterials = {
    "Iron": {
        "icon": 305,
        "colour": "#ccffff",
        "count": 0
    },
    "Tharium": {
        "icon": 309,
        "colour": "#ccffff",
        "count": 0
    },
    "Reisium": {
        "icon": 308,
        "colour": "#ccffff",
        "count": 0
    },
    "Alerite": {
        "icon": 301,
        "colour": "#ccffff",
        "count": 0
    },
    "Cabrite": {
        "icon": 303,
        "colour": "#ccffff",
        "count": 0
    },
    "Ashfilum": {
        "icon": 302,
        "colour": "#ccffff",
        "count": 0
    },
    "Denebite": {
        "icon": 304,
        "colour": "#ccffff",
        "count": 0
    },
    "Aegirine": {
        "icon": 300,
        "colour": "#ccffff",
        "count": 0
    },
    "Nuidinium": {
        "icon": 307,
        "colour": "#ccffff",
        "count": 0
    },
    "Gredian": {
        "icon": 306,
        "colour": "#ccffff",
        "count": 0
    }
}

shipItems = {
    "AMC": {
        "icon": 261, #default symbol for AMC2
        "colour": "#00b300",
        "count": 0
    },
    "Life Support": {
        "icon": 280,
        "colour": "#00b300",
        "count": 0
    },
    "Artificial Grav": {
        "icon": 263,
        "colour": "#00b300",
        "count": 0
    },
    "Targeting Array": {
        "icon": 216,
        "colour": "#00b300",
        "count": 0
    },
    "FCS": {
        "icon": 54, #to update
        "colour": "#ccffff",
        "count": 0
    }
}

#update the commodities database to match items in the tier1 AMC system
commoditiesDatabase = {
    "Comms Relay": {
        "icon": 209,
        "colour": "#ccffff",
        "count": 0,
    },
    "Sensor Buoy": {
        "icon": 219,
        "colour": "#ccffff",
        "count": 0,
    },
    "Black Box": {
        "icon": 36,
        "colour": "#ccffff",
        "count": 0,
    },
    "Aid Package": {
        "icon": 206,
        "colour": "#ccffff",
        "count": 0,
    },
    "Repair Materials": {
        "icon": 218,
        "colour": "#ccffff",
        "count": 0,
    },
    "Medical Supplies": {
        "icon": 208,
        "colour": "#ccffff",
        "count": 0
    },
    "Iso B Circuit": {
        "icon": 212,
        "colour": "#ccffff",
        "count": 0
    },
    "Container": {
        "icon": 221,
        "colour": "#ccffff",
        "count": 0
    },
    "Micro Controller": {
        "icon": 215,
        "colour": "#ccffff",
        "count": 0
    },
    "High Yield Warhead": {
        "icon": 211,
        "colour": "#ccffff",
        "count": 0
    },
    "Warhead": {
        "icon": 210,
        "colour": "#ccffff",
        "count": 0
    },
    "Torpedo Casing": {
        "icon": 245,
        "colour": "#ccffff",
        "count": 0,
    },
    "Guidance System": {
        "icon": 200,
        "colour": "#ccffff",
        "count": 0,
    },
    "Denebite Crystals": {
        "icon": 304,
        "colour": "#ccffff",
        "count": 0,
    },
    "Tharium Plating": {
        "icon": 214,
        "colour": "#ccffff",
        "count": 0,
    },
    "Sensor Suite": {
        "icon": 213,
        "colour": "#ccffff",
        "count": 0
    },
    "Casing": {
        "icon": 220,
        "colour": "#ccffff",
        "count": 0
    },
    "Transmitter": {
        "icon": 11, #to update
        "colour": "#ccffff",
        "count": 0
    },
    "Receiver": {
        "icon": 34, #to update
        "colour": "#ccffff",
        "count": 0
    },
    "Power Relay": {
        "icon": 205,
        "colour": "#ccffff",
        "count": 0,
    },
    "Analysis Suite": {
        "icon": 30, #to update
        "colour": "#ccffff",
        "count": 0
    }
}

ordnanceDatabase = {
    "Homing": {
        "icon": 241,
        "colour": "#0077ff",
        "count": 0,

        "speed": 40,
        "lifetime": 10,
        "flare_color": "white",
        "trail_color": "white",
        "warhead": ["standard", 0],
        "damage": 55,
        "explosion_size": 10,
        "explosion_color": "fire",
        "behavior": "homing",
        "energy_conversion_value": 0
    },
    "Nuke": {
        "icon": 240,
        "colour": "red",
        "count": 0,

        "speed": 40,
        "lifetime": 10,
        "flare_color": "white",
        "trail_color": "#99f",
        "warhead": ["blast", 2000],
        "damage": 8,
        "explosion_size": 20,
        "explosion_color": "fire",
        "behavior": "homing",
        "energy_conversion_value": 0
    },
    "EMP": {
        "icon": 243,
        "colour": "yellow",
        "count": 0,

        "speed": 40,
        "lifetime": 10,
        "flare_color": "yellow",
        "trail_color": "#99f",
        "warhead": ["blast, reduce_shields", 2000],
        "damage": 50,
        "explosion_size": 20,
        "explosion_color": "#11F",
        "behavior": "homing",
        "energy_conversion_value": 0
    },
    "Mine": {
        "icon": 244,
        "colour": "#0ed100",
        "count": 0,

        "speed": 40,
        "lifetime": 10,
        "flare_color": "white",
        "trail_color": "white",
        "warhead": ["blast", 2000],
        "damage": 16,
        "explosion_size": 20,
        "explosion_color": "fire",
        "behavior": "mine",
        "energy_conversion_value": 0
    }
}

masterDatabase = {}
masterDatabase.update(commoditiesDatabase)
masterDatabase.update(rawMaterials)
masterDatabase.update(shipItems)
masterDatabase.update(ordnanceDatabase)

factions = {
    "Hegemony": ["Torgoth", "Arvonian", "Kralien", "Skaraan"],
    "USFP": ["TSN", "Hjorden", "USFP"],
    "Pirate": ["Euphini", "Skull"]
}

usfpCivilians = {
    "transport_ship": {
        "tags": ["ship", "civilian", "usfp", "noncombat", "transport"],
        "systems": ["Manoeuvre", "Impulse", "Shields"],
        "race": "USFP",
        "type": "Transport Vessel",
        "scandata": NPC_ScanData.genericScanData
    },
    "luxury_liner": {
        "tags": ["ship", "civilian", "usfp", "noncombat", "cargo", "transport"],
        "systems": ["Manoeuvre", "Impulse", "Shields"],
        "race": "USFP",
        "type": "Luxury Liner",
        "scandata": NPC_ScanData.genericScanData
    },
    "cargo_ship": {
        "tags": ["ship", "civilian", "usfp", "noncombat", "cargo"],
        "systems": ["Manoeuvre", "Impulse", "Shields"],
        "race": "USFP",
        "type": "Cargo Vessel",
        "scandata": NPC_ScanData.genericScanData
    },
    "science_ship": {
        "tags": ["ship", "civilian", "usfp", "noncombat"],
        "systems": ["Manoeuvre", "Impulse", "Shields"],
        "race": "USFP",
        "type": "Science Vessel",
        "scandata": NPC_ScanData.genericScanData
    },
}

kralienShips = {
    "kralien_cruiser": {
        "tags": ["hegemony", "light", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Kralien",
        "type": "Cruiser",
        "scandata": NPC_ScanData.kralienScanData
    },
    "kralien_battleship": {
        "tags": ["hegemony", "medium", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Kralien",
        "type": "Battleship",
        "scandata": NPC_ScanData.kralienScanData
    },
    "kralien_dreadnought": {
        "tags": ["hegemony", "heavy", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Kralien",
        "type": "Dreadnought",
        "scandata": NPC_ScanData.kralienScanData
    },
}

skaraanShips = {
    "skaraan_defiler": {
        "tags": ["hegemony", "light", "combat", "ship", "elite"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Skaraan",
        "type": "Defiler",
        "scandata": NPC_ScanData.genericScanData
    },
    "skaraan_executer": {
        "tags": ["hegemony", "medium", "combat", "ship", "elite"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Skaraan",
        "type": "Executer",
        "scandata": NPC_ScanData.genericScanData
    },
    "skaraan_enforcer": {
        "tags": ["hegemony", "heavy", "combat", "ship", "elite"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Skaraan",
        "type": "Enforcer",
        "scandata": NPC_ScanData.genericScanData
    },
}

torgothShips = {
    "torgoth_destroyer": {
        "tags": ["hegemony", "support", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Torgoth",
        "type": "Destroyer",
        "scandata": NPC_ScanData.torgothScanData
    },
    "torgoth_goliath": {
        "tags": ["hegemony", "light", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Torgoth",
        "type": "Goliath",
        "scandata": NPC_ScanData.torgothScanData
    },
    "torgoth_leviathan": {
        "tags": ["hegemony", "medium", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Torgoth",
        "type": "Leviathan",
        "scandata": NPC_ScanData.torgothScanData
    },
    "torgoth_behemoth": {
        "tags": ["hegemony", "heavy", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Torgoth",
        "type": "Behemoth",
        "scandata": NPC_ScanData.torgothScanData
    },
}

arvonianShips = {
    "arvonian_fighter": {
        "tags": ["hegemony", "fighter", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Beams"],
        "race": "Arvonian",
        "type": "Fighter",
        "scandata": NPC_ScanData.genericScanData
    },
    "arvonian_destroyer": {
        "tags": ["hegemony", "support", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Arvonian",
        "type": "Destroyer",
        "scandata": NPC_ScanData.genericScanData
    },
    "arvonian_light_carrier": {
        "tags": ["hegemony", "medium", "combat", "ship", "carrier"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Beams"],
        "race": "Arvonian",
        "type": "Light Carrier",
        "scandata": NPC_ScanData.genericScanData
    },
    "arvonian_carrier": {
        "tags": ["hegemony", "heavy", "combat", "ship", "carrier"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Beams"],
        "race": "Arvonian",
        "type": "Carrier",
        "scandata": NPC_ScanData.genericScanData
    },
}

skullShips = {
    "pirate_fighter": {
        "tags": ["pirate", "fighter", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Skull",
        "type": "Fighter",
        "scandata": NPC_ScanData.genericScanData
    },
    "pirate_longbow": {
        "tags": ["pirate", "light", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Skull",
        "type": "Longbow",
        "scandata": NPC_ScanData.genericScanData
    },
    "pirate_strongbow": {
        "tags": ["pirate", "medium", "combat", "ship"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Skull",
        "type": "Strongbow",
        "scandata": NPC_ScanData.genericScanData
    },
    "pirate_brigantine": {
        "tags": ["pirate", "heavy", "combat", "ship", "carrier"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "Skull",
        "type": "Brigantine",
        "scandata": NPC_ScanData.genericScanData
    },
}

tsnShips = {
    "tsn_fighter": {
        "tags": ["fighter", "combat", "ship", "usfp"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "TSN",
        "type": "Fighter",
        "scandata": NPC_ScanData.genericScanData
    },
    "tsn_light_cruiser": {
        "tags": ["ship", "combat", "tsn"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "TSN",
        "type": "Light Cruiser",
        "scandata": NPC_ScanData.genericScanData
    },
    "tsn_battle_cruiser": {
        "tags": ["ship", "combat", "tsn"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "TSN",
        "type": "Battle Cruiser",
        "scandata": NPC_ScanData.genericScanData
    },
    "tsn_destroyer": {
        "tags": ["ship", "combat", "tsn"],
        "systems": ["Manoeuvre", "Impulse", "Shields", "Torpedoes", "Beams"],
        "race": "TSN",
        "type": "Destroyer",
        "scandata": NPC_ScanData.genericScanData
    },
}

euphiniShips = {}
hjordenShips = {}

usfpStations = {
    "starbase_civil": {
        "tags": ["station", "usfp", "civilian", "cargo"],
        "type": "Civilian",
        "race": 'USFP',
        "scandata": NPC_ScanData.genericScanData,
        "Teams":    {"Medics": 2},
        "Shuttles": {"Cargo Shuttle": 1,
                     "Transport Shuttle": 1
                     },
    },
    "starbase_industry": {
        "tags": ["station", "usfp", "civilian", "cargo"],
        "type": "Industrial",
        "race": 'USFP',
        "scandata": NPC_ScanData.genericScanData,
        "Teams":    {"DamCon": 6,
                     "Medics": 2},
        "Shuttles": {"Cargo Shuttle": 1,
                     "Transport Shuttle": 1
                     },
    },
    "starbase_science": {
        "tags": ["station", "usfp", "civilian"],
        "type": "Science",
        "race": 'USFP',
        "scandata": NPC_ScanData.genericScanData,
        "Teams":    {"Medics": 2},
        "Shuttles": {"Ranger": 1,
                     "Cargo Shuttle": 1,
                     "Transport Shuttle": 1
                     },
    },
    "usfp_industrial_1": {
        "tags": ["station", "usfp", "civilian", "industrial"],
        "type": "Industrial",
        "race": 'USFP',
        "scandata": NPC_ScanData.genericScanData,
        "Teams": {"Medics": 2},
        "Shuttles": {"Ranger": 1,
                     "Cargo Shuttle": 1,
                     "Transport Shuttle": 1
                     },
    },
    "usfp_storage_1": {
        "tags": ["station", "usfp", "civilian", "industrial"],
        "type": "Industrial",
        "race": 'USFP',
        "scandata": NPC_ScanData.genericScanData,
        "Teams": {"Medics": 2},
        "Shuttles": {"Ranger": 1,
                     "Cargo Shuttle": 1,
                     "Transport Shuttle": 1
                     },
    }
}

tsnStations = {
    "starbase_command": {
        "tags": ["station", "usfp"],
        "type": "Command",
        "race": 'TSN',
        "scandata": NPC_ScanData.genericScanData,
        "Teams":    {"DamCon": 6,
                     "Medics": 4,
                     "Marines": 2,
                     "Combat Engineers": 4,
                     },
        "Shuttles": {"Ranger": 3,
                     "Cargo Shuttle": 2,
                     "Fighter": 8
                     },
    },
}

arvonianStations = {
    "starbase_arvonian": {
        "tags": ["station", "hegemony"],
        "type": "Command",
        "race": 'Arvonian',
        "scandata": NPC_ScanData.genericScanData,
        "Teams":    {},
        "Shuttles": {},
    },
}

torgothStations = {
    "starbase_torgoth": {
        "tags": ["station", "hegemony"],
        "type": "Command",
        "race": 'Torgoth',
        "scandata": NPC_ScanData.genericScanData,
        "Teams":    {},
        "Shuttles": {},
    }
}

skaraanStations = {}

kralienStations = {
    "starbase_kralien": {
        "tags": ["station", "hegemony"],
        "type": "Command",
        "race": 'Kralien',
        "scandata": NPC_ScanData.genericScanData,
        "Teams":    {},
        "Shuttles": {},
    },
    "hegemony_generator": {
        "tags": ["station", "hegemony"],
        "type": "Generator",
        "race": 'Kralien',
        "scandata": NPC_ScanData.genericScanData,
        "Teams": {},
        "Shuttles": {},
    },
}

hjordenStations = {}

euphiniStations = {
    "pirate_military_base": {
        "tags": ["station", "pirate"],
        "type": "Command",
        "race": 'Euphini',
        "scandata": NPC_ScanData.genericScanData,
        "Teams": {},
        "Shuttles": {},
    },
}

skullStations = {}

infrastructure = {
    "jump_node": {
        "tags": ["node"],
        "type": "Jump Node",
        "race": "USFP",
        "scandata": NPC_ScanData.genericScanData

    }
}

shipProperties = usfpCivilians | kralienShips | skaraanShips | torgothShips | arvonianShips | skullShips | tsnShips | euphiniShips | hjordenShips
stationProperties = usfpStations | arvonianStations | kralienStations | torgothStations | tsnStations | skaraanStations | hjordenStations | euphiniStations | skullStations
allProperties = shipProperties | stationProperties | infrastructure

eliteabilities = ["elite_drone_launcher", "elite_main_scn_invis"]


#compiling in game database of all shipData.json entries
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

TagsDatabase = set()
for object, data in allProperties.items():
    tags = data.get("tags")
    for tag in tags:
        TagsDatabase.add(tag)

shuttleNames = {
    "TSN":
        ["Apollo",
        "Arcturus",
        "Atlas",
        "Andromeda",
        "Aurora",
        "Antares",
        "Astra",
        "Alpha",
        "Archer",
        "Aegis",
        "Astraeus",
        "Altair",
        "Argo",
        "Aether",
        "Astrid",
        "Avalon",
        "Alcyone",
        "Arcadia",
        "Artemis",
        "Aurorae",
        "Borealis",
        "Banshee",
        "Bastion",
        "Bellatrix",
        "Boreas",
        "Beacon",
        "Bravo",
        "Blaze",
        "Bluebird",
        "Brilliance",
        "Bolt",
        "Balder",
        "Beta",
        "Borealis",
        "Blitz",
        "Buccaneer",
        "Brimstone",
        "Bravado",
        "Barbarian",
        "Boomerang",
        "Cosmos",
        "Celestial",
        "Comet",
        "Cygnus",
        "Centauri",
        "Corona",
        "Chariot",
        "Cyclone",
        "Challenger",
        "Constellation",
        "Calypso",
        "Colossus"
        "Ceres",
        "Celestia",
        "Charon",
        "Cypher",
        "Conquest",
        "Crusader",
        "Catalyst",
        "Cerberus",
        "Dauntless",
        "Discovery",
        "Dragon",
        "Destiny",
        "Diligence",
        "Draco",
        "Dione",
        "Dawn",
        "Delphinus",
        "Delphine",
        "Dominator",
        "Defender",
        "Daring",
        "Dynamo",
        "Draco",
        "Descent",
        "Demeter",
        "Diamond",
        "Defiance",
        "Divinity",
        "Endeavour",
        "Enterprise",
        "Equinox",
        "Eclipse",
        "Elara",
        "Eos",
        "Electra",
        "Excalibur",
        "Elysium",
        "Ember",
        "Emissary",
        "Echo",
        "Eridanus",
        "Epiphany",
        "Eternal",
        "Explorer",
        "Excelsior",
        "Ecliptic",
        "Ethereal",
        "Empyrean"]
}

EngineeringPowerSliderDatabase = {
    0: "Beams",
    1: "Torps",
    2: "Impulse",
    3: "Warp",
    4: "Maneuver",
    5: "Sensors",
    6: "F. Shield",
    7: "R. Shield"
}

EngineeringCoolantDatabase = {
    0: "Weapons",
    1: "Engines",
    2: "Sensors",
    3: "Shields"
}

hotkeys = ["KEY_0",
    "KEY_1",
    "KEY_2",
    "KEY_3",
    "KEY_4",
    "KEY_5",
    "KEY_6",
    "KEY_7",
    "KEY_8",
    "KEY_9",
    "KEY_A",
    "KEY_B",
    "KEY_C",
    "KEY_D",
    "KEY_E",
    "KEY_F",
    "KEY_G",
    "KEY_H",
    "KEY_I",
    "KEY_J",
    "KEY_K",
    "KEY_L",
    "KEY_M",
    "KEY_N",
    "KEY_O",
    "KEY_P",
    "KEY_Q",
    "KEY_R",
    "KEY_S",
    "KEY_T",
    "KEY_U",
    "KEY_V",
    "KEY_W",
    "KEY_X",
    "KEY_Y",
    "KEY_Z",
    "KEY_NUMPAD0",
    "KEY_NUMPAD1",
    "KEY_NUMPAD2",
    "KEY_NUMPAD3",
    "KEY_NUMPAD4",
    "KEY_NUMPAD5",
    "KEY_NUMPAD6",
    "KEY_NUMPAD7",
    "KEY_NUMPAD8",
    "KEY_NUMPAD9"]
