
def FCS(sim, shipID):
    player = sim.get_space_object(shipID)
    blob = player.data_set
    current_throttle = blob.get("playerThrottle", 0)
    if 0.1 < current_throttle < 0.5:
        energy_value = blob.get("energy", 0)
        if energy_value < 1000:
            energy_value += 100 * blob.get("eng_control_value", 8)
            blob.set("energy", energy_value)
