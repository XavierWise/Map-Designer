
# to add a new fleettype, simply update the faction's fleettypes database

# to add a new faction, first add it to the factions database and then list the races in the faction
# next, create a fleettypes database for the faction and update the masterFleettypes database
import tsn_databases
from Objects import OtherObjects

factions = tsn_databases.factions

#each type of fleet available to each faction
Kralienfleettypes = {
    "Kralien Light": {
        "name": "Kralien Light",
        "ships": ["kralien_cruiser"],
        "fleetsize": 3,
                     },
    "Kralien Medium": {
        "name": "Kralien Medium",
        "ships": ["kralien_cruiser", "kralien_battleship", "kralien_dreadnought"],
        "fleetsize": 6,
                    },
    "Kralien Heavy": {
        "name": "Kralien Heavy",
        "ships": ["kralien_cruiser", "kralien_battleship", "kralien_dreadnought"],
        "fleetsize": 9,
    },
}

Torgothfleettypes = {
    "Torgoth Light": {
        "name": "Torgoth Light",
        "ships":    ["torgoth_destroyer", "torgoth_goliath", "torgoth_leviathan"],
        "fleetsize": 2
                    },
    "Torgoth Heavy": {
        "name": "Torgoth Heavy",
        "ships":    ["torgoth_goliath", "torgoth_leviathan", "torgoth_behemoth"],
        "fleetsize": 4
    },
}

Arvonianfleettypes = {
    "Arvonian Carrier": {
        "name": "Arv. Carrier",
        "ships": ["arvonian_light_carrier", "arvonian_carrier"],
        "fleetsize": 2
    }
}

TSNfleettypes = {
    "TSN Light": {
        "name": "TSN Lt.",
        "ships": ["tsn_destroyer"],
        "fleetsize": 2
    },
}

USFPfleettypes = {
    "USFP Transport": {
        "name": "Transport",
        "ships": ["transport_ship"],
        "fleetsize": 1
    },
    "USFP Cargo": {
        "name": "Cargo",
        "ships": ["cargo_ship"],
        "fleetsize": 1
    },
}

Skaraanfleettypes = {
    "Skaraan Light": {
        "name": "Skaraan Lt.",
        "ships": ["skaraan_defiler"],
        "fleetsize": 2
    },
    "Skaraan Medium": {
        "name": "Skaraan Med.",
        "ships": ["skaraan_defiler", "skaraan_executor"],
        "fleetsize": 3
    },
    "Skaraan Heavy": {
        "name": "Skaraan Hvy.",
        "ships": ["skaraan_enforcer", "skaraan_executor"],
        "fleetsize": 3
    }
}

Hjordenfleettypes = {}
Euphinifleettypes = {}
Skullfleettypes = {}

masterFleetTypes = {
    "Kralien": Kralienfleettypes,
    "Torgoth": Torgothfleettypes,
    "Arvonian": Arvonianfleettypes,
    "TSN": TSNfleettypes,
    "Skaraan": Skaraanfleettypes,
    "Hjorden": Hjordenfleettypes,
    "Euphini": Euphinifleettypes,
    "Skull": Skullfleettypes,
    "USFP": USFPfleettypes
}

masterShipTypes = {
    "Kralien": tsn_databases.kralienShips,
    "Torgoth": tsn_databases.torgothShips,
    "Arvonian": tsn_databases.arvonianShips,
    "TSN": tsn_databases.tsnShips,
    "Skaraan": tsn_databases.skaraanShips,
    "Hjorden": tsn_databases.hjordenShips,
    "Euphini": tsn_databases.euphiniShips,
    "Skull": tsn_databases.skullShips,
    "USFP": tsn_databases.usfpCivilians
}

otherObjectsDatabase = {
    "Marines": OtherObjects.MarineTeam,
    "Medics": OtherObjects.MedicTeam,
    "DamCon": OtherObjects.DamConTeam,
    "Combat Engineers": OtherObjects.CombatEngTeam,
    "Evacuees": OtherObjects.EvacueeTeam
}

for item in tsn_databases.masterDatabase.keys():
    if item == "Comms Relay":
        otherObjectsDatabase.update({item: OtherObjects.CommsRelay})
    elif item == "Sensor Buoy":
        otherObjectsDatabase.update({item: OtherObjects.SensorBuoy})
    else:
        otherObjectsDatabase.update({item: OtherObjects.CargoPod})

masterStationTypes = {
    "USFP": tsn_databases.usfpStations,
    "Kralien": tsn_databases.kralienStations,
    "Torgoth": tsn_databases.torgothStations,
    "Arvonian": tsn_databases.arvonianStations,
    "TSN": tsn_databases.tsnStations,
    "Skaraan": tsn_databases.skaraanStations,
    "Hjorden": tsn_databases.hjordenStations,
    "Euphini": tsn_databases.euphiniStations,
    "Skull": tsn_databases.skullStations
}

terrainDatabase = {}
