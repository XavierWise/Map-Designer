

standardOrders = {
                "Fleet Task": "Attack",
                "Targets": ["ship", "station"],
                "Parameters": {
                    "Sensor Range": 25000,
                    "Fleet Separation": 100,
                    "Max Distance": 900,
                    "Locations": [],
                    "Support Elements": "Support Leader",
                    "Fleet Speed": 1.0,
                    "Patrol Point": 0,
                    "SpecialData": [None, None, None]
                }
            }

surrenderOrders = {
                "Fleet Task": "Surrender",
                "Targets": [],
                "Parameters": {
                    "Sensor Range": 25000,
                    "Fleet Separation": 100,
                    "Max Distance": 900,
                    "Locations": [],
                    "Support Elements": "Surrender",
                    "Fleet Speed": 0,
                    "Patrol Point": 0,
                    "SpecialData": [None, None, None]
                }
            }

carrierOrders = { #special orders, modified for carriers
                    "Fleet Task": "Carrier Operations",
                    "Targets": ["ship", "station"],
                    "Parameters": {
                        "Sensor Range": 25000,
                        "Fleet Separation": 100,
                        "Max Distance": 900,
                        "Locations": [],
                        "Support Elements": "Carrier Support",
                        "Fleet Speed": 1.0,
                        "Patrol Point": 0,
                        "SpecialData": [None, None, None]
                    }
                }

fighterOrders = {
            "Fleet Task": "Strike",
            "Targets": ["ship", "station"],
            "Parameters": {
                "Sensor Range": 12000,
                "Fleet Separation": 100,
                "Max Distance": 900,
                "Locations": [],
                "Support Elements": "Support Leader",
                "Fleet Speed": 1.0,
                "Patrol Point": 0,
                "SpecialData": [None, None, None]
            }
        }

evasiveOrders = {
            "Fleet Task": "Evade",
            "Targets": ["ship", "station"],
            "Parameters": {
                "Sensor Range": 12000,
                "Fleet Separation": 100,
                "Max Distance": 900,
                "Locations": [],
                "Support Elements": "Evade",
                "Fleet Speed": 1.0,
                "Patrol Point": 0,
                "SpecialData": [None, None, None]
            }
        }

fallbackOrders = {
            "Fleet Task": "Fall Back",
            "Targets": ["ship", "station"],
            "Parameters": {
                "Sensor Range": 12000,
                "Fleet Separation": 100,
                "Max Distance": 900,
                "Locations": [],
                "Support Elements": "Support Leader",
                "Fleet Speed": 1.0,
                "Patrol Point": 0,
                "SpecialData": [None, None, None]
            }
        }

reformOrders = {
            "Fleet Task": "Reform",
            "Targets": ["ship", "station"],
            "Parameters": {
                "Sensor Range": 25000,
                "Fleet Separation": 100,
                "Max Distance": 900,
                "Locations": [],
                "Support Elements": "Support Leader",
                "Fleet Speed": 1.0,
                "Patrol Point": 0,
                "SpecialData": [None, None, None]
            }
        }

pirateOrders = {
            "Fleet Task": "Reform",
            "Targets": ["ship", "station", "civilian", "noncombat", "cargo", "transport"],
            "Parameters": {
                "Sensor Range": 25000,
                "Fleet Separation": 100,
                "Max Distance": 900,
                "Locations": [],
                "Support Elements": "Support Leader",
                "Fleet Speed": 1.0,
                "Patrol Point": 0,
                "SpecialData": [None, None, None]
            }
        }


